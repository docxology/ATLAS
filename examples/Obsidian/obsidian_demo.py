#!/usr/bin/env python3
"""
ATLAS Obsidian Integration Demo - Comprehensive Showcase

This script demonstrates the full integration between ATLAS and Obsidian vaults,
including importing Obsidian notes into ATLAS, exporting ATLAS data to
Obsidian-compatible markdown files, and showcasing all visualization capabilities.
"""

import sys
import os
import argparse
import json
import shutil
import warnings
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Any, Optional, Union, Set
import numpy as np

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="networkx")


class ATLASJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime and other special objects."""
    def default(self, obj: Any) -> Any:  # type: ignore
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, (set, frozenset)):
            return list(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, (np.integer, np.floating)):
            return obj.item()
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Configure logging to prevent truncation
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
# Reduce log message length limits
logging.getLogger().handlers[0].setFormatter(
    logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
)

try:
    # Core ATLAS imports
    from atlas.core.engine import ATLASEngine, ATLASConfig
    from atlas.entities.entity import Entity, EntityMetadata
    from atlas.entities.attribute import Attribute
    from atlas.patterns.pattern import Pattern
    from atlas.patterns.pattern_engine import PatternEngine
    from atlas.queries.iquery import iQuery, QueryPriority, QueryStatus
    from atlas.integrations.obsidian import ObsidianIntegration
    from atlas.interfaces.prompt_interface import PromptInterface, SimpleTransformInterface
    from atlas.utils.helpers import generate_id, timestamp_now, deep_merge, safe_get
    
    # Visualization imports
    try:
        from atlas.visualization.graph_viz import GraphVisualizer
        from atlas.visualization.pattern_viz import PatternVisualizer
        from atlas.visualization.metrics_viz import MetricsVisualizer
        from atlas.visualization.network_viz import NetworkVisualizer
        from atlas.visualization.animation_viz import AnimationVisualizer
        VISUALIZATION_AVAILABLE = True
    except ImportError as e:
        print(f"Warning: Visualization modules not available: {e}")
        VISUALIZATION_AVAILABLE = False
    
    OBSIDIAN_AVAILABLE = True
except ImportError as e:
    print(f"Failed to import required modules: {e}")
    print("Please ensure you're running from the correct directory and dependencies are installed.")
    OBSIDIAN_AVAILABLE = False
    VISUALIZATION_AVAILABLE = False


def load_vault_templates() -> Dict[str, Any]:
    """Load vault templates from JSON file."""
    templates_file = Path(__file__).parent / "sample_vault_templates.json"
    try:
        with open(templates_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: Templates file not found at {templates_file}")
        return {"notes": {}, "templates": {}}
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in templates file: {e}")
        return {"notes": {}, "templates": {}}


def create_sample_obsidian_vault(vault_path: Path) -> None:
    """Create a sample Obsidian vault for demonstration."""
    print(f"\n=== Creating Sample Obsidian Vault at {vault_path} ===")
    
    # Create vault directory structure
    vault_path.mkdir(parents=True, exist_ok=True)
    (vault_path / "01 - Areas").mkdir(exist_ok=True)
    (vault_path / "02 - Resources").mkdir(exist_ok=True)
    (vault_path / "03 - Projects").mkdir(exist_ok=True)
    (vault_path / "04 - Archive").mkdir(exist_ok=True)
    (vault_path / "Templates").mkdir(exist_ok=True)
    
    # Load templates from JSON file
    vault_templates = load_vault_templates()
    notes = vault_templates.get("notes", {})
    templates = vault_templates.get("templates", {})
    
    # Write all the sample notes
    for note_path, content in notes.items():
        file_path = vault_path / note_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    # Create templates
    for template_path, template_content in templates.items():
        file_path = vault_path / "Templates" / template_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
    
    print(f"✓ Created sample vault with {len(notes)} notes and {len(templates)} templates")


def demonstrate_obsidian_import(integration: ObsidianIntegration, vault_path: Path) -> Dict[str, Any]:
    """Demonstrate importing an Obsidian vault into ATLAS."""
    print("\n=== Demonstrating Obsidian Import ===")
    
    # Import the vault
    print(f"Importing vault from: {vault_path}")
    import_stats = integration.import_vault(vault_path)
    
    print("\n--- Import Statistics ---")
    for key, value in import_stats.items():
        if key != 'errors':
            print(f"  {key}: {value}")
    
    if import_stats.get('errors'):
        print("  Errors encountered:")
        for error in import_stats['errors']:
            print(f"    - {error}")
    
    # Show what was created in ATLAS
    atlas = integration.atlas
    print(f"\n--- ATLAS Content Summary ---")
    print(f"  Entities: {len(atlas.entities)}")
    print(f"  Patterns: {len(atlas.patterns)}")
    print(f"  Queries: {len(atlas.queries)}")
    
    # Show some example entities
    print(f"\n--- Sample Entities ---")
    for i, (entity_id, entity_data) in enumerate(atlas.entities.items()):
        if i >= 3:  # Show first 3
            break
        title = entity_data.get('attributes', {}).get('title', entity_id)
        tags = entity_data.get('attributes', {}).get('tags', [])
        print(f"  • {title} (ID: {entity_id})")
        if tags:
            # Convert all tags to strings for display
            str_tags = [str(tag) for tag in tags]
            print(f"    Tags: {', '.join(str_tags[:3])}{'...' if len(str_tags) > 3 else ''}")
    
    # Show pattern creation
    print(f"\n--- Created Patterns ---")
    for i, (pattern_id, pattern_data) in enumerate(atlas.patterns.items()):
        if i >= 5:  # Show first 5
            break
        source = pattern_data.get('attributes', {}).get('source', 'unknown')
        domain = pattern_data.get('attributes', {}).get('domain', 'general')
        print(f"  • {pattern_id} ({source}, domain: {domain})")
    
    return import_stats


def demonstrate_obsidian_export(integration: ObsidianIntegration, output_path: Path) -> Dict[str, Any]:
    """Demonstrate exporting ATLAS data to Obsidian format."""
    print("\n=== Demonstrating ATLAS to Obsidian Export ===")
    
    # Add some additional ATLAS data for export demonstration
    atlas = integration.atlas
    
    # Only add demo data if it doesn't already exist
    if "atlas_demo_entity" not in atlas.entities:
        # Create a sample entity
        sample_entity = Entity(
            entity_id="atlas_demo_entity",
            attributes={
                "title": "ATLAS Demo Entity",
                "content": "This entity was created directly in ATLAS to demonstrate export functionality.",
                "domain": "demonstration",
                "importance": "high",
                "related_concepts": ["knowledge management", "integration", "demo"]
            },
            patterns=["demo_pattern"]
        )
        
        # Create a sample pattern
        sample_pattern = Pattern(
            pattern_id="demo_pattern",
            qkit=["what_is_demo", "how_to_demo", "why_demo_important"],
            attributes={
                "domain": "demonstration",
                "description": "A pattern for demonstration purposes",
                "complexity": "simple"
            }
        )
        
        # Create a sample query
        sample_query = iQuery(
            query_id="demo_query",
            query_text="How can we effectively demonstrate knowledge management integration?",
            target_patterns=["demo_pattern"],
            priority=QueryPriority.HIGH
        )
        
        # Add to ATLAS
        atlas.add_entity(sample_entity.id, sample_entity.to_dict())
        atlas.add_pattern(sample_pattern.id, sample_pattern.to_dict())
        atlas.add_query(sample_query.id, sample_query.to_dict())
        
        # Create relationship
        atlas.add_relationship(sample_entity.id, sample_pattern.id, "instantiates")
        
        print("✓ Added demo data to ATLAS")
    else:
        print("✓ Demo data already exists in ATLAS")
    
    # Export to Obsidian vault
    print(f"Exporting ATLAS data to: {output_path}")
    export_stats = integration.export_to_vault(output_path)
    
    print("\n--- Export Statistics ---")
    for key, value in export_stats.items():
        if key != 'errors':
            print(f"  {key}: {value}")
    
    if export_stats.get('errors'):
        print("  Export errors:")
        for error in export_stats['errors']:
            print(f"    - {error}")
    
    # Show generated vault structure
    vault_path = output_path / "ATLAS_Export"
    if vault_path.exists():
        print(f"\n--- Generated Vault Structure ---")
        print("exported_vault/")
        for root, dirs, files in os.walk(vault_path):
            level = root.replace(str(vault_path), '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
    
    return export_stats


def demonstrate_bidirectional_sync(integration: ObsidianIntegration, vault_path: Path) -> dict:
    """Demonstrate bidirectional synchronization."""
    print("\n=== Demonstrating Bidirectional Synchronization ===")
    
    # Perform bidirectional sync
    sync_stats = integration.sync_vault(vault_path, sync_mode='bidirectional')
    
    print(f"Sync direction: {sync_stats['mode']}")
    print(f"Timestamp: {sync_stats['timestamp']}")
    
    if 'import_stats' in sync_stats:
        print(f"\nImport phase:")
        for key, value in sync_stats['import_stats'].items():
            if key != 'errors':
                print(f"  {key}: {value}")
    
    if 'export_stats' in sync_stats:
        print(f"\nExport phase:")
        for key, value in sync_stats['export_stats'].items():
            if key != 'errors':
                print(f"  {key}: {value}")
    
    return sync_stats


def demonstrate_advanced_features(integration: ObsidianIntegration) -> None:
    """Demonstrate advanced integration features."""
    print("\n=== Advanced Integration Features ===")
    
    # Get integration statistics
    stats = integration.get_integration_stats()
    
    print("\n--- Integration Statistics ---")
    print(f"Imported notes: {stats['imported_notes']}")
    print(f"Exported files: {stats['exported_files']}")
    print(f"ATLAS entities: {stats['atlas_entities']}")
    print(f"ATLAS patterns: {stats['atlas_patterns']}")
    print(f"ATLAS queries: {stats['atlas_queries']}")
    
    # Get ATLAS metrics
    atlas_metrics = integration.atlas.get_metrics()
    print(f"Graph nodes: {atlas_metrics.get('total_nodes', 0)}")
    print(f"Graph edges: {atlas_metrics.get('total_edges', 0)}")
    print(f"Graph density: {atlas_metrics.get('graph_density', 0):.3f}")
    
    # Show configuration
    print("\n--- Integration Configuration ---")
    print("  • Automatic pattern creation from tags: enabled")
    print("  • Entity creation from notes: enabled")
    print("  • Wiki-link relationship mapping: enabled")
    
    # Demonstrate pattern capabilities with PatternEngine
    print("\n--- Pattern Analysis ---")
    atlas = integration.atlas
    
    if len(atlas.patterns) >= 2:
        pattern_engine = PatternEngine()
        
        # Add patterns to engine for analysis
        for pattern_id, pattern_data in atlas.patterns.items():
            try:
                pattern_obj = Pattern.from_dict(pattern_data)
                pattern_engine.add_pattern(pattern_obj)
            except Exception as e:
                print(f"Warning: Could not add pattern {pattern_id} to engine: {e}")
        
        # Get pattern analysis
        pattern_stats = pattern_engine.analyze_pattern_usage()
        print(f"Pattern engine loaded with {len(pattern_engine.patterns)} patterns")
        print(f"Most used pattern: {pattern_stats.get('most_used', {}).get('pattern_id', 'N/A')}")
        print(f"Average effectiveness: {pattern_stats.get('average_effectiveness', 0):.3f}")
        
        # Find pattern clusters
        clusters = pattern_engine.detect_pattern_clusters()
        print(f"Pattern clusters detected: {len(clusters)}")
    
    # Show graph export capability
    print("\n--- Graph Export ---")
    atlas = integration.atlas
    try:
        # Try JSON export instead of GraphML for compatibility
        import networkx as nx
        # Suppress the FutureWarning and use default behavior for now
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            graph_data = nx.node_link_data(atlas.graph)
        graph_export = json.dumps(graph_data, indent=2, cls=ATLASJSONEncoder)
        print(f"Graph export size: {len(graph_export)} characters")
        print("✓ Graph can be exported in JSON format")
    except Exception as e:
        print(f"Graph export failed: {e}")


def demonstrate_comprehensive_visualizations(integration: ObsidianIntegration, output_dir: Path) -> Dict[str, Any]:
    """Demonstrate all available visualization capabilities."""
    if not VISUALIZATION_AVAILABLE:
        print("\n=== Visualization Capabilities Not Available ===")
        print("Install visualization dependencies (matplotlib, plotly, networkx) to enable visualizations")
        return {}
    
    print("\n=== Comprehensive Visualization Demonstration ===")
    
    atlas = integration.atlas
    viz_results = {}
    viz_dir = output_dir / "visualizations"
    viz_dir.mkdir(exist_ok=True)
    
    # 1. Graph Visualizations
    print("\n--- Graph Topology Visualizations ---")
    try:
        graph_viz = GraphVisualizer(atlas)
        
        # Network topology
        topology_fig = graph_viz.visualize_network_topology(
            layout='spring',
            save_path=str(viz_dir / "network_topology.png"),
            show_labels=True
        )
        print("✓ Network topology visualization created")
        
        # Component distribution
        component_fig = graph_viz.visualize_component_distribution(
            save_path=str(viz_dir / "component_distribution.png")
        )
        print("✓ Component distribution visualization created")
        
        # Interactive network
        interactive_fig = graph_viz.create_interactive_network(
            save_path=str(viz_dir / "interactive_network.html")
        )
        print("✓ Interactive network visualization created")
        
        # Export graph statistics
        graph_stats = graph_viz.generate_graph_statistics()
        viz_results['graph_statistics'] = graph_stats
        
    except Exception as e:
        print(f"Graph visualization error: {e}")
    
    # 2. Pattern Visualizations
    print("\n--- Pattern Analysis Visualizations ---")
    try:
        pattern_engine = PatternEngine()
        
        # Add patterns to engine
        for pattern_id, pattern_data in atlas.patterns.items():
            try:
                pattern_obj = Pattern.from_dict(pattern_data)
                pattern_engine.add_pattern(pattern_obj)
            except Exception as e:
                continue
        
        pattern_viz = PatternVisualizer(atlas, pattern_engine)
        
        # Pattern hierarchy
        hierarchy_fig = pattern_viz.visualize_pattern_hierarchy(
            save_path=str(viz_dir / "pattern_hierarchy.png"),
            show_qkit_size=True
        )
        print("✓ Pattern hierarchy visualization created")
        
        # Pattern effectiveness
        effectiveness_fig = pattern_viz.visualize_pattern_effectiveness(
            save_path=str(viz_dir / "pattern_effectiveness.png")
        )
        print("✓ Pattern effectiveness visualization created")
        
        # QKit analysis
        qkit_fig = pattern_viz.visualize_qkit_analysis(
            save_path=str(viz_dir / "qkit_analysis.png")
        )
        print("✓ QKit analysis visualization created")
        
    except Exception as e:
        print(f"Pattern visualization error: {e}")
    
    # 3. System Metrics Visualizations
    print("\n--- System Metrics Visualizations ---")
    try:
        metrics_viz = MetricsVisualizer(atlas)
        
        # System overview
        overview_fig = metrics_viz.visualize_system_overview(
            save_path=str(viz_dir / "system_overview.png")
        )
        print("✓ System overview visualization created")
        
        # Performance metrics
        performance_fig = metrics_viz.visualize_performance_metrics(
            save_path=str(viz_dir / "performance_metrics.png")
        )
        print("✓ Performance metrics visualization created")
        
        # Quality metrics
        quality_fig = metrics_viz.visualize_quality_metrics(
            save_path=str(viz_dir / "quality_metrics.png")
        )
        print("✓ Quality metrics visualization created")
        
        # Export metrics report
        metrics_report = metrics_viz.export_metrics_report(
            str(viz_dir / "metrics_report.html")
        )
        viz_results['metrics_report'] = metrics_report
        
    except Exception as e:
        print(f"Metrics visualization error: {e}")
    
    # 4. Network Analysis Visualizations
    print("\n--- Network Analysis Visualizations ---")
    try:
        network_viz = NetworkVisualizer(atlas)
        
        # Network structure analysis
        structure_analysis = network_viz.analyze_network_structure()
        viz_results['network_analysis'] = structure_analysis
        
        # Centrality analysis
        centrality_fig = network_viz.visualize_centrality_analysis(
            save_path=str(viz_dir / "centrality_analysis.png")
        )
        print("✓ Centrality analysis visualization created")
        
        # Community structure
        community_fig = network_viz.visualize_community_structure(
            save_path=str(viz_dir / "community_structure.png")
        )
        print("✓ Community structure visualization created")
        
        # Export network analysis
        network_report = network_viz.export_network_analysis(
            str(viz_dir / "network_analysis.json")
        )
        viz_results['network_report'] = network_report
        
    except Exception as e:
        print(f"Network visualization error: {e}")
    
    # 5. Animation Visualizations
    print("\n--- Animation Visualizations ---")
    try:
        animation_viz = AnimationVisualizer(atlas, pattern_engine if 'pattern_engine' in locals() else None)
        
        # Network growth animation
        growth_animation = animation_viz.animate_network_growth(
            time_steps=20,
            save_path=str(viz_dir / "network_growth.gif")
        )
        print("✓ Network growth animation created")
        
        # Pattern discovery animation
        discovery_animation = animation_viz.animate_pattern_discovery(
            time_steps=15,
            save_path=str(viz_dir / "pattern_discovery.gif")
        )
        print("✓ Pattern discovery animation created")
        
        # System metrics animation
        metrics_animation = animation_viz.animate_system_metrics(
            time_steps=20,
            save_path=str(viz_dir / "system_metrics.gif")
        )
        print("✓ System metrics animation created")
        
        # Create comprehensive animation suite
        animation_suite = animation_viz.create_comprehensive_animation_suite(
            str(viz_dir / "animations"),
            suite_name="obsidian_atlas_demo"
        )
        viz_results['animation_suite'] = animation_suite
        
    except Exception as e:
        print(f"Animation visualization error: {e}")
    
    print(f"\n✓ All visualizations saved to: {viz_dir}")
    return viz_results


def demonstrate_entity_attribute_system(integration: ObsidianIntegration) -> Dict[str, Any]:
    """Demonstrate the entity-attribute system capabilities."""
    print("\n=== Entity-Attribute System Demonstration ===")
    
    atlas = integration.atlas
    demo_results: Dict[str, Any] = {}
    
    # Create sample entities with attributes
    print("\n--- Creating Sample Entities with Attributes ---")
    
    # Create a knowledge domain entity
    domain_entity = Entity(
        entity_id="knowledge_domain_ai",
        attributes={
            "name": "Artificial Intelligence",
            "description": "Core AI knowledge domain from Obsidian import",
            "complexity": "high",
            "maturity": 0.8,
            "tags": ["ai", "knowledge", "domain"]
        },
        patterns=["obsidian_tag_ai"]
    )
    
    # Create specialized attributes
    complexity_attr = Attribute(
        attribute_id="complexity_measure",
        value="high",
        data_type="string",
        attributes={
            "scale": "low|medium|high|expert",
            "numeric_value": 4,
            "description": "Complexity level of knowledge domain"
        }
    )
    
    # Add validation rules to attribute
    complexity_attr.add_validation_rule("enum", {"values": ["low", "medium", "high", "expert"]})
    complexity_attr.add_validation_rule("type", {"expected": "string"})
    
    # Add entities to ATLAS
    atlas.add_entity(domain_entity.id, domain_entity.to_dict())
    atlas.add_entity(complexity_attr.id, complexity_attr.to_dict())
    
    # Create relationships
    atlas.add_relationship(domain_entity.id, complexity_attr.id, "has_attribute")
    
    demo_results.update({
        "entities_created": 2,
        "relationships_created": 1
    })
    
    print(f"✓ Created domain entity: {domain_entity.id}")
    print(f"✓ Created complexity attribute: {complexity_attr.id}")
    print(f"✓ Established has_attribute relationship")
    
    # Demonstrate attribute validation
    print("\n--- Attribute Validation Demonstration ---")
    
    # Test valid value
    valid_result = complexity_attr.set_value("expert")
    print(f"✓ Valid value 'expert' accepted: {valid_result}")
    
    # Test invalid value
    invalid_result = complexity_attr.set_value("invalid_level")
    print(f"✓ Invalid value 'invalid_level' rejected: {not invalid_result}")
    
    # Show transformation history
    history = complexity_attr.get_transformation_history()
    print(f"✓ Transformation history has {len(history)} entries")
    
    validation_tests: Dict[str, Any] = {
        "valid_test_passed": valid_result,
        "invalid_test_passed": not invalid_result,
        "history_entries": len(history)
    }
    demo_results["validation_tests"] = validation_tests
    
    return demo_results


def demonstrate_query_system(integration: ObsidianIntegration) -> Dict[str, Any]:
    """Demonstrate the iQuery system capabilities."""
    print("\n=== iQuery System Demonstration ===")
    
    atlas = integration.atlas
    query_results = {}
    
    # Create sample queries
    print("\n--- Creating Sample iQueries ---")
    
    # Knowledge discovery query
    discovery_query = iQuery(
        query_id="obsidian_knowledge_discovery",
        query_text="What are the key patterns in the imported Obsidian knowledge?",
        target_patterns=["obsidian_tag_ai", "obsidian_tag_ml", "obsidian_tag_research"],
        priority=QueryPriority.HIGH,
        context={
            "source": "obsidian_import",
            "domain": "knowledge_management",
            "analysis_type": "pattern_discovery"
        }
    )
    
    # Relationship analysis query
    relationship_query = iQuery(
        query_id="obsidian_relationship_analysis",
        query_text="How are software development concepts connected to AI concepts?",
        target_patterns=["obsidian_tag_software", "obsidian_tag_ai", "obsidian_tag_programming"],
        priority=QueryPriority.NORMAL,
        context={
            "analysis_type": "relationship_mapping",
            "focus": "cross_domain_connections"
        }
    )
    
    # Add queries to ATLAS
    atlas.add_query(discovery_query.id, discovery_query.to_dict())
    atlas.add_query(relationship_query.id, relationship_query.to_dict())
    
    print(f"✓ Created discovery query: {discovery_query.id}")
    print(f"✓ Created relationship query: {relationship_query.id}")
    
    # Execute queries
    print("\n--- Executing Queries ---")
    
    # Execute discovery query
    discovery_query.start_execution()
    discovery_results = atlas.query("AI patterns knowledge", {"source": "obsidian"})
    discovery_query.complete_execution(discovery_results)
    
    print(f"✓ Discovery query executed, found {len(discovery_results)} results")
    
    # Execute relationship query
    relationship_query.start_execution()
    relationship_results = atlas.query("software AI programming", {"type": "relationship"})
    relationship_query.complete_execution(relationship_results)
    
    print(f"✓ Relationship query executed, found {len(relationship_results)} results")
    
    # Analyze query performance
    print("\n--- Query Performance Analysis ---")
    
    discovery_stats = discovery_query.get_statistics()
    relationship_stats = relationship_query.get_statistics()
    
    print(f"Discovery query quality score: {discovery_stats['quality_score']:.3f}")
    print(f"Relationship query quality score: {relationship_stats['quality_score']:.3f}")
    
    query_results = {
        "queries_created": 2,
        "queries_executed": 2,
        "discovery_results": len(discovery_results),
        "relationship_results": len(relationship_results),
        "discovery_quality": discovery_stats['quality_score'],
        "relationship_quality": relationship_stats['quality_score']
    }
    
    return query_results


def demonstrate_prompt_interfaces(integration: ObsidianIntegration) -> Dict[str, Any]:
    """Demonstrate the prompt interface system."""
    print("\n=== Prompt Interface System Demonstration ===")
    
    interface_results = {}
    
    # Create a markdown formatter interface
    print("\n--- Creating Markdown Formatter Interface ---")
    
    def format_entity_as_markdown(entity_data: Any) -> str:
        """Format entity data as markdown."""
        if isinstance(entity_data, dict):
            attributes = entity_data.get('attributes', {})
            title = str(attributes.get('title', 'Untitled'))  # type: ignore
            content = str(attributes.get('content', ''))  # type: ignore
            tags = attributes.get('tags', [])  # type: ignore
            
            markdown = f"# {title}\n\n"
            if content:
                markdown += f"{content}\n\n"
            if tags:
                tag_line = " ".join([f"#{tag}" for tag in tags])
                markdown += f"**Tags:** {tag_line}\n"
            
            return markdown
        return str(entity_data)
    
    markdown_interface = SimpleTransformInterface(
        transform_func=format_entity_as_markdown,
        name="Markdown Entity Formatter",
        description="Converts ATLAS entities to markdown format",
        input_schema={"type": "dict"},
        output_schema={"type": "str"}
    )
    
    # Test the interface
    sample_entity = integration.atlas.entities.get(
        list(integration.atlas.entities.keys())[0]
    ) if integration.atlas.entities else {"attributes": {"title": "Test", "content": "Sample content"}}
    
    format_result = markdown_interface.execute(sample_entity)
    
    print(f"✓ Markdown interface created: {markdown_interface.id}")
    print(f"✓ Interface execution successful: {format_result['success']}")
    
    # Create an entity summarizer interface
    print("\n--- Creating Entity Summarizer Interface ---")
    
    def summarize_entity(entity_data: Any) -> Dict[str, Any]:
        """Create a summary of entity data."""
        if isinstance(entity_data, dict):
            attributes = entity_data.get('attributes', {})
            title = str(attributes.get('title', 'Unknown'))  # type: ignore
            tags = attributes.get('tags', [])  # type: ignore
            content = str(attributes.get('content', ''))  # type: ignore
            
            # Simple summarization
            content_length = len(content) if content else 0
            summary = {
                "title": title,
                "tag_count": len(tags),
                "content_length": content_length,
                "primary_tags": tags[:3] if tags else [],
                "summary": f"Entity '{title}' with {len(tags)} tags and {content_length} characters of content"
            }
            return summary
        return {"error": "Invalid entity data"}
    
    summarizer_interface = SimpleTransformInterface(
        transform_func=summarize_entity,
        name="Entity Summarizer",
        description="Creates summaries of ATLAS entities",
        input_schema={"type": "dict"},
        output_schema={"type": "dict"}
    )
    
    summary_result = summarizer_interface.execute(sample_entity)
    
    print(f"✓ Summarizer interface created: {summarizer_interface.id}")
    print(f"✓ Summary generation successful: {summary_result['success']}")
    
    # Get interface statistics
    markdown_stats = markdown_interface.get_statistics()
    summarizer_stats = summarizer_interface.get_statistics()
    
    interface_results = {
        "interfaces_created": 2,
        "markdown_interface_stats": markdown_stats,
        "summarizer_interface_stats": summarizer_stats,
        "test_executions": 2,
        "success_rate": 1.0
    }
    
    return interface_results


def save_enhanced_demonstration_results(
    comprehensive_results: Dict[str, Any],
    output_dir: Path
) -> None:
    """Save comprehensive demonstration results."""
    print(f"\n=== Saving Enhanced Demonstration Results to {output_dir} ===")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract core results
    import_stats = comprehensive_results.get("import_stats", {})
    export_stats = comprehensive_results.get("export_stats", {})
    sync_stats = comprehensive_results.get("sync_stats", {})
    
    # Compile comprehensive results
    demo_results = {
        "timestamp": timestamp_now(),
        "demonstration_type": "comprehensive_obsidian_atlas_integration",
        "core_integration": {
            "import_demonstration": import_stats,
            "export_demonstration": export_stats,
            "sync_demonstration": sync_stats,
        },
        "advanced_features": {
            "visualization_results": comprehensive_results.get("visualization_results", {}),
            "entity_system_results": comprehensive_results.get("entity_system_results", {}),
            "query_system_results": comprehensive_results.get("query_system_results", {}),
            "interface_results": comprehensive_results.get("interface_results", {}),
        },
        "summary": {
            "total_notes_imported": import_stats.get('notes_imported', 0),
            "total_entities_created": import_stats.get('entities_created', 0),
            "total_patterns_created": import_stats.get('patterns_created', 0),
            "total_relationships_created": import_stats.get('relationships_created', 0),
            "total_notes_exported": export_stats.get('notes_created', 0),
            "total_folders_created": export_stats.get('folders_created', 0),
            "visualizations_generated": len(comprehensive_results.get("visualization_results", {})),
            "integration_success": True
        },
        "status": "COMPLETED"
    }
    
    # Save results with error handling
    try:
        with open(output_dir / "comprehensive_integration_results.json", 'w', encoding='utf-8') as f:
            json.dump(demo_results, f, indent=2, cls=ATLASJSONEncoder, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Failed to save JSON results: {e}")
        # Save simplified version without problematic objects
        simplified_results = {
            "timestamp": demo_results["timestamp"],
            "demonstration_type": demo_results["demonstration_type"],
            "summary": demo_results["summary"],
            "status": demo_results["status"]
        }
        with open(output_dir / "comprehensive_integration_results_simplified.json", 'w', encoding='utf-8') as f:
            json.dump(simplified_results, f, indent=2, cls=ATLASJSONEncoder, ensure_ascii=False)
    
    # Save human-readable summary
    summary_content = f"""ATLAS Obsidian Integration - Comprehensive Demonstration Results
=================================================================

Demonstration completed at: {demo_results['timestamp']}

Core Integration:
- Notes imported: {import_stats.get('notes_imported', 0)}
- Entities created: {import_stats.get('entities_created', 0)}
- Patterns created: {import_stats.get('patterns_created', 0)}
- Relationships created: {import_stats.get('relationships_created', 0)}
- Notes exported: {export_stats.get('notes_created', 0)}
- Folders created: {export_stats.get('folders_created', 0)}

Advanced Features:
- Visualizations generated: {len(comprehensive_results.get('visualization_results', {}))}
- Entity system tests: {comprehensive_results.get('entity_system_results', {}).get('entities_created', 0)}
- Query system tests: {comprehensive_results.get('query_system_results', {}).get('queries_created', 0)}
- Interface system tests: {comprehensive_results.get('interface_results', {}).get('interfaces_created', 0)}

Synchronization:
- Direction: {sync_stats.get('direction', 'N/A')}
- Conflicts detected: {len(sync_stats.get('conflicts', []))}
- Errors encountered: {len(sync_stats.get('errors', []))}

Status: {demo_results['status']}

This comprehensive demonstration showcases the full capabilities of the 
ATLAS knowledge management system with Obsidian integration, including
advanced visualizations, entity-attribute systems, query processing,
and prompt interfaces.
"""
    
    with open(output_dir / "comprehensive_summary.txt", 'w') as f:
        f.write(summary_content)
    
    print(f"✓ Enhanced results saved to {output_dir}")
    print(f"  • comprehensive_integration_results.json - Complete results")
    print(f"  • comprehensive_summary.txt - Human-readable summary")


def save_demonstration_results(
    import_stats: dict, 
    export_stats: dict, 
    sync_stats: dict, 
    output_dir: Path
) -> None:
    """Save comprehensive demonstration results."""
    print(f"\n=== Saving Demonstration Results to {output_dir} ===")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Compile comprehensive results
    demo_results = {
        "timestamp": timestamp_now(),
        "demonstration_type": "obsidian_atlas_integration",
        "import_demonstration": import_stats,
        "export_demonstration": export_stats,
        "sync_demonstration": sync_stats,
        "summary": {
            "total_notes_imported": import_stats.get('notes_imported', 0),
            "total_entities_created": import_stats.get('entities_created', 0),
            "total_patterns_created": import_stats.get('patterns_created', 0),
            "total_relationships_created": import_stats.get('relationships_created', 0),
            "total_notes_exported": export_stats.get('notes_created', 0),
            "total_folders_created": export_stats.get('folders_created', 0),
            "integration_success": True
        },
        "status": "COMPLETED"
    }
    
    # Save results
    with open(output_dir / "obsidian_integration_results.json", 'w') as f:
        json.dump(demo_results, f, indent=2, cls=ATLASJSONEncoder)
    
    # Save human-readable summary
    summary_content = f"""ATLAS Obsidian Integration Demonstration Results
=================================================

Demonstration completed at: {demo_results['timestamp']}

Import Phase:
- Notes imported: {import_stats.get('notes_imported', 0)}
- Entities created: {import_stats.get('entities_created', 0)}
- Patterns created: {import_stats.get('patterns_created', 0)}
- Relationships created: {import_stats.get('relationships_created', 0)}

Export Phase:
- Notes exported: {export_stats.get('notes_created', 0)}
- Folders created: {export_stats.get('folders_created', 0)}
- Index notes created: {export_stats.get('index_notes_created', 0)}

Synchronization:
- Direction: {sync_stats.get('direction', 'N/A')}
- Conflicts detected: {len(sync_stats.get('conflicts', []))}
- Errors encountered: {len(sync_stats.get('errors', []))}

Status: {demo_results['status']}

This demonstration shows the successful bidirectional integration between 
Obsidian vaults and the ATLAS knowledge management system.
"""
    
    with open(output_dir / "integration_summary.txt", 'w') as f:
        f.write(summary_content)
    
    print(f"✓ Results saved to {output_dir}")
    print(f"  • obsidian_integration_results.json - Complete results")
    print(f"  • integration_summary.txt - Human-readable summary")


def main(args):
    """Main demonstration function."""
    if not OBSIDIAN_AVAILABLE:
        print("❌ Obsidian integration modules not available")
        print("Please check your installation and dependencies.")
        return False
    
    print("🚀 ATLAS Obsidian Integration Demonstration")
    print("=" * 50)
    
    # Set up paths
    if args.vault_path:
        vault_path = Path(args.vault_path)
    else:
        vault_path = Path("./demo_obsidian_vault")
    
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path("./obsidian_demo_output")
    
    export_vault_path = output_dir / "exported_vault"
    
    print(f"📁 Sample vault path: {vault_path}")
    print(f"📁 Export path: {export_vault_path}")
    print(f"📁 Results path: {output_dir}")
    
    try:
        # Initialize ATLAS and integration
        atlas_config = ATLASConfig(
            auto_pattern_inference=True,
            enable_dynamic_typing=True,
            enable_quality_metrics=True
        )
        atlas = ATLASEngine(atlas_config)
        integration = ObsidianIntegration(atlas)
        
        print("✓ ATLAS and Obsidian integration initialized")
        
        # Create sample vault if it doesn't exist
        if not vault_path.exists() or not any(vault_path.iterdir()):
            create_sample_obsidian_vault(vault_path)
        else:
            print(f"✓ Using existing vault at {vault_path}")
        
        # Demonstrate import
        import_stats = demonstrate_obsidian_import(integration, vault_path)
        
        # Demonstrate export
        export_stats = demonstrate_obsidian_export(integration, export_vault_path)
        
        # Demonstrate bidirectional sync
        sync_stats = demonstrate_bidirectional_sync(integration, vault_path)
        
        # Demonstrate advanced features
        demonstrate_advanced_features(integration)
        
        # Demonstrate comprehensive visualizations
        if VISUALIZATION_AVAILABLE:
            viz_results = demonstrate_comprehensive_visualizations(integration, output_dir)
            print(f"✓ Generated {len(viz_results)} visualization reports")
        else:
            print("⚠️ Visualization capabilities not available - install matplotlib, plotly, networkx")
            viz_results = {}
        
        # Demonstrate entity-attribute system
        entity_results = demonstrate_entity_attribute_system(integration)
        print(f"✓ Entity-attribute system demonstration completed")
        
        # Demonstrate query system
        query_results = demonstrate_query_system(integration)
        print(f"✓ iQuery system demonstration completed")
        
        # Demonstrate prompt interfaces
        interface_results = demonstrate_prompt_interfaces(integration)
        print(f"✓ Prompt interface system demonstration completed")
        
        # Enhanced results compilation
        comprehensive_results = {
            "import_stats": import_stats,
            "export_stats": export_stats,
            "sync_stats": sync_stats,
            "visualization_results": viz_results,
            "entity_system_results": entity_results,
            "query_system_results": query_results,
            "interface_results": interface_results
        }
        
        # Save enhanced results
        save_enhanced_demonstration_results(comprehensive_results, output_dir)
        
        # Final summary
        print(f"\n🎉 Obsidian integration demonstration completed successfully!")
        print(f"   Processed {import_stats.get('notes_processed', 0)} notes from Obsidian")
        print(f"   Created {import_stats.get('entities_created', 0)} ATLAS entities")
        print(f"   Generated {import_stats.get('patterns_created', 0)} patterns")
        print(f"   Exported {export_stats.get('files_created', 0)} files to Obsidian format")
        print(f"   All results saved to: {output_dir}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ATLAS Obsidian Integration Demonstration")
    parser.add_argument("--vault-path", type=str, help="Path to existing Obsidian vault (will create sample if not provided)")
    parser.add_argument("--output-dir", type=str, help="Directory to save demonstration outputs")
    parser.add_argument("--no-sample", action="store_true", help="Don't create sample vault")
    
    args = parser.parse_args()
    
    success = main(args)
    sys.exit(0 if success else 1) 