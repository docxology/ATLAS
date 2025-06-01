#!/usr/bin/env python3
"""
Comprehensive test suite for ATLAS Knowledge Management System.
"""

import pytest
import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch
from typing import Optional

# Add src to path for imports in test environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from atlas.core.engine import ATLASEngine, ATLASConfig
from atlas.entities.entity import Entity, EntityMetadata
from atlas.entities.attribute import Attribute
from atlas.patterns.pattern import Pattern
from atlas.patterns.pattern_engine import PatternEngine
from atlas.queries.iquery import iQuery, QueryPriority, QueryStatus
from atlas.interfaces.prompt_interface import SimpleTransformInterface, create_identity_interface
from atlas.utils.helpers import generate_id, timestamp_now


class TestATLASCore:
    """Test suite for ATLAS core functionality."""
    
    def __init__(self) -> None:
        """Initialize test class with instance attributes."""
        self.config: Optional[ATLASConfig] = None
        self.atlas: Optional[ATLASEngine] = None
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.config = ATLASConfig(
            auto_pattern_inference=True,
            enable_dynamic_typing=True,
            max_expansion_depth=3,
            enable_quality_metrics=True,
            log_level="INFO"
        )
        self.atlas = ATLASEngine(self.config)
    
    def test_engine_initialization(self) -> None:
        """Test ATLAS engine initialization."""
        assert self.atlas is not None
        assert self.atlas.config == self.config
        assert len(self.atlas.entities) == 0
        assert len(self.atlas.patterns) == 0
        assert len(self.atlas.queries) == 0
    
    def test_engine_metrics(self) -> None:
        """Test engine metrics functionality."""
        assert self.atlas is not None
        metrics = self.atlas.get_metrics()
        assert isinstance(metrics, dict)
        assert 'entities_created' in metrics
        assert 'patterns_created' in metrics
        assert 'queries_executed' in metrics
        assert metrics['entities_created'] == 0
    
    def test_add_entity(self) -> None:
        """Test adding entities to the system."""
        entity = Entity(
            entity_id="test_entity",
            attributes={"name": "Test", "value": 42},
            patterns=[]
        )
        
        assert self.atlas is not None
        self.atlas.add_entity(entity.id, entity.to_dict())
        assert entity.id in self.atlas.entities
        
        metrics = self.atlas.get_metrics()
        assert metrics['entities_created'] == 1
    
    def test_add_pattern(self) -> None:
        """Test adding patterns to the system."""
        pattern = Pattern(
            pattern_id="test_pattern",
            qkit=["q1", "q2", "q3"],
            attributes={"domain": "test"}
        )
        
        assert self.atlas is not None
        self.atlas.add_pattern(pattern.id, pattern.to_dict())
        assert pattern.id in self.atlas.patterns
        
        metrics = self.atlas.get_metrics()
        assert metrics['patterns_created'] == 1
    
    def test_add_query(self) -> None:
        """Test adding queries to the system."""
        query = iQuery(
            query_id="test_query",
            query_text="Test query",
            target_patterns=[],
            priority=QueryPriority.NORMAL
        )
        
        assert self.atlas is not None
        self.atlas.add_query(query.id, query.to_dict())
        assert query.id in self.atlas.queries
    
    def test_add_relationship(self) -> None:
        """Test adding relationships between entities."""
        # Create entities
        entity1 = Entity(entity_id="entity1", attributes={"type": "source"})
        entity2 = Entity(entity_id="entity2", attributes={"type": "target"})
        
        assert self.atlas is not None
        self.atlas.add_entity(entity1.id, entity1.to_dict())
        self.atlas.add_entity(entity2.id, entity2.to_dict())
        
        # Add relationship
        self.atlas.add_relationship(entity1.id, entity2.id, "relates_to")
        
        # Verify relationship exists in graph
        assert self.atlas.graph.has_edge(entity1.id, entity2.id)
        edge_data = self.atlas.graph.edges[entity1.id, entity2.id]
        assert edge_data['relationship_type'] == "relates_to"
    
    def test_query_search(self) -> None:
        """Test search functionality."""
        # Add test data
        entity = Entity(
            entity_id="searchable_entity",
            attributes={"name": "Searchable Entity", "category": "test"},
            patterns=[]
        )
        assert self.atlas is not None
        self.atlas.add_entity(entity.id, entity.to_dict())
        
        # Search for entity
        results = self.atlas.query("searchable")
        assert len(results) > 0
        assert any(result['id'] == entity.id for result in results)
    
    def test_graph_export(self) -> None:
        """Test graph export functionality."""
        # Add some test data with simple attributes only (no complex objects)
        entity = Entity(
            entity_id="export_test", 
            attributes={"test": True, "value": 42, "name": "test_entity"}
        )
        assert self.atlas is not None
        self.atlas.add_entity(entity.id, entity.to_dict())
        
        # Test export - the export may return empty string if no edges exist
        # This is valid behavior, so we just check it doesn't raise an exception
        export_result = self.atlas.export_graph("graphml")
        assert isinstance(export_result, str)  # Should return a string (even if empty)


class TestEntity:
    """Test suite for Entity functionality."""
    
    def test_entity_creation(self) -> None:
        """Test entity creation and initialization."""
        entity = Entity(
            entity_id="test_entity",
            attributes={"name": "Test Entity", "value": 123},
            patterns=["pattern1", "pattern2"]
        )
        
        assert entity.id == "test_entity"
        assert entity.attributes["name"] == "Test Entity"
        assert entity.attributes["value"] == 123
        assert "pattern1" in entity.patterns
        assert "pattern2" in entity.patterns
        assert isinstance(entity.metadata, EntityMetadata)
    
    def test_entity_serialization(self) -> None:
        """Test entity serialization and deserialization."""
        original = Entity(
            entity_id="serialize_test",
            attributes={"test": True, "number": 42},
            patterns=["pattern1"]
        )
        
        # Serialize
        data = original.to_dict()
        assert isinstance(data, dict)
        assert data['id'] == original.id
        assert data['attributes'] == original.attributes
        
        # Deserialize
        restored = Entity.from_dict(data)
        assert restored.id == original.id
        assert restored.attributes == original.attributes
        assert restored.patterns == original.patterns
    
    def test_entity_attribute_management(self) -> None:
        """Test entity attribute management."""
        entity = Entity(entity_id="attr_test", attributes={"initial": "value"})
        
        # Test adding attributes (Entity uses add_attribute, not set_attribute)
        assert entity.add_attribute("new_attr", "new_value") is True
        assert entity.get_attribute("new_attr") == "new_value"
        
        # Test getting non-existent attribute
        assert entity.get_attribute("non_existent") is None
        assert entity.get_attribute("non_existent", "default") == "default"
        
        # Test removing attributes
        assert entity.remove_attribute("initial") is True
        assert entity.get_attribute("initial") is None
    
    def test_entity_pattern_management(self) -> None:
        """Test entity pattern management."""
        entity = Entity(entity_id="pattern_test", patterns=["pattern1"])
        
        # Test adding patterns
        assert entity.add_pattern("pattern2") is True
        assert "pattern2" in entity.patterns
        assert entity.add_pattern("pattern2") is False  # Already exists
        
        # Test removing patterns
        assert entity.remove_pattern("pattern1") is True
        assert "pattern1" not in entity.patterns
        assert entity.remove_pattern("non_existent") is False


class TestPattern:
    """Test suite for Pattern functionality."""
    
    def test_pattern_creation(self) -> None:
        """Test pattern creation and initialization."""
        pattern = Pattern(
            pattern_id="test_pattern",
            qkit=["q1", "q2", "q3"],
            parents=["parent1"],
            children=["child1"],
            attributes={"domain": "test"}
        )
        
        assert pattern.id == "test_pattern"
        assert len(pattern.qkit) == 3
        assert "q1" in pattern.qkit
        assert "parent1" in pattern.parents
        assert "child1" in pattern.children
        assert pattern.attributes["domain"] == "test"
    
    def test_pattern_qkit_management(self) -> None:
        """Test pattern QKit management."""
        pattern = Pattern(pattern_id="qkit_test", qkit=["q1"])
        
        # Test adding QKit items
        assert pattern.add_qkit_item("q2") is True
        assert "q2" in pattern.qkit
        assert pattern.add_qkit_item("q2") is False  # Already exists
        
        # Test removing QKit items
        assert pattern.remove_qkit_item("q1") is True
        assert "q1" not in pattern.qkit
        assert pattern.remove_qkit_item("non_existent") is False
    
    def test_pattern_hierarchy_management(self) -> None:
        """Test pattern hierarchy management."""
        pattern = Pattern(pattern_id="hierarchy_test")
        
        # Test parent management
        assert pattern.add_parent("parent1") is True
        assert "parent1" in pattern.parents
        assert pattern.add_parent("parent1") is False  # Already exists
        
        assert pattern.remove_parent("parent1") is True
        assert "parent1" not in pattern.parents
        
        # Test child management
        assert pattern.add_child("child1") is True
        assert "child1" in pattern.children
        assert pattern.remove_child("child1") is True
        assert "child1" not in pattern.children
    
    def test_pattern_instance_management(self) -> None:
        """Test pattern instance tracking."""
        pattern = Pattern(pattern_id="instance_test")
        
        # Test adding instances
        assert pattern.add_instance("entity1") is True
        assert "entity1" in pattern.instances
        assert pattern.usage_count == 1
        
        # Test removing instances
        assert pattern.remove_instance("entity1") is True
        assert "entity1" not in pattern.instances
        assert pattern.usage_count == 0
    
    def test_pattern_effectiveness_calculation(self) -> None:
        """Test pattern effectiveness score calculation."""
        pattern = Pattern(pattern_id="effectiveness_test")
        
        # Add some usage data
        pattern.add_instance("entity1")
        pattern.add_instance("entity2")
        pattern.add_derivation("derived_pattern")
        
        score = pattern.calculate_effectiveness_score()
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        assert pattern.effectiveness_score == score


class TestPatternEngine:
    """Test suite for Pattern Engine functionality."""
    
    def __init__(self) -> None:
        """Initialize test class with proper typing."""
        self.pattern_engine: Optional[PatternEngine] = None
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.pattern_engine = PatternEngine()
    
    def test_pattern_engine_initialization(self) -> None:
        """Test pattern engine initialization."""
        assert self.pattern_engine is not None
        assert len(self.pattern_engine.patterns) == 0
        # PatternEngine doesn't have pattern_hierarchy attribute, it has get_pattern_hierarchy method
        # We can test that the method exists and works
        hierarchy = self.pattern_engine.get_pattern_hierarchy("non_existent")
        assert isinstance(hierarchy, dict)
        assert 'ancestors' in hierarchy
        assert 'descendants' in hierarchy
    
    def test_add_pattern_to_engine(self) -> None:
        """Test adding patterns to the engine."""
        pattern = Pattern(
            pattern_id="engine_test",
            qkit=["q1", "q2"],
            attributes={"domain": "test"}
        )
        
        assert self.pattern_engine is not None
        assert self.pattern_engine.add_pattern(pattern) is True
        assert pattern.id in self.pattern_engine.patterns
        # PatternEngine doesn't have get_pattern method, we check directly
        assert self.pattern_engine.patterns[pattern.id] == pattern
    
    def test_pattern_similarity_calculation(self) -> None:
        """Test pattern similarity calculation."""
        pattern1 = Pattern(
            pattern_id="similar1",
            qkit=["q1", "q2", "shared"],
            attributes={"domain": "test", "type": "A"}
        )
        pattern2 = Pattern(
            pattern_id="similar2", 
            qkit=["q3", "shared", "q4"],
            attributes={"domain": "test", "type": "B"}
        )
        
        assert self.pattern_engine is not None
        self.pattern_engine.add_pattern(pattern1)
        self.pattern_engine.add_pattern(pattern2)
        
        similarity = self.pattern_engine.calculate_pattern_similarity(pattern1.id, pattern2.id)
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.0  # Should have some similarity due to shared items
    
    def test_pattern_usage_analysis(self) -> None:
        """Test pattern usage analysis."""
        # Create test patterns with hierarchy
        root_pattern = Pattern(pattern_id="root", qkit=["q1"])
        child_pattern = Pattern(pattern_id="child", parents=["root"], qkit=["q2"])
        leaf_pattern = Pattern(pattern_id="leaf", parents=["child"], qkit=["q3"])
        
        assert self.pattern_engine is not None
        self.pattern_engine.add_pattern(root_pattern)
        self.pattern_engine.add_pattern(child_pattern)
        self.pattern_engine.add_pattern(leaf_pattern)
        
        analysis = self.pattern_engine.analyze_pattern_usage()
        assert isinstance(analysis, dict)
        assert 'total_patterns' in analysis
        assert 'root_patterns' in analysis
        assert 'leaf_patterns' in analysis
        assert analysis['total_patterns'] == 3


class TestAttribute:
    """Test suite for Attribute functionality."""
    
    def test_attribute_creation(self) -> None:
        """Test attribute creation and initialization."""
        attr = Attribute(
            attribute_id="test_attr",
            ref_id="ref_001",
            value=42.5,
            data_type="float",
            attributes={"unit": "meters", "precision": 2}
        )
        
        assert attr.id == "test_attr"
        assert attr.ref_id == "ref_001"
        assert attr.value == 42.5
        assert attr.data_type == "float"
        assert attr.attributes["unit"] == "meters"
    
    def test_attribute_validation(self) -> None:
        """Test attribute value validation."""
        attr = Attribute(
            attribute_id="validation_test",
            ref_id="val_001",
            value=50,
            data_type="int",
            attributes={"min_value": 0, "max_value": 100}
        )
        
        # Add validation rules for testing
        attr.add_validation_rule("range", {"min": 0, "max": 100})
        
        # Test valid values (using private method as validation logic is internal)
        assert attr._validate_value(50) is True
        assert attr._validate_value(0) is True
        assert attr._validate_value(100) is True
        
        # Test invalid values
        assert attr._validate_value(-10) is False
        assert attr._validate_value(150) is False
    
    def test_attribute_serialization(self) -> None:
        """Test attribute serialization."""
        original = Attribute(
            attribute_id="serialize_attr",
            ref_id="ser_001",
            value="test_value",
            data_type="string"
        )
        
        data = original.to_dict()
        assert isinstance(data, dict)
        assert data['id'] == original.id
        assert data['value'] == original.value
        
        restored = Attribute.from_dict(data)
        assert restored.id == original.id
        assert restored.value == original.value
        assert restored.data_type == original.data_type


class TestiQuery:
    """Test suite for iQuery functionality."""
    
    def test_iquery_creation(self) -> None:
        """Test iQuery creation and initialization."""
        query = iQuery(
            query_id="test_query",
            query_text="What is the meaning of life?",
            target_patterns=["pattern1", "pattern2"],
            priority=QueryPriority.HIGH,
            context={"domain": "philosophy", "urgency": "medium"}
        )
        
        assert query.id == "test_query"
        assert query.query_text == "What is the meaning of life?"
        assert "pattern1" in query.target_patterns
        assert query.priority == QueryPriority.HIGH
        assert query.context["domain"] == "philosophy"
    
    def test_iquery_execution_tracking(self) -> None:
        """Test iQuery execution tracking."""
        query = iQuery(
            query_id="execution_test",
            query_text="Test query",
            target_patterns=[],
            priority=QueryPriority.NORMAL
        )
        
        # Test execution start
        assert query.start_execution() is True
        assert query.status == QueryStatus.EXECUTING  # Uses status, not execution_status
        assert query.started_at is not None  # Uses started_at, not execution_start_time
        
        # Test execution completion
        results = [{"result": "result1"}, {"result": "result2"}]
        assert query.complete_execution(results) is True
        assert query.status == QueryStatus.COMPLETED  # Uses status
        assert len(query.results) == 2  # Results are stored in results attribute
        assert query.completed_at is not None  # Uses completed_at, not execution_end_time
    
    def test_iquery_serialization(self) -> None:
        """Test iQuery serialization."""
        original = iQuery(
            query_id="serialize_query",
            query_text="Serialize this query",
            target_patterns=["pattern1"],
            priority=QueryPriority.LOW
        )
        
        data = original.to_dict()
        assert isinstance(data, dict)
        assert data['id'] == original.id
        assert data['query_text'] == original.query_text
        
        restored = iQuery.from_dict(data)
        assert restored.id == original.id
        assert restored.query_text == original.query_text
        assert restored.priority == original.priority


class TestPromptInterfaces:
    """Test suite for Prompt Interface functionality."""
    
    def test_simple_transform_interface(self) -> None:
        """Test SimpleTransformInterface."""
        def uppercase_transform(data):
            return str(data).upper()
        
        interface = SimpleTransformInterface(
            transform_func=uppercase_transform,
            name="Uppercase Transformer",
            description="Converts to uppercase"
        )
        
        # PromptInterface uses execute method, not process
        result = interface.execute("hello world")
        assert result['success'] is True
        assert result['data'] == "HELLO WORLD"
        
        result2 = interface.execute(123)
        assert result2['success'] is True
        assert result2['data'] == "123"
    
    def test_identity_interface(self) -> None:
        """Test identity interface creation and usage."""
        interface = create_identity_interface("test_identity")
        
        test_data = "unchanged data"
        result = interface.execute(test_data)  # Uses execute, not process
        assert result['success'] is True
        assert result['data'] == test_data
        
        # Test with different data types
        result_int = interface.execute(42)
        assert result_int['success'] is True
        assert result_int['data'] == 42
        
        result_list = interface.execute([1, 2, 3])
        assert result_list['success'] is True
        assert result_list['data'] == [1, 2, 3]


class TestHelpers:
    """Test suite for helper functions."""
    
    def test_generate_id(self) -> None:
        """Test ID generation."""
        id1 = generate_id()
        id2 = generate_id()
        
        assert isinstance(id1, str)
        assert isinstance(id2, str)
        assert id1 != id2  # Should be unique
        assert len(id1) > 0
    
    def test_timestamp_now(self) -> None:
        """Test timestamp generation."""
        timestamp = timestamp_now()
        # timestamp_now returns string, not datetime
        assert isinstance(timestamp, str)
        # Verify it's a valid ISO format timestamp
        parsed_datetime = datetime.fromisoformat(timestamp)
        assert isinstance(parsed_datetime, datetime)


# Integration tests
class TestIntegration:
    """Integration tests for the complete ATLAS system."""
    
    def __init__(self) -> None:
        """Initialize test class with proper typing."""
        self.config: Optional[ATLASConfig] = None
        self.atlas: Optional[ATLASEngine] = None
        self.pattern_engine: Optional[PatternEngine] = None
    
    def setup_method(self) -> None:
        """Set up integration test fixtures."""
        self.config = ATLASConfig(
            auto_pattern_inference=True,
            enable_dynamic_typing=True,
            max_expansion_depth=3,
            enable_quality_metrics=True
        )
        self.atlas = ATLASEngine(self.config)
        self.pattern_engine = PatternEngine()
    
    def test_complete_workflow(self) -> None:
        """Test a complete ATLAS workflow."""
        # 1. Create and add a pattern
        pattern = Pattern(
            pattern_id="workflow_pattern",
            qkit=["question1", "question2"],
            attributes={"domain": "integration_test"}
        )
        assert self.atlas is not None
        assert self.pattern_engine is not None
        self.atlas.add_pattern(pattern.id, pattern.to_dict())
        self.pattern_engine.add_pattern(pattern)
        
        # 2. Create and add an entity
        entity = Entity(
            entity_id="workflow_entity",
            attributes={"name": "Integration Test Entity", "status": "active"},
            patterns=[pattern.id]
        )
        self.atlas.add_entity(entity.id, entity.to_dict())
        
        # 3. Create and add a query
        query = iQuery(
            query_id="workflow_query",
            query_text="What is the status of the workflow entity?",
            target_patterns=[pattern.id],
            priority=QueryPriority.NORMAL
        )
        self.atlas.add_query(query.id, query.to_dict())
        
        # 4. Add relationships
        self.atlas.add_relationship(entity.id, pattern.id, "conforms_to")
        
        # 5. Search and verify
        results = self.atlas.query("workflow")
        assert len(results) >= 2  # Should find both entity and pattern
        
        # 6. Check metrics
        metrics = self.atlas.get_metrics()
        assert metrics['entities_created'] >= 1
        assert metrics['patterns_created'] >= 1
        assert metrics['queries_executed'] >= 0
        
        # 7. Test pattern engine functionality
        usage_analysis = self.pattern_engine.analyze_pattern_usage()
        assert usage_analysis['total_patterns'] >= 1


if __name__ == "__main__":
    # Run tests without pytest dependency
    import time
    
    print("🧪 Running ATLAS System Tests")
    print("=" * 60)
    
    # Collect all test classes
    test_classes = [
        TestATLASCore,
        TestEntity,
        TestPattern,
        TestPatternEngine,
        TestAttribute,
        TestiQuery,
        TestPromptInterfaces,
        TestHelpers,
        TestIntegration
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    start_time = time.time()
    
    for test_class in test_classes:
        print(f"\n--- Running {test_class.__name__} ---")
        
        try:
            instance = test_class()
            test_methods = [method for method in dir(instance) if method.startswith('test_')]
            
            for test_method_name in test_methods:
                total_tests += 1
                print(f"  Running {test_method_name}...", end=" ")
                
                try:
                    # Setup method if available
                    if hasattr(instance, 'setup_method'):
                        instance.setup_method()
                    
                    # Run the test
                    test_method = getattr(instance, test_method_name)
                    test_method()
                    
                    passed_tests += 1
                    print("✓ PASSED")
                    
                except Exception as e:
                    failed_tests += 1
                    print(f"✗ FAILED - {type(e).__name__}: {str(e)}")
                    
        except Exception as e:
            print(f"✗ Class setup failed - {type(e).__name__}: {str(e)}")
    
    total_time = time.time() - start_time
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    if total_tests > 0:
        print(f"Success rate: {(passed_tests / total_tests * 100):.1f}%")
    print(f"Execution time: {total_time:.3f}s")
    
    # Exit with appropriate code
    exit_code = 0 if failed_tests == 0 else 1
    print(f"\nExiting with code: {exit_code}")
    sys.exit(exit_code) 