from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from . import database
from .config import get_openai_client
import sqlite3
import logging

database.init_db()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Document Analyzer")

app.mount("/static", StaticFiles(directory="src/frontend"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (use with caution in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Set default database path
app.state.db_path = "src/database/docs.db"

class DocumentCreate(BaseModel):
    content: str
    topic: Optional[str] = None

class DocumentUpdate(BaseModel):
    content: Optional[str] = None
    topic: Optional[str] = None

class Document(DocumentCreate):
    id: int
    created_at: datetime
    updated_at: datetime

class DocumentAnalysis(BaseModel):
    topic: str
    summary: str

@app.post("/documents/{doc_id}/analyze", response_model=DocumentAnalysis)
async def analyze_document(doc_id: int):
    """Analyze a document using OpenAI."""
    try:
        result = database.load_document(doc_id, app.state.db_path)
        if not result:
            raise HTTPException(status_code=404, detail="Document not found")
        
        content, current_topic, _, _ = result
        
        if not content or len(content.strip()) < 10:
            raise HTTPException(status_code=400, detail="Document content is too short for analysis")
        
        client = get_openai_client()
        
        prompt = f"""Please analyze the following text carefully and provide:
        1. A specific, descriptive topic (1-3 words)
        2. A comprehensive summary (3-4 sentences) that captures the main points, key arguments, or central themes.

        Text to analyze:
        {content}

        Please ensure your response follows this exact format:
        Topic: <concise topic>
        Summary: <detailed summary>
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a precise document analyzer. Provide specific, concrete analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        ai_response = response.choices[0].message.content
        
        try:
            topic_line = next(line for line in ai_response.split('\n') if line.startswith('Topic:'))
            summary_line = next(line for line in ai_response.split('\n') if line.startswith('Summary:'))
            
            topic = topic_line.replace('Topic:', '').strip()
            summary = summary_line.replace('Summary:', '').strip()
            
            if not topic or not summary:
                raise ValueError("Empty topic or summary")
                
        except (StopIteration, ValueError) as e:
            logger.error(f"Error parsing OpenAI response: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to parse analysis results")
        
        if not current_topic:
            database.update_document(doc_id, content, topic, app.state.db_path)
        
        return DocumentAnalysis(topic=topic, summary=summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents", response_model=Document, status_code=201)
async def create_document(document: DocumentCreate):
    """Create a new document."""
    try:
        doc_id = database.store_document(document.content, document.topic, app.state.db_path)
        result = database.load_document(doc_id, app.state.db_path)
        if result:
            content, topic, created_at, updated_at = result
            return Document(
                id=doc_id,
                content=content,
                topic=topic,
                created_at=created_at,
                updated_at=updated_at
            )
        raise HTTPException(status_code=500, detail="Failed to create document")
    except Exception as e:
        logger.error(f"Error creating document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model=List[Document])
async def read_documents():
    """Retrieve all documents."""
    try:
        results = database.load_documents(app.state.db_path)
        return [
            Document(
                id=id,
                content=content,
                topic=topic,
                created_at=created_at,
                updated_at=updated_at
            )
            for id, content, topic, created_at, updated_at in results
        ]
    except Exception as e:
        logger.error(f"Error reading documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{document_id}", response_model=Document)
async def read_document(document_id: int):
    """Retrieve a specific document by ID."""
    try:
        result = database.load_document(document_id, app.state.db_path)
        if not result:
            raise HTTPException(status_code=404, detail="Document not found")
        content, topic, created_at, updated_at = result
        return Document(
            id=document_id,
            content=content,
            topic=topic,
            created_at=created_at,
            updated_at=updated_at
        )
    except Exception as e:
        logger.error(f"Error reading document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/documents/{document_id}", response_model=Document)
async def update_document(document_id: int, document: DocumentUpdate):
    """Update a specific document by ID."""
    try:
        current_doc = database.load_document(document_id, app.state.db_path)
        if not current_doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        content = document.content if document.content is not None else current_doc[0]
        topic = document.topic if document.topic is not None else current_doc[1]
        
        database.update_document(document_id, content, topic, app.state.db_path)
        
        updated_doc = database.load_document(document_id, app.state.db_path)
        if updated_doc:
            content, topic, created_at, updated_at = updated_doc
            return Document(
                id=document_id,
                content=content,
                topic=topic,
                created_at=created_at,
                updated_at=updated_at
            )
        raise HTTPException(status_code=500, detail="Failed to update document")
    except Exception as e:
        logger.error(f"Error updating document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_id}", status_code=204)
async def delete_document(document_id: int):
    """Delete a specific document by ID."""
    try:
        result = database.load_document(document_id, app.state.db_path)
        if not result:
            raise HTTPException(status_code=404, detail="Document not found")
        
        database.delete_document(document_id, app.state.db_path)
        return  # 204 No Content automatically
    except Exception as e:
        logger.error(f"Error deleting document {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
