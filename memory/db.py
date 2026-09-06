"""
SQLite Database Storage Layer for Project Jarvis.
Manages persistent episodic conversation logs, user preferences, and fact stores.
"""

import sqlite3
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

class Database:
    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = Path(db_path)
        else:
            base_dir = Path(__file__).resolve().parent.parent
            self.db_path = base_dir / "data" / "jarvis_memory.db"
            
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode = WAL;")  # High concurrency WAL mode
        return conn

    def _init_db(self):
        """Create tables and indices if they do not exist."""
        with self._get_connection() as conn:
            # Conversations table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    speaker TEXT NOT NULL,
                    text TEXT NOT NULL,
                    timestamp REAL NOT NULL
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conv_timestamp ON conversations(timestamp);")

            # Memories and Facts table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL DEFAULT 'fact',
                    topic TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding BLOB,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL
                );
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memories_topic ON memories(topic);")
            conn.commit()

    def log_conversation(self, speaker: str, text: str, session_id: str = "default"):
        """Save a single conversation turn."""
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO conversations (session_id, speaker, text, timestamp) VALUES (?, ?, ?, ?)",
                (session_id, speaker, text, time.time())
            )
            conn.commit()

    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent conversation turns."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT speaker, text, timestamp FROM conversations ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [{"speaker": r["speaker"], "text": r["text"], "timestamp": r["timestamp"]} for r in reversed(rows)]

    def insert_or_update_memory(self, topic: str, content: str, category: str = "fact", embedding: Optional[bytes] = None) -> int:
        """Insert or update a memory by topic."""
        now = time.time()
        with self._get_connection() as conn:
            # Check if topic exists
            cursor = conn.execute("SELECT id FROM memories WHERE LOWER(topic) = LOWER(?)", (topic.strip(),))
            row = cursor.fetchone()
            if row:
                conn.execute(
                    "UPDATE memories SET content = ?, category = ?, embedding = ?, updated_at = ? WHERE id = ?",
                    (content.strip(), category, embedding, now, row["id"])
                )
                conn.commit()
                return row["id"]
            else:
                cursor = conn.execute(
                    "INSERT INTO memories (category, topic, content, embedding, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (category, topic.strip(), content.strip(), embedding, now, now)
                )
                conn.commit()
                return cursor.lastrowid

    def delete_memory(self, topic: str) -> bool:
        """Delete a memory by topic."""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM memories WHERE LOWER(topic) = LOWER(?)", (topic.strip(),))
            conn.commit()
            return cursor.rowcount > 0

    def get_all_memories(self) -> List[Dict[str, Any]]:
        """Fetch all stored memories."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT id, category, topic, content, embedding, updated_at FROM memories ORDER BY updated_at DESC")
            return [dict(r) for r in cursor.fetchall()]
