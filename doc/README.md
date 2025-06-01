# ATLAS: Adaptive Thinking and Learning Architecture System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Overview

ATLAS (Adaptive Thinking and Learning Architecture System) is a dynamic and comprehensive knowledge management framework that addresses the complexities of modern information supply chains. Evolving since the late 1990s from the original Atlas of Risk, ATLAS integrates pattern language approaches with question-oriented procedures to manage and interpret meaning and context across diverse knowledge domains.

## Key Features

- **Dynamic Pattern Management**: Flexible pattern assignment and inheritance system
- **Question-Oriented Knowledge Discovery**: iQuery system for structured information requests
- **Modular Entity Architecture**: Composable entities with flexible attributes
- **Cross-Domain Interoperability**: Data exchange without requiring shared standards
- **Information Exchange Environments**: Support for both standard and verified information exchange
- **Cognitive Security Framework**: Built-in approaches for managing information quality and provenance

## Architecture

ATLAS is built on five core components:

1. **Entities**: Fundamental objects with attributes and pattern assignments
2. **Patterns**: Abstract templates that entities can instantiate or exemplify
3. **iQueries**: Itemized queries that manage information requests and discovery
4. **Attributes**: Flexible metadata containers with reference IDs
5. **Prompt Interfaces**: Translation layers for system interoperability

## Quick Start

```python
from atlas.core.engine import ATLASEngine, ATLASConfig
from atlas.entities.entity import Entity
from atlas.patterns.pattern import Pattern
from atlas.queries.iquery import iQuery

# Initialize ATLAS engine
config = ATLASConfig(auto_pattern_inference=True, enable_quality_metrics=True)
atlas = ATLASEngine(config)

# Create a pattern
pattern = Pattern(
    pattern_id="cognitive_bias",
    qkit=["what_triggers_bias", "how_to_mitigate", "examples_in_practice"],
    attributes={"domain": "cognitive_science", "severity": "high"}
)

# Create an entity
entity = Entity(
    entity_id="confirmation_bias",
    attributes={
        "definition": "Tendency to search for information that confirms preconceptions",
        "impact": "decision_making"
    },
    patterns=[pattern.id]
)

# Add to ATLAS
atlas.add_pattern(pattern.id, pattern.to_dict())
atlas.add_entity(entity.id, entity.to_dict())

# Query the system
results = atlas.query("cognitive bias")
print(f"Found {len(results)} results")

# Get system metrics
metrics = atlas.get_metrics()
print(f"System contains {metrics['entities_created']} entities")
```

## Installation

### Core Installation
```bash
# Clone the repository
git clone https://github.com/atlas-team/atlas.git
cd atlas

# Install core dependencies
pip install -e .

# Run basic test
python3 examples/basic_test.py
```

### Full Installation (with visualization)
```bash
# Install with visualization capabilities
pip install -e ".[viz]"

# Run comprehensive demo
python3 examples/comprehensive_demo.py

# Run test suite
pytest tests/ -v
```

### Development Installation
```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests with coverage
pytest tests/ --cov=atlas

# Format code
black src/ tests/ examples/
```

## Project Structure

```
ATLAS/
├── src/atlas/           # Core ATLAS implementation
│   ├── core/           # Core engine and orchestration
│   ├── entities/       # Entity management system
│   ├── patterns/       # Pattern language implementation
│   ├── queries/        # iQuery system
│   ├── interfaces/     # Prompt interfaces and adapters
│   ├── utils/          # Utilities and helpers
│   └── __init__.py
├── tests/              # Comprehensive test suite
├── doc/                # Documentation and specifications
├── examples/           # Usage examples and tutorials
├── requirements.txt    # Python dependencies
└── README.md
```

## Documentation

- [Technical Specification](doc/specification.md)
- [Architecture Guide](doc/architecture.md)
- [API Reference](doc/api.md)
- [Pattern Language Guide](doc/patterns.md)
- [Examples and Tutorials](examples/)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use ATLAS in your research, please cite:

```bibtex
@misc{atlas2023,
  title={ATLAS: A Question Oriented Approach to the Use of Pattern Languages in Knowledge Management},
  author={Cordes, R.J. and David, Scott and Friedman, Daniel and Mikhailova, Alexandra and Penland, Andrew and Young, Sam and Zacharias, Colten},
  year={2023},
  doi={10.5281/zenodo.10362561}
}
```

## Acknowledgments

ATLAS builds upon decades of research in pattern languages, knowledge management, and cognitive security. We acknowledge the foundational work of Christopher Alexander on pattern languages and the contributions of the cognitive security community. 
