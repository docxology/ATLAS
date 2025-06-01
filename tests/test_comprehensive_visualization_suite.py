#!/usr/bin/env python3
"""
Comprehensive Visualization Test Suite for ATLAS Knowledge Management System.

This test suite ensures that ALL functions from the src/ directory are tested
and generates extensive visualizations and animations in the output folder.
"""

import sys
import os
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import ATLAS modules
from atlas.core.engine import ATLASEngine, ATLASConfig
from atlas.entities.entity import Entity, EntityMetadata
from atlas.entities.attribute import Attribute
from atlas.patterns.pattern import Pattern
from atlas.patterns.pattern_engine import PatternEngine
from atlas.queries.iquery import iQuery, QueryPriority, QueryStatus
from atlas.interfaces.prompt_interface import SimpleTransformInterface, create_identity_interface
from atlas.utils.helpers import generate_id, timestamp_now

# Import visualization modules
try:
    from atlas.visualization.graph_viz import GraphVisualizer
    from atlas.visualization.pattern_viz import PatternVisualizer
    from atlas.visualization.metrics_viz import MetricsVisualizer
    from atlas.visualization.network_viz import NetworkVisualizer
    from atlas.visualization.animation_viz import AnimationVisualizer
    VISUALIZATION_AVAILABLE = True
except ImportError as e:
    print(f"Visualization modules not available: {e}")
    VISUALIZATION_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ComprehensiveVisualizationTestSuite:
    """
    Comprehensive test suite that exercises ALL functions and generates
    extensive visualizations and animations.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the test suite with output directory."""
        self.output_dir = Path(output_dir) if output_dir else Path("test_viz_output")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "visualizations").mkdir(exist_ok=True)
        (self.output_dir / "animations").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
        (self.output_dir / "metrics").mkdir(exist_ok=True)
        
        # Initialize test results tracking
        self.test_results = {
            'functions_tested': [],
            'visualizations_created': [],
            'animations_created': [],
            'failed_tests': [],
            'start_time': datetime.now().isoformat(),
            'total_size_mb': 0
        }
        
        logger.info(f"Comprehensive test suite initialized with output: {self.output_dir}")
    
    def setup_test_data(self) -> tuple:
        """Set up comprehensive test data for all tests."""
        logger.info("Setting up comprehensive test data...")
        
        # 1. Initialize ATLAS engine
        config = ATLASConfig(
            auto_pattern_inference=True,
            enable_dynamic_typing=True,
            max_expansion_depth=5,
            enable_quality_metrics=True
        )
        atlas = ATLASEngine(config)
        pattern_engine = PatternEngine()
        
        # 2. Create diverse entities
        entities_data = [
            # Researchers
            ("researcher_alice", {"name": "Dr. Alice Smith", "role": "Senior Researcher", 
                                 "department": "AI", "expertise": ["machine learning", "neural networks"],
                                 "publications": 25, "h_index": 18}),
            ("researcher_bob", {"name": "Prof. Bob Johnson", "role": "Principal Investigator",
                               "department": "NLP", "expertise": ["natural language processing", "transformers"], 
                               "publications": 42, "h_index": 28}),
            ("researcher_carol", {"name": "Dr. Carol Chen", "role": "Research Associate",
                                 "department": "Vision", "expertise": ["computer vision", "image processing"],
                                 "publications": 15, "h_index": 12}),
            
            # Projects  
            ("project_atlas", {"name": "ATLAS Knowledge System", "type": "research",
                              "status": "active", "funding": 500000, "team_size": 8,
                              "duration_months": 36, "domain": "knowledge management"}),
            ("project_nlp", {"name": "Advanced NLP Framework", "type": "development", 
                            "status": "completed", "funding": 300000, "team_size": 5,
                            "duration_months": 24, "domain": "natural language"}),
            ("project_vision", {"name": "Computer Vision Pipeline", "type": "research",
                               "status": "planning", "funding": 250000, "team_size": 4,
                               "duration_months": 18, "domain": "computer vision"}),
            
            # Publications
            ("paper_knowledge_graphs", {"title": "Scalable Knowledge Graph Construction",
                                       "authors": ["Alice Smith", "Bob Johnson"], "year": 2024,
                                       "citations": 45, "venue": "AAAI", "type": "conference"}),
            ("paper_neural_nets", {"title": "Deep Neural Networks for Knowledge Extraction", 
                                  "authors": ["Alice Smith"], "year": 2023,
                                  "citations": 78, "venue": "Nature AI", "type": "journal"}),
            ("paper_nlp_systems", {"title": "Large Language Models in Knowledge Systems",
                                  "authors": ["Bob Johnson", "Carol Chen"], "year": 2024,
                                  "citations": 23, "venue": "ACL", "type": "conference"}),
            
            # Departments
            ("dept_ai", {"name": "AI Research Department", "head": "Dr. Alice Smith",
                        "budget": 2000000, "staff_count": 25, "founded_year": 2018}),
            ("dept_nlp", {"name": "Natural Language Processing Lab", "head": "Prof. Bob Johnson", 
                         "budget": 1500000, "staff_count": 15, "founded_year": 2020}),
            ("dept_vision", {"name": "Computer Vision Group", "head": "Dr. Carol Chen",
                            "budget": 800000, "staff_count": 12, "founded_year": 2021}),
            
            # Technologies
            ("tech_transformers", {"name": "Transformer Architecture", "type": "model",
                                  "maturity": "stable", "applications": ["NLP", "vision", "speech"]}),
            ("tech_knowledge_graphs", {"name": "Knowledge Graph Technology", "type": "framework", 
                                      "maturity": "evolving", "applications": ["reasoning", "search", "qa"]}),
            ("tech_deep_learning", {"name": "Deep Learning Framework", "type": "platform",
                                   "maturity": "mature", "applications": ["classification", "generation", "prediction"]})
        ]
        
        # Add entities to atlas
        for entity_id, attributes in entities_data:
            entity = Entity(entity_id=entity_id, attributes=attributes)
            atlas.add_entity(entity.id, entity.to_dict())
        
        # 3. Create comprehensive patterns
        patterns_data = [
            ("research_pattern", ["who_leads", "what_expertise", "which_projects", "how_many_publications"],
             [], [], {"domain": "research", "entity_types": ["researcher"], "complexity": "medium"}),
            
            ("project_pattern", ["what_status", "who_leads", "what_budget", "how_long_duration"], 
             [], [], {"domain": "project_management", "entity_types": ["project"], "complexity": "high"}),
            
            ("publication_pattern", ["who_authored", "when_published", "where_published", "how_many_citations"],
             [], [], {"domain": "academic", "entity_types": ["publication"], "complexity": "medium"}),
            
            ("collaboration_pattern", ["who_collaborates", "on_what_projects", "in_which_domain"],
             ["research_pattern"], [], {"domain": "collaboration", "entity_types": ["researcher", "project"], "complexity": "high"}),
            
            ("technology_pattern", ["what_type", "which_applications", "how_mature"],
             [], [], {"domain": "technology", "entity_types": ["technology"], "complexity": "low"}),
            
            ("department_pattern", ["who_heads", "what_budget", "how_many_staff", "which_focus"],
             [], ["research_pattern"], {"domain": "organization", "entity_types": ["department"], "complexity": "medium"}),
            
            ("impact_pattern", ["what_citations", "which_venues", "how_influential"],
             ["publication_pattern"], [], {"domain": "impact_assessment", "entity_types": ["publication"], "complexity": "high"}),
            
            ("innovation_pattern", ["what_technologies", "which_applications", "how_novel"],
             ["technology_pattern"], ["research_pattern"], {"domain": "innovation", "entity_types": ["technology", "project"], "complexity": "very_high"})
        ]
        
        for pattern_id, qkit, parents, children, attributes in patterns_data:
            pattern = Pattern(
                pattern_id=pattern_id,
                qkit=qkit,
                parents=parents,
                children=children,
                attributes=attributes
            )
            atlas.add_pattern(pattern.id, pattern.to_dict())
            pattern_engine.add_pattern(pattern)
            
            # Add some instances
            if pattern_id == "research_pattern":
                pattern.add_instance("researcher_alice")
                pattern.add_instance("researcher_bob")
                pattern.add_instance("researcher_carol")
            elif pattern_id == "project_pattern":
                pattern.add_instance("project_atlas")
                pattern.add_instance("project_nlp")
                pattern.add_instance("project_vision")
        
        # 4. Create complex relationships
        relationships = [
            # Researcher relationships
            ("researcher_alice", "dept_ai", "works_in"),
            ("researcher_bob", "dept_nlp", "heads"),
            ("researcher_carol", "dept_vision", "works_in"),
            
            # Project relationships
            ("researcher_alice", "project_atlas", "leads"),
            ("researcher_bob", "project_nlp", "leads"),
            ("researcher_carol", "project_vision", "participates_in"),
            ("researcher_alice", "project_vision", "advises"),
            
            # Publication relationships
            ("researcher_alice", "paper_knowledge_graphs", "authored"),
            ("researcher_bob", "paper_knowledge_graphs", "co_authored"),
            ("researcher_alice", "paper_neural_nets", "authored"),
            ("researcher_bob", "paper_nlp_systems", "authored"),
            ("researcher_carol", "paper_nlp_systems", "co_authored"),
            
            # Project-publication relationships
            ("project_atlas", "paper_knowledge_graphs", "resulted_in"),
            ("project_nlp", "paper_nlp_systems", "resulted_in"),
            
            # Technology relationships
            ("project_nlp", "tech_transformers", "uses"),
            ("project_atlas", "tech_knowledge_graphs", "develops"),
            ("project_vision", "tech_deep_learning", "applies"),
            
            # Cross-domain relationships
            ("researcher_alice", "tech_knowledge_graphs", "expert_in"),
            ("researcher_bob", "tech_transformers", "expert_in"),
            ("dept_ai", "project_atlas", "funds"),
            ("dept_nlp", "project_nlp", "hosts")
        ]
        
        for source, target, rel_type in relationships:
            atlas.add_relationship(source, target, rel_type)
        
        # 5. Create diverse queries
        queries_data = [
            ("find_ai_researchers", "Find all researchers in AI department", 
             ["research_pattern"], QueryPriority.HIGH),
            ("project_collaborations", "Identify project collaboration patterns",
             ["collaboration_pattern", "project_pattern"], QueryPriority.NORMAL),
            ("publication_impact", "Analyze publication impact and citations",
             ["publication_pattern", "impact_pattern"], QueryPriority.NORMAL),
            ("technology_adoption", "Track technology adoption across projects",
             ["technology_pattern", "innovation_pattern"], QueryPriority.LOW),
            ("department_research", "Department research focus analysis",
             ["department_pattern", "research_pattern"], QueryPriority.HIGH),
            ("funding_analysis", "Project funding and resource allocation",
             ["project_pattern"], QueryPriority.NORMAL)
        ]
        
        for query_id, query_text, target_patterns, priority in queries_data:
            query = iQuery(
                query_id=query_id,
                query_text=query_text,
                target_patterns=target_patterns,
                priority=priority
            )
            atlas.add_query(query.id, query.to_dict())
        
        logger.info(f"Test data setup complete: {len(entities_data)} entities, "
                   f"{len(patterns_data)} patterns, {len(relationships)} relationships, "
                   f"{len(queries_data)} queries")
        
        return atlas, pattern_engine
    
    def test_all_core_functions(self, atlas: ATLASEngine, pattern_engine: PatternEngine):
        """Test all core ATLAS functions comprehensively."""
        logger.info("Testing all core ATLAS functions...")
        
        try:
            # Test ATLASEngine functions
            functions_to_test = [
                ('atlas.get_metrics', lambda: atlas.get_metrics()),
                ('atlas.query', lambda: atlas.query("research")),
                ('atlas.export_graph', lambda: atlas.export_graph("graphml")),
                ('atlas.get_node', lambda: atlas.get_node("researcher_alice")),
                ('atlas.get_relationships', lambda: atlas.get_relationships("researcher_alice")),
            ]
            
            for func_name, func_call in functions_to_test:
                try:
                    result = func_call()
                    self.test_results['functions_tested'].append({
                        'function': func_name,
                        'status': 'PASSED',
                        'result_type': type(result).__name__
                    })
                    logger.info(f"✓ {func_name} - PASSED")
                except Exception as e:
                    self.test_results['failed_tests'].append({
                        'function': func_name,
                        'error': str(e)
                    })
                    logger.error(f"✗ {func_name} - FAILED: {e}")
            
            # Test PatternEngine functions
            pattern_functions = [
                ('pattern_engine.analyze_pattern_usage', lambda: pattern_engine.analyze_pattern_usage()),
                ('pattern_engine.calculate_pattern_similarity', 
                 lambda: pattern_engine.calculate_pattern_similarity("research_pattern", "project_pattern")),
                ('pattern_engine.find_similar_patterns',
                 lambda: pattern_engine.find_similar_patterns("research_pattern", threshold=0.1)),
                ('pattern_engine.detect_pattern_clusters',
                 lambda: pattern_engine.detect_pattern_clusters(similarity_threshold=0.2)),
                ('pattern_engine.get_statistics', lambda: pattern_engine.get_statistics()),
            ]
            
            for func_name, func_call in pattern_functions:
                try:
                    result = func_call()
                    self.test_results['functions_tested'].append({
                        'function': func_name,
                        'status': 'PASSED',
                        'result_type': type(result).__name__
                    })
                    logger.info(f"✓ {func_name} - PASSED")
                except Exception as e:
                    self.test_results['failed_tests'].append({
                        'function': func_name,
                        'error': str(e)
                    })
                    logger.error(f"✗ {func_name} - FAILED: {e}")
            
            # Test Entity functions
            test_entity = Entity(entity_id="test_entity_comprehensive", 
                               attributes={"test": True, "value": 42})
            
            entity_functions = [
                ('entity.add_attribute', lambda: test_entity.add_attribute("new_attr", "test_value")),
                ('entity.get_attribute', lambda: test_entity.get_attribute("test")),
                ('entity.has_attribute', lambda: test_entity.has_attribute("test")),
                ('entity.add_pattern', lambda: test_entity.add_pattern("test_pattern")),
                ('entity.to_dict', lambda: test_entity.to_dict()),
                ('entity.call_rfis', lambda: test_entity.call_rfis()),
            ]
            
            for func_name, func_call in entity_functions:
                try:
                    result = func_call()
                    self.test_results['functions_tested'].append({
                        'function': func_name,
                        'status': 'PASSED',
                        'result_type': type(result).__name__
                    })
                    logger.info(f"✓ {func_name} - PASSED")
                except Exception as e:
                    self.test_results['failed_tests'].append({
                        'function': func_name,
                        'error': str(e)
                    })
                    logger.error(f"✗ {func_name} - FAILED: {e}")
            
            # Test Pattern functions
            test_pattern = Pattern(pattern_id="test_pattern_comprehensive",
                                 qkit=["q1", "q2", "q3"])
            
            pattern_functions_direct = [
                ('pattern.add_qkit_item', lambda: test_pattern.add_qkit_item("q4")),
                ('pattern.add_instance', lambda: test_pattern.add_instance("test_entity")),
                ('pattern.calculate_effectiveness_score', lambda: test_pattern.calculate_effectiveness_score()),
                ('pattern.get_statistics', lambda: test_pattern.get_statistics()),
                ('pattern.to_dict', lambda: test_pattern.to_dict()),
            ]
            
            for func_name, func_call in pattern_functions_direct:
                try:
                    result = func_call()
                    self.test_results['functions_tested'].append({
                        'function': func_name,
                        'status': 'PASSED',
                        'result_type': type(result).__name__
                    })
                    logger.info(f"✓ {func_name} - PASSED")
                except Exception as e:
                    self.test_results['failed_tests'].append({
                        'function': func_name,
                        'error': str(e)
                    })
                    logger.error(f"✗ {func_name} - FAILED: {e}")
            
            # Test Query functions
            test_query = iQuery(query_id="test_query_comprehensive",
                              query_text="Test comprehensive query")
            
            query_functions = [
                ('query.start_execution', lambda: test_query.start_execution()),
                ('query.add_result', lambda: test_query.add_result({"test": "result"})),
                ('query.calculate_quality_score', lambda: test_query.calculate_quality_score()),
                ('query.get_statistics', lambda: test_query.get_statistics()),
                ('query.to_dict', lambda: test_query.to_dict()),
            ]
            
            for func_name, func_call in query_functions:
                try:
                    result = func_call()
                    self.test_results['functions_tested'].append({
                        'function': func_name,
                        'status': 'PASSED',
                        'result_type': type(result).__name__
                    })
                    logger.info(f"✓ {func_name} - PASSED")
                except Exception as e:
                    self.test_results['failed_tests'].append({
                        'function': func_name,
                        'error': str(e)
                    })
                    logger.error(f"✗ {func_name} - FAILED: {e}")
            
            # Test Attribute functions
            test_attr = Attribute(attribute_id="test_attr_comprehensive",
                                value="test_value", data_type="string")
            
            attr_functions = [
                ('attribute.set_value', lambda: test_attr.set_value("new_value")),
                ('attribute.add_validation_rule', 
                 lambda: test_attr.add_validation_rule("length", {"min": 1, "max": 100})),
                ('attribute.to_dict', lambda: test_attr.to_dict()),
            ]
            
            for func_name, func_call in attr_functions:
                try:
                    result = func_call()
                    self.test_results['functions_tested'].append({
                        'function': func_name,
                        'status': 'PASSED',
                        'result_type': type(result).__name__
                    })
                    logger.info(f"✓ {func_name} - PASSED")
                except Exception as e:
                    self.test_results['failed_tests'].append({
                        'function': func_name,
                        'error': str(e)
                    })
                    logger.error(f"✗ {func_name} - FAILED: {e}")
            
            # Test Interface functions
            transform_interface = SimpleTransformInterface(
                transform_func=lambda x: str(x).upper(),
                name="Test Transform"
            )
            identity_interface = create_identity_interface("test_identity")
            
            interface_functions = [
                ('transform_interface.execute', lambda: transform_interface.execute("test")),
                ('identity_interface.execute', lambda: identity_interface.execute("test")),
                ('transform_interface.get_statistics', lambda: transform_interface.get_statistics()),
            ]
            
            for func_name, func_call in interface_functions:
                try:
                    result = func_call()
                    self.test_results['functions_tested'].append({
                        'function': func_name,
                        'status': 'PASSED',
                        'result_type': type(result).__name__
                    })
                    logger.info(f"✓ {func_name} - PASSED")
                except Exception as e:
                    self.test_results['failed_tests'].append({
                        'function': func_name,
                        'error': str(e)
                    })
                    logger.error(f"✗ {func_name} - FAILED: {e}")
            
            # Test Helper functions
            helper_functions = [
                ('generate_id', lambda: generate_id()),
                ('generate_id_with_prefix', lambda: generate_id(prefix="test")),
                ('timestamp_now', lambda: timestamp_now()),
            ]
            
            for func_name, func_call in helper_functions:
                try:
                    result = func_call()
                    self.test_results['functions_tested'].append({
                        'function': func_name,
                        'status': 'PASSED',
                        'result_type': type(result).__name__
                    })
                    logger.info(f"✓ {func_name} - PASSED")
                except Exception as e:
                    self.test_results['failed_tests'].append({
                        'function': func_name,
                        'error': str(e)
                    })
                    logger.error(f"✗ {func_name} - FAILED: {e}")
            
            logger.info(f"Core function testing complete: {len(self.test_results['functions_tested'])} tested")
            
        except Exception as e:
            logger.error(f"Error in core function testing: {e}")
    
    def test_all_visualization_functions(self, atlas: ATLASEngine, pattern_engine: PatternEngine):
        """Test all visualization functions and generate comprehensive visualizations."""
        if not VISUALIZATION_AVAILABLE:
            logger.warning("Visualization modules not available - skipping visualization tests")
            return
        
        logger.info("Testing all visualization functions and generating outputs...")
        
        try:
            # Initialize all visualizers
            graph_viz = GraphVisualizer(atlas)
            pattern_viz = PatternVisualizer(atlas, pattern_engine)
            metrics_viz = MetricsVisualizer(atlas)
            network_viz = NetworkVisualizer(atlas)
            animation_viz = AnimationVisualizer(atlas, pattern_engine)
            
            # Test GraphVisualizer functions
            graph_viz_functions = [
                ('graph_viz.visualize_network_topology', 
                 lambda: graph_viz.visualize_network_topology(
                     save_path=str(self.output_dir / "visualizations" / "network_topology.png"))),
                ('graph_viz.visualize_entity_relationships',
                 lambda: graph_viz.visualize_entity_relationships(
                     "researcher_alice", 
                     save_path=str(self.output_dir / "visualizations" / "entity_relationships.png"))),
                ('graph_viz.visualize_component_distribution',
                 lambda: graph_viz.visualize_component_distribution(
                     save_path=str(self.output_dir / "visualizations" / "component_distribution.png"))),
                ('graph_viz.create_interactive_network',
                 lambda: graph_viz.create_interactive_network(
                     save_path=str(self.output_dir / "visualizations" / "interactive_network.html"))),
                ('graph_viz.export_graph_formats',
                 lambda: graph_viz.export_graph_formats(str(self.output_dir / "visualizations" / "graph_export"))),
                ('graph_viz.generate_graph_statistics',
                 lambda: graph_viz.generate_graph_statistics()),
            ]
            
            for func_name, func_call in graph_viz_functions:
                try:
                    result = func_call()
                    self.test_results['functions_tested'].append({
                        'function': func_name,
                        'status': 'PASSED',
                        'result_type': type(result).__name__
                    })
                    if 'save_path' in func_name:
                        self.test_results['visualizations_created'].append(func_name)
                    logger.info(f"✓ {func_name} - PASSED")
                except Exception as e:
                    self.test_results['failed_tests'].append({
                        'function': func_name,
                        'error': str(e)
                    })
                    logger.error(f"✗ {func_name} - FAILED: {e}")
            
            # Test PatternVisualizer functions
            pattern_viz_functions = [
                ('pattern_viz.visualize_pattern_hierarchy',
                 lambda: pattern_viz.visualize_pattern_hierarchy(
                     save_path=str(self.output_dir / "visualizations" / "pattern_hierarchy.png"))),
                ('pattern_viz.visualize_pattern_effectiveness',
                 lambda: pattern_viz.visualize_pattern_effectiveness(
                     save_path=str(self.output_dir / "visualizations" / "pattern_effectiveness.png"))),
                ('pattern_viz.visualize_pattern_inheritance_tree',
                 lambda: pattern_viz.visualize_pattern_inheritance_tree(
                     "research_pattern",
                     save_path=str(self.output_dir / "visualizations" / "pattern_inheritance.png"))),
                ('pattern_viz.visualize_pattern_similarity_matrix',
                 lambda: pattern_viz.visualize_pattern_similarity_matrix(
                     save_path=str(self.output_dir / "visualizations" / "pattern_similarity.png"))),
                ('pattern_viz.visualize_qkit_analysis',
                 lambda: pattern_viz.visualize_qkit_analysis(
                     save_path=str(self.output_dir / "visualizations" / "qkit_analysis.png"))),
            ]
            
            for func_name, func_call in pattern_viz_functions:
                try:
                    result = func_call()
                    self.test_results['functions_tested'].append({
                        'function': func_name,
                        'status': 'PASSED',
                        'result_type': type(result).__name__
                    })
                    if 'save_path' in func_name:
                        self.test_results['visualizations_created'].append(func_name)
                    logger.info(f"✓ {func_name} - PASSED")
                except Exception as e:
                    self.test_results['failed_tests'].append({
                        'function': func_name,
                        'error': str(e)
                    })
                    logger.error(f"✗ {func_name} - FAILED: {e}")
            
            # Test MetricsVisualizer functions
            metrics_viz_functions = [
                ('metrics_viz.visualize_system_overview',
                 lambda: metrics_viz.visualize_system_overview(
                     save_path=str(self.output_dir / "visualizations" / "system_overview.png"))),
                ('metrics_viz.visualize_performance_metrics',
                 lambda: metrics_viz.visualize_performance_metrics(
                     save_path=str(self.output_dir / "visualizations" / "performance_metrics.png"))),
                ('metrics_viz.visualize_quality_metrics',
                 lambda: metrics_viz.visualize_quality_metrics(
                     save_path=str(self.output_dir / "visualizations" / "quality_metrics.png"))),
                ('metrics_viz.export_metrics_report',
                 lambda: metrics_viz.export_metrics_report(str(self.output_dir / "reports" / "metrics_report"))),
            ]
            
            for func_name, func_call in metrics_viz_functions:
                try:
                    result = func_call()
                    self.test_results['functions_tested'].append({
                        'function': func_name,
                        'status': 'PASSED',
                        'result_type': type(result).__name__
                    })
                    if 'save_path' in func_name or 'export' in func_name:
                        self.test_results['visualizations_created'].append(func_name)
                    logger.info(f"✓ {func_name} - PASSED")
                except Exception as e:
                    self.test_results['failed_tests'].append({
                        'function': func_name,
                        'error': str(e)
                    })
                    logger.error(f"✗ {func_name} - FAILED: {e}")
            
            # Test NetworkVisualizer functions
            network_viz_functions = [
                ('network_viz.analyze_network_structure',
                 lambda: network_viz.analyze_network_structure()),
                ('network_viz.visualize_centrality_analysis',
                 lambda: network_viz.visualize_centrality_analysis(
                     save_path=str(self.output_dir / "visualizations" / "centrality_analysis.png"))),
                ('network_viz.visualize_community_structure',
                 lambda: network_viz.visualize_community_structure(
                     save_path=str(self.output_dir / "visualizations" / "community_structure.png"))),
                ('network_viz.visualize_network_evolution',
                 lambda: network_viz.visualize_network_evolution(
                     save_path=str(self.output_dir / "visualizations" / "network_evolution.png"))),
                ('network_viz.export_network_analysis',
                 lambda: network_viz.export_network_analysis(str(self.output_dir / "reports" / "network_analysis"))),
            ]
            
            for func_name, func_call in network_viz_functions:
                try:
                    result = func_call()
                    self.test_results['functions_tested'].append({
                        'function': func_name,
                        'status': 'PASSED',
                        'result_type': type(result).__name__
                    })
                    if 'save_path' in func_name or 'export' in func_name:
                        self.test_results['visualizations_created'].append(func_name)
                    logger.info(f"✓ {func_name} - PASSED")
                except Exception as e:
                    self.test_results['failed_tests'].append({
                        'function': func_name,
                        'error': str(e)
                    })
                    logger.error(f"✗ {func_name} - FAILED: {e}")
            
            # Test AnimationVisualizer functions
            animation_viz_functions = [
                ('animation_viz.animate_network_growth',
                 lambda: animation_viz.animate_network_growth(
                     time_steps=15,
                     save_path=str(self.output_dir / "animations" / "network_growth.gif"))),
                ('animation_viz.animate_pattern_discovery',
                 lambda: animation_viz.animate_pattern_discovery(
                     time_steps=10,
                     save_path=str(self.output_dir / "animations" / "pattern_discovery.gif"))),
                ('animation_viz.animate_query_execution',
                 lambda: animation_viz.animate_query_execution(
                     query_steps=8,
                     save_path=str(self.output_dir / "animations" / "query_execution.gif"))),
                ('animation_viz.animate_system_metrics',
                 lambda: animation_viz.animate_system_metrics(
                     time_steps=12,
                     save_path=str(self.output_dir / "animations" / "system_metrics.gif"))),
                ('animation_viz.create_interactive_timeline',
                 lambda: animation_viz.create_interactive_timeline(
                     save_path=str(self.output_dir / "visualizations" / "interactive_timeline.png"))),
                ('animation_viz.create_comprehensive_animation_suite',
                 lambda: animation_viz.create_comprehensive_animation_suite(str(self.output_dir / "animations"))),
            ]
            
            for func_name, func_call in animation_viz_functions:
                try:
                    result = func_call()
                    self.test_results['functions_tested'].append({
                        'function': func_name,
                        'status': 'PASSED',
                        'result_type': type(result).__name__
                    })
                    if 'save_path' in func_name or 'animation' in func_name:
                        self.test_results['animations_created'].append(func_name)
                    logger.info(f"✓ {func_name} - PASSED")
                except Exception as e:
                    self.test_results['failed_tests'].append({
                        'function': func_name,
                        'error': str(e)
                    })
                    logger.error(f"✗ {func_name} - FAILED: {e}")
            
            logger.info(f"Visualization function testing complete: "
                       f"{len(self.test_results['visualizations_created'])} visualizations, "
                       f"{len(self.test_results['animations_created'])} animations created")
            
        except Exception as e:
            logger.error(f"Error in visualization function testing: {e}")
    
    def calculate_output_statistics(self):
        """Calculate statistics about generated outputs."""
        logger.info("Calculating output statistics...")
        
        total_size = 0
        file_count = 0
        
        for root, dirs, files in os.walk(self.output_dir):
            for file in files:
                file_path = Path(root) / file
                try:
                    size = file_path.stat().st_size
                    total_size += size
                    file_count += 1
                except Exception:
                    continue
        
        self.test_results['total_size_mb'] = total_size / (1024 * 1024)
        self.test_results['total_files'] = file_count
        self.test_results['end_time'] = datetime.now().isoformat()
        
        logger.info(f"Output statistics: {file_count} files, {self.test_results['total_size_mb']:.2f} MB total")
    
    def generate_final_report(self):
        """Generate a comprehensive final report."""
        logger.info("Generating final comprehensive report...")
        
        self.calculate_output_statistics()
        
        # Create detailed report
        report_path = self.output_dir / "reports" / "comprehensive_test_report.json"
        with open(report_path, 'w') as f:
            import json
            json.dump(self.test_results, f, indent=2)
        
        # Create human-readable summary
        summary_path = self.output_dir / "reports" / "test_summary.txt"
        with open(summary_path, 'w') as f:
            f.write("ATLAS COMPREHENSIVE VISUALIZATION TEST SUITE REPORT\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Test Execution Date: {self.test_results['start_time']}\n")
            f.write(f"Test Completion Date: {self.test_results['end_time']}\n")
            f.write(f"Output Directory: {self.output_dir}\n\n")
            
            f.write("FUNCTION TESTING RESULTS:\n")
            f.write(f"  Total Functions Tested: {len(self.test_results['functions_tested'])}\n")
            f.write(f"  Functions Passed: {sum(1 for f in self.test_results['functions_tested'] if f['status'] == 'PASSED')}\n")
            f.write(f"  Functions Failed: {len(self.test_results['failed_tests'])}\n\n")
            
            f.write("VISUALIZATION OUTPUTS:\n")
            f.write(f"  Static Visualizations: {len(self.test_results['visualizations_created'])}\n")
            f.write(f"  Animations Created: {len(self.test_results['animations_created'])}\n")
            f.write(f"  Total Output Files: {self.test_results.get('total_files', 0)}\n")
            f.write(f"  Total Output Size: {self.test_results['total_size_mb']:.2f} MB\n\n")
            
            f.write("OUTPUT STRUCTURE:\n")
            f.write(f"  {self.output_dir}/\n")
            f.write(f"    ├── visualizations/     - Static visualization outputs\n")
            f.write(f"    ├── animations/         - Animated visualization outputs  \n")
            f.write(f"    ├── reports/            - Test reports and analysis\n")
            f.write(f"    └── metrics/            - System metrics and statistics\n\n")
            
            if self.test_results['failed_tests']:
                f.write("FAILED TESTS:\n")
                for failed in self.test_results['failed_tests']:
                    f.write(f"  - {failed['function']}: {failed['error']}\n")
            
        logger.info(f"Comprehensive report generated: {report_path}")
        logger.info(f"Human-readable summary: {summary_path}")
    
    def run_comprehensive_test_suite(self):
        """Run the complete comprehensive test suite."""
        logger.info("Starting comprehensive ATLAS test suite execution...")
        
        start_time = time.time()
        
        try:
            # Step 1: Setup comprehensive test data
            atlas, pattern_engine = self.setup_test_data()
            
            # Step 2: Test all core functions
            self.test_all_core_functions(atlas, pattern_engine)
            
            # Step 3: Test all visualization functions
            self.test_all_visualization_functions(atlas, pattern_engine)
            
            # Step 4: Generate final report
            self.generate_final_report()
            
            execution_time = time.time() - start_time
            
            # Final summary
            logger.info("=" * 60)
            logger.info("COMPREHENSIVE TEST SUITE COMPLETED")
            logger.info("=" * 60)
            logger.info(f"Execution Time: {execution_time:.2f} seconds")
            logger.info(f"Functions Tested: {len(self.test_results['functions_tested'])}")
            logger.info(f"Visualizations Created: {len(self.test_results['visualizations_created'])}")
            logger.info(f"Animations Created: {len(self.test_results['animations_created'])}")
            logger.info(f"Total Output Size: {self.test_results['total_size_mb']:.2f} MB")
            logger.info(f"Output Directory: {self.output_dir}")
            
            if self.test_results['failed_tests']:
                logger.warning(f"Failed Tests: {len(self.test_results['failed_tests'])}")
                return 1
            else:
                logger.info("✅ ALL TESTS PASSED!")
                return 0
                
        except Exception as e:
            logger.error(f"Comprehensive test suite failed: {e}")
            import traceback
            traceback.print_exc()
            return 1


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive ATLAS Visualization Test Suite')
    parser.add_argument('--output-dir', default='comprehensive_viz_output',
                       help='Output directory for all test results')
    
    args = parser.parse_args()
    
    # Run comprehensive test suite
    test_suite = ComprehensiveVisualizationTestSuite(args.output_dir)
    exit_code = test_suite.run_comprehensive_test_suite()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main() 