# ATLAS Examples

This directory contains practical examples demonstrating ATLAS capabilities, organized into themed subdirectories for easy navigation.

## Directory Structure

```
examples/
├── README.md                       # This file
├── basic/                          # Basic functionality examples
│   └── basic_test.py               # Core ATLAS functionality test
├── advanced/                       # Advanced use cases and demos
│   └── comprehensive_demo.py       # Full-featured demonstration
├── Obsidian/                       # Obsidian integration examples
│   └── obsidian_demo.py           # Bidirectional Obsidian conversion
└── tutorials/                      # Tutorial examples (coming soon)
```

## Available Examples

### 1. Basic Examples (`basic/`)

#### Basic Test (`basic/basic_test.py`)

**Purpose**: Demonstrates core ATLAS functionality and serves as a comprehensive system test.

**Features Demonstrated**:
- ATLAS Engine initialization and configuration
- Entity creation and management
- Pattern creation and hierarchy
- iQuery functionality and execution
- Attribute management with validation
- Prompt interfaces and data transformation
- Serialization and persistence
- System metrics and reporting

**Usage**:
```bash
# Run basic test with default output
python3 examples/basic/basic_test.py

# Run with custom output directory
python3 examples/basic/basic_test.py --output-dir my_test_output/

# Run specific test components
python3 examples/basic/basic_test.py --test basic
python3 examples/basic/basic_test.py --test pattern_engine
python3 examples/basic/basic_test.py --test interfaces
```

**Expected Output**:
- Console output showing test progress and results
- JSON files with test results and system metrics
- Basic visualizations (if visualization dependencies available)

### 2. Advanced Examples (`advanced/`)

#### Comprehensive Demo (`advanced/comprehensive_demo.py`)

**Purpose**: Full-featured demonstration of ATLAS as a knowledge management system.

**Features Demonstrated**:
- Complex knowledge base construction
- Pattern inheritance and relationships
- Advanced query processing
- Visualization and analysis
- Network analysis and community detection
- Animation and interactive visualizations
- Quality assessment and metrics
- Graph export and persistence

**Usage**:
```bash
# Run comprehensive demo with default output
python3 examples/advanced/comprehensive_demo.py

# Run with custom output directory
python3 examples/advanced/comprehensive_demo.py --output-dir demo_results/
```

**Expected Output**:
- Extensive visualization suite (PNG, HTML, GIF files)
- Graph exports (GraphML format)
- Analysis reports (JSON format)
- Demonstration summary and metrics

### 3. Obsidian Integration (`Obsidian/`)

#### Obsidian Demo (`Obsidian/obsidian_demo.py`)

**Purpose**: Demonstrates bidirectional conversion between Obsidian vaults and ATLAS knowledge bases.

**Features Demonstrated**:
- Obsidian vault creation and population
- Markdown-to-ATLAS entity conversion
- ATLAS-to-Obsidian export
- Wikilink and tag handling
- Frontmatter metadata processing
- Template-based content generation

**Usage**:
```bash
# Run Obsidian integration demo
python3 examples/Obsidian/obsidian_demo.py

# Run with custom output directory
python3 examples/Obsidian/obsidian_demo.py --output-dir obsidian_results/
```

## Quick Start

To run all example categories:

```bash
# Run basic functionality test
python3 examples/basic/basic_test.py --output-dir test_output/

# Run comprehensive demonstration
python3 examples/advanced/comprehensive_demo.py --output-dir demo_output/

# Run Obsidian integration demo
python3 examples/Obsidian/obsidian_demo.py --output-dir obsidian_output/
```

## Output Directory Structure

When you run examples with `--output-dir`, the following structure is created:

```
output_directory/
├── reports/
│   ├── system_report.json          # System analysis
│   ├── test_results.json           # Test outcomes
│   └── summary.txt                 # Human-readable summary
├── logs/
│   └── *.log                       # Execution logs
├── visualizations/
│   ├── *.png                       # Static charts
│   ├── *.html                      # Interactive visualizations
│   └── animations/
│       └── *.gif                   # Animated visualizations
└── data/
    ├── *.graphml                   # Graph exports
    ├── *.json                      # Data exports
    └── *.yaml                      # Configuration exports
```

## Dependencies

### Core Dependencies (Required)
- Python 3.8+
- networkx
- numpy
- python-dateutil

### Optional Dependencies (For Full Functionality)
- matplotlib (static visualizations)
- plotly (interactive visualizations)
- seaborn (statistical plots)
- pandas (data analysis)

### Installation

For complete installation instructions, see the [Installation Guide](../doc/INSTALL.md) or [Installation Reference](../doc/installation-reference.md).

**Quick Setup for Examples**:
```bash
# Recommended for all examples
pip install -e ".[viz]"
```

## Example Use Cases

### Research and Academia
- **basic_test.py**: Verify ATLAS installation and functionality
- **comprehensive_demo.py**: Demonstrate capabilities to colleagues

### Development and Testing
- **basic_test.py**: Automated testing and validation
- **comprehensive_demo.py**: Performance benchmarking

### Learning and Training
- Follow the examples in order: basic_test.py → comprehensive_demo.py
- Examine output files to understand ATLAS data structures
- Modify examples to experiment with different configurations

## Troubleshooting

### Common Issues

- **Visualization Issues**: See [Installation Reference](../doc/installation-reference.md#troubleshooting)
- **Import Errors**: Ensure `pip install -e .` was run from project root
- **Dependencies**: Use `pip install -e ".[viz]"` for visualization support

For detailed troubleshooting, see the [FAQ](../doc/reference/faq.md).

### Performance Issues
For better performance:
- Use smaller datasets initially
- Enable only necessary visualizations
- Consider using `--output-dir` to organize outputs

## Next Steps

After running the examples:

1. **Explore the Documentation**: Check `doc/` for detailed guides
2. **Read the Code**: Examine example source code for implementation details
3. **Build Your Own**: Create custom ATLAS applications
4. **Contribute**: Add new examples or improve existing ones

## Additional Resources

- [API Documentation](../doc/api/index.md)
- [User Guide](../doc/user-guide/index.md)
- [Architecture Overview](../doc/architecture/index.md)
- [Getting Started Tutorial](../doc/getting-started/quickstart.md)

---

*For questions about examples, please refer to the [FAQ](../doc/reference/faq.md) or [Contributing Guide](../doc/community/contributing.md).* 