import pytest
import os
from src.database import init_db, store_document, load_document, load_documents, update_document

@pytest.fixture(scope="function")
def test_db():
    # Use a test database file
    test_db_path = "test_documents.db"
    
    # Initialize test database
    init_db(test_db_path)
    
    yield test_db_path
    
    # Cleanup after tests
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

def test_store_document(test_db):
    doc_id = store_document("Test content", "Test topic", test_db)
    assert isinstance(doc_id, int)
    assert doc_id > 0

def test_load_document(test_db):
    # First store a document
    doc_id = store_document("Test content", "Test topic", test_db)
    
    # Then load it
    result = load_document(doc_id, test_db)
    assert result is not None
    content, topic, created_at, updated_at = result
    assert content == "Test content"
    assert topic == "Test topic"
    assert created_at is not None
    assert updated_at is not None

def test_load_documents(test_db):
    # Store multiple documents
    store_document("Content 1", "Topic 1", test_db)
    store_document("Content 2", "Topic 2", test_db)
    
    # Load all documents
    results = load_documents(test_db)
    assert len(results) == 2
    assert all(len(row) == 5 for row in results)  # id, content, topic, created_at, updated_at

def test_update_document(test_db):
    # First store a document
    doc_id = store_document("Original content", "Original topic", test_db)
    
    # Update the document
    update_document(doc_id, "Updated content", "Updated topic", test_db)
    
    # Verify the update
    result = load_document(doc_id, test_db)
    assert result is not None
    content, topic, created_at, updated_at = result
    assert content == "Updated content"
    assert topic == "Updated topic"

def test_load_nonexistent_document(test_db):
    result = load_document(999, test_db)
    assert result is None

def test_update_nonexistent_document(test_db):
    # Should not raise an error, but should not update anything
    update_document(999, "content", "topic", test_db)
    result = load_document(999, test_db)
    assert result is None