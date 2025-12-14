# backend/database.py - ENHANCED DATABASE
import sqlite3
from contextlib import contextmanager
import logging
import json

class ProductionDatabase:
    """Production-grade database management"""

    def __init__(self, db_path='progress.db'):
        self.db_path = db_path
        self.setup_production_tables()

    def setup_production_tables(self):
        """Setup production database tables with indexes"""
        with self.get_connection() as conn:
            # Main progress table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS progress_updates (
                    id TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    status TEXT NOT NULL,
                    progress REAL,
                    description TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT DEFAULT 'system'
                )
            ''')

            # Analytics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    event_data TEXT,
                    user_agent TEXT,
                    ip_address TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_category ON progress_updates(category)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON progress_updates(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_event_type ON analytics(event_type)')

            conn.commit()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def log_analytics_event(self, event_type: str, event_data: dict = None,
                          user_agent: str = None, ip_address: str = None):
        """Log analytics events for business intelligence"""
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO analytics (event_type, event_data, user_agent, ip_address)
                VALUES (?, ?, ?, ?)
            ''', (event_type,
                  json.dumps(event_data) if event_data else None,
                  user_agent, ip_address))
