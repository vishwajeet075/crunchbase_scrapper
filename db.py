# db.py
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path="/app/data/startups.db"):
        self.db_path = db_path

    def init_db(self):
        """Initialize database and create table if not exists."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS startups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_name TEXT NOT NULL UNIQUE,
                        source_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    def save_startups(self, startups, source_url):
        """Save startups to database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for company_name in startups:
                    try:
                        cursor.execute("""
                            INSERT OR IGNORE INTO startups (company_name, source_url)
                            VALUES (?, ?)
                        """, (company_name, source_url))
                    except sqlite3.IntegrityError:
                        continue
                conn.commit()
            logger.info(f"Saved {len(startups)} startups from {source_url}")
        except Exception as e:
            logger.error(f"Database error while saving startups: {str(e)}")
            raise