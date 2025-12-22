import sqlite3
from typing import Optional
from pathlib import Path


class DatabaseConnection:
    def __init__(self, db_path: str = "database/lottery_warehouse.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._ensure_db_directory()
    
    def _ensure_db_directory(self):
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def connect(self) -> sqlite3.Connection:
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def execute(self, query: str, params: tuple = ()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor
    
    def executemany(self, query: str, params: list):
        cursor = self.conn.cursor()
        cursor.executemany(query, params)
        self.conn.commit()
        return cursor
    
    def fetchall(self, query: str, params: tuple = ()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def fetchone(self, query: str, params: tuple = ()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
