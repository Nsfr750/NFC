"""
Database module for NFC tag management and versioning.

This module provides functionality to store and manage NFC tag data,
including version history and metadata.
"""
import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, asdict
import hashlib

@dataclass
class TagRecord:
    """Represents a single tag record in the database."""
    id: int = None
    tag_id: str = None
    tag_type: str = None
    data: str = None
    data_hash: str = None
    created_at: str = None
    updated_at: str = None
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the record to a dictionary."""
        result = asdict(self)
        if self.metadata and isinstance(self.metadata, str):
            result['metadata'] = json.loads(self.metadata)
        return result

class TagDatabase:
    """Manages the SQLite database for NFC tag storage and versioning."""
    
    def __init__(self, db_path: str = "data/tags.db"):
        """Initialize the database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._ensure_data_dir()
        self._init_db()
    
    def _ensure_data_dir(self) -> None:
        """Ensure the data directory exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self) -> None:
        """Initialize the database schema."""
        with self._get_connection() as conn:
            # Tags table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag_id TEXT NOT NULL,
                    tag_type TEXT NOT NULL,
                    data TEXT,
                    data_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    UNIQUE(tag_id, data_hash)
                )
            ''')
            
            # Tag history table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tag_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tag_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    data TEXT,
                    data_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (tag_id) REFERENCES tags (tag_id) ON DELETE CASCADE,
                    UNIQUE(tag_id, version)
                )
            ''')
            
            # Create indexes
            conn.execute('CREATE INDEX IF NOT EXISTS idx_tags_tag_id ON tags(tag_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_tag_history_tag_id ON tag_history(tag_id)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_tag_history_created_at ON tag_history(created_at)')
    
    def _calculate_hash(self, data: str) -> str:
        """Calculate a hash for the tag data."""
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    def store_tag(self, tag_id: str, tag_type: str, data: str, 
                 metadata: Optional[Dict[str, Any]] = None) -> TagRecord:
        """Store or update a tag in the database.
        
        Args:
            tag_id: Unique identifier for the tag
            tag_type: Type of the NFC tag
            data: Tag data content
            metadata: Optional metadata dictionary
            
        Returns:
            The created or updated TagRecord
        """
        data_hash = self._calculate_hash(data)
        metadata_str = json.dumps(metadata) if metadata else None
        now = datetime.utcnow().isoformat()
        
        with self._get_connection() as conn:
            # Check if this exact data is already stored for this tag
            cursor = conn.execute(
                'SELECT * FROM tags WHERE tag_id = ? AND data_hash = ?',
                (tag_id, data_hash)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update the existing record
                conn.execute('''
                    UPDATE tags 
                    SET updated_at = ?
                    WHERE id = ?
                ''', (now, existing['id']))
                record_id = existing['id']
            else:
                # Insert new record
                cursor = conn.execute('''
                    INSERT INTO tags (tag_id, tag_type, data, data_hash, metadata, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (tag_id, tag_type, data, data_hash, metadata_str, now))
                record_id = cursor.lastrowid
                
                # Add to history
                self._add_to_history(tag_id, data, data_hash, metadata_str, conn)
            
            # Get the full record
            cursor = conn.execute('SELECT * FROM tags WHERE id = ?', (record_id,))
            return self._row_to_tag_record(cursor.fetchone())
    
    def _add_to_history(self, tag_id: str, data: str, data_hash: str, 
                       metadata: Optional[str], conn: sqlite3.Connection) -> None:
        """Add a record to the tag history."""
        # Get the next version number
        cursor = conn.execute(
            'SELECT COALESCE(MAX(version), 0) + 1 FROM tag_history WHERE tag_id = ?',
            (tag_id,)
        )
        version = cursor.fetchone()[0] or 1
        
        # Insert history record
        conn.execute('''
            INSERT INTO tag_history (tag_id, version, data, data_hash, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (tag_id, version, data, data_hash, metadata))
    
    def get_tag(self, tag_id: str) -> Optional[TagRecord]:
        """Get the latest version of a tag by ID.
        
        Args:
            tag_id: The tag ID to look up
            
        Returns:
            The latest TagRecord, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM tags WHERE tag_id = ? ORDER BY updated_at DESC LIMIT 1',
                (tag_id,)
            )
            row = cursor.fetchone()
            return self._row_to_tag_record(row) if row else None
    
    def get_tag_history(self, tag_id: str) -> List[TagRecord]:
        """Get the version history of a tag.
        
        Args:
            tag_id: The tag ID to get history for
            
        Returns:
            List of TagRecords in chronological order (oldest first)
        """
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT t.*, th.version 
                FROM tag_history th
                JOIN tags t ON th.tag_id = t.tag_id AND th.data_hash = t.data_hash
                WHERE t.tag_id = ?
                ORDER BY th.version ASC
            ''', (tag_id,))
            return [self._row_to_tag_record(row) for row in cursor.fetchall()]
    
    def search_tags(self, query: str, field: str = 'data', 
                   limit: int = 100) -> List[TagRecord]:
        """Search for tags by content.
        
        Args:
            query: Search query string
            field: Field to search in ('data' or 'metadata')
            limit: Maximum number of results to return
            
        Returns:
            List of matching TagRecords
        """
        if field not in ('data', 'metadata'):
            raise ValueError("Field must be either 'data' or 'metadata'")
            
        with self._get_connection() as conn:
            if field == 'metadata':
                # For metadata, we need to search the JSON string
                cursor = conn.execute(f'''
                    SELECT DISTINCT t.*
                    FROM tags t, json_each(t.metadata)
                    WHERE json_each.value LIKE ?
                    LIMIT ?
                ''', (f'%{query}%', limit))
            else:
                cursor = conn.execute(
                    f'SELECT * FROM tags WHERE {field} LIKE ? LIMIT ?',
                    (f'%{query}%', limit)
                )
            return [self._row_to_tag_record(row) for row in cursor.fetchall()]
    
    def delete_tag(self, tag_id: str) -> bool:
        """Delete a tag and all its history.
        
        Args:
            tag_id: The tag ID to delete
            
        Returns:
            True if the tag was deleted, False if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute('DELETE FROM tags WHERE tag_id = ?', (tag_id,))
            return cursor.rowcount > 0
    
    def get_all_tags(self, limit: int = 1000) -> List[TagRecord]:
        """Get all tags in the database.
        
        Args:
            limit: Maximum number of tags to return
            
        Returns:
            List of TagRecords
        """
        with self._get_connection() as conn:
            cursor = conn.execute('''
                SELECT * FROM tags 
                ORDER BY updated_at DESC 
                LIMIT ?
            ''', (limit,))
            return [self._row_to_tag_record(row) for row in cursor.fetchall()]
    
    def _row_to_tag_record(self, row: sqlite3.Row) -> TagRecord:
        """Convert a database row to a TagRecord object."""
        if not row:
            return None
            
        metadata = None
        if row.get('metadata'):
            try:
                metadata = json.loads(row['metadata'])
            except (json.JSONDecodeError, TypeError):
                metadata = {'raw_metadata': row['metadata']}
        
        return TagRecord(
            id=row['id'],
            tag_id=row['tag_id'],
            tag_type=row['tag_type'],
            data=row['data'],
            data_hash=row['data_hash'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            metadata=metadata
        )

# Global instance for easy access
tag_db = TagDatabase()
