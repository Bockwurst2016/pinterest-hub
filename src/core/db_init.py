import sqlite3
import os
from datetime import datetime

DB_PATH = "data/pipeline.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Core Niche Definition
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Niches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        prompt_modifiers TEXT, -- JSON: {"tone": "aesthetic", "style": "minimalist"}
        audience TEXT,         -- Target demographic
        is_active BOOLEAN DEFAULT 1
    );
    """)

    # Trend Discovery
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Trends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        niche_id INTEGER,
        source TEXT,           -- e.g., "Google Trends", "Pinterest Trends", "Reddit"
        keyword TEXT,
        confidence_score REAL, 
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (niche_id) REFERENCES Niches(id)
    );
    """)

    # Product Mapping
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trend_id INTEGER,
        title TEXT,
        description TEXT,
        amazon_link TEXT,
        status TEXT DEFAULT 'pending', -- pending, active, exhausted
        FOREIGN KEY (trend_id) REFERENCES Trends(id)
    );
    """)

    # The State Machine Queue
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Content_Queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        status TEXT CHECK(status IN ('queued', 'text_gen', 'image_gen', 'branding', 'published', 'failed')),
        text_content TEXT,
        image_path TEXT,
        pin_id TEXT,
        metrics_json TEXT,      -- JSON: {"saves": 0, "clicks": 0, "impressions": 0}
        retry_count INTEGER DEFAULT 0,
        error_log TEXT,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (product_id) REFERENCES Products(id)
    );
    """)

    # Branding Assets
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Branding_Assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_type TEXT,        -- 'logo', 'watermark', 'border', 'overlay_text'
        file_path TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
