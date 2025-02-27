"""
Database module for OEIS Parser.
Handles SQLite database operations.
"""

import sqlite3
import json
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime


class OEISDatabase:
    """SQLite database handler for OEIS data."""
    
    def __init__(self, db_path: str = "oeis.db"):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.initialize_db()
    
    def initialize_db(self) -> None:
        """Initialize the database with schema if it doesn't exist."""
        # Create database directory if it doesn't exist
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
            
        # Connect to database
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        # Execute schema file
        with open('schema.sql', 'r') as f:
            self.conn.executescript(f.read())
        
        self.conn.commit()
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def insert_sequence(self, sequence_data: Dict[str, Any]) -> None:
        """Insert a sequence into the database.
        
        Args:
            sequence_data: Dictionary containing sequence data
        """
        a_number = sequence_data.get('a_number')
        if not a_number:
            raise ValueError("Sequence data must contain an a_number")
        
        # Extract main sequence fields
        sequence = {
            'a_number': a_number,
            'name': sequence_data.get('name', ''),
            'description': sequence_data.get('description', ''),
            'terms': json.dumps(sequence_data.get('terms', [])),
            'comments': sequence_data.get('comments', ''),
            'formula': sequence_data.get('formula', ''),
            'example': sequence_data.get('example', ''),
            'data': json.dumps(sequence_data.get('data', {})),
            'fetched_at': datetime.now().isoformat()
        }
        
        # Insert sequence
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO sequences 
            (a_number, name, description, terms, comments, formula, example, data, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sequence['a_number'],
            sequence['name'],
            sequence['description'],
            sequence['terms'],
            sequence['comments'],
            sequence['formula'],
            sequence['example'],
            sequence['data'],
            sequence['fetched_at']
        ))
        
        # Insert implementations if present
        implementations = sequence_data.get('implementations', [])
        for impl in implementations:
            cursor.execute('''
                INSERT INTO implementations (a_number, language, code)
                VALUES (?, ?, ?)
            ''', (a_number, impl.get('language', ''), impl.get('code', '')))
        
        # Insert cross references if present
        cross_refs = sequence_data.get('cross_references', [])
        for ref in cross_refs:
            cursor.execute('''
                INSERT INTO cross_references (source_a_number, target_a_number, reference_type)
                VALUES (?, ?, ?)
            ''', (a_number, ref.get('target_a_number', ''), ref.get('reference_type', '')))
        
        self.conn.commit()
    
    def get_sequence(self, a_number: str) -> Optional[Dict[str, Any]]:
        """Retrieve a sequence by A-number.
        
        Args:
            a_number: The A-number of the sequence to retrieve
            
        Returns:
            Dictionary containing sequence data or None if not found
        """
        cursor = self.conn.cursor()
        
        # Get sequence data
        cursor.execute('SELECT * FROM sequences WHERE a_number = ?', (a_number,))
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Convert row to dictionary
        sequence = dict(row)
        sequence['terms'] = json.loads(sequence['terms'])
        sequence['data'] = json.loads(sequence['data'])
        
        # Get implementations
        cursor.execute('SELECT language, code FROM implementations WHERE a_number = ?', (a_number,))
        implementations = [{'language': row['language'], 'code': row['code']} for row in cursor.fetchall()]
        sequence['implementations'] = implementations
        
        # Get cross references
        cursor.execute(
            'SELECT target_a_number, reference_type FROM cross_references WHERE source_a_number = ?', 
            (a_number,)
        )
        cross_refs = [
            {'target_a_number': row['target_a_number'], 'reference_type': row['reference_type']} 
            for row in cursor.fetchall()
        ]
        sequence['cross_references'] = cross_refs
        
        return sequence
    
    def get_all_sequences(self) -> List[str]:
        """Get all sequence A-numbers in the database.
        
        Returns:
            List of A-numbers
        """
        cursor = self.conn.cursor()
        cursor.execute('SELECT a_number FROM sequences')
        return [row['a_number'] for row in cursor.fetchall()]
    
    def search_sequences(self, query: str) -> List[Dict[str, Any]]:
        """Search sequences by name or description.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching sequence dictionaries
        """
        cursor = self.conn.cursor()
        search_param = f'%{query}%'
        
        cursor.execute('''
            SELECT a_number, name, description 
            FROM sequences 
            WHERE name LIKE ? OR description LIKE ?
        ''', (search_param, search_param))
        
        return [dict(row) for row in cursor.fetchall()]
