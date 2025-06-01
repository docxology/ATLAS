#!/usr/bin/env python3
"""
Edge case and validation testing for ATLAS Knowledge Management System.
This module tests boundary conditions, error handling, and system robustness.
"""

import sys
import os
import time
from typing import Dict, List, Any

# Add src to path for imports in test environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from atlas.core.engine import ATLASEngine, ATLASConfig
from atlas.entities.entity import Entity, EntityMetadata
from atlas.entities.attribute import Attribute
from atlas.patterns.pattern import Pattern
from atlas.patterns.pattern_engine import PatternEngine
from atlas.queries.iquery import iQuery, QueryPriority, QueryStatus
from atlas.interfaces.prompt_interface import SimpleTransformInterface
from atlas.utils.helpers import generate_id, timestamp_now


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def setup_method(self):
        """Set up edge case test fixtures."""
        self.config = ATLASConfig()
        self.atlas = ATLASEngine(self.config)
    
    def test_empty_and_none_values(self):
        """Test handling of empty and None values."""
        # Test entity with empty attributes
        entity = Entity(entity_id="empty_test", attributes={})
        assert self.atlas.add_entity(entity.id, entity.to_dict()) is True
        
        # Test entity with None attribute values
        entity_none = Entity(
            entity_id="none_test", 
            attributes={"empty_string": "", "none_value": None, "zero": 0, "false": False}
        )
        assert self.atlas.add_entity(entity_none.id, entity_none.to_dict()) is True
        
        # Test pattern with empty qkit
        pattern = Pattern(pattern_id="empty_pattern", qkit=[])
        assert self.atlas.add_pattern(pattern.id, pattern.to_dict()) is True
        
        # Test query with empty text
        query = iQuery(query_id="empty_query", query_text="")
        assert self.atlas.add_query(query.id, query.to_dict()) is True
    
    def test_extremely_long_strings(self):
        """Test handling of extremely long strings."""
        # Create very long strings
        long_string = "x" * 10000
        very_long_string = "y" * 100000
        
        # Test entity with long attribute values
        entity = Entity(
            entity_id="long_string_test",
            attributes={
                "long_description": long_string,
                "very_long_data": very_long_string,
                "normal": "short"
            }
        )
        assert self.atlas.add_entity(entity.id, entity.to_dict()) is True
        
        # Test search with long query
        results = self.atlas.query(long_string[:100])  # Search with part of long string
        # Should handle gracefully without errors
        assert isinstance(results, list)
    
    def test_special_characters_and_unicode(self):
        """Test handling of special characters and Unicode."""
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        unicode_text = "Hello 世界 🌍 émojis 🚀 ñoño"
        
        # Test entity with special characters
        entity = Entity(
            entity_id="special_chars_test",
            attributes={
                "special": special_chars,
                "unicode": unicode_text,
                "mixed": f"{special_chars} {unicode_text}"
            }
        )
        assert self.atlas.add_entity(entity.id, entity.to_dict()) is True
        
        # Test search with special characters
        results = self.atlas.query("🌍")
        assert isinstance(results, list)
        
        # Test pattern with Unicode qkit
        pattern = Pattern(
            pattern_id="unicode_pattern",
            qkit=["question_ñ", "pregunta_🤔", "질문"],
            attributes={"language": "multilingual"}
        )
        assert self.atlas.add_pattern(pattern.id, pattern.to_dict()) is True
    
    def test_invalid_data_types(self):
        """Test handling of invalid or unexpected data types."""
        # Test with complex nested structures
        complex_data = {
            "nested_dict": {"level1": {"level2": {"level3": "deep"}}},
            "nested_list": [1, [2, [3, [4, 5]]]],
            "mixed": {"list": [1, 2, {"inner": "value"}], "number": 42}
        }
        
        entity = Entity(
            entity_id="complex_data_test",
            attributes=complex_data
        )
        assert self.atlas.add_entity(entity.id, entity.to_dict()) is True
        
        # Test serialization and deserialization of complex data
        data = entity.to_dict()
        restored = Entity.from_dict(data)
        assert restored.attributes == entity.attributes
    
    def test_circular_references_in_patterns(self):
        """Test handling of circular references in pattern hierarchies."""
        # Create patterns with potential circular references
        pattern_a = Pattern(
            pattern_id="pattern_a",
            qkit=["qa1", "qa2"],
            children=["pattern_b"]
        )
        
        pattern_b = Pattern(
            pattern_id="pattern_b", 
            qkit=["qb1", "qb2"],
            parents=["pattern_a"],
            children=["pattern_c"]
        )
        
        pattern_c = Pattern(
            pattern_id="pattern_c",
            qkit=["qc1", "qc2"],
            parents=["pattern_b"],
            children=["pattern_a"]  # This creates a cycle
        )
        
        # Add patterns to engine
        pattern_engine = PatternEngine()
        assert pattern_engine.add_pattern(pattern_a) is True
        assert pattern_engine.add_pattern(pattern_b) is True
        assert pattern_engine.add_pattern(pattern_c) is True
        
        # Test hierarchy analysis with cycles
        hierarchy = pattern_engine.get_pattern_hierarchy("pattern_a")
        assert isinstance(hierarchy, dict)
        assert 'ancestors' in hierarchy
        assert 'descendants' in hierarchy
    
    def test_massive_data_volumes(self):
        """Test handling of large volumes of data."""
        # Create many entities rapidly
        entity_count = 1000
        start_time = time.time()
        
        for i in range(entity_count):
            entity = Entity(
                entity_id=f"bulk_entity_{i}",
                attributes={
                    "index": i,
                    "category": f"cat_{i % 10}",
                    "data": f"bulk_data_{i}"
                }
            )
            self.atlas.add_entity(entity.id, entity.to_dict())
        
        creation_time = time.time() - start_time
        print(f"Created {entity_count} entities in {creation_time:.3f} seconds")
        
        # Verify all entities were created
        assert len(self.atlas.entities) >= entity_count
        
        # Test search performance with large dataset
        start_time = time.time()
        results = self.atlas.query("bulk_data")
        search_time = time.time() - start_time
        
        print(f"Search found {len(results)} results in {search_time:.6f} seconds")
        assert len(results) >= entity_count
        assert search_time < 1.0  # Should be reasonably fast
    
    def test_duplicate_ids_and_conflicts(self):
        """Test handling of duplicate IDs and conflicts."""
        # Test adding entity with duplicate ID
        entity1 = Entity(entity_id="duplicate_id", attributes={"version": 1})
        entity2 = Entity(entity_id="duplicate_id", attributes={"version": 2})
        
        assert self.atlas.add_entity(entity1.id, entity1.to_dict()) is True
        # Second add should succeed but update existing
        assert self.atlas.add_entity(entity2.id, entity2.to_dict()) is True
        
        # Verify the entity was updated
        stored_entity = self.atlas.entities["duplicate_id"]
        assert stored_entity["attributes"]["version"] == 2
        
        # Test pattern duplicate handling
        pattern1 = Pattern(pattern_id="duplicate_pattern", qkit=["q1"])
        pattern2 = Pattern(pattern_id="duplicate_pattern", qkit=["q2"])
        
        assert self.atlas.add_pattern(pattern1.id, pattern1.to_dict()) is True
        assert self.atlas.add_pattern(pattern2.id, pattern2.to_dict()) is True


class TestErrorHandling:
    """Test error handling and recovery scenarios."""
    
    def test_malformed_data_recovery(self):
        """Test recovery from malformed data."""
        atlas = ATLASEngine(ATLASConfig())
        
        # Test with malformed entity data
        try:
            malformed_entity = Entity(entity_id="", attributes=None)
            # Should handle gracefully
            result = atlas.add_entity(malformed_entity.id, malformed_entity.to_dict())
            # System should continue functioning
            assert isinstance(result, bool)
        except Exception:
            # If it raises an exception, that's also acceptable
            pass
        
        # Test with valid data after malformed attempt
        valid_entity = Entity(entity_id="valid_after_error", attributes={"test": True})
        assert atlas.add_entity(valid_entity.id, valid_entity.to_dict()) is True
        
        # System should still be functional
        metrics = atlas.get_metrics()
        assert isinstance(metrics, dict)
    
    def test_invalid_relationships(self):
        """Test handling of invalid relationships."""
        atlas = ATLASEngine(ATLASConfig())
        
        # Test relationship between non-existent entities
        result = atlas.add_relationship("nonexistent_1", "nonexistent_2", "invalid_rel")
        # Should handle gracefully without crashing
        assert isinstance(result, bool)
        
        # Test relationship with empty/None IDs
        result = atlas.add_relationship("", "valid_id", "empty_source")
        assert isinstance(result, bool)
        
        result = atlas.add_relationship("valid_id", "", "empty_target")
        assert isinstance(result, bool)
        
        # Test with None relationship type
        entity = Entity(entity_id="rel_test")
        atlas.add_entity(entity.id, entity.to_dict())
        
        result = atlas.add_relationship(entity.id, entity.id, "")
        assert isinstance(result, bool)
    
    def test_query_edge_cases(self):
        """Test query edge cases."""
        atlas = ATLASEngine(ATLASConfig())
        
        # Test query with no data
        results = atlas.query("anything")
        assert isinstance(results, list)
        assert len(results) == 0
        
        # Test empty query string
        results = atlas.query("")
        assert isinstance(results, list)
        
        # Test None query
        try:
            results = atlas.query(None)
            assert isinstance(results, list)
        except (TypeError, AttributeError):
            # This is acceptable - None query should fail
            pass
        
        # Test extremely long query
        long_query = "x" * 10000
        results = atlas.query(long_query)
        assert isinstance(results, list)


class TestAttributeValidationEdgeCases:
    """Test attribute validation edge cases."""
    
    def test_validation_rule_edge_cases(self):
        """Test edge cases in validation rules."""
        attr = Attribute(attribute_id="edge_validation", value=50)
        
        # Test with boundary values
        attr.add_validation_rule("range", {"min": 50, "max": 50})
        assert attr.set_value(50) is True  # Exact boundary
        assert attr.set_value(49) is False  # Just below
        assert attr.set_value(51) is False  # Just above
        
        # Test with negative ranges
        attr.add_validation_rule("range", {"min": -100, "max": -1})
        assert attr.set_value(-50) is True
        assert attr.set_value(0) is False
        
        # Test with floating point precision
        attr.add_validation_rule("range", {"min": 0.1, "max": 0.9})
        assert attr.set_value(0.5) is True
        assert attr.set_value(0.0999999) is False
        assert attr.set_value(0.9000001) is False
    
    def test_invalid_validation_rules(self):
        """Test handling of invalid validation rules."""
        attr = Attribute(attribute_id="invalid_validation", value="test")
        
        # Test invalid rule configuration
        attr.add_validation_rule("range", {"invalid": "config"})
        # Should not crash when validating
        result = attr.set_value("new_value")
        assert isinstance(result, bool)
        
        # Test nonsensical rule
        attr.add_validation_rule("nonexistent_rule", {"anything": "goes"})
        result = attr.set_value("another_value")
        assert isinstance(result, bool)
    
    def test_type_inference_edge_cases(self):
        """Test type inference edge cases."""
        # Test with unusual values
        test_cases = [
            (None, "null"),
            (True, "boolean"),
            (False, "boolean"),
            (0, "integer"),
            (-1, "integer"),
            (3.14, "float"),
            (-2.71, "float"),
            ("", "string"),
            ("text", "string"),
            ([], "array"),
            ([1, 2, 3], "array"),
            ({}, "object"),
            ({"key": "value"}, "object"),
        ]
        
        for value, expected_type in test_cases:
            attr = Attribute(attribute_id=f"type_test_{id(value)}", value=value)
            assert attr.data_type == expected_type, f"Failed for {value}: expected {expected_type}, got {attr.data_type}"


class TestPatternEngineEdgeCases:
    """Test pattern engine edge cases."""
    
    def test_empty_pattern_engine(self):
        """Test pattern engine with no patterns."""
        engine = PatternEngine()
        
        # Test operations on empty engine
        similarity = engine.calculate_pattern_similarity("nonexistent1", "nonexistent2")
        assert similarity == 0.0
        
        clusters = engine.detect_pattern_clusters()
        assert isinstance(clusters, dict)
        assert len(clusters) == 0
        
        analysis = engine.analyze_pattern_usage()
        assert isinstance(analysis, dict)
        assert analysis.get('total_patterns', 0) == 0
    
    def test_single_pattern_operations(self):
        """Test operations with only one pattern."""
        engine = PatternEngine()
        pattern = Pattern(pattern_id="lonely_pattern", qkit=["q1", "q2"])
        engine.add_pattern(pattern)
        
        # Test similarity with itself
        similarity = engine.calculate_pattern_similarity("lonely_pattern", "lonely_pattern")
        assert similarity == 1.0  # Should be identical to itself
        
        # Test finding similar patterns
        similar = engine.find_similar_patterns("lonely_pattern", threshold=0.0)
        assert len(similar) == 0  # Should not include itself
        
        # Test clustering with single pattern
        clusters = engine.detect_pattern_clusters()
        assert isinstance(clusters, dict)
    
    def test_pattern_with_identical_qkits(self):
        """Test patterns with identical QKits."""
        engine = PatternEngine()
        
        pattern1 = Pattern(pattern_id="identical1", qkit=["q1", "q2", "q3"])
        pattern2 = Pattern(pattern_id="identical2", qkit=["q1", "q2", "q3"])
        
        engine.add_pattern(pattern1)
        engine.add_pattern(pattern2)
        
        # Should have very high similarity
        similarity = engine.calculate_pattern_similarity("identical1", "identical2")
        assert similarity > 0.9
        
        # Should be found as similar
        similar = engine.find_similar_patterns("identical1", threshold=0.8)
        assert len(similar) >= 1
        assert any(pid == "identical2" for pid, _ in similar)


class TestConcurrencyAndRaceConditions:
    """Test concurrency and race condition handling."""
    
    def test_rapid_sequential_operations(self):
        """Test rapid sequential operations."""
        atlas = ATLASEngine(ATLASConfig())
        
        # Rapid entity creation and modification
        for i in range(100):
            entity = Entity(entity_id=f"rapid_{i}", attributes={"index": i})
            atlas.add_entity(entity.id, entity.to_dict())
            
            # Immediate search
            results = atlas.query(f"rapid_{i}")
            assert len(results) >= 1
            
            # Immediate relationship creation
            if i > 0:
                atlas.add_relationship(f"rapid_{i-1}", f"rapid_{i}", "follows")
        
        # Verify final state
        assert len(atlas.entities) >= 100
        assert atlas.graph.number_of_edges() >= 99
    
    def test_interleaved_operations(self):
        """Test interleaved create/read/update operations."""
        atlas = ATLASEngine(ATLASConfig())
        
        # Interleave different types of operations
        for i in range(50):
            # Create entity
            entity = Entity(entity_id=f"interleaved_{i}", attributes={"value": i})
            atlas.add_entity(entity.id, entity.to_dict())
            
            # Create pattern
            pattern = Pattern(pattern_id=f"pattern_{i}", qkit=[f"q_{i}"])
            atlas.add_pattern(pattern.id, pattern.to_dict())
            
            # Search
            results = atlas.query(f"interleaved_{i}")
            assert len(results) >= 1
            
            # Create query
            query = iQuery(query_id=f"query_{i}", query_text=f"Query {i}")
            atlas.add_query(query.id, query.to_dict())
            
            # Add relationship
            atlas.add_relationship(entity.id, pattern.id, "conforms_to")
        
        # Verify consistency
        metrics = atlas.get_metrics()
        assert metrics['entities_created'] >= 50
        assert metrics['patterns_created'] >= 50


class TestMemoryAndResourceManagement:
    """Test memory and resource management edge cases."""
    
    def test_large_attribute_cleanup(self):
        """Test cleanup of large attributes."""
        atlas = ATLASEngine(ATLASConfig())
        
        # Create entity with large attributes
        large_data = {
            "large_list": list(range(10000)),
            "large_string": "x" * 100000,
            "nested_data": {f"key_{i}": f"value_{i}" for i in range(1000)}
        }
        
        entity = Entity(entity_id="large_entity", attributes=large_data)
        atlas.add_entity(entity.id, entity.to_dict())
        
        # Verify it was added
        assert "large_entity" in atlas.entities
        
        # Clear and verify cleanup
        atlas.clear()
        assert len(atlas.entities) == 0
        assert len(atlas.graph.nodes) == 0
    
    def test_repeated_clear_operations(self):
        """Test repeated clear operations."""
        atlas = ATLASEngine(ATLASConfig())
        
        for cycle in range(10):
            # Add data
            for i in range(10):
                entity = Entity(entity_id=f"cycle_{cycle}_entity_{i}")
                atlas.add_entity(entity.id, entity.to_dict())
            
            # Verify data exists
            assert len(atlas.entities) >= 10
            
            # Clear
            atlas.clear()
            assert len(atlas.entities) == 0
            
            # Verify metrics reset
            metrics = atlas.get_metrics()
            assert metrics['entities_created'] == 0


class TestBoundaryValueAnalysis:
    """Test boundary value analysis for numeric operations."""
    
    def test_numeric_boundary_values(self):
        """Test numeric boundary values."""
        # Test with various numeric edge cases
        boundary_values = [
            0,           # Zero
            1,           # Minimum positive
            -1,          # Maximum negative
            2**31 - 1,   # Max 32-bit signed int
            -(2**31),    # Min 32-bit signed int
            2**63 - 1,   # Max 64-bit signed int
            -(2**63),    # Min 64-bit signed int
            float('inf'),    # Positive infinity
            float('-inf'),   # Negative infinity
            1e-10,       # Very small positive
            -1e-10,      # Very small negative
            1e10,        # Very large positive
            -1e10,       # Very large negative
        ]
        
        atlas = ATLASEngine(ATLASConfig())
        
        for i, value in enumerate(boundary_values):
            # Skip NaN and infinity for practical testing
            if str(value) in ['inf', '-inf', 'nan']:
                continue
                
            entity = Entity(
                entity_id=f"boundary_{i}",
                attributes={
                    "boundary_value": value,
                    "index": i,
                    "type": type(value).__name__
                }
            )
            
            # Should handle all boundary values gracefully
            result = atlas.add_entity(entity.id, entity.to_dict())
            assert result is True
            
            # Should be searchable
            results = atlas.query(str(value))
            assert isinstance(results, list)
    
    def test_string_length_boundaries(self):
        """Test string length boundary conditions."""
        atlas = ATLASEngine(ATLASConfig())
        
        # Test various string lengths
        lengths = [0, 1, 10, 100, 1000, 10000]
        
        for length in lengths:
            test_string = "a" * length
            entity = Entity(
                entity_id=f"string_len_{length}",
                attributes={
                    "test_string": test_string,
                    "length": length
                }
            )
            
            result = atlas.add_entity(entity.id, entity.to_dict())
            assert result is True
            
            # Verify it can be retrieved
            stored = atlas.entities[entity.id]
            assert len(stored["attributes"]["test_string"]) == length


def run_edge_case_tests():
    """Run all edge case tests."""
    print("Running ATLAS Edge Case Tests")
    print("=" * 50)
    
    test_classes = [
        TestEdgeCases,
        TestErrorHandling,
        TestAttributeValidationEdgeCases,
        TestPatternEngineEdgeCases,
        TestConcurrencyAndRaceConditions,
        TestMemoryAndResourceManagement,
        TestBoundaryValueAnalysis
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_class in test_classes:
        print(f"\n=== Running {test_class.__name__} ===")
        instance = test_class()
        
        # Run setup if it exists
        if hasattr(instance, 'setup_method'):
            instance.setup_method()
        
        # Find and run all test methods
        for attr_name in dir(instance):
            if attr_name.startswith('test_'):
                test_method = getattr(instance, attr_name)
                if callable(test_method):
                    total_tests += 1
                    start_time = time.time()
                    
                    try:
                        # Run setup before each test if it exists
                        if hasattr(instance, 'setup_method'):
                            instance.setup_method()
                        
                        test_method()
                        duration = time.time() - start_time
                        passed_tests += 1
                        print(f"✓ {attr_name} ({duration:.3f}s)")
                    except Exception as e:
                        duration = time.time() - start_time
                        failed_tests += 1
                        print(f"✗ {attr_name} - {type(e).__name__}: {str(e)} ({duration:.3f}s)")
    
    print(f"\n{'='*50}")
    print(f"Edge Case Test Summary: {passed_tests} passed, {failed_tests} failed")
    print(f"Total tests: {total_tests}")
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    
    return passed_tests, failed_tests


if __name__ == "__main__":
    passed, failed = run_edge_case_tests()
    sys.exit(0 if failed == 0 else 1) 