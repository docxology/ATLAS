#!/usr/bin/env python3
"""
Comprehensive test suite for ATLAS Knowledge Management System.
This test suite provides extensive coverage with proper typing and no linter errors.
"""

import pytest
import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch
from typing import Optional, Dict, List, Any

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


class TestATLASEngineComprehensive:
    """Test suite for comprehensive ATLAS engine functionality."""
    
    def __init__(self):
        self.config: ATLASConfig
        self.atlas: ATLASEngine
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.config = ATLASConfig(
            auto_pattern_inference=True,
            enable_dynamic_typing=True,
            max_expansion_depth=5,
            enable_quality_metrics=True
        )
        self.atlas = ATLASEngine(self.config)
    
    def test_engine_initialization_comprehensive(self) -> None:
        """Test comprehensive engine initialization."""
        assert self.atlas is not None
        assert self.atlas.config == self.config
        assert len(self.atlas.entities) == 0
        assert len(self.atlas.patterns) == 0
        assert len(self.atlas.queries) == 0
        assert self.atlas.graph is not None
        assert self.atlas.metrics is not None
    
    def test_multiple_entity_operations(self) -> None:
        """Test multiple entity operations."""
        # Create patterns first that entities will conform to
        for i in range(2):
            pattern = Pattern(
                pattern_id=f"pattern_{i}",
                qkit=[f"q{i}", f"q{i+1}"],
                attributes={"type": "test_pattern", "index": i}
            )
            assert self.atlas.add_pattern(pattern.id, pattern.to_dict()) is True
        
        # Create multiple entities
        entities = []
        for i in range(5):
            entity = Entity(
                entity_id=f"entity_{i}",
                attributes={"index": i, "category": "test"},
                patterns=[f"pattern_{i % 2}"]
            )
            entities.append(entity)
            assert self.atlas.add_entity(entity.id, entity.to_dict()) is True
        
        # Verify all entities exist
        assert len(self.atlas.entities) == 5
        
        # Test bulk operations
        for entity in entities:
            assert self.atlas.add_relationship(entity.id, f"pattern_{0}", "conforms_to") is True
        
        # Test search across multiple entities
        results = self.atlas.query("test")
        assert len(results) >= 5
        
        # Test category-based search
        category_results = self.atlas.query("category")
        assert len(category_results) >= 5
    
    def test_pattern_hierarchy_operations(self) -> None:
        """Test complex pattern hierarchy operations."""
        # Create a hierarchy of patterns
        root_pattern = Pattern(
            pattern_id="root_pattern",
            qkit=["q1", "q2"],
            attributes={"level": "root", "domain": "hierarchy_test"}
        )
        
        child_pattern = Pattern(
            pattern_id="child_pattern",
            qkit=["q2", "q3"],
            parents=["root_pattern"],
            attributes={"level": "child", "domain": "hierarchy_test"}
        )
        
        grandchild_pattern = Pattern(
            pattern_id="grandchild_pattern",
            qkit=["q3", "q4"],
            parents=["child_pattern"],
            attributes={"level": "grandchild", "domain": "hierarchy_test"}
        )
        
        # Add patterns to engine
        self.atlas.add_pattern(root_pattern.id, root_pattern.to_dict())
        self.atlas.add_pattern(child_pattern.id, child_pattern.to_dict())
        self.atlas.add_pattern(grandchild_pattern.id, grandchild_pattern.to_dict())
        
        # Test pattern retrieval
        assert len(self.atlas.patterns) == 3
        
        # Test relationships in graph
        assert self.atlas.graph.has_edge("root_pattern", "child_pattern")
        assert self.atlas.graph.has_edge("child_pattern", "grandchild_pattern")
    
    def test_query_execution_lifecycle(self) -> None:
        """Test complete query execution lifecycle."""
        # Create test data
        entity = Entity(
            entity_id="test_entity", 
            attributes={"name": "Test Entity", "status": "active"}
        )
        self.atlas.add_entity(entity.id, entity.to_dict())
        
        # Create query
        query = iQuery(
            query_id="lifecycle_query",
            query_text="Find active entities",
            target_patterns=[],
            priority=QueryPriority.HIGH
        )
        
        # Test query lifecycle
        assert query.status == QueryStatus.PENDING
        
        # Start execution
        assert query.start_execution() is True
        assert query.status == QueryStatus.EXECUTING
        assert query.started_at is not None
        
        # Add results
        test_results = [
            {"entity_id": "test_entity", "match_score": 0.95},
            {"entity_id": "other_entity", "match_score": 0.75}
        ]
        
        for result in test_results:
            query.add_result(result)
        
        # Complete execution
        assert query.complete_execution() is True
        assert query.status == QueryStatus.COMPLETED
        assert query.completed_at is not None
        assert len(query.results) == 2
        assert query.execution_time is not None
        
        # Add query to ATLAS
        self.atlas.add_query(query.id, query.to_dict())
        assert query.id in self.atlas.queries
    
    def test_graph_export_and_metrics(self) -> None:
        """Test graph export functionality and metrics calculation."""
        # Add test data
        entity = Entity(entity_id="export_test", attributes={"test": True})
        pattern = Pattern(pattern_id="export_pattern", qkit=["q1"])
        
        self.atlas.add_entity(entity.id, entity.to_dict())
        self.atlas.add_pattern(pattern.id, pattern.to_dict())
        self.atlas.add_relationship(entity.id, pattern.id, "implements")
        
        # Test metrics
        metrics = self.atlas.get_metrics()
        assert metrics['entities_created'] >= 1
        assert metrics['patterns_created'] >= 1
        assert metrics['relationships_added'] >= 1
        assert 'total_nodes' in metrics
        assert 'total_edges' in metrics
        
        # Test graph export
        graphml_export = self.atlas.export_graph("graphml")
        assert isinstance(graphml_export, str)
        
        # Test graph structure
        assert self.atlas.graph.has_node(entity.id)
        assert self.atlas.graph.has_node(pattern.id)
        assert self.atlas.graph.has_edge(entity.id, pattern.id)


class TestAdvancedEntityOperations:
    """Test suite for advanced entity operations."""
    
    def test_entity_attribute_validation(self) -> None:
        """Test entity attribute validation and management."""
        entity = Entity(entity_id="validation_test")
        
        # Test adding various attribute types
        assert entity.add_attribute("string_attr", "test_value") is True
        assert entity.add_attribute("int_attr", 42) is True
        assert entity.add_attribute("float_attr", 3.14) is True
        assert entity.add_attribute("list_attr", [1, 2, 3]) is True
        assert entity.add_attribute("dict_attr", {"key": "value"}) is True
        
        # Test attribute retrieval
        assert entity.get_attribute("string_attr") == "test_value"
        assert entity.get_attribute("int_attr") == 42
        assert entity.get_attribute("nonexistent", "default") == "default"
        
        # Test attribute existence
        assert entity.has_attribute("string_attr") is True
        assert entity.has_attribute("nonexistent") is False
        
        # Test overwrite protection
        assert entity.add_attribute("string_attr", "new_value", overwrite=False) is False
        assert entity.get_attribute("string_attr") == "test_value"
        
        # Test overwrite allowed
        assert entity.add_attribute("string_attr", "new_value", overwrite=True) is True
        assert entity.get_attribute("string_attr") == "new_value"
    
    def test_entity_pattern_management(self) -> None:
        """Test entity pattern management operations."""
        entity = Entity(entity_id="pattern_test", patterns=["initial_pattern"])
        
        # Test adding patterns
        assert entity.add_pattern("new_pattern") is True
        assert "new_pattern" in entity.patterns
        assert entity.has_pattern("new_pattern") is True
        
        # Test duplicate prevention
        assert entity.add_pattern("new_pattern") is False
        
        # Test removing patterns
        assert entity.remove_pattern("initial_pattern") is True
        assert "initial_pattern" not in entity.patterns
        assert entity.has_pattern("initial_pattern") is False
        
        # Test removing non-existent pattern
        assert entity.remove_pattern("nonexistent") is False
    
    def test_entity_anomaly_and_exception_tracking(self) -> None:
        """Test entity anomaly and exception tracking."""
        entity = Entity(entity_id="tracking_test")
        
        # Test anomaly marking
        entity.mark_anomaly("query_1", "Unusual pattern detected")
        anomalies = entity.get_anomalies()
        assert "query_1" in anomalies
        assert anomalies["query_1"] == "Unusual pattern detected"
        
        # Test exception marking
        entity.mark_exception("query_2", "Expected but missing data")
        exceptions = entity.get_exceptions()
        assert "query_2" in exceptions
        assert exceptions["query_2"] == "Expected but missing data"
        
        # Test RFI operations
        entity.add_attribute("empty_field", None)
        entity.add_attribute("empty_string", "")
        
        rfis = entity.call_rfis()
        assert len(rfis) >= 2
        pending_rfis = entity.get_pending_rfis()
        assert len(pending_rfis) >= 2
        
        # Test RFI resolution
        rfi_id = next(iter(rfis))
        assert entity.resolve_rfi(rfi_id, "resolved_value") is True
        assert rfi_id not in entity.get_pending_rfis()


class TestAdvancedPatternOperations:
    """Test suite for advanced pattern operations."""
    
    def test_pattern_qkit_management(self) -> None:
        """Test pattern QKit management operations."""
        pattern = Pattern(pattern_id="qkit_test", qkit=["q1", "q2"])
        
        # Test adding QKit items
        assert pattern.add_qkit_item("q3") is True
        assert "q3" in pattern.qkit
        assert pattern.add_qkit_item("q3") is False  # Duplicate
        
        # Test removing QKit items
        assert pattern.remove_qkit_item("q1") is True
        assert "q1" not in pattern.qkit
        assert pattern.remove_qkit_item("q1") is False  # Already removed
    
    def test_pattern_instance_tracking(self) -> None:
        """Test pattern instance tracking and effectiveness."""
        pattern = Pattern(pattern_id="tracking_test")
        
        # Test adding instances
        assert pattern.add_instance("entity_1") is True
        assert pattern.add_instance("entity_2") is True
        assert pattern.add_instance("entity_1") is False  # Duplicate
        
        assert len(pattern.instances) == 2
        assert pattern.usage_count == 2
        
        # Test adding derivations
        assert pattern.add_derivation("derived_pattern_1") is True
        assert len(pattern.derivations) == 1
        
        # Test effectiveness calculation
        effectiveness = pattern.calculate_effectiveness_score()
        assert isinstance(effectiveness, float)
        assert 0.0 <= effectiveness <= 1.0
        assert pattern.effectiveness_score == effectiveness
        
        # Test statistics
        stats = pattern.get_statistics()
        assert stats['usage_count'] == 2
        assert stats['instance_count'] == 2
        assert stats['derivation_count'] == 1
        assert 'effectiveness_score' in stats


class TestPatternEngineAdvanced:
    """Test suite for advanced pattern engine functionality."""
    
    def __init__(self):
        self.pattern_engine: PatternEngine
        self.patterns: List[Pattern]
    
    def setup_method(self) -> None:
        """Set up test fixtures."""
        self.pattern_engine = PatternEngine()
        
        # Create test patterns
        self.patterns = [
            Pattern(pattern_id="pattern_1", qkit=["q1", "q2"], attributes={"domain": "test"}),
            Pattern(pattern_id="pattern_2", qkit=["q2", "q3"], attributes={"domain": "test"}),
            Pattern(pattern_id="pattern_3", qkit=["q1", "q3"], attributes={"domain": "other"})
        ]
        
        for pattern in self.patterns:
            self.pattern_engine.add_pattern(pattern)
    
    def test_pattern_similarity_analysis(self) -> None:
        """Test pattern similarity analysis."""
        # Test similarity calculation
        similarity = self.pattern_engine.calculate_pattern_similarity(
            "pattern_1", "pattern_2"
        )
        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.0  # Should have some similarity due to shared items
        
        # Test finding similar patterns
        similar = self.pattern_engine.find_similar_patterns("pattern_1", threshold=0.1)
        assert len(similar) >= 1
        assert all(isinstance(sim, float) for _, sim in similar)
    
    def test_pattern_clustering(self) -> None:
        """Test pattern clustering functionality."""
        clusters = self.pattern_engine.detect_pattern_clusters(similarity_threshold=0.1)
        assert isinstance(clusters, dict)
        assert len(clusters) >= 1
        
        # Verify cluster contents
        total_patterns_in_clusters = sum(len(cluster) for cluster in clusters.values())
        assert total_patterns_in_clusters <= len(self.patterns)
    
    def test_pattern_usage_analysis(self) -> None:
        """Test pattern usage analysis."""
        # Add some usage data
        self.patterns[0].add_instance("entity_1")
        self.patterns[0].add_instance("entity_2")
        self.patterns[1].add_instance("entity_3")
        
        analysis = self.pattern_engine.analyze_pattern_usage()
        assert isinstance(analysis, dict)
        assert 'total_patterns' in analysis
        assert 'total_usage' in analysis
        assert 'average_usage' in analysis
        assert 'most_used_patterns' in analysis
        assert 'least_used_patterns' in analysis
        assert analysis['total_patterns'] == len(self.patterns)
    
    def test_pattern_hierarchy_optimization(self) -> None:
        """Test pattern hierarchy optimization suggestions."""
        # Create patterns with relationships
        parent = Pattern(pattern_id="parent", qkit=["q1"])
        child = Pattern(pattern_id="child", parents=["parent"], qkit=["q2"])
        
        self.pattern_engine.add_pattern(parent)
        self.pattern_engine.add_pattern(child)
        
        suggestions = self.pattern_engine.optimize_pattern_hierarchy()
        assert isinstance(suggestions, list)
        # Should not suggest any issues for a simple valid hierarchy


class TestAdvancedAttributeOperations:
    """Test suite for advanced attribute operations."""
    
    def test_attribute_validation_rules(self) -> None:
        """Test attribute validation rules."""
        attr = Attribute(
            attribute_id="validation_test",
            ref_id="ref_001",
            value=50,
            data_type="integer"
        )
        
        # Add validation rules
        assert attr.add_validation_rule("range", {"min": 0, "max": 100}) is True
        assert attr.add_validation_rule("type", {"expected": "integer"}) is True
        
        # Test valid values
        assert attr.set_value(75) is True
        assert attr.value == 75
        
        # Test invalid values (should fail validation)
        assert attr.set_value(150) is False  # Out of range
        assert attr.value == 75  # Should remain unchanged
        
        # Test removing validation rules
        assert attr.remove_validation_rule("range") is True
        assert attr.set_value(150) is True  # Should now work
    
    def test_attribute_transformation_history(self) -> None:
        """Test attribute transformation history tracking."""
        attr = Attribute(
            attribute_id="history_test",
            value="initial_value"
        )
        
        # Track value changes
        attr.set_value("second_value", track_history=True)
        attr.set_value("third_value", track_history=True)
        
        history = attr.get_transformation_history()
        assert len(history) == 2
        assert history[0]['old_value'] == "initial_value"
        assert history[0]['new_value'] == "second_value"
        assert history[1]['old_value'] == "second_value"
        assert history[1]['new_value'] == "third_value"
        
        # Test clearing history
        attr.clear_transformation_history()
        assert len(attr.get_transformation_history()) == 0
    
    def test_attribute_linking(self) -> None:
        """Test attribute linking functionality."""
        attr1 = Attribute(attribute_id="attr_1")
        attr2 = Attribute(attribute_id="attr_2")
        
        # Test linking
        assert attr1.link_attribute(attr2.id) is True
        assert attr2.id in attr1.linked_attributes
        
        # Test duplicate linking prevention
        assert attr1.link_attribute(attr2.id) is False
        
        # Test unlinking
        assert attr1.unlink_attribute(attr2.id) is True
        assert attr2.id not in attr1.linked_attributes
        
        # Test unlinking non-existent
        assert attr1.unlink_attribute("nonexistent") is False


class TestAdvancedQueryOperations:
    """Test suite for advanced query operations."""
    
    def test_query_context_management(self) -> None:
        """Test query context management."""
        query = iQuery(
            query_id="context_test",
            query_text="Test query with context"
        )
        
        # Test setting context
        query.set_context("domain", "test_domain")
        query.set_context("priority_level", "high")
        query.set_context("max_results", 10)
        
        # Test getting context
        assert query.get_context("domain") == "test_domain"
        assert query.get_context("priority_level") == "high"
        assert query.get_context("nonexistent", "default") == "default"
    
    def test_query_prompt_management(self) -> None:
        """Test query prompt interface management."""
        query = iQuery(query_id="prompt_test")
        
        # Test adding prompts
        assert query.add_prompt("prompt_1") is True
        assert query.add_prompt("prompt_2") is True
        assert "prompt_1" in query.prompts
        assert "prompt_2" in query.prompts
        
        # Test duplicate prevention
        assert query.add_prompt("prompt_1") is False
        
        # Test removing prompts
        assert query.remove_prompt("prompt_1") is True
        assert "prompt_1" not in query.prompts
        assert query.remove_prompt("nonexistent") is False
    
    def test_query_quality_and_confidence_scoring(self) -> None:
        """Test query quality and confidence scoring."""
        query = iQuery(query_id="scoring_test")
        
        # Add test results
        results = [
            {"entity_id": "entity_1", "score": 0.9},
            {"entity_id": "entity_2", "score": 0.8},
            {"derived_patterns": ["pattern_1", "pattern_2"]}
        ]
        
        for result in results:
            query.add_result(result)
        
        # Test quality score calculation
        quality_score = query.calculate_quality_score()
        assert isinstance(quality_score, float)
        assert 0.0 <= quality_score <= 1.0
        
        # Test confidence score calculation
        confidence_score = query.calculate_confidence_score()
        assert isinstance(confidence_score, float)
        assert 0.0 <= confidence_score <= 1.0
        
        # Test statistics
        stats = query.get_statistics()
        assert 'quality_score' in stats
        assert 'confidence_score' in stats
        assert 'result_count' in stats
        assert stats['result_count'] == len(results)


class TestPromptInterfaceAdvanced:
    """Test suite for advanced prompt interface operations."""
    
    def test_simple_transform_interface_validation(self) -> None:
        """Test simple transform interface with validation."""
        def validate_and_transform(data: Any) -> str:
            if not isinstance(data, (str, int, float)):
                raise ValueError("Invalid data type")
            return str(data).upper()
        
        interface = SimpleTransformInterface(
            transform_func=validate_and_transform,
            name="Validating Transformer",
            input_schema={"type": "str"},
            output_schema={"type": "str"}
        )
        
        # Test successful transformation
        result = interface.execute("test")
        assert result['success'] is True
        assert result['data'] == "TEST"
        
        # Test statistics tracking
        stats = interface.get_statistics()
        assert stats['usage_count'] >= 1
        assert stats['success_rate'] > 0.0
    
    def test_interface_error_handling(self) -> None:
        """Test interface error handling."""
        def failing_transform(data: Any) -> str:
            raise ValueError("Intentional failure")
        
        interface = SimpleTransformInterface(
            transform_func=failing_transform,
            name="Failing Transformer"
        )
        
        result = interface.execute("test")
        assert result['success'] is False
        assert 'error' in result
        assert result['data'] is None
        
        # Check error statistics
        stats = interface.get_statistics()
        assert stats['error_count'] >= 1
        assert stats['success_rate'] < 1.0


class TestHelperFunctionsAdvanced:
    """Test suite for advanced helper function operations."""
    
    def test_id_generation_uniqueness(self) -> None:
        """Test ID generation uniqueness and format."""
        # Generate multiple IDs
        ids = [generate_id() for _ in range(100)]
        
        # Check uniqueness
        assert len(set(ids)) == len(ids)
        
        # Test with prefix
        prefixed_ids = [generate_id(prefix="test") for _ in range(10)]
        assert all(id.startswith("test_") for id in prefixed_ids)
        
        # Test with custom length
        custom_ids = [generate_id(length=12) for _ in range(10)]
        assert all(len(id) == 12 for id in custom_ids)
    
    def test_timestamp_consistency(self) -> None:
        """Test timestamp generation consistency."""
        timestamp1 = timestamp_now()
        timestamp2 = timestamp_now()
        
        # Both should be valid ISO format timestamps
        datetime.fromisoformat(timestamp1)
        datetime.fromisoformat(timestamp2)
        
        # Second timestamp should be same or later
        assert timestamp2 >= timestamp1


class TestIntegrationScenarios:
    """Test suite for integration scenarios."""
    
    def __init__(self):
        self.config: ATLASConfig
        self.atlas: ATLASEngine
        self.pattern_engine: PatternEngine
    
    def setup_method(self) -> None:
        """Set up test fixtures for integration scenarios."""
        self.config = ATLASConfig(
            auto_pattern_inference=True,
            enable_dynamic_typing=True,
            max_expansion_depth=3,
            enable_quality_metrics=True
        )
        
        self.atlas = ATLASEngine(self.config)
        self.pattern_engine = PatternEngine()
    
    def test_knowledge_graph_construction(self) -> None:
        """Test construction of a complex knowledge graph."""
        # Create entities representing a simple domain model
        entities_data = [
            ("person_1", {"name": "Alice", "role": "researcher", "department": "AI"}),
            ("person_2", {"name": "Bob", "role": "engineer", "department": "AI"}),
            ("project_1", {"name": "ATLAS", "type": "research", "status": "active"}),
            ("publication_1", {"title": "Knowledge Graphs", "year": 2024, "authors": ["Alice", "Bob"]}),
            ("department_ai", {"name": "AI Department", "budget": 1000000, "head": "Alice"})
        ]
        
        # Add entities
        for entity_id, attributes in entities_data:
            entity = Entity(entity_id=entity_id, attributes=attributes)
            self.atlas.add_entity(entity.id, entity.to_dict())
        
        # Create relationships
        relationships = [
            ("person_1", "department_ai", "works_in"),
            ("person_2", "department_ai", "works_in"),
            ("person_1", "project_1", "leads"),
            ("person_2", "project_1", "contributes_to"),
            ("publication_1", "project_1", "result_of"),
            ("person_1", "publication_1", "authored"),
            ("person_2", "publication_1", "authored")
        ]
        
        for source, target, rel_type in relationships:
            self.atlas.add_relationship(source, target, rel_type)
        
        # Verify graph structure
        assert len(self.atlas.entities) == 5
        assert self.atlas.graph.number_of_edges() == 7
        
        # Test complex queries
        ai_results = self.atlas.query("AI")
        assert len(ai_results) >= 3  # Should find people and department
        
        research_results = self.atlas.query("research")
        assert len(research_results) >= 2  # Should find person and project
    
    def test_pattern_discovery_and_application(self) -> None:
        """Test pattern discovery and application workflow."""
        # Create patterns for different entity types
        person_pattern = Pattern(
            pattern_id="person_pattern",
            qkit=["what_is_name", "what_is_role", "which_department"],
            attributes={"entity_type": "person", "required_fields": ["name", "role"]}
        )
        
        project_pattern = Pattern(
            pattern_id="project_pattern", 
            qkit=["what_is_name", "what_is_status", "who_leads"],
            attributes={"entity_type": "project", "required_fields": ["name", "status"]}
        )
        
        # Add patterns to both engines
        self.atlas.add_pattern(person_pattern.id, person_pattern.to_dict())
        self.atlas.add_pattern(project_pattern.id, project_pattern.to_dict())
        self.pattern_engine.add_pattern(person_pattern)
        self.pattern_engine.add_pattern(project_pattern)
        
        # Create entities that conform to patterns
        alice = Entity(
            entity_id="alice",
            attributes={"name": "Alice", "role": "researcher"},
            patterns=["person_pattern"]
        )
        
        atlas_project = Entity(
            entity_id="atlas_project",
            attributes={"name": "ATLAS", "status": "active"},
            patterns=["project_pattern"]
        )
        
        self.atlas.add_entity(alice.id, alice.to_dict())
        self.atlas.add_entity(atlas_project.id, atlas_project.to_dict())
        
        # Track pattern usage
        person_pattern.add_instance(alice.id)
        project_pattern.add_instance(atlas_project.id)
        
        # Analyze pattern effectiveness
        person_effectiveness = person_pattern.calculate_effectiveness_score()
        project_effectiveness = project_pattern.calculate_effectiveness_score()
        
        assert person_effectiveness > 0.0
        assert project_effectiveness > 0.0
        
        # Test pattern engine analysis
        usage_analysis = self.pattern_engine.analyze_pattern_usage()
        assert usage_analysis['total_patterns'] == 2
    
    def test_query_driven_discovery(self) -> None:
        """Test query-driven knowledge discovery."""
        # Create entities with searchable attributes
        ml_expert = Entity(
            entity_id="expert_alice",
            attributes={
                "name": "Alice Smith",
                "expertise": "machine learning",
                "department": "AI Research",
                "skills": ["neural networks", "deep learning", "python"],
                "projects": ["image recognition", "nlp system"]
            }
        )
        
        ai_researcher = Entity(
            entity_id="expert_bob", 
            attributes={
                "name": "Bob Johnson",
                "expertise": "artificial intelligence",
                "department": "AI Research",
                "skills": ["reinforcement learning", "computer vision"],
                "projects": ["autonomous systems", "robotics"]
            }
        )
        
        # Add entities to the system
        assert self.atlas is not None
        self.atlas.add_entity(ml_expert.id, ml_expert.to_dict())
        self.atlas.add_entity(ai_researcher.id, ai_researcher.to_dict())
        
        # Create ML expertise pattern
        ml_pattern = Pattern(
            pattern_id="ml_expertise_pattern",
            qkit=["what_ml_skills", "what_projects"],
            attributes={"domain": "machine_learning", "type": "expertise"}
        )
        self.atlas.add_pattern(ml_pattern.id, ml_pattern.to_dict())
        
        # Create and execute a discovery query
        query = iQuery(
            query_id="find_ml_experts",
            query_text="Find experts in machine learning",
            target_patterns=[ml_pattern.id],
            priority=QueryPriority.HIGH
        )
        
        # Add query to system
        self.atlas.add_query(query.id, query.to_dict())
        
        # Start query execution
        assert query.start_execution() is True
        
        # Execute the actual search using the engine's query method
        search_results = self.atlas.query("machine learning")
        
        # Convert search results to query results format
        query_results = []
        for result in search_results:
            if result['type'] == 'entity':
                query_results.append({
                    'entity_id': result['id'],
                    'relevance_score': result.get('relevance_score', 0.0),
                    'matched_attributes': ['expertise', 'skills'],
                    'discovered_patterns': [ml_pattern.id]
                })
        
        # Complete query execution with results
        assert query.complete_execution(query_results) is True
        
        # Verify results
        assert len(query.results) > 0
        assert query.status == QueryStatus.COMPLETED
        
        # Verify we found the ML expert
        entity_ids = [r.get('entity_id') for r in query.results if 'entity_id' in r]
        assert ml_expert.id in entity_ids
        
        # Test quality scoring
        quality_score = query.calculate_quality_score()
        assert quality_score > 0.0
    
    def test_error_handling_and_recovery(self) -> None:
        """Test system error handling and recovery."""
        # Test malformed entity handling
        try:
            malformed_entity = Entity(entity_id="", attributes=None)  # Invalid
            result = self.atlas.add_entity(malformed_entity.id, malformed_entity.to_dict())
            # Should handle gracefully
        except Exception as e:
            # Expected for malformed data
            assert isinstance(e, (ValueError, TypeError, AttributeError))
        
        # Test invalid relationship handling
        result = self.atlas.add_relationship("nonexistent_1", "nonexistent_2", "invalid")
        # Should handle gracefully without crashing
        
        # Test query with no results
        empty_results = self.atlas.query("nonexistent_term")
        assert isinstance(empty_results, list)
        assert len(empty_results) == 0
        
        # Test pattern engine with empty data
        empty_analysis = self.pattern_engine.analyze_pattern_usage()
        assert isinstance(empty_analysis, dict)
        assert empty_analysis.get('total_patterns', 0) == 0


if __name__ == "__main__":
    # Run tests without pytest dependency
    import time
    
    print("🧪 Running ATLAS Comprehensive Tests")
    print("=" * 60)
    
    # Collect all test classes
    test_classes = [
        TestATLASEngineComprehensive,
        TestAdvancedEntityOperations,
        TestAdvancedPatternOperations,
        TestPatternEngineAdvanced,
        TestAdvancedAttributeOperations,
        TestAdvancedQueryOperations,
        TestPromptInterfaceAdvanced,
        TestHelperFunctionsAdvanced,
        TestIntegrationScenarios
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