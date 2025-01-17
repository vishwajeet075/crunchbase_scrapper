# db1.py
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)

class EnhancedDatabaseManager:
    def __init__(self, db_path="/app/data/startups.db"):
        self.db_path = db_path

    def init_db(self):
        """Initialize database with both startup and enriched data tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create startups table (if not exists)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS startups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        company_name TEXT NOT NULL UNIQUE,
                        source_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create enriched_data table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS enriched_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        startup_id INTEGER NOT NULL,
                        company_url TEXT,
                        employees TEXT,
                        funding TEXT,
                        mission TEXT,
                        vision TEXT,
                        email TEXT,
                        product TEXT,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (startup_id) REFERENCES startups(id),
                        UNIQUE(startup_id)
                    )
                """)
                
                conn.commit()
            logger.info("Enhanced database initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize enhanced database: {str(e)}")
            raise

    def save_enriched_data(self, startup_id: int, data: Dict[str, str]):
        """Save enriched data for a startup."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO enriched_data 
                    (startup_id, company_url, employees, funding, mission, 
                     vision, email, product, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (
                    startup_id,
                    data['company_url'],
                    data['employees'],
                    data['funding'],
                    data['mission'],
                    data['vision'],
                    data['email'],
                    data['product']
                ))
                
                conn.commit()
            logger.info(f"Saved enriched data for startup ID {startup_id}")
        except Exception as e:
            logger.error(f"Database error while saving enriched data: {str(e)}")
            raise

    def get_startups_without_enrichment(self) -> List[tuple]:
        """Get startups that haven't been enriched yet."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT s.id, s.company_name 
                    FROM startups s
                    LEFT JOIN enriched_data e ON s.id = e.startup_id
                    WHERE e.id IS NULL
                """)
                
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting startups without enrichment: {str(e)}")
            return []

    def get_all_enriched_data(self) -> List[Dict]:
        """Get all startups with their enriched data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT 
                        s.company_name,
                        e.company_url,
                        e.employees,
                        e.funding,
                        e.mission,
                        e.vision,
                        e.email,
                        e.product
                    FROM startups s
                    JOIN enriched_data e ON s.id = e.startup_id
                """)
                
                columns = ['company_name', 'company_url', 'employees', 'funding',
                          'mission', 'vision', 'email', 'product']
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting enriched data: {str(e)}")
            return []