"""
ATLAS Test Fixtures Package

This package contains shared test data, utilities, and fixtures used across
the ATLAS test suite for consistent and reliable testing.

Fixtures include:
- Sample entities, patterns, and queries
- Mock data generators
- Test configuration helpers
- Shared test utilities
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Test fixture directory
FIXTURES_DIR = Path(__file__).parent

class TestDataGenerator:
    """Generator for consistent test data across test suites."""
    
    @staticmethod
    def create_sample_entity(entity_id: str = "test_entity") -> Dict[str, Any]:
        """Create a sample entity for testing."""
        return {
            'id': entity_id,
            'attributes': {
                'name': f'Test Entity {entity_id}',
                'type': 'test',
                'created': datetime.now().isoformat(),
                'active': True
            },
            'patterns': []
        }
    
    @staticmethod
    def create_sample_pattern(pattern_id: str = "test_pattern") -> Dict[str, Any]:
        """Create a sample pattern for testing."""
        return {
            'id': pattern_id,
            'qkit': [f'q{i}' for i in range(1, 4)],
            'attributes': {
                'domain': 'test',
                'complexity': 'simple',
                'created': datetime.now().isoformat()
            },
            'parents': [],
            'children': [],
            'instances': [],
            'derivations': []
        }
    
    @staticmethod
    def create_sample_query(query_id: str = "test_query") -> Dict[str, Any]:
        """Create a sample query for testing."""
        return {
            'id': query_id,
            'query_text': f'Test query {query_id}',
            'target_patterns': [],
            'priority': 'normal',
            'context': {'test': True},
            'results': [],
            'prompts': []
        }
    
    @staticmethod
    def create_test_dataset(entity_count: int = 10, pattern_count: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Create a complete test dataset with entities and patterns."""
        entities = []
        patterns = []
        
        for i in range(pattern_count):
            pattern = TestDataGenerator.create_sample_pattern(f"pattern_{i}")
            patterns.append(pattern)
        
        for i in range(entity_count):
            entity = TestDataGenerator.create_sample_entity(f"entity_{i}")
            # Assign some patterns to entities
            if patterns:
                entity['patterns'] = [patterns[i % len(patterns)]['id']]
            entities.append(entity)
        
        return {
            'entities': entities,
            'patterns': patterns
        }

class MockATLASConfig:
    """Mock ATLAS configuration for testing."""
    
    def __init__(self, **kwargs):
        self.auto_pattern_inference = kwargs.get('auto_pattern_inference', True)
        self.enable_dynamic_typing = kwargs.get('enable_dynamic_typing', True)
        self.max_expansion_depth = kwargs.get('max_expansion_depth', 3)
        self.enable_quality_metrics = kwargs.get('enable_quality_metrics', True)
        self.log_level = kwargs.get('log_level', 'INFO')

def load_test_fixture(fixture_name: str) -> Optional[Dict[str, Any]]:
    """
    Load a test fixture from the fixtures directory.
    
    Args:
        fixture_name: Name of the fixture file (without .json extension)
        
    Returns:
        Fixture data as dictionary, or None if not found
    """
    fixture_file = FIXTURES_DIR / f"{fixture_name}.json"
    if fixture_file.exists():
        try:
            with open(fixture_file, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    return None

def save_test_fixture(fixture_name: str, data: Dict[str, Any]) -> bool:
    """
    Save test data as a fixture.
    
    Args:
        fixture_name: Name for the fixture file
        data: Data to save
        
    Returns:
        True if saved successfully, False otherwise
    """
    try:
        fixture_file = FIXTURES_DIR / f"{fixture_name}.json"
        with open(fixture_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception:
        return False

# Export main classes and functions
__all__ = [
    'TestDataGenerator',
    'MockATLASConfig',
    'load_test_fixture',
    'save_test_fixture',
    'FIXTURES_DIR'
] 