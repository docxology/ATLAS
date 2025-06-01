# API Reference

Complete reference documentation for all ATLAS classes, methods, and functions.

## Core API

### ATLASEngine
The main orchestration class for the ATLAS system.

```python
from atlas.core import ATLASEngine, ATLASConfig

# Initialize with configuration
config = ATLASConfig(auto_pattern_inference=True)
atlas = ATLASEngine(config)
```

**Key Methods:**
- `add_entity()` - Add entities to the system
- `add_pattern()` - Create and manage patterns  
- `add_query()` - Register iQueries
- `query()` - Execute queries and searches
- `get_metrics()` - Retrieve system statistics
- `export_graph()` - Export knowledge graph

### Entity
Fundamental objects within the ATLAS system.

```python
from atlas.entities import Entity

entity = Entity(
    entity_id="example_entity",
    attributes={"name": "Example", "type": "demo"},
    patterns=["basic_pattern"]
)
```

**Key Methods:**
- `add_attribute()` - Add or update attributes
- `add_pattern()` - Assign patterns to entity
- `mark_anomaly()` - Flag as anomalous to query
- `mark_exception()` - Flag as exception to query
- `call_rfis()` - Generate information requests

### Pattern
Abstract templates that entities can instantiate.

```python
from atlas.patterns import Pattern

pattern = Pattern(
    pattern_id="research_pattern",
    qkit=["what_is_methodology", "who_are_authors"],
    parents=["academic_pattern"]
)
```

**Key Methods:**
- `add_qkit_item()` - Add questions to pattern
- `add_parent()` - Define pattern inheritance
- `calculate_effectiveness_score()` - Assess pattern utility

### iQuery
Structured queries for information discovery.

```python
from atlas.queries import iQuery, QueryPriority

query = iQuery(
    query_id="find_researchers",
    query_text="Who are the researchers in this domain?",
    target_patterns=["researcher_pattern"],
    priority=QueryPriority.HIGH
)
```

**Key Methods:**
- `start_execution()` - Begin query processing
- `add_result()` - Store query results
- `calculate_quality_score()` - Assess result quality

### Attribute
Specialized entities for metadata management.

```python
from atlas.entities import Attribute

attr = Attribute(
    attribute_id="publication_date",
    ref_id="pubdate_001",
    value="2023-10-15",
    data_type="date"
)
```

**Key Methods:**
- `set_value()` - Update attribute value
- `add_validation_rule()` - Define validation constraints
- `link_attribute()` - Connect to other attributes

## Interface API

### PromptInterface
Base class for data transformation interfaces.

```python
from atlas.interfaces import PromptInterface

class CustomInterface(PromptInterface):
    def transform(self, data, context=None):
        # Custom transformation logic
        return transformed_data
```

### SimpleTransformInterface
Function-based transformation interface.

```python
from atlas.interfaces import SimpleTransformInterface

interface = SimpleTransformInterface(
    transform_func=lambda x: x.upper(),
    name="Uppercase Transform"
)
```

### HTTPPromptInterface
HTTP-based external service interface.

```python
from atlas.interfaces import HTTPPromptInterface

api_interface = HTTPPromptInterface(
    endpoint_url="https://api.example.com/data",
    method="POST",
    headers={"Authorization": "Bearer token"}
)
```

## Pattern API

### PatternEngine
Advanced pattern analysis and management.

```python
from atlas.patterns import PatternEngine

engine = PatternEngine()
engine.add_pattern(pattern)
similarity = engine.calculate_pattern_similarity("pattern1", "pattern2")
```

**Key Methods:**
- `calculate_pattern_similarity()` - Compare patterns
- `find_similar_patterns()` - Discover related patterns
- `analyze_pattern_usage()` - Generate usage statistics
- `optimize_pattern_hierarchy()` - Improve pattern structure

## Utility API

### Helpers
Utility functions for common operations.

```python
from atlas.utils import helpers

# Generate unique IDs
entity_id = helpers.generate_id("entity", length=8)

# Timestamp utilities
timestamp = helpers.timestamp_now()

# Data manipulation
merged = helpers.deep_merge(dict1, dict2)
flattened = helpers.flatten_dict(nested_dict)
```

## Visualization API

### GraphVisualizer
Network and graph visualization tools.

```python
from atlas.visualization import GraphVisualizer

viz = GraphVisualizer(atlas_engine)
fig = viz.visualize_network_topology(save_path="network.png")
```

### PatternVisualizer
Pattern hierarchy and relationship visualization.

```python
from atlas.visualization import PatternVisualizer

pattern_viz = PatternVisualizer(atlas_engine, pattern_engine)
fig = pattern_viz.visualize_pattern_hierarchy()
```

### MetricsVisualizer
System metrics and performance visualization.

```python
from atlas.visualization import MetricsVisualizer

metrics_viz = MetricsVisualizer(atlas_engine)
fig = metrics_viz.visualize_system_overview()
```

### NetworkVisualizer
Network analysis and community detection visualization.

```python
from atlas.visualization import NetworkVisualizer

net_viz = NetworkVisualizer(atlas_engine)
analysis = net_viz.analyze_network_structure()
```

## Configuration API

### ATLASConfig
System configuration dataclass.

```python
from atlas.core import ATLASConfig

config = ATLASConfig(
    auto_pattern_inference=True,
    enable_dynamic_typing=True,
    max_expansion_depth=10,
    enable_quality_metrics=True,
    log_level="INFO"
)
```

## Quick Reference

### Import Statements

```python
# Core components
from atlas import ATLASEngine, Entity, Pattern, iQuery
from atlas.core import ATLASConfig

# Entities and attributes
from atlas.entities import Entity, Attribute

# Patterns
from atlas.patterns import Pattern, PatternEngine

# Queries
from atlas.queries import iQuery, QueryPriority, QueryStatus

# Interfaces
from atlas.interfaces import (
    PromptInterface,
    SimpleTransformInterface, 
    HTTPPromptInterface
)

# Visualization
from atlas.visualization import (
    GraphVisualizer,
    PatternVisualizer,
    MetricsVisualizer,
    NetworkVisualizer
)

# Utilities
from atlas.utils import helpers
```

### Common Patterns

```python
# Basic ATLAS setup
config = ATLASConfig()
atlas = ATLASEngine(config)

# Entity creation and addition
entity = Entity("entity_id", attributes={"key": "value"})
atlas.add_entity(entity.id, entity.to_dict())

# Pattern creation and addition
pattern = Pattern("pattern_id", qkit=["question1", "question2"])
atlas.add_pattern(pattern.id, pattern.to_dict())

# Query creation and execution
query = iQuery("query_id", query_text="Find entities")
atlas.add_query(query.id, query.to_dict())
results = atlas.query("search_term")

# Visualization
viz = GraphVisualizer(atlas)
fig = viz.visualize_network_topology()
```

---

*For detailed information about any component, refer to the specific API documentation sections.* 