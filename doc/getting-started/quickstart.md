# Quick Start Tutorial

This tutorial will guide you through creating your first ATLAS knowledge management system in just a few minutes.

## Prerequisites

Before starting, ensure you have:
- [ATLAS installed](installation.md) on your system
- Basic Python knowledge
- A text editor or IDE

## Your First ATLAS System

Let's build a simple knowledge base about coffee production - a perfect example to demonstrate ATLAS's capabilities.

### Step 1: Initialize ATLAS

```python
from atlas import ATLASEngine, Entity, Pattern, iQuery
from atlas.core import ATLASConfig

# Create ATLAS configuration
config = ATLASConfig(
    auto_pattern_inference=True,
    enable_dynamic_typing=True,
    max_expansion_depth=5,
    enable_quality_metrics=True
)

# Initialize the ATLAS engine
atlas = ATLASEngine(config)
print("ATLAS engine initialized!")
```

### Step 2: Create Patterns

Patterns are templates that define what kinds of information we expect about certain types of objects.

```python
# Create a pattern for coffee beans
bean_pattern = Pattern(
    pattern_id="coffee_bean",
    qkit=[
        "what_is_the_origin",
        "what_is_the_roast_level", 
        "what_is_the_flavor_profile",
        "who_is_the_supplier"
    ],
    attributes={
        "domain": "coffee_production",
        "type": "agricultural_product",
        "description": "Coffee beans from farm to roaster"
    }
)

# Create a pattern for coffee shops
shop_pattern = Pattern(
    pattern_id="coffee_shop",
    qkit=[
        "where_is_the_location",
        "what_are_the_hours",
        "who_supplies_the_beans",
        "what_is_the_specialty"
    ],
    attributes={
        "domain": "retail",
        "type": "business",
        "description": "Coffee retail establishments"
    }
)

# Create a hierarchical pattern for specialty coffee (child of coffee_bean)
specialty_pattern = Pattern(
    pattern_id="specialty_coffee", 
    qkit=[
        "what_is_the_processing_method",
        "what_is_the_altitude",
        "what_certification_does_it_have"
    ],
    parents=["coffee_bean"],  # Inherits from coffee_bean pattern
    attributes={
        "domain": "coffee_production",
        "type": "premium_product",
        "description": "High-quality coffee with specific characteristics"
    }
)

# Add patterns to ATLAS
atlas.add_pattern(bean_pattern.id, bean_pattern.to_dict())
atlas.add_pattern(shop_pattern.id, shop_pattern.to_dict())
atlas.add_pattern(specialty_pattern.id, specialty_pattern.to_dict())

print(f"Created {len(atlas.patterns)} patterns")
```

### Step 3: Create Entities

Entities are specific instances that conform to patterns.

```python
# Create specific coffee bean entities
ethiopian_beans = Entity(
    entity_id="ethiopian_yirgacheffe",
    attributes={
        "name": "Ethiopian Yirgacheffe",
        "origin": "Ethiopia, Yirgacheffe region",
        "roast_level": "Light",
        "flavor_profile": ["floral", "citrus", "bright acidity"],
        "supplier": "Direct Trade Coffee Co",
        "price_per_pound": 18.50,
        "processing_method": "washed",
        "altitude": "1700-2200m",
        "certification": "organic"
    },
    patterns=["coffee_bean", "specialty_coffee"]  # Conforms to both patterns
)

guatemalan_beans = Entity(
    entity_id="guatemalan_antigua",
    attributes={
        "name": "Guatemalan Antigua",
        "origin": "Guatemala, Antigua region", 
        "roast_level": "Medium",
        "flavor_profile": ["chocolate", "spicy", "smoky"],
        "supplier": "Mountain Coffee Imports",
        "price_per_pound": 16.00
    },
    patterns=["coffee_bean"]
)

# Create coffee shop entities
local_cafe = Entity(
    entity_id="downtown_coffee_house",
    attributes={
        "name": "Downtown Coffee House",
        "location": "123 Main St, Downtown",
        "hours": "6:00 AM - 8:00 PM",
        "specialty": "Single origin pour-overs",
        "bean_suppliers": ["Direct Trade Coffee Co", "Mountain Coffee Imports"],
        "seating_capacity": 45,
        "wifi": True
    },
    patterns=["coffee_shop"]
)

# Add entities to ATLAS
atlas.add_entity(ethiopian_beans.id, ethiopian_beans.to_dict())
atlas.add_entity(guatemalan_beans.id, guatemalan_beans.to_dict())
atlas.add_entity(local_cafe.id, local_cafe.to_dict())

print(f"Created {len(atlas.entities)} entities")
```

### Step 4: Create Relationships

Link entities to show how they relate to each other.

```python
# Create relationships between entities
atlas.add_relationship(
    local_cafe.id, 
    ethiopian_beans.id, 
    "sources_from"
)

atlas.add_relationship(
    local_cafe.id,
    guatemalan_beans.id, 
    "sources_from"
)

# Create pattern hierarchy relationship
atlas.add_relationship(
    bean_pattern.id,
    specialty_pattern.id,
    "parent_of"
)

print("Relationships created!")
```

### Step 5: Create and Execute Queries

Use iQueries to discover information and patterns in your knowledge base.

```python
from atlas.queries import iQuery, QueryPriority

# Create a query to find all coffee beans
bean_query = iQuery(
    query_id="find_coffee_beans",
    query_text="What coffee beans are available?",
    target_patterns=["coffee_bean"],
    priority=QueryPriority.NORMAL,
    context={"search_type": "inventory"}
)

# Create a query to find specialty coffees
specialty_query = iQuery(
    query_id="find_specialty_coffee",
    query_text="What specialty coffee options do we have?",
    target_patterns=["specialty_coffee"],
    priority=QueryPriority.HIGH,
    context={"customer_preference": "premium"}
)

# Add queries to ATLAS
atlas.add_query(bean_query.id, bean_query.to_dict())
atlas.add_query(specialty_query.id, specialty_query.to_dict())

# Execute searches
coffee_results = atlas.query("coffee")
specialty_results = atlas.query("specialty")

print(f"Found {len(coffee_results)} coffee-related items")
print(f"Found {len(specialty_results)} specialty items")

# Display results
for result in coffee_results:
    print(f"- {result['type']}: {result['id']}")
```

### Step 6: Explore Your Knowledge Base

```python
# Get system metrics
metrics = atlas.get_metrics()
print("\nSystem Metrics:")
print(f"- Entities: {metrics.get('entities_created', 0)}")
print(f"- Patterns: {metrics.get('patterns_created', 0)}")
print(f"- Queries: {metrics.get('queries_executed', 0)}")
print(f"- Relationships: {metrics.get('relationships_added', 0)}")
print(f"- Graph Density: {metrics.get('graph_density', 0):.3f}")

# Find relationships for the coffee shop
shop_relationships = atlas.get_relationships(local_cafe.id)
print(f"\nCoffee shop relationships: {len(shop_relationships)}")
for target, rel_type in shop_relationships:
    print(f"  {local_cafe.id} --[{rel_type}]--> {target}")

# Check pattern inheritance
if specialty_pattern.has_pattern("coffee_bean"):
    print("\n✓ Specialty coffee correctly inherits from coffee bean pattern")
```

### Step 7: Add Dynamic Discovery

ATLAS can automatically discover new patterns and generate questions:

```python
# Simulate adding a new coffee with missing information
new_coffee = Entity(
    entity_id="mystery_coffee",
    attributes={
        "name": "Mystery Single Origin",
        "origin": None,  # Missing information
        "roast_level": None,  # Missing information
        "supplier": "Unknown Roaster"
    },
    patterns=["coffee_bean"]
)

atlas.add_entity(new_coffee.id, new_coffee.to_dict())

# Generate RFIs (Requests for Information) for missing data
missing_info_requests = new_coffee.call_rfis()
print(f"\nGenerated {len(missing_info_requests)} information requests:")
for rfi in missing_info_requests:
    print(f"  - {rfi}")
```

## Complete Example Script

Here's the complete script you can run:

```python
from atlas import ATLASEngine, Entity, Pattern, iQuery
from atlas.core import ATLASConfig
from atlas.queries import QueryPriority

def main():
    # Initialize ATLAS
    config = ATLASConfig(auto_pattern_inference=True)
    atlas = ATLASEngine(config)
    
    # Create patterns
    bean_pattern = Pattern("coffee_bean", qkit=["origin", "roast_level"])
    shop_pattern = Pattern("coffee_shop", qkit=["location", "hours"])
    
    atlas.add_pattern(bean_pattern.id, bean_pattern.to_dict())
    atlas.add_pattern(shop_pattern.id, shop_pattern.to_dict())
    
    # Create entities
    beans = Entity("ethiopian_beans", 
                  attributes={"origin": "Ethiopia", "roast": "Light"},
                  patterns=["coffee_bean"])
    
    cafe = Entity("local_cafe",
                 attributes={"location": "Downtown", "hours": "6AM-8PM"},
                 patterns=["coffee_shop"])
    
    atlas.add_entity(beans.id, beans.to_dict())
    atlas.add_entity(cafe.id, cafe.to_dict())
    
    # Create relationship
    atlas.add_relationship(cafe.id, beans.id, "sources_from")
    
    # Query the system
    results = atlas.query("coffee")
    print(f"Found {len(results)} coffee-related items")
    
    # Get metrics
    metrics = atlas.get_metrics()
    print(f"System has {metrics['total_nodes']} nodes and {metrics['total_edges']} edges")

if __name__ == "__main__":
    main()
```

## What You've Learned

In this tutorial, you've learned how to:

1. **Initialize** an ATLAS engine with configuration
2. **Create patterns** that define expected information structure
3. **Create entities** that represent real-world objects
4. **Establish relationships** between different components
5. **Query** your knowledge base to find relevant information
6. **Generate RFIs** for missing information
7. **Use metrics** to understand your knowledge base structure

## Next Steps

Now that you understand the basics, explore these advanced topics:

- [Basic Concepts](concepts.md) - Deeper understanding of ATLAS principles
- [Entity Management](../user-guide/entities.md) - Advanced entity operations
- [Pattern Languages](../user-guide/patterns.md) - Complex pattern hierarchies
- [Query System](../user-guide/queries.md) - Advanced query techniques
- [Visualization](../user-guide/visualization.md) - Visualizing your knowledge graphs

## Troubleshooting

### Common Issues

**Q: My patterns don't seem to inherit properly**  
A: Ensure parent patterns are added to ATLAS before child patterns that reference them.

**Q: Queries return no results**  
A: Check that your entities have the patterns you're querying for, and that attribute values contain searchable text.

**Q: Performance is slow with many entities**  
A: Consider reducing `max_expansion_depth` in your config or disable `enable_quality_metrics` for better performance.

### Getting Help

- Check the [FAQ](../reference/faq.md) for common questions
- Browse [examples](../examples/index.md) for more use cases  
- Visit [community support](../community/support.md) for help

---

*Ready for more? Continue with [Basic Concepts](concepts.md) to deepen your understanding.* 