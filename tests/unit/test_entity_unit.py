#!/usr/bin/env python3
"""
Unit tests for ATLAS Entity class.

These tests focus on testing the Entity class in isolation.
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

# Import ATLAS entities - if import fails, the test will fail appropriately
from atlas.entities.entity import Entity, EntityMetadata


class TestEntityUnit:
    """Unit tests for Entity class."""
    
    def __init__(self):
        """Initialize test class."""
        self.entity_id = "test_entity_001"
        self.attributes = {"name": "Test Entity", "value": 42}
        self.patterns = ["pattern1", "pattern2"]
    
    def setup_method(self):
        """Set up test fixtures."""
        # Reset test data for each test
        self.entity_id = "test_entity_001"
        self.attributes = {"name": "Test Entity", "value": 42}
        self.patterns = ["pattern1", "pattern2"]
    
    def test_entity_creation(self):
        """Test entity creation with basic parameters."""
        entity = Entity(
            entity_id=self.entity_id,
            attributes=self.attributes,
            patterns=self.patterns
        )
        
        assert entity.id == self.entity_id
        assert entity.attributes == self.attributes
        assert entity.patterns == self.patterns
    
    def test_entity_creation_with_defaults(self):
        """Test entity creation with default parameters."""
        entity = Entity(entity_id=self.entity_id)
        
        assert entity.id == self.entity_id
        assert isinstance(entity.attributes, dict)
        assert isinstance(entity.patterns, list)
    
    def test_entity_serialization(self):
        """Test entity serialization to dictionary."""
        entity = Entity(
            entity_id=self.entity_id,
            attributes=self.attributes,
            patterns=self.patterns
        )
        
        data = entity.to_dict()
        assert isinstance(data, dict)
        assert data['id'] == self.entity_id
        assert data['attributes'] == self.attributes
        assert data['patterns'] == self.patterns
    
    def test_entity_deserialization(self):
        """Test entity deserialization from dictionary."""
        data = {
            'id': self.entity_id,
            'attributes': self.attributes,
            'patterns': self.patterns
        }
        
        entity = Entity.from_dict(data)
        assert entity.id == self.entity_id
        assert entity.attributes == self.attributes
        assert entity.patterns == self.patterns
    
    def test_entity_roundtrip_serialization(self):
        """Test entity serialization roundtrip."""
        original = Entity(
            entity_id=self.entity_id,
            attributes=self.attributes,
            patterns=self.patterns
        )
        
        # Serialize and deserialize
        data = original.to_dict()
        restored = Entity.from_dict(data)
        
        # Verify roundtrip
        assert restored.id == original.id
        assert restored.attributes == original.attributes
        assert restored.patterns == original.patterns
    
    def test_entity_empty_attributes(self):
        """Test entity with empty attributes."""
        entity = Entity(entity_id=self.entity_id, attributes={})
        
        assert entity.id == self.entity_id
        assert entity.attributes == {}
        assert len(entity.attributes) == 0
    
    def test_entity_empty_patterns(self):
        """Test entity with empty patterns."""
        entity = Entity(entity_id=self.entity_id, patterns=[])
        
        assert entity.id == self.entity_id
        assert entity.patterns == []
        assert len(entity.patterns) == 0
    
    def test_entity_complex_attributes(self):
        """Test entity with complex attribute values."""
        complex_attributes = {
            "string": "test",
            "number": 42,
            "float": 3.14,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"nested": "value"}
        }
        
        entity = Entity(
            entity_id=self.entity_id,
            attributes=complex_attributes
        )
        
        assert entity.attributes == complex_attributes
        
        # Test serialization with complex attributes
        data = entity.to_dict()
        restored = Entity.from_dict(data)
        assert restored.attributes == complex_attributes 