# Working with Entities

Entities are the fundamental building blocks of any ATLAS knowledge management system. This guide covers everything you need to know about creating, managing, and working with entities effectively.

## Understanding Entities

An entity in ATLAS represents any identifiable object, concept, or phenomenon that you want to track and relate to other information. Entities are flexible containers that can represent:

- **Concrete objects**: People, places, documents, products
- **Abstract concepts**: Ideas, theories, methodologies, patterns
- **Events**: Meetings, publications, discoveries, incidents
- **Relationships**: Collaborations, dependencies, influences

### Entity Structure

Every entity consists of:

1. **Unique Identifier**: A string that uniquely identifies the entity
2. **Attributes**: Key-value pairs containing information about the entity
3. **Patterns**: List of pattern IDs that define the entity's type and expected behavior
4. **Metadata**: System-managed information about creation, updates, and provenance

## Creating Entities

### Basic Entity Creation

```python
from atlas import Entity

# Create a simple entity
person = Entity(
    entity_id="john_doe_researcher",
    attributes={
        "name": "John Doe",
        "email": "john.doe@university.edu",
        "profession": "researcher",
        "institution": "Example University"
    },
    patterns=["person", "researcher"]
)

# Add to ATLAS system
atlas.add_entity(person.id, person.to_dict())
```

### Entity ID Best Practices

Choose meaningful, consistent entity IDs:

```python
# Good: Descriptive and consistent
"marie_curie_scientist"
"coffee_bean_ethiopian_yirgacheffe"
"paper_2023_atlas_specification"

# Avoid: Generic or inconsistent
"entity_1"
"user123" 
"doc"
```

### Working with Attributes

Attributes are flexible key-value pairs that store information about your entity:

```python
# Rich attribute example
research_paper = Entity(
    entity_id="smith_2023_knowledge_graphs",
    attributes={
        # Basic bibliographic information
        "title": "Knowledge Graphs in Modern AI",
        "authors": ["Jane Smith", "Bob Johnson"],
        "publication_year": 2023,
        "journal": "AI Research Quarterly",
        
        # Structured data
        "keywords": ["knowledge graphs", "artificial intelligence", "semantic web"],
        "page_range": "45-67",
        "doi": "10.1234/airq.2023.0045",
        
        # Quality and provenance
        "peer_reviewed": True,
        "citation_count": 12,
        "added_by": "librarian_system",
        "confidence_score": 0.95,
        
        # Relationships
        "related_papers": ["jones_2022_semantic_networks", "lee_2023_graph_databases"],
        "methodology": "systematic_review"
    }
)
```

### Dynamic Attribute Addition

You can add attributes to entities after creation:

```python
# Add new attribute
person.add_attribute("phone_number", "+1-555-0123")

# Add with validation
if person.add_attribute("salary", 75000, overwrite=False):
    print("Salary added successfully")
else:
    print("Salary already exists")

# Bulk attribute update
new_attributes = {
    "research_areas": ["machine learning", "knowledge representation"],
    "h_index": 15,
    "recent_publications": 8
}

for key, value in new_attributes.items():
    person.add_attribute(key, value)
```

## Managing Entity Patterns

Patterns define what type of entity you're working with and what information is expected:

### Adding Patterns

```python
# Add a single pattern
person.add_pattern("department_head")

# Check if pattern was added
if person.has_pattern("department_head"):
    print("Person is now recognized as a department head")

# Add multiple patterns through entity creation
complex_entity = Entity(
    entity_id="startup_company_ai_tech",
    attributes={"name": "AI Innovations Inc.", "founded": 2020},
    patterns=["company", "startup", "technology_company", "ai_company"]
)
```

### Pattern Inheritance

When you assign a pattern to an entity, it automatically inherits all parent patterns:

```python
# If "phd_student" pattern has parent "student" and "researcher"
entity.add_pattern("phd_student")

# Entity now automatically has these patterns:
# - "phd_student" (explicitly added)
# - "student" (inherited from parent)
# - "researcher" (inherited from parent)
# - "person" (inherited if "student" has "person" as parent)
```

## Entity Relationships

### Creating Relationships

```python
# Direct relationship creation
atlas.add_relationship(
    source_id="john_doe_researcher",
    target_id="ai_innovations_inc", 
    relationship_type="works_for"
)

atlas.add_relationship(
    source_id="smith_2023_knowledge_graphs",
    target_id="john_doe_researcher",
    relationship_type="authored_by"
)

# Multiple relationships
collaborators = ["jane_smith_researcher", "bob_johnson_researcher"] 
for collaborator in collaborators:
    atlas.add_relationship(
        source_id="john_doe_researcher",
        target_id=collaborator,
        relationship_type="collaborates_with"
    )
```

### Relationship Types

Use meaningful relationship names that express the connection:

```python
# Academic relationships
"supervised_by", "mentors", "collaborates_with", "cites", "builds_on"

# Business relationships  
"works_for", "partners_with", "competes_with", "supplies_to", "invests_in"

# Content relationships
"contains", "references", "extends", "implements", "critiques"

# Temporal relationships
"precedes", "follows", "occurs_during", "triggers", "results_from"
```

## Advanced Entity Operations

### Entity Queries and Discovery

```python
# Find entities by attribute
def find_entities_by_attribute(atlas, attr_key, attr_value):
    matching_entities = []
    for entity_id, entity_data in atlas.entities.items():
        if entity_data.get('attributes', {}).get(attr_key) == attr_value:
            matching_entities.append(entity_id)
    return matching_entities

# Find all researchers
researchers = find_entities_by_attribute(atlas, "profession", "researcher")

# Find entities with specific patterns
phd_students = [entity_id for entity_id, data in atlas.entities.items() 
                if "phd_student" in data.get('patterns', [])]
```

### Entity Validation and Quality Control

```python
# Validate entity completeness
def validate_entity_completeness(entity, required_attributes):
    missing_attrs = []
    for attr in required_attributes:
        if not entity.has_attribute(attr):
            missing_attrs.append(attr)
    return missing_attrs

# For a researcher entity
required_attrs = ["name", "email", "institution", "research_areas"]
missing = validate_entity_completeness(person, required_attrs)

if missing:
    print(f"Missing required attributes: {missing}")
    # Generate RFIs for missing information
    rfi_requests = person.call_rfis()
    print(f"Generated {len(rfi_requests)} information requests")
```

### Entity Anomaly Detection

```python
# Mark entity as anomaly for specific query
person.mark_anomaly(
    iquery_id="find_contact_information", 
    reason="Email format appears invalid"
)

# Mark as exception (valid but special case)
person.mark_exception(
    iquery_id="find_publication_metrics",
    reason="Researcher is emeritus, no recent publications expected"
)

# Check anomalies and exceptions
anomalies = person.get_anomalies()
exceptions = person.get_exceptions()

print(f"Entity has {len(anomalies)} anomalies and {len(exceptions)} exceptions")
```

## Entity Serialization and Persistence

### Converting to/from Dictionaries

```python
# Convert entity to dictionary for storage
entity_dict = person.to_dict()

# Save to JSON file
import json
with open('person_entity.json', 'w') as f:
    json.dump(entity_dict, f, indent=2)

# Load from dictionary
with open('person_entity.json', 'r') as f:
    loaded_dict = json.load(f)

restored_person = Entity.from_dict(loaded_dict)
```

### Batch Entity Operations

```python
# Create multiple entities from data
def create_entities_from_csv(csv_file, pattern_list):
    import csv
    entities = []
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            entity_id = f"{row['name'].lower().replace(' ', '_')}_person"
            entity = Entity(
                entity_id=entity_id,
                attributes=dict(row),
                patterns=pattern_list
            )
            entities.append(entity)
    
    return entities

# Load and add to ATLAS
people = create_entities_from_csv('researchers.csv', ['person', 'researcher'])
for person in people:
    atlas.add_entity(person.id, person.to_dict())
```

## Entity Best Practices

### Naming Conventions

1. **Use descriptive IDs**: `marie_curie_physicist` not `person_1`
2. **Be consistent**: Use same format across similar entities
3. **Include type hints**: `paper_2023_atlas_spec` not just `atlas_spec`
4. **Avoid spaces**: Use underscores or hyphens

### Attribute Design

1. **Use consistent keys**: `publication_year` not sometimes `pub_year` or `year_published`
2. **Store structured data**: Use lists/dicts for complex information
3. **Include metadata**: Add quality scores, sources, timestamps
4. **Plan for evolution**: Design attributes to accommodate future needs

### Pattern Assignment

1. **Start general, get specific**: Assign broad patterns first, then specialized ones
2. **Use hierarchies**: Take advantage of pattern inheritance
3. **Be consistent**: Same types of entities should have same base patterns
4. **Document patterns**: Maintain clear documentation of what each pattern means

### Relationship Design

1. **Use bidirectional thinking**: Consider relationships from both directions
2. **Be specific**: `mentors` is better than generic `related_to`
3. **Maintain consistency**: Use same relationship names for similar connections
4. **Consider temporal aspects**: Some relationships change over time

## Common Patterns

### Academic Entities

```python
# Researcher entity
researcher = Entity(
    entity_id="researcher_id",
    attributes={
        "name": "Full Name",
        "institution": "University Name", 
        "department": "Department Name",
        "position": "Associate Professor",
        "research_areas": ["area1", "area2"],
        "h_index": 25,
        "total_citations": 1500
    },
    patterns=["person", "researcher", "academic"]
)

# Research paper entity
paper = Entity(
    entity_id="paper_id",
    attributes={
        "title": "Paper Title",
        "authors": ["Author 1", "Author 2"],
        "journal": "Journal Name",
        "year": 2023,
        "doi": "10.xxxx/xxxxx",
        "abstract": "Paper abstract...",
        "keywords": ["keyword1", "keyword2"]
    },
    patterns=["document", "academic_paper", "peer_reviewed"]
)
```

### Business Entities

```python
# Company entity
company = Entity(
    entity_id="company_id",
    attributes={
        "name": "Company Name",
        "industry": "Technology",
        "founded": 2010,
        "headquarters": "City, Country",
        "employee_count": 500,
        "revenue": 50000000,
        "stock_symbol": "COMP"
    },
    patterns=["organization", "company", "technology_company"]
)

# Product entity
product = Entity(
    entity_id="product_id",
    attributes={
        "name": "Product Name",
        "category": "Software",
        "price": 99.99,
        "launch_date": "2023-01-15",
        "features": ["feature1", "feature2"],
        "target_market": "enterprise"
    },
    patterns=["product", "software_product", "enterprise_software"]
)
```

## Troubleshooting

### Common Issues

**Problem**: Entity creation fails  
**Solution**: Check that entity_id is unique and attributes are serializable

**Problem**: Patterns not inherited properly  
**Solution**: Ensure parent patterns exist in ATLAS before adding child patterns

**Problem**: Attributes not updating  
**Solution**: Use `overwrite=True` parameter in `add_attribute()` method

**Problem**: Poor query performance  
**Solution**: Review attribute structure and consider indexing frequently queried fields

### Performance Considerations

- **Attribute size**: Keep individual attribute values reasonable
- **Relationship density**: High relationship counts can slow queries
- **Pattern complexity**: Deeply nested pattern hierarchies affect performance
- **Batch operations**: Use bulk operations for creating many entities

---

*Next: Learn about [Patterns](patterns.md) to understand how to organize and classify your entities effectively.* 