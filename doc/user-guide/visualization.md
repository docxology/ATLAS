# Visualization Guide

Complete guide to visualizing ATLAS knowledge graphs, patterns, and system metrics.

## Overview

ATLAS provides comprehensive visualization capabilities through the Visualization API, enabling you to explore your knowledge graphs, understand pattern relationships, and monitor system performance.

## Graph Visualization

### Basic Network Visualization

```python
from atlas.visualization import GraphVisualizer

# Initialize visualizer
viz = GraphVisualizer(atlas_engine)

# Create basic network visualization
fig = viz.visualize_network_topology(
    layout='spring',
    node_size_by='degree',
    color_by='pattern',
    save_path='network.png'
)
```

### Advanced Network Options

```python
# Customize visualization
fig = viz.visualize_network_topology(
    layout='hierarchical',
    node_size_by='centrality',
    color_by='community',
    edge_weight_threshold=0.5,
    highlight_entities=['entity1', 'entity2'],
    save_path='advanced_network.png'
)
```

### Interactive Visualizations

```python
# Create interactive plotly visualization
fig = viz.create_interactive_network(
    height=600,
    width=800,
    physics_enabled=True
)
fig.show()
```

## Pattern Visualization

### Pattern Hierarchy

```python
from atlas.visualization import PatternVisualizer

pattern_viz = PatternVisualizer(atlas_engine, pattern_engine)

# Visualize pattern inheritance hierarchy
fig = pattern_viz.visualize_pattern_hierarchy(
    layout='tree',
    show_effectiveness_scores=True,
    highlight_paths=['research_pattern']
)
```

### Pattern Usage Analysis

```python
# Analyze pattern usage statistics
usage_fig = pattern_viz.visualize_pattern_usage(
    metric='entity_count',
    top_n=10,
    chart_type='bar'
)
```

### Pattern Similarity Networks

```python
# Show pattern relationships based on similarity
similarity_fig = pattern_viz.visualize_pattern_similarity(
    similarity_threshold=0.7,
    layout='force_directed',
    cluster_similar=True
)
```

## System Metrics Visualization

### Performance Dashboards

```python
from atlas.visualization import MetricsVisualizer

metrics_viz = MetricsVisualizer(atlas_engine)

# Comprehensive system overview
dashboard = metrics_viz.visualize_system_overview(
    include_performance=True,
    include_usage=True,
    include_quality=True
)
```

### Query Performance Analysis

```python
# Analyze query execution metrics
perf_fig = metrics_viz.visualize_query_performance(
    time_range='24h',
    group_by='pattern',
    metric='execution_time'
)
```

### Quality Metrics

```python
# Visualize data quality trends
quality_fig = metrics_viz.visualize_quality_metrics(
    metric='completeness',
    aggregate_by='pattern',
    time_series=True
)
```

## Network Analysis

### Community Detection

```python
from atlas.visualization import NetworkVisualizer

net_viz = NetworkVisualizer(atlas_engine)

# Detect and visualize communities
communities = net_viz.analyze_network_structure(
    algorithm='louvain',
    visualize=True
)
```

### Centrality Analysis

```python
# Identify important nodes
centrality_fig = net_viz.visualize_centrality_measures(
    measures=['betweenness', 'closeness', 'degree'],
    top_n=20
)
```

### Path Analysis

```python
# Visualize shortest paths
path_fig = net_viz.visualize_paths(
    source='entity1',
    target='entity2',
    max_paths=5,
    highlight_critical_nodes=True
)
```

## Custom Visualizations

### Creating Custom Charts

```python
import matplotlib.pyplot as plt
from atlas.utils import get_entity_data

# Custom visualization function
def create_custom_chart(atlas_engine):
    data = get_entity_data(atlas_engine)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    # Custom plotting logic
    ax.scatter(data['x'], data['y'], c=data['category'])
    ax.set_title('Custom Entity Analysis')
    
    return fig

# Use custom visualization
custom_fig = create_custom_chart(atlas_engine)
```

### Integration with External Tools

```python
# Export data for external visualization tools
def export_for_gephi(atlas_engine, output_path):
    """Export graph data in Gephi-compatible format"""
    graph_data = atlas_engine.export_graph(format='gexf')
    with open(output_path, 'w') as f:
        f.write(graph_data)

# Export for analysis in Gephi
export_for_gephi(atlas_engine, 'atlas_graph.gexf')
```

## Visualization Configuration

### Styling and Themes

```python
# Configure visualization theme
viz_config = {
    'theme': 'dark',
    'color_palette': 'viridis',
    'font_size': 12,
    'node_size_range': (10, 100),
    'edge_width_range': (0.5, 5.0)
}

viz = GraphVisualizer(atlas_engine, config=viz_config)
```

### Output Formats

```python
# Save in different formats
viz.visualize_network_topology(
    save_path='network.png',  # PNG format
    dpi=300,                  # High resolution
    transparent=True          # Transparent background
)

# Vector formats for publications
viz.visualize_network_topology(
    save_path='network.svg',  # SVG format
    bbox_inches='tight'       # Tight bounding box
)
```

## Performance Considerations

### Large Graph Visualization

```python
# Optimize for large graphs
large_viz = GraphVisualizer(atlas_engine, optimize_for_size=True)

# Use sampling for very large networks
fig = large_viz.visualize_network_topology(
    sample_nodes=1000,        # Sample 1000 nodes
    preserve_structure=True,  # Maintain graph structure
    layout='sfdp'            # Scalable force-directed layout
)
```

### Memory Management

```python
# Clear visualization cache
viz.clear_cache()

# Use generators for large datasets
for batch in viz.batch_visualize(batch_size=100):
    batch.save(f'batch_{batch.id}.png')
```

## Common Use Cases

### Research Analysis

```python
# Visualize research collaboration network
def visualize_research_network(atlas_engine):
    viz = GraphVisualizer(atlas_engine)
    
    # Filter for research entities
    research_filter = {'patterns': ['researcher_pattern', 'publication_pattern']}
    
    fig = viz.visualize_network_topology(
        entity_filter=research_filter,
        layout='force_directed',
        color_by='institution',
        size_by='publication_count',
        title='Research Collaboration Network'
    )
    return fig
```

### Knowledge Domain Mapping

```python
# Map knowledge domains and relationships
def create_domain_map(atlas_engine):
    pattern_viz = PatternVisualizer(atlas_engine)
    
    fig = pattern_viz.visualize_pattern_hierarchy(
        focus_domain='knowledge_domain',
        show_entity_counts=True,
        layout='radial',
        title='Knowledge Domain Structure'
    )
    return fig
```

## Troubleshooting

### Common Issues

1. **Memory errors with large graphs**
   - Use sampling: `sample_nodes=1000`
   - Reduce detail: `simplify_graph=True`
   - Batch processing: `batch_visualize()`

2. **Slow rendering**
   - Choose efficient layouts: `layout='sfdp'`
   - Reduce node/edge counts: apply filters
   - Use static instead of interactive plots

3. **Export issues**
   - Check file permissions
   - Verify output directory exists
   - Use supported formats: PNG, SVG, PDF

### Performance Tips

- Use `layout='spring'` for small graphs (< 100 nodes)
- Use `layout='sfdp'` for large graphs (> 1000 nodes)  
- Enable caching: `enable_cache=True`
- Pre-filter data before visualization

## Next Steps

- Learn about [System Metrics](../api/index.md#visualization-api) for advanced analysis
- Explore [Pattern Analysis](patterns.md) for pattern-specific visualizations
- Check the [API Reference](../api/index.md#visualization-api) for detailed method documentation

---

*For technical details about visualization classes and methods, see the [API Reference](../api/index.md#visualization-api).* 