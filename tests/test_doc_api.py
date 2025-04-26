import pytest
from fastapi.testclient import TestClient
from src.doc_api import app
from src.database import init_db
import os

client = TestClient(app)

@pytest.fixture(scope="function")
def test_api():
    # Use a test database file
    test_db_path = "test_documents.db"
    
    # Initialize test database
    init_db(test_db_path)
    
    # Create a test client with the test database path
    app.state.db_path = test_db_path
    test_client = TestClient(app)
    
    yield test_client
    
    # Cleanup after tests
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

def test_create_document(test_api):
    response = test_api.post(
        "/documents/",
        json={"content": "Test content", "topic": "Test topic"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Test content"
    assert data["topic"] == "Test topic"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_read_documents(test_api):
    # First create a document
    test_api.post(
        "/documents/",
        json={"content": "Test content", "topic": "Test topic"}
    )
    
    # Then read all documents
    response = test_api.get("/documents/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["content"] == "Test content"
    assert data[0]["topic"] == "Test topic"

def test_read_document(test_api):
    # First create a document
    create_response = test_api.post(
        "/documents/",
        json={"content": "Test content", "topic": "Test topic"}
    )
    doc_id = create_response.json()["id"]
    
    # Then read the specific document
    response = test_api.get(f"/documents/{doc_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Test content"
    assert data["topic"] == "Test topic"

def test_update_document(test_api):
    # First create a document
    create_response = test_api.post(
        "/documents/",
        json={"content": "Original content", "topic": "Original topic"}
    )
    doc_id = create_response.json()["id"]
    
    # Then update it
    response = test_api.put(
        f"/documents/{doc_id}",
        json={"content": "Updated content", "topic": "Updated topic"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Updated content"
    assert data["topic"] == "Updated topic"

def test_read_nonexistent_document(test_api):
    response = test_api.get("/documents/999")
    assert response.status_code == 404

def test_update_nonexistent_document(test_api):
    response = test_api.put(
        "/documents/999",
        json={"content": "Updated content", "topic": "Updated topic"}
    )
    assert response.status_code == 404
