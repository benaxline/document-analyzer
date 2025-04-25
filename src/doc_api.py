from fastapi import FastAPI, HTTPException
from .config import Settings, get_settings
from pydantic import BaseModel, Field
from typing import Optional, List
import openai
import os
from dotenv import load_dotenv
from uuid import UUID, uuid4
from datetime import datetime

# Load environment variables
# load_dotenv()

app = FastAPI(title="Document Analyzer")

class DocumentBase(BaseModel):
    content: str
    topic: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class DocumentUpdate(BaseModel):
    content: Optional[str] = None
    topic: Optional[str] = None

class FeedbackResponse(BaseModel):
    feedback: str
    grade: float
    suggestions: List[str]

# in-memory storage
documents: dict[UUID, Document] = {}

# CRUD operations
@app.post("/documents/", response_model=Document, status_code=201)
async def create_document(document: DocumentCreate):
    """
    Create a new document.
    """
    new_document = Document(
        content=document.content,
        topic=document.topic,
    )
    documents[new_document.id] = new_document
    return new_document

@app.get("/documents/", response_model=List[Document])
async def read_documents():
    """
    Retrieve all documents.
    """
    return list(documents.values())

@app.get("/documents/{document_id}", response_model=Document)
async def read_document(document_id: UUID):
    """
    Retrieve a specific document by ID.
    """
    if document_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    return documents[document_id]

@app.put("/documents/{document_id}", response_model=Document)
async def update_document(document_id: UUID, document: DocumentUpdate):
    """
    Update a specific document by ID.
    """
    if document_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    
    stored_document = documents[document_id]
    update_data = document.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(stored_document, field, value)

    stored_document.updated_at = datetime.now()
    return stored_document

@app.delete("/documents/{document_id}", status_code=204)
async def delete_document(document_id: UUID):
    """
    Delete a specific document by ID.
    """
    if document_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")
    del documents[document_id]

@app.post("/documents/{document_id}/analyze", response_model=FeedbackResponse)
async def analyze_document(document_id: UUID):
    """
    Analyze a specific document by ID.
    """
    if document_id not in documents:
        raise HTTPException(status_code=404, detail="Document not found")

    document = documents[document_id]
    try:
        # TODO: openai shit
        return FeedbackResponse(
            feedback=f"Analysis of document: {document.topic if document.topic else 'Untitled'}",
            grade=0.0,
            suggestions=["Add more detail", "Check grammar", "Check spelling", "Check punctuation"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

