from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from . import database
import sqlite3
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Document Analyzer")

# Set default database path
app.state.db_path = "docs.db"

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    try:
        # Create tables if they don't exist
        conn = sqlite3.connect(app.state.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                topic TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

class DocumentBase(BaseModel):
    content: str
    topic: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class DocumentUpdate(BaseModel):
    content: Optional[str] = None
    topic: Optional[str] = None

@app.post("/documents/", response_model=Document, status_code=201)
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

@app.get("/documents/", response_model=List[Document])
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

@app.put("/documents/{document_id}", response_model=Document)
async def update_document(document_id: int, document: DocumentUpdate):
    """Update a specific document by ID."""
    # First check if document exists
    current_doc = database.load_document(document_id, app.state.db_path)
    if not current_doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Update the document with new values, keeping old values if new ones aren't provided
    content = document.content if document.content is not None else current_doc[0]
    topic = document.topic if document.topic is not None else current_doc[1]
    
    database.update_document(document_id, content, topic, app.state.db_path)
    
    # Fetch and return updated document
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

