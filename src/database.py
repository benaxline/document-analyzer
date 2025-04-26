import sqlite3
from sqlite3 import Connection
from datetime import datetime
from typing import List, Tuple

def init_db(db_path: str = "documents.db"):
    """
    initializes SQLite database
    :returns: Connection object
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
    return conn

def store_document(content: str, topic: str, db_path: str = "docs.db") -> int:
    """
    stores document in database
    :param content: document content
    :param topic: document topic
    :returns: document id
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO documents (content, topic) VALUES (?, ?)", (content, topic))
    conn.commit()
    doc_id = cursor.lastrowid
    conn.close()
    return doc_id

def load_document(doc_id: int, db_path: str = "docs.db") -> Tuple[str, str, datetime, datetime]:
    """
    loads document from database
    :param doc_id: document id
    :returns: document content, topic, created_at, updated_at
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT content, topic, created_at, updated_at FROM documents WHERE id = ?", (doc_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def load_documents(db_path: str = "docs.db") -> List[Tuple[int, str, str, datetime, datetime]]:
    """
    loads all documents from database
    :returns: list of document content, topic, created_at, updated_at
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, content, topic, created_at, updated_at FROM documents")
    results = cursor.fetchall()
    conn.close()
    return results

