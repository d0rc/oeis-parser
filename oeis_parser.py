"""
OEIS Parser module.
Handles fetching and parsing data from the OEIS API.
"""

import json
import re
import time
import requests
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import quote


class OEISParser:
    """Parser for OEIS sequence data."""
    
    BASE_URL = "https://oeis.org/search"
    RATE_LIMIT_DELAY = 1.0  # seconds between requests
    
    def __init__(self):
        """Initialize the OEIS parser."""
        self.session = requests.Session()
        self.last_request_time = 0
    
    def _respect_rate_limit(self) -> None:
        """Ensure we respect OEIS rate limits."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.RATE_LIMIT_DELAY:
            sleep_time = self.RATE_LIMIT_DELAY - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def fetch_sequence(self, a_number: str) -> Dict[str, Any]:
        """Fetch sequence data from OEIS.
        
        Args:
            a_number: The A-number of the sequence (e.g., 'A000032')
            
        Returns:
            Dictionary containing parsed sequence data
            
        Raises:
            ValueError: If the A-number is invalid
            requests.RequestException: If the request fails
        """
        # Validate A-number format
        if not re.match(r'^A\d{6}$', a_number):
            raise ValueError(f"Invalid A-number format: {a_number}. Expected format: A######")
        
        # Respect rate limit
        self._respect_rate_limit()
        
        # Fetch data from OEIS API
        params = {
            'q': f'id:{a_number}',
            'fmt': 'json'
        }
        
        response = self.session.get(self.BASE_URL, params=params)
        response.raise_for_status()
        
        # Parse JSON response
        data = response.json()
        
        # Check if sequence was found
        if not data or len(data) == 0:
            raise ValueError(f"Sequence {a_number} not found")
        
        # Extract sequence data
        sequence_data = data[0]
        
        # Parse and structure the data
        return self._parse_sequence_data(sequence_data, data)
    
    def _parse_sequence_data(self, sequence_data: Dict[str, Any], raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and structure sequence data.
        
        Args:
            sequence_data: Raw sequence data from OEIS API
            raw_data: Complete raw JSON response
            
        Returns:
            Structured sequence data dictionary
        """
        # Extract A-number
        a_number = sequence_data.get('number')
        if a_number is not None:
            a_number = f"A{a_number:06d}"
        
        # Extract sequence terms
        terms = []
        if 'data' in sequence_data:
            terms_str = sequence_data['data']
            terms = [int(t) for t in terms_str.split(',') if t.strip()]
        
        # Extract name and description
        name = sequence_data.get('name', '')
        
        # Extract comments, formula, examples
        comments = self._extract_field(sequence_data, 'comment')
        formula = self._extract_field(sequence_data, 'formula')
        example = self._extract_field(sequence_data, 'example')
        
        # Extract implementations
        implementations = self._extract_implementations(sequence_data)
        
        # Extract cross-references
        cross_references = self._extract_cross_references(sequence_data)
        
        # Construct result
        result = {
            'a_number': a_number,
            'name': name,
            'description': name,  # Use name as description for now
            'terms': terms,
            'comments': comments,
            'formula': formula,
            'example': example,
            'implementations': implementations,
            'cross_references': cross_references,
            'data': raw_data  # Store the complete raw data
        }
        
        return result
    
    def _extract_field(self, sequence_data: Dict[str, Any], field_name: str) -> str:
        """Extract a field from sequence data, joining multiple entries if needed.
        
        Args:
            sequence_data: Raw sequence data
            field_name: Name of the field to extract
            
        Returns:
            Extracted field as a string
        """
        if field_name not in sequence_data:
            return ''
        
        field_data = sequence_data[field_name]
        if isinstance(field_data, list):
            return '\n'.join(field_data)
        return str(field_data)
    
    def _extract_implementations(self, sequence_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract code implementations from sequence data.
        
        Args:
            sequence_data: Raw sequence data
            
        Returns:
            List of implementation dictionaries
        """
        implementations = []
        
        # Map of OEIS program field names to language names
        language_map = {
            'maple': 'Maple',
            'mathematica': 'Mathematica',
            'prog': 'PARI/GP',
            'haskell': 'Haskell',
            'python': 'Python',
            'julia': 'Julia',
            'scheme': 'Scheme',
            'sage': 'SageMath',
            'magma': 'Magma',
            'r': 'R',
            'pari': 'PARI/GP',
            'gp': 'PARI/GP'
        }
        
        # Extract implementations from various fields
        for field, language in language_map.items():
            if field in sequence_data:
                code = sequence_data[field]
                if isinstance(code, list):
                    code = '\n'.join(code)
                
                implementations.append({
                    'language': language,
                    'code': code
                })
        
        return implementations
    
    def _extract_cross_references(self, sequence_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract cross-references to other sequences.
        
        Args:
            sequence_data: Raw sequence data
            
        Returns:
            List of cross-reference dictionaries
        """
        cross_references = []
        
        # Extract cross-references from various fields
        ref_fields = {
            'xref': 'CROSSREF',
            'keyword': 'KEYWORD',
            'offset': 'OFFSET'
        }
        
        for field, ref_type in ref_fields.items():
            if field in sequence_data:
                refs = sequence_data[field]
                if isinstance(refs, str):
                    refs = [refs]
                
                for ref in refs:
                    # Extract A-numbers using regex
                    a_numbers = re.findall(r'A\d{6}', ref)
                    for a_number in a_numbers:
                        cross_references.append({
                            'target_a_number': a_number,
                            'reference_type': ref_type
                        })
        
        return cross_references
    
    # Note: fetch_sequence_range method has been removed
    # Range fetching is now handled directly in main.py to provide
    # more detailed progress information
