from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Document Analyzer")

class Document(BaseModel):
    content: str
    topic: Optional[str] = None

class FeedbackResponse(BaseModel):
    feedback: str
    grade: float
    suggestions: list[str]

@app.post("/analyze", response_model=FeedbackResponse)
async def analyze_document(document: Document):
    try:
        # Add your LLM integration here
        # This is a placeholder response
        return FeedbackResponse(
            feedback="Document received for analysis",
            grade=0.0,
            suggestions=["Add more detail", "Check grammar"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)