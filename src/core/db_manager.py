import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL;") # High concurrency mode

    def insert_niche(self, name: str, prompt_modifiers: Dict, audience: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Niches (name, prompt_modifiers, audience)
            VALUES (?, ?, ?)
        """, (name, json.dumps(prompt_modifiers), audience))
        self.conn.commit()
        return cursor.lastrowid

    def insert_trend(self, niche_id: int, source: str, keyword: str, confidence: float) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Trends (niche_id, source, keyword, confidence_score)
            VALUES (?, ?, ?, ?)
        """, (niche_id, source, keyword, confidence))
        self.conn.commit()
        return cursor.lastrowid

    def insert_product(self, trend_id: int, title: str, description: str, amazon_link: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO Products (trend_id, title, description, amazon_link)
            VALUES (?, ?, ?, ?)
        """, (trend_id, title, description, amazon_link))
        self.conn.commit()
        return cursor.lastrowid

    def get_queued_content(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, product_id, status, retry_count 
            FROM Content_Queue 
            WHERE status IN ('queued', 'failed') AND retry_count < 3
            ORDER BY id ASC
        """)
        return [dict(row) for row in cursor.fetchall()]

    def update_status(self, content_id: int, status: str, image_path: Optional[str] = None, 
                       text_content: Optional[str] = None, pin_id: Optional[str] = None, 
                       error_log: Optional[str] = None):
        cursor = self.conn.cursor()
        if text_content:
            cursor.execute("UPDATE Content_Queue SET status = ?, text_content = ? WHERE id = ?", 
                           (status, text_content, content_id))
        elif image_path:
            cursor.execute("UPDATE Content_Queue SET status = ?, image_path = ? WHERE id = ?", 
                           (status, image_path, content_id))
        elif pin_id:
            cursor.execute("UPDATE Content_Queue SET status = ?, pin_id = ? WHERE id = ?", 
                           (status, pin_id, content_id))
        else:
            cursor.execute("UPDATE Content_Queue SET status = ?, error_log = ? WHERE id = ?", 
                           (status, error_log, content_id))
        
        cursor.execute("UPDATE Content_Queue SET last_updated = ? WHERE id = ?", 
                       (datetime.now(), content_id))
        self.conn.commit()

    def increment_retry(self, content_id: int):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE Content_Queue SET retry_count = retry_count + 1 WHERE id = ?", (content_id,))
        self.conn.commit()

    def get_published_content(self) -> List[Dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.*, p.title, p.amazon_link 
            FROM Content_Queue c
            JOIN Products p ON c.product_id = p.id
            WHERE c.status = 'published'
        """)
        return [dict(row) for row in cursor.fetchall()]

    def update_web_content(self, product_id: int, content_id: int, title: str, description: str, image_path: str):
        """
        Updates the public-facing content for the WebHub.
        This is used to update the 'Active' gallery on your website.
        """
        cursor = self.conn.cursor()
        # We'll use the Content_Queue to store the final "Web Version"
        cursor.execute("""
            UPDATE Content_Queue 
            SET status = 'web_published', 
                text_content = ?,
                image_path = ?
            WHERE id = ?
        """, (description, image_path, content_id))
        self.conn.commit()

    def close(self):
        self.conn.close()
