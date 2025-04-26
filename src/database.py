import sqlite3
from datetime import datetime
from typing import Optional, Tuple, List, Union

def init_db(db_path: str = "documents.db") -> None:
    """
    initializes SQLite database
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS documents (
                   id INTEGER PRIMARY KEY, 
                   content TEXT, 
                   topic TEXT, 
                   created_at DATETIME DEFAULT CURRENT_TIMESTAMP, 
                   updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()
    conn.close()

def store_document(content: str, topic: Optional[str], db_path: str) -> int:
    """
    stores document in database
    :param content: document content
    :param topic: document topic
    :returns: document id
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO documents (content, topic) VALUES (?, ?)",
            (content, topic)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()

def load_document(doc_id: int, db_path: str) -> Optional[Tuple[str, Optional[str], str, str]]:
    """
    loads document from database
    :param doc_id: document id
    :returns: document content, topic, created_at, updated_at
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT content, topic, created_at, updated_at FROM documents WHERE id = ?",
            (doc_id,)
        )
        result = cursor.fetchone()
        return result if result is None else tuple(result)
    finally:
        conn.close()

def load_documents(db_path: str) -> List[Tuple[int, str, Optional[str], str, str]]:
    """
    loads all documents from database
    :returns: list of document id, content, topic, created_at, updated_at
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT id, content, topic, created_at, updated_at FROM documents"
        )
        return cursor.fetchall()
    finally:
        conn.close()

def update_document(doc_id: int, content: str, topic: Optional[str], db_path: str) -> bool:
    """
    updates document in database
    :param doc_id: document id
    :param content: new document content
    :param topic: new document topic
    :returns: True if document was updated
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE documents 
            SET content = ?, topic = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
            """,
            (content, topic, doc_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
