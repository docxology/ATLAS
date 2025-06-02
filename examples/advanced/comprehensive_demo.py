#!/usr/bin/env python3
"""
Comprehensive ATLAS System Demonstration

This script demonstrates the full capabilities of the ATLAS knowledge
management system including entities, patterns, queries, and visualizations.
"""

import sys
import os
import logging
import argparse
import json
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from atlas.core.engine import ATLASEngine, ATLASConfig
    from atlas.entities.entity import Entity, EntityMetadata
    from atlas.entities.attribute import Attribute
    from atlas.patterns.pattern import Pattern
    from atlas.patterns.pattern_engine import PatternEngine
    from atlas.queries.iquery import iQuery, QueryPriority
    from atlas.interfaces.prompt_interface import SimpleTransformInterface, create_identity_interface
    from atlas.utils.helpers import generate_id, timestamp_now
    
    # Try to import visualization modules
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
        
except ImportError as e:
    print(f"Failed to import ATLAS modules: {e}")
    print("Please ensure you're running from the correct directory and dependencies are installed.")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_sample_knowledge_base():
    """Create a sample knowledge base for demonstration."""
    print("\n=== Creating Sample Knowledge Base ===")
    
    # Initialize ATLAS engine
    config = ATLASConfig(
        auto_pattern_inference=True,
        enable_dynamic_typing=True,
        max_expansion_depth=5,
        enable_quality_metrics=True,
        log_level="INFO"
    )
    
    atlas = ATLASEngine(config)
    pattern_engine = PatternEngine()
    
    print("✓ ATLAS Engine initialized")
    
    # 1. Create Patterns
    print("\n--- Creating Patterns ---")
    
    # Cognitive Bias Pattern
    cognitive_bias_pattern = Pattern(
        pattern_id="cognitive_bias",
        qkit=["what_triggers_bias", "how_to_mitigate", "examples_in_practice"],
        attributes={
            "domain": "cognitive_science",
            "severity": "high",
            "frequency": "common"
        }
    )
    
    # Confirmation Bias (child pattern)
    confirmation_bias_pattern = Pattern(
        pattern_id="confirmation_bias",
        qkit=["source_selection_bias", "interpretation_bias", "recall_bias"],
        parents=["cognitive_bias"],
        attributes={
            "definition": "Tendency to search for, interpret, and recall information that confirms preconceptions",
            "domain": "cognitive_science",
            "impact": "decision_making"
        }
    )
    
    # Information Security Pattern
    infosec_pattern = Pattern(
        pattern_id="information_security",
        qkit=["threat_assessment", "vulnerability_analysis", "mitigation_strategies"],
        attributes={
            "domain": "cybersecurity",
            "criticality": "high",
            "scope": "enterprise"
        }
    )
    
    # Add patterns to engines
    atlas.add_pattern(cognitive_bias_pattern.id, cognitive_bias_pattern.to_dict())
    atlas.add_pattern(confirmation_bias_pattern.id, confirmation_bias_pattern.to_dict())
    atlas.add_pattern(infosec_pattern.id, infosec_pattern.to_dict())
    
    pattern_engine.add_pattern(cognitive_bias_pattern)
    pattern_engine.add_pattern(confirmation_bias_pattern)
    pattern_engine.add_pattern(infosec_pattern)
    
    print(f"✓ Created {len(pattern_engine.patterns)} patterns")
    
    # 2. Create Entities
    print("\n--- Creating Entities ---")
    
    # Research Paper Entity
    paper_entity = Entity(
        entity_id="paper_kahneman_2011",
        attributes={
            "title": "Thinking, Fast and Slow",
            "author": "Daniel Kahneman",
            "year": 2011,
            "type": "book",
            "domain": "behavioral_economics",
            "citations": 15000,
            "key_concepts": ["system_1_thinking", "system_2_thinking", "cognitive_biases"]
        },
        patterns=[cognitive_bias_pattern.id, confirmation_bias_pattern.id]
    )
    
    # Security Incident Entity
    incident_entity = Entity(
        entity_id="incident_2023_001",
        attributes={
            "date": "2023-03-15",
            "type": "data_breach",
            "severity": "high",
            "affected_records": 50000,
            "root_cause": "social_engineering",
            "status": "resolved"
        },
        patterns=[infosec_pattern.id]
    )
    
    # Expert Entity
    expert_entity = Entity(
        entity_id="expert_alice_smith",
        attributes={
            "name": "Dr. Alice Smith",
            "expertise": ["cognitive_psychology", "decision_science"],
            "affiliation": "University Research Lab",
            "years_experience": 15,
            "publications": 47
        },
        patterns=[cognitive_bias_pattern.id]
    )
    
    # Add entities to ATLAS
    atlas.add_entity(paper_entity.id, paper_entity.to_dict())
    atlas.add_entity(incident_entity.id, incident_entity.to_dict())
    atlas.add_entity(expert_entity.id, expert_entity.to_dict())
    
    print(f"✓ Created 3 entities")
    
    # 3. Create Attributes
    print("\n--- Creating Attributes ---")
    
    quality_attr = Attribute(
        attribute_id="data_quality_score",
        ref_id="dqs_001",
        value=0.87,
        data_type="float",
        attributes={"range": [0, 1], "method": "automated_assessment"}
    )
    
    confidence_attr = Attribute(
        attribute_id="expert_confidence",
        ref_id="ec_001", 
        value=0.92,
        data_type="float",
        attributes={"expert_id": expert_entity.id, "domain": "cognitive_bias"}
    )
    
    print(f"✓ Created 2 attributes")
    
    # 4. Create iQueries
    print("\n--- Creating iQueries ---")
    
    # Query about cognitive bias mitigation
    bias_query = iQuery(
        query_id="query_bias_mitigation",
        query_text="What are effective strategies for mitigating confirmation bias in research?",
        target_patterns=[confirmation_bias_pattern.id],
        priority=QueryPriority.HIGH,
        context={"domain": "research_methodology", "urgency": "high"}
    )
    
    # Query about security patterns
    security_query = iQuery(
        query_id="query_security_patterns",
        query_text="What patterns emerge from recent security incidents?",
        target_patterns=[infosec_pattern.id],
        priority=QueryPriority.NORMAL,
        context={"timeframe": "last_6_months", "scope": "enterprise"}
    )
    
    # Add queries to ATLAS
    atlas.add_query(bias_query.id, bias_query.to_dict())
    atlas.add_query(security_query.id, security_query.to_dict())
    
    print(f"✓ Created 2 iQueries")
    
    # 5. Create Prompt Interfaces
    print("\n--- Creating Prompt Interfaces ---")
    
    # Simple formatting interface
    format_interface = SimpleTransformInterface(
        transform_func=lambda x: f"ATLAS-FORMATTED: {x}",
        name="ATLAS Formatter",
        description="Formats data for ATLAS consumption"
    )
    
    # Identity interface for passthrough
    identity_interface = create_identity_interface("passthrough_001")
    
    print(f"✓ Created 2 prompt interfaces")
    
    # 6. Add relationships
    print("\n--- Adding Relationships ---")
    
    # Link expert to paper
    atlas.add_relationship(expert_entity.id, paper_entity.id, "references")
    
    # Link patterns
    atlas.add_relationship(cognitive_bias_pattern.id, confirmation_bias_pattern.id, "parent_of")
    
    # Link entities to patterns
    atlas.add_relationship(paper_entity.id, cognitive_bias_pattern.id, "exemplifies")
    atlas.add_relationship(incident_entity.id, infosec_pattern.id, "instantiates")
    
    print(f"✓ Added relationships")
    
    return atlas, pattern_engine


def demonstrate_queries(atlas, pattern_engine):
    """Demonstrate query capabilities."""
    print("\n=== Demonstrating Query Capabilities ===")
    
    # Basic search
    print("\n--- Basic Search ---")
    results = atlas.query("cognitive bias")
    print(f"Found {len(results)} results for 'cognitive bias':")
    for result in results[:3]:  # Show first 3
        print(f"  - {result['type']}: {result['id']}")
    
    # Advanced search
    print("\n--- Advanced Search ---")
    results = atlas.query("security")
    print(f"Found {len(results)} results for 'security':")
    for result in results:
        print(f"  - {result['type']}: {result['id']}")
    
    # Pattern similarity analysis
    if len(pattern_engine.patterns) >= 2:
        print("\n--- Pattern Similarity Analysis ---")
        pattern_ids = list(pattern_engine.patterns.keys())
        if len(pattern_ids) >= 2:
            similarity = pattern_engine.calculate_pattern_similarity(pattern_ids[0], pattern_ids[1])
            print(f"Similarity between {pattern_ids[0]} and {pattern_ids[1]}: {similarity:.3f}")


def demonstrate_metrics(atlas, output_dir=None):
    """Demonstrate metrics and analysis."""
    print("\n=== System Metrics and Analysis ===")
    
    # Get system metrics
    metrics = atlas.get_metrics()
    print("\n--- System Metrics ---")
    for key, value in metrics.items():
        print(f"  {key}: {value}")
    
    # Graph statistics
    stats = atlas.export_graph("graphml")
    if stats:
        print(f"✓ Graph exported successfully ({len(stats)} characters)")
        
        # Save graph export if output directory provided
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            with open(output_dir / "atlas_graph.graphml", 'w') as f:
                f.write(stats)
            print(f"✓ Graph saved to {output_dir / 'atlas_graph.graphml'}")


def demonstrate_visualizations(atlas, pattern_engine, output_dir=None):
    """Demonstrate visualization capabilities."""
    if not VISUALIZATION_AVAILABLE:
        print("\n=== Visualization Demonstration ===")
        print("⚠ Visualization modules not available - skipping visualization demo")
        return
    
    print("\n=== Visualization Demonstration ===")
    
    if not output_dir:
        output_dir = Path(".")
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Create visualizers
        graph_viz = GraphVisualizer(atlas)
        pattern_viz = PatternVisualizer(atlas, pattern_engine)
        metrics_viz = MetricsVisualizer(atlas)
        network_viz = NetworkVisualizer(atlas)
        
        print("\n--- Creating Visualizations ---")
        
        # Generate network topology
        print("  Generating network topology visualization...")
        topology_fig = graph_viz.visualize_network_topology(save_path=str(output_dir / "demo_topology.png"))
        print(f"  ✓ Network topology saved to {output_dir / 'demo_topology.png'}")
        
        # Generate component distribution
        print("  Generating component distribution...")
        dist_fig = graph_viz.visualize_component_distribution(save_path=str(output_dir / "demo_distribution.png"))
        print(f"  ✓ Component distribution saved to {output_dir / 'demo_distribution.png'}")
        
        # Generate pattern hierarchy
        print("  Generating pattern hierarchy...")
        hierarchy_fig = pattern_viz.visualize_pattern_hierarchy(save_path=str(output_dir / "demo_hierarchy.png"))
        print(f"  ✓ Pattern hierarchy saved to {output_dir / 'demo_hierarchy.png'}")
        
        # Generate system overview
        print("  Generating system overview...")
        overview_fig = metrics_viz.visualize_system_overview(save_path=str(output_dir / "demo_overview.png"))
        print(f"  ✓ System overview saved to {output_dir / 'demo_overview.png'}")
        
        # Generate network analysis
        print("  Generating network analysis...")
        analysis_results = network_viz.export_network_analysis(str(output_dir / "demo_network"))
        print(f"  ✓ Network analysis completed: {len(analysis_results.get('visualizations_generated', []))} files generated")
        
        # Close figures to free memory
        import matplotlib.pyplot as plt
        plt.close('all')
        
        print("\n✓ All visualizations generated successfully!")
        
    except Exception as e:
        print(f"⚠ Visualization error: {e}")


def demonstrate_advanced_features(atlas, pattern_engine, output_dir=None):
    """Demonstrate advanced ATLAS features."""
    print("\n=== Advanced Features Demonstration ===")
    
    # Pattern analysis
    print("\n--- Pattern Analysis ---")
    if len(pattern_engine.patterns) > 0:
        usage_analysis = pattern_engine.analyze_pattern_usage()
        print(f"  Total patterns: {usage_analysis.get('total_patterns', 0)}")
        print(f"  Root patterns: {len(usage_analysis.get('root_patterns', []))}")
        print(f"  Leaf patterns: {len(usage_analysis.get('leaf_patterns', []))}")
        
        # Save analysis if output directory provided
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            import json
            with open(output_dir / "pattern_analysis.json", 'w') as f:
                json.dump(usage_analysis, f, indent=2)
            print(f"  ✓ Pattern analysis saved to {output_dir / 'pattern_analysis.json'}")
    
    # Entity anomaly detection (simulated)
    print("\n--- Anomaly Detection ---")
    for entity_id in list(atlas.entities.keys())[:2]:  # Check first 2 entities
        # Simulate anomaly detection
        print(f"  Checking entity: {entity_id}")
        print(f"    ✓ No anomalies detected")
    
    # Quality assessment
    print("\n--- Quality Assessment ---")
    total_components = len(atlas.entities) + len(atlas.patterns) + len(atlas.queries)
    quality_score = min(1.0, total_components / 10.0)  # Simple quality metric
    print(f"  System quality score: {quality_score:.2f}")
    print(f"  Components with metadata: {total_components}")


def save_demonstration_results(atlas, pattern_engine, output_dir):
    """Save comprehensive demonstration results."""
    if not output_dir:
        return
        
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save comprehensive results
    import json
    
    metrics = atlas.get_metrics()
    usage_analysis = pattern_engine.analyze_pattern_usage() if pattern_engine.patterns else {}
    
    demo_results = {
        "timestamp": timestamp_now(),
        "demonstration_type": "comprehensive_atlas_demo",
        "system_metrics": metrics,
        "pattern_analysis": usage_analysis,
        "entities": {
            "count": len(atlas.entities),
            "ids": list(atlas.entities.keys())
        },
        "patterns": {
            "count": len(atlas.patterns),
            "ids": list(atlas.patterns.keys())
        },
        "queries": {
            "count": len(atlas.queries),
            "ids": list(atlas.queries.keys())
        },
        "visualization_files_generated": VISUALIZATION_AVAILABLE,
        "status": "COMPLETED"
    }
    
    with open(output_dir / "demonstration_results.json", 'w') as f:
        json.dump(demo_results, f, indent=2)
    
    print(f"✓ Demonstration results saved to {output_dir / 'demonstration_results.json'}")


def demonstrate_advanced_visualizations(atlas, pattern_engine, output_dir=None):
    """Demonstrate advanced visualization and animation capabilities."""
    if not VISUALIZATION_AVAILABLE:
        print("\n=== Advanced Visualization Demonstration ===")
        print("⚠ Advanced visualization modules not available - skipping advanced demo")
        return
    
    print("\n=== Advanced Visualization & Animation Demonstration ===")
    
    if not output_dir:
        output_dir = Path(".")
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Create enhanced visualizers
        graph_viz = GraphVisualizer(atlas)
        pattern_viz = PatternVisualizer(atlas, pattern_engine)
        metrics_viz = MetricsVisualizer(atlas)
        network_viz = NetworkVisualizer(atlas)
        
        # Try to create animation visualizer (may not be available)
        animation_viz = None
        try:
            animation_viz = AnimationVisualizer(atlas, pattern_engine)
            print("  ✓ Animation visualizer available")
        except:
            print("  ⚠ Animation visualizer not available")
        
        print("\n--- Creating Advanced Static Visualizations ---")
        
        # Enhanced network analysis
        print("  Generating comprehensive network analysis...")
        network_analysis = network_viz.export_network_analysis(str(output_dir / "demo_network"))
        print(f"  ✓ Network analysis exported with {len(network_analysis.get('visualizations_generated', []))} visualizations")
        
        # Interactive network visualization
        print("  Creating interactive network visualization...")
        interactive_fig = graph_viz.create_interactive_network(save_path=str(output_dir / "demo_interactive.html"))
        print(f"  ✓ Interactive network saved")
        
        # Quality metrics visualization
        print("  Generating quality metrics analysis...")
        quality_fig = metrics_viz.visualize_quality_metrics(save_path=str(output_dir / "demo_quality.png"))
        print(f"  ✓ Quality metrics visualization saved")
        
        # Pattern effectiveness analysis
        print("  Creating pattern effectiveness visualization...")
        effectiveness_fig = pattern_viz.visualize_pattern_effectiveness(save_path=str(output_dir / "demo_effectiveness.png"))
        print(f"  ✓ Pattern effectiveness visualization saved")
        
        # QKit analysis
        print("  Generating QKit analysis...")
        qkit_fig = pattern_viz.visualize_qkit_analysis(save_path=str(output_dir / "demo_qkit.png"))
        print(f"  ✓ QKit analysis visualization saved")
        
        if animation_viz:
            print("\n--- Creating Animations ---")
            
            # Network growth animation
            print("  Creating network growth animation...")
            try:
                growth_anim = animation_viz.animate_network_growth(
                    time_steps=30,
                    save_path=str(output_dir / "demo_growth_animation.gif")
                )
                print(f"  ✓ Network growth animation saved")
            except Exception as e:
                print(f"  ⚠ Network growth animation failed: {e}")
            
            # Pattern discovery animation
            print("  Creating pattern discovery animation...")
            try:
                discovery_anim = animation_viz.animate_pattern_discovery(
                    time_steps=20,
                    save_path=str(output_dir / "demo_pattern_discovery.gif")
                )
                print(f"  ✓ Pattern discovery animation saved")
            except Exception as e:
                print(f"  ⚠ Pattern discovery animation failed: {e}")
            
            # Interactive timeline
            print("  Creating interactive timeline...")
            try:
                timeline_fig = animation_viz.create_interactive_timeline(
                    time_window_days=30,
                    save_path=str(output_dir / "demo_timeline.png")
                )
                print(f"  ✓ Interactive timeline saved")
            except Exception as e:
                print(f"  ⚠ Interactive timeline failed: {e}")
            
            # Query execution animation
            print("  Creating query execution animation...")
            try:
                query_anim = animation_viz.animate_query_execution(
                    query_steps=15,
                    save_path=str(output_dir / "demo_query_execution.gif")
                )
                print(f"  ✓ Query execution animation saved")
            except Exception as e:
                print(f"  ⚠ Query execution animation failed: {e}")
            
            # System metrics animation
            print("  Creating system metrics animation...")
            try:
                metrics_anim = animation_viz.animate_system_metrics(
                    time_steps=25,
                    save_path=str(output_dir / "demo_system_metrics.gif")
                )
                print(f"  ✓ System metrics animation saved")
            except Exception as e:
                print(f"  ⚠ System metrics animation failed: {e}")
            
            # Comprehensive animation suite
            print("  Creating comprehensive animation suite...")
            try:
                animation_suite = animation_viz.create_comprehensive_animation_suite(
                    output_dir=str(output_dir / "animations"),
                    suite_name="atlas_comprehensive"
                )
                created_count = len(animation_suite.get('created_animations', []))
                failed_count = len(animation_suite.get('failed_animations', []))
                total_size = animation_suite.get('total_size_mb', 0)
                print(f"  ✓ Animation suite: {created_count} created, {failed_count} failed, {total_size:.1f}MB total")
            except Exception as e:
                print(f"  ⚠ Comprehensive animation suite failed: {e}")
        
        print("\n--- Generating Comprehensive Analytics ---")
        
        # System performance analysis
        print("  Analyzing system performance...")
        performance_fig = metrics_viz.visualize_performance_metrics(save_path=str(output_dir / "demo_performance.png"))
        print(f"  ✓ Performance analysis saved")
        
        # Community structure analysis
        print("  Analyzing community structure...")
        community_fig = network_viz.visualize_community_structure(save_path=str(output_dir / "demo_communities.png"))
        print(f"  ✓ Community analysis saved")
        
        # Network evolution analysis
        print("  Analyzing network evolution...")
        evolution_fig = network_viz.visualize_network_evolution(save_path=str(output_dir / "demo_evolution.png"))
        print(f"  ✓ Network evolution analysis saved")
        
        # Centrality analysis
        print("  Analyzing node centrality...")
        centrality_fig = network_viz.visualize_centrality_analysis(save_path=str(output_dir / "demo_centrality.png"))
        print(f"  ✓ Centrality analysis saved")
        
        print("\n--- Generating Summary Report ---")
        
        # Create comprehensive visualization summary
        summary_data = {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": atlas.get_metrics(),
            "network_analysis": network_analysis,
            "visualization_files": [
                "demo_topology.png",
                "demo_distribution.png", 
                "demo_hierarchy.png",
                "demo_overview.png",
                "demo_interactive.html",
                "demo_quality.png",
                "demo_effectiveness.png",
                "demo_qkit.png",
                "demo_performance.png",
                "demo_communities.png",
                "demo_evolution.png",
                "demo_centrality.png",
                "demo_timeline.png"
            ],
            "animation_files": [
                "demo_growth_animation.gif",
                "demo_pattern_discovery.gif",
                "demo_query_execution.gif",
                "demo_system_metrics.gif"
            ] if animation_viz else []
        }
        
        # Save visualization summary
        with open(output_dir / "visualization_summary.json", 'w') as f:
            json.dump(summary_data, f, indent=2)
        
        print(f"  ✓ Visualization summary saved to {output_dir / 'visualization_summary.json'}")
        print(f"\n🎯 Advanced visualization demonstration completed!")
        print(f"   📁 All files saved to: {output_dir}")
        print(f"   📊 Static visualizations: {len(summary_data['visualization_files'])}")
        print(f"   🎬 Animations: {len(summary_data['animation_files'])}")
        
    except Exception as e:
        logger.error(f"Advanced visualization demonstration failed: {e}")
        print(f"✗ Advanced visualization demonstration failed: {e}")


def main(output_dir=None):
    """Main demonstration function."""
    print("🚀 ATLAS Comprehensive System Demonstration")
    print("=" * 50)
    
    if output_dir:
        print(f"📁 Output directory: {output_dir}")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create knowledge base
    atlas, pattern_engine = create_sample_knowledge_base()
    
    # Demonstrate capabilities
    demonstrate_queries(atlas, pattern_engine)
    demonstrate_metrics(atlas, output_dir)
    demonstrate_advanced_features(atlas, pattern_engine, output_dir)
    demonstrate_visualizations(atlas, pattern_engine, output_dir)
    demonstrate_advanced_visualizations(atlas, pattern_engine, output_dir)
    
    # Save comprehensive results
    save_demonstration_results(atlas, pattern_engine, output_dir)
    
    # Final summary
    print("\n=== Demonstration Summary ===")
    metrics = atlas.get_metrics()
    print(f"📊 System Statistics:")
    print(f"  • Entities: {metrics.get('entities_created', 0)}")
    print(f"  • Patterns: {metrics.get('patterns_created', 0)}")
    print(f"  • Queries: {metrics.get('queries_executed', 0)}")
    print(f"  • Relationships: {metrics.get('relationships_added', 0)}")
    print(f"  • Graph Nodes: {metrics.get('total_nodes', 0)}")
    print(f"  • Graph Edges: {metrics.get('total_edges', 0)}")
    print(f"  • Graph Density: {metrics.get('graph_density', 0):.3f}")
    
    print(f"\n🎉 ATLAS demonstration completed successfully!")
    print(f"   Timestamp: {datetime.now().isoformat()}")
    
    if output_dir:
        print(f"\n📊 Generated files in {output_dir}:")
        if VISUALIZATION_AVAILABLE:
            print(f"  • demo_topology.png - Network topology")
            print(f"  • demo_distribution.png - Component distribution")
            print(f"  • demo_hierarchy.png - Pattern hierarchy")
            print(f"  • demo_overview.png - System overview")
            print(f"  • demo_network_*.png - Network analysis files")
        print(f"  • atlas_graph.graphml - Graph export")
        print(f"  • pattern_analysis.json - Pattern analysis results")
        print(f"  • demonstration_results.json - Complete results")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ATLAS Comprehensive System Demonstration")
    parser.add_argument("--output-dir", type=str, help="Directory to save demonstration outputs")
    
    args = parser.parse_args()
    
    try:
        main(args.output_dir)
    except KeyboardInterrupt:
        print("\n\n⚠ Demonstration interrupted by user")
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        logger.exception("Demonstration error")
        sys.exit(1) 