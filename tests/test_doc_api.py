from fastapi.testclient import TestClient
from src.doc_api import app
import pytest
from uuid import UUID

client = TestClient(app)

@pytest.fixture
def sample_document():
    """Create a sample document and return its data"""
    document_data = {
        "content": "This is a test document",
        "topic": "testing"
    }
    response = client.post("/documents/", json=document_data)
    return response.json()

def test_create_document():
    """Test document creation"""
    document_data = {
        "content": "Test content",
        "topic": "Test topic"
    }
    response = client.post("/documents/", json=document_data)
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == document_data["content"]
    assert data["topic"] == document_data["topic"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_read_documents(sample_document):
    """Test getting all documents"""
    response = client.get("/documents/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(d["id"] == sample_document["id"] for d in data)

def test_read_document(sample_document):
    """Test getting a specific document"""
    response = client.get(f"/documents/{sample_document['id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_document["id"]
    assert data["content"] == sample_document["content"]
    assert data["topic"] == sample_document["topic"]

def test_read_nonexistent_document():
    """Test getting a document that doesn't exist"""
    non_existent_id = "123e4567-e89b-12d3-a456-426614174000"
    response = client.get(f"/documents/{non_existent_id}")
    assert response.status_code == 404

def test_update_document(sample_document):
    """Test updating a document"""
    update_data = {
        "content": "Updated content",
        "topic": "Updated topic"
    }
    response = client.put(
        f"/documents/{sample_document['id']}", 
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == update_data["content"]
    assert data["topic"] == update_data["topic"]
    assert data["id"] == sample_document["id"]

def test_update_nonexistent_document():
    """Test updating a document that doesn't exist"""
    non_existent_id = "123e4567-e89b-12d3-a456-426614174000"
    update_data = {"content": "Updated content"}
    response = client.put(f"/documents/{non_existent_id}", json=update_data)
    assert response.status_code == 404

def test_delete_document(sample_document):
    """Test deleting a document"""
    response = client.delete(f"/documents/{sample_document['id']}")
    assert response.status_code == 204
    
    # Verify the document is gone
    get_response = client.get(f"/documents/{sample_document['id']}")
    assert get_response.status_code == 404

def test_delete_nonexistent_document():
    """Test deleting a document that doesn't exist"""
    non_existent_id = "123e4567-e89b-12d3-a456-426614174000"
    response = client.delete(f"/documents/{non_existent_id}")
    assert response.status_code == 404

def test_analyze_document(sample_document):
    """Test document analysis"""
    response = client.post(f"/documents/{sample_document['id']}/analyze")
    assert response.status_code == 200
    data = response.json()
    assert "feedback" in data
    assert "grade" in data
    assert "suggestions" in data
    assert isinstance(data["suggestions"], list)

def test_analyze_nonexistent_document():
    """Test analyzing a document that doesn't exist"""
    non_existent_id = "123e4567-e89b-12d3-a456-426614174000"
    response = client.post(f"/documents/{non_existent_id}/analyze")
    assert response.status_code == 404