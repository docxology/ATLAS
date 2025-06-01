#!/usr/bin/env python3
"""
Comprehensive test coverage for all ATLAS source modules.
This test suite ensures complete coverage of all functions and methods in the src directory.
"""

import pytest
import sys
import os
from typing import Any, Dict, List, Optional
from unittest.mock import Mock, patch
import tempfile
import json

# Add src to path for imports in test environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from atlas.core.engine import ATLASEngine, ATLASConfig
from atlas.entities.entity import Entity, EntityMetadata
from atlas.entities.attribute import Attribute
from atlas.patterns.pattern import Pattern
from atlas.patterns.pattern_engine import PatternEngine
from atlas.queries.iquery import iQuery, QueryPriority, QueryStatus
from atlas.interfaces.prompt_interface import SimpleTransformInterface, create_identity_interface
from atlas.utils.helpers import generate_id, timestamp_now, deep_merge, flatten_dict

# Import visualization modules (if available)
try:
    from atlas.visualization.graph_viz import GraphVisualizer
    from atlas.visualization.pattern_viz import PatternVisualizer
    from atlas.visualization.metrics_viz import MetricsVisualizer
    from atlas.visualization.network_viz import NetworkVisualizer
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


class TestCompleteSourceCoverage:
    """Comprehensive test coverage for all source modules."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = ATLASConfig()
        self.atlas = ATLASEngine(self.config)
        self.pattern_engine = PatternEngine()
    
    # Core Engine Tests
    def test_atlas_engine_complete_functionality(self):
        """Test all ATLASEngine methods and functionality."""
        # Test initialization
        assert self.atlas.config is not None
        assert self.atlas.graph is not None
        assert len(self.atlas.entities) == 0
        
        # Test entity operations
        entity = Entity(entity_id="test_entity", attributes={"test": True})
        assert self.atlas.add_entity(entity.id, entity.to_dict()) is True
        assert entity.id in self.atlas.entities
        
        # Test pattern operations
        pattern = Pattern(pattern_id="test_pattern", qkit=["q1"])
        assert self.atlas.add_pattern(pattern.id, pattern.to_dict()) is True
        assert pattern.id in self.atlas.patterns
        
        # Test query operations
        query = iQuery(query_id="test_query", query_text="test")
        assert self.atlas.add_query(query.id, query.to_dict()) is True
        assert query.id in self.atlas.queries
        
        # Test relationships
        assert self.atlas.add_relationship(entity.id, pattern.id, "test_rel") is True
        assert self.atlas.graph.has_edge(entity.id, pattern.id)
        
        # Test search functionality
        results = self.atlas.query("test")
        assert isinstance(results, list)
        
        # Test metrics
        metrics = self.atlas.get_metrics()
        assert isinstance(metrics, dict)
        assert 'entities_created' in metrics
        
        # Test graph export
        export = self.atlas.export_graph("graphml")
        assert isinstance(export, str)
        
        # Test node retrieval
        node = self.atlas.get_node(entity.id)
        assert node is not None
        assert node['type'] == 'entity'
        
        # Test relationship retrieval
        rels = self.atlas.get_relationships(entity.id)
        assert isinstance(rels, list)
        
        # Test clear functionality
        self.atlas.clear()
        assert len(self.atlas.entities) == 0
    
    # Entity Tests
    def test_entity_complete_functionality(self):
        """Test all Entity methods and functionality."""
        entity = Entity(entity_id="complete_test")
        
        # Test attribute management
        assert entity.add_attribute("test_attr", "value") is True
        assert entity.get_attribute("test_attr") == "value"
        assert entity.has_attribute("test_attr") is True
        assert entity.remove_attribute("test_attr") is True
        assert not entity.has_attribute("test_attr")
        
        # Test pattern management
        assert entity.add_pattern("test_pattern") is True
        assert entity.has_pattern("test_pattern") is True
        assert entity.remove_pattern("test_pattern") is True
        assert not entity.has_pattern("test_pattern")
        
        # Test anomaly tracking
        entity.mark_anomaly("query1", "test anomaly")
        anomalies = entity.get_anomalies()
        assert "query1" in anomalies
        
        # Test exception tracking
        entity.mark_exception("query2", "test exception")
        exceptions = entity.get_exceptions()
        assert "query2" in exceptions
        
        # Test RFI functionality
        entity.add_attribute("empty_field", None)
        rfis = entity.call_rfis()
        assert len(rfis) > 0
        
        pending = entity.get_pending_rfis()
        assert len(pending) > 0
        
        # Test RFI resolution
        rfi_id = next(iter(rfis))
        assert entity.resolve_rfi(rfi_id, "resolved") is True
        
        # Test statistics
        stats = entity.get_statistics()
        assert isinstance(stats, dict)
        
        # Test serialization
        entity_dict = entity.to_dict()
        assert isinstance(entity_dict, dict)
        
        new_entity = Entity.from_dict(entity_dict)
        assert new_entity.id == entity.id
    
    # Attribute Tests
    def test_attribute_complete_functionality(self):
        """Test all Attribute methods and functionality."""
        attr = Attribute(
            attribute_id="test_attr",
            ref_id="ref123",
            value="test_value",
            data_type="string"
        )
        
        # Test value setting
        assert attr.set_value("new_value") is True
        assert attr.value == "new_value"
        
        # Test validation rules
        assert attr.add_validation_rule("type", {"expected": "string"}) is True
        assert attr.set_value("still_string") is True  # Should pass
        
        # Test linking
        assert attr.link_attribute("other_attr") is True
        assert "other_attr" in attr.linked_attributes
        assert attr.unlink_attribute("other_attr") is True
        
        # Test history
        history = attr.get_transformation_history()
        assert isinstance(history, list)
        
        attr.clear_transformation_history()
        assert len(attr.get_transformation_history()) == 0
        
        # Test serialization
        attr_dict = attr.to_dict()
        assert isinstance(attr_dict, dict)
        
        new_attr = Attribute.from_dict(attr_dict)
        assert new_attr.id == attr.id
    
    # Pattern Tests
    def test_pattern_complete_functionality(self):
        """Test all Pattern methods and functionality."""
        pattern = Pattern(pattern_id="test_pattern", qkit=["q1", "q2"])
        
        # Test QKit management
        assert pattern.add_qkit_item("q3") is True
        assert "q3" in pattern.qkit
        assert pattern.remove_qkit_item("q1") is True
        assert "q1" not in pattern.qkit
        
        # Test parent/child management
        assert pattern.add_parent("parent_pattern") is True
        assert "parent_pattern" in pattern.parents
        assert pattern.remove_parent("parent_pattern") is True
        
        assert pattern.add_child("child_pattern") is True
        assert "child_pattern" in pattern.children
        assert pattern.remove_child("child_pattern") is True
        
        # Test instance tracking
        assert pattern.add_instance("entity1") is True
        assert "entity1" in pattern.instances
        
        # Test derivation tracking
        assert pattern.add_derivation("derived_pattern") is True
        assert "derived_pattern" in pattern.derivations
        
        # Test effectiveness calculation
        score = pattern.calculate_effectiveness_score()
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        
        # Test statistics
        stats = pattern.get_statistics()
        assert isinstance(stats, dict)
        assert "usage_count" in stats
        
        # Test serialization
        pattern_dict = pattern.to_dict()
        assert isinstance(pattern_dict, dict)
        
        new_pattern = Pattern.from_dict(pattern_dict)
        assert new_pattern.id == pattern.id
    
    # Pattern Engine Tests
    def test_pattern_engine_complete_functionality(self):
        """Test all PatternEngine methods and functionality."""
        pattern1 = Pattern(pattern_id="pattern1", qkit=["q1", "q2"])
        pattern2 = Pattern(pattern_id="pattern2", qkit=["q2", "q3"])
        
        # Test pattern addition/removal
        assert self.pattern_engine.add_pattern(pattern1) is True
        assert self.pattern_engine.add_pattern(pattern2) is True
        assert "pattern1" in self.pattern_engine.patterns
        
        assert self.pattern_engine.remove_pattern("pattern1") is True
        assert "pattern1" not in self.pattern_engine.patterns
        
        # Re-add for further tests
        self.pattern_engine.add_pattern(pattern1)
        
        # Test similarity calculation
        similarity = self.pattern_engine.calculate_pattern_similarity("pattern1", "pattern2")
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
        
        # Test pattern hierarchy
        hierarchy = self.pattern_engine.get_pattern_hierarchy("pattern1")
        assert isinstance(hierarchy, dict)
        
        # Test usage analysis
        usage = self.pattern_engine.analyze_pattern_usage()
        assert isinstance(usage, dict)
        
        # Test optimization suggestions
        suggestions = self.pattern_engine.optimize_pattern_hierarchy()
        assert isinstance(suggestions, list)
        
        # Test clustering
        clusters = self.pattern_engine.cluster_patterns()
        assert isinstance(clusters, dict)
        
        # Test clearing
        self.pattern_engine.clear()
        assert len(self.pattern_engine.patterns) == 0
    
    # Query Tests
    def test_iquery_complete_functionality(self):
        """Test all iQuery methods and functionality."""
        query = iQuery(
            query_id="test_query",
            query_text="test query text",
            target_patterns=["pattern1"],
            priority=QueryPriority.HIGH
        )
        
        # Test context management
        query.set_context("key", "value")
        assert query.get_context("key") == "value"
        assert query.get_context("nonexistent", "default") == "default"
        
        # Test execution lifecycle
        assert query.start_execution() is True
        assert query.status == QueryStatus.EXECUTING
        
        # Test result management
        query.add_result({"test": "result"})
        assert len(query.results) == 1
        
        test_results = [{"result1": "data"}, {"result2": "data"}]
        assert query.complete_execution(test_results) is True
        assert query.status == QueryStatus.COMPLETED
        assert len(query.results) == 3  # 1 + 2 new results
        
        # Test prompt management
        assert query.add_prompt("prompt1") is True
        assert "prompt1" in query.prompts
        assert query.remove_prompt("prompt1") is True
        assert "prompt1" not in query.prompts
        
        # Test scoring
        quality_score = query.calculate_quality_score()
        assert isinstance(quality_score, float)
        
        confidence_score = query.calculate_confidence_score()
        assert isinstance(confidence_score, float)
        
        # Test statistics
        stats = query.get_statistics()
        assert isinstance(stats, dict)
        
        # Test serialization
        query_dict = query.to_dict()
        assert isinstance(query_dict, dict)
        
        new_query = iQuery.from_dict(query_dict)
        assert new_query.id == query.id
    
    # Interface Tests
    def test_prompt_interface_complete_functionality(self):
        """Test all prompt interface functionality."""
        # Test simple transform interface
        def test_transform(data):
            return str(data).upper()
        
        interface = SimpleTransformInterface("test_interface", test_transform)
        result = interface.process("hello")
        assert result == "HELLO"
        
        # Test identity interface
        identity = create_identity_interface("identity_test")
        result = identity.process("test_data")
        assert result == "test_data"
        
        # Test interface with validation
        def validate_transform(data):
            if not isinstance(data, str):
                raise ValueError("Input must be string")
            return data.lower()
        
        validated_interface = SimpleTransformInterface("validated", validate_transform)
        result = validated_interface.process("TEST")
        assert result == "test"
        
        # Test error handling
        try:
            validated_interface.process(123)
            assert False, "Should have raised error"
        except ValueError:
            pass  # Expected
    
    # Utility Tests
    def test_utils_complete_functionality(self):
        """Test all utility functions."""
        # Test ID generation
        id1 = generate_id()
        id2 = generate_id()
        assert isinstance(id1, str)
        assert isinstance(id2, str)
        assert id1 != id2  # Should be unique
        
        # Test timestamp generation
        timestamp = timestamp_now()
        assert isinstance(timestamp, str)
        
        # Test deep merge
        dict1 = {"a": 1, "b": {"c": 2}}
        dict2 = {"b": {"d": 3}, "e": 4}
        merged = deep_merge(dict1, dict2)
        assert merged["a"] == 1
        assert merged["b"]["c"] == 2
        assert merged["b"]["d"] == 3
        assert merged["e"] == 4
        
        # Test flatten dict
        nested = {"a": 1, "b": {"c": 2, "d": {"e": 3}}}
        flattened = flatten_dict(nested)
        assert "a" in flattened
        assert "b.c" in flattened
        assert "b.d.e" in flattened
    
    @pytest.mark.skipif(not VISUALIZATION_AVAILABLE, reason="Visualization modules not available")
    def test_visualization_complete_functionality(self):
        """Test all visualization functionality (if available)."""
        # Create test data
        entity = Entity(entity_id="viz_entity", attributes={"type": "test"})
        pattern = Pattern(pattern_id="viz_pattern", qkit=["q1"])
        self.atlas.add_entity(entity.id, entity.to_dict())
        self.atlas.add_pattern(pattern.id, pattern.to_dict())
        self.atlas.add_relationship(entity.id, pattern.id, "test_rel")
        
        # Test graph visualizer
        graph_viz = GraphVisualizer(self.atlas)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            fig = graph_viz.visualize_network_topology(save_path=f.name)
            assert fig is not None
            os.unlink(f.name)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            fig = graph_viz.visualize_component_distribution(save_path=f.name)
            assert fig is not None
            os.unlink(f.name)
        
        # Test pattern visualizer
        pattern_viz = PatternVisualizer(self.atlas, self.pattern_engine)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            fig = pattern_viz.visualize_pattern_hierarchy(save_path=f.name)
            assert fig is not None
            os.unlink(f.name)
        
        # Test metrics visualizer
        metrics_viz = MetricsVisualizer(self.atlas)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            fig = metrics_viz.visualize_system_overview(save_path=f.name)
            assert fig is not None
            os.unlink(f.name)
        
        # Test network visualizer
        network_viz = NetworkVisualizer(self.atlas)
        analysis = network_viz.analyze_network_structure()
        assert isinstance(analysis, dict)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            fig = network_viz.visualize_centrality_analysis(save_path=f.name)
            assert fig is not None
            os.unlink(f.name)
    
    def test_error_handling_and_edge_cases(self):
        """Test error handling and edge cases across all modules."""
        # Test with invalid data
        try:
            Entity(entity_id="", attributes=None)
        except:
            pass  # Expected to handle gracefully
        
        # Test with empty engine
        empty_engine = ATLASEngine()
        results = empty_engine.query("nonexistent")
        assert isinstance(results, list)
        assert len(results) == 0
        
        # Test pattern engine with no patterns
        empty_pattern_engine = PatternEngine()
        usage = empty_pattern_engine.analyze_pattern_usage()
        assert isinstance(usage, dict)
        
        # Test invalid relationships
        result = self.atlas.add_relationship("nonexistent1", "nonexistent2", "invalid")
        assert isinstance(result, bool)
        
        # Test serialization with invalid data
        entity = Entity(entity_id="test")
        entity_dict = entity.to_dict()
        assert isinstance(entity_dict, dict)


class TestModularArchitecture:
    """Test the modular architecture and component integration."""
    
    def test_module_independence(self):
        """Test that modules can work independently."""
        # Test entity without engine
        entity = Entity(entity_id="independent")
        assert entity.id == "independent"
        
        # Test pattern without engine
        pattern = Pattern(pattern_id="independent")
        assert pattern.id == "independent"
        
        # Test pattern engine without atlas engine
        pattern_engine = PatternEngine()
        pattern = Pattern(pattern_id="test")
        assert pattern_engine.add_pattern(pattern) is True
    
    def test_component_integration(self):
        """Test that components integrate properly."""
        atlas = ATLASEngine()
        pattern_engine = PatternEngine()
        
        # Create interconnected components
        entity = Entity(entity_id="integrated_entity")
        pattern = Pattern(pattern_id="integrated_pattern")
        query = iQuery(query_id="integrated_query")
        
        # Add to both engines
        atlas.add_entity(entity.id, entity.to_dict())
        atlas.add_pattern(pattern.id, pattern.to_dict())
        atlas.add_query(query.id, query.to_dict())
        pattern_engine.add_pattern(pattern)
        
        # Test integration
        assert entity.id in atlas.entities
        assert pattern.id in atlas.patterns
        assert pattern.id in pattern_engine.patterns
        
        # Test cross-engine consistency
        atlas_pattern = atlas.patterns[pattern.id]
        engine_pattern = pattern_engine.patterns[pattern.id]
        assert atlas_pattern['id'] == engine_pattern.id
    
    def test_extensibility(self):
        """Test that the system is extensible."""
        # Test custom attribute types
        custom_attr = Attribute(
            attribute_id="custom",
            value={"complex": "data"},
            data_type="object"
        )
        assert custom_attr.data_type == "object"
        
        # Test custom patterns
        custom_pattern = Pattern(
            pattern_id="custom",
            qkit=["custom_q1", "custom_q2"],
            attributes={"custom_field": "custom_value"}
        )
        assert "custom_field" in custom_pattern.attributes


def run_comprehensive_coverage_tests():
    """Run all comprehensive coverage tests."""
    test_classes = [TestCompleteSourceCoverage, TestModularArchitecture]
    
    for test_class in test_classes:
        print(f"\n=== Running {test_class.__name__} ===")
        instance = test_class()
        
        if hasattr(instance, 'setup_method'):
            instance.setup_method()
        
        for attr_name in dir(instance):
            if attr_name.startswith('test_'):
                test_method = getattr(instance, attr_name)
                if callable(test_method):
                    try:
                        if hasattr(instance, 'setup_method'):
                            instance.setup_method()
                        test_method()
                        print(f"✓ {attr_name}")
                    except Exception as e:
                        print(f"✗ {attr_name} - {type(e).__name__}: {str(e)}")


if __name__ == "__main__":
    run_comprehensive_coverage_tests() 