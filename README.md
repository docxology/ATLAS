# ATLAS Knowledge Management System

A comprehensive knowledge management framework with modular composability, dynamic pattern recognition, and question-oriented information discovery.

> **📖 For a complete system overview, see [ATLAS_overview.md](ATLAS_overview.md) - the comprehensive guide to all ATLAS features and technology.**

## Quick Start

Run the main script to install, test, and explore the system:

```bash
python3 main.py
```

This will:
- 🧹 Clean up any previous standalone output directories
- ✅ Check system requirements
- ✅ Install ATLAS dependencies  
- ✅ Run comprehensive tests
- ✅ Discover and test available examples
- ✅ Run demonstration with visualizations
- ✅ Generate system reports
- 📁 **Centralize ALL outputs in a single timestamped directory**

## Centralized Output Structure

When you run `main.py`, **ALL outputs** are automatically organized in a single timestamped directory. No more scattered test folders!

```
atlas_output_YYYYMMDD_HHMMSS/
├── reports/
│   ├── atlas_system_report.json    # Complete system analysis
│   └── summary.txt                  # Human-readable summary
├── logs/
│   └── *.log                       # Command execution logs
├── visualizations/
│   ├── demo_topology.png           # Network topology chart
│   ├── demo_distribution.png       # Component distribution
│   ├── demo_hierarchy.png          # Pattern hierarchy
│   ├── demo_overview.png           # System overview
│   ├── demo_network_*.png          # Network analysis files
│   ├── atlas_graph.graphml         # Graph export
│   ├── pattern_analysis.json       # Pattern analysis
│   └── demonstration_results.json  # Demo results
└── test_results/
    ├── pytest_results.xml          # Test results
    ├── basic_test_results.json     # Basic test outputs
    └── test_summary.json           # Test summary
```

## What You Get

After running `main.py`, you'll see:
- **Installation status**: Whether ATLAS installed successfully
- **Test results**: Pass/fail status of all tests with detailed logs
- **Available examples**: List of runnable examples with commands
- **Visualizations**: Charts showing system structure and metrics
- **Reports**: Comprehensive JSON and text reports
- **Output directory**: All files organized in timestamped folder

## Running Individual Components

You can also run components separately with custom output directories:

```bash
# Run basic tests
python3 examples/basic_test.py --output-dir my_test_results/

# Run comprehensive demo
python3 examples/comprehensive_demo.py --output-dir my_demo_results/

# Run specific test
python3 examples/basic_test.py --test basic --output-dir specific_test/
```

## Architecture

The ATLAS system consists of 5 core components:
1. **Entities**: Knowledge objects with attributes and patterns
2. **Patterns**: Abstract templates for knowledge organization  
3. **iQueries**: Information-seeking queries with priority and context
4. **Attributes**: Flexible metadata containers
5. **Interfaces**: Translation layers for system interoperability

## Documentation

- Full documentation: `doc/README.md`
- Installation guide: `doc/INSTALL.md` 
- System overview: `doc/ATLAS_SYSTEM_OVERVIEW.md`
- Legacy files: `doc/legacy/`

## License

MIT License - see `doc/LICENSE` for details.
