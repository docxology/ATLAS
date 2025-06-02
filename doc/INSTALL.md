# ATLAS Installation Guide

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/atlas-team/atlas.git
cd atlas
```

### 2. Install Dependencies

#### Core Installation (Minimal)
```bash
pip install -e .
```

#### Full Installation (with visualization)
```bash
pip install -e ".[viz]"
```

#### Development Installation
```bash
pip install -e ".[dev]"
```

#### Complete Installation (all features)
```bash
pip install -e ".[all]"
```

### 3. Verify Installation

#### Basic Test (No Visualization Dependencies)
```bash
cd examples
python basic_test.py
```

#### Full Demo (Requires Visualization Dependencies)
```bash
cd examples  
python comprehensive_demo.py
```

#### Run Test Suite
```bash
pytest tests/ -v
```

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 512MB RAM (2GB+ recommended for large graphs)
- **Storage**: 100MB for core installation

## Core Dependencies

- `networkx>=2.6.0` - Graph data structures and algorithms
- `numpy>=1.19.0` - Numerical computations
- `python-dateutil>=2.8.0` - Date/time handling

## Optional Dependencies

### Visualization (`[viz]`)
- `matplotlib>=3.3.0` - Static plotting
- `seaborn>=0.11.0` - Statistical visualization
- `pandas>=1.2.0` - Data manipulation
- `plotly>=5.0.0` - Interactive plots

### Development (`[dev]`)
- `pytest>=6.0.0` - Testing framework
- `pytest-cov>=2.10.0` - Test coverage
- `black>=20.8b1` - Code formatting
- `flake8>=3.8.0` - Linting
- `mypy>=0.812` - Type checking

## Installation Methods

### Method 1: Development Install (Recommended)
```bash
# Clone repository
git clone https://github.com/atlas-team/atlas.git
cd atlas

# Create virtual environment (optional but recommended)
python -m venv atlas-env
source atlas-env/bin/activate  # On Windows: atlas-env\Scripts\activate

# Install in development mode
pip install -e ".[all]"
```

### Method 2: Direct Install from Repository
```bash
pip install git+https://github.com/atlas-team/atlas.git
```

### Method 3: From PyPI (when published)
```bash
pip install atlas-knowledge
```

## Troubleshooting

### Common Issues

#### Import Errors
If you encounter import errors, ensure you're running from the correct directory:
```bash
# Add src to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/atlas/src"
```

#### Visualization Dependencies
If visualization features are not working:
```bash
# Install visualization dependencies separately
pip install matplotlib seaborn pandas plotly
```

#### NetworkX Compatibility
For older Python versions, you may need specific NetworkX versions:
```bash
# Python 3.8
pip install "networkx>=2.6.0,<3.0"
```

#### Memory Issues with Large Graphs
For large knowledge graphs:
- Increase system memory
- Use graph sampling for visualization
- Consider graph databases for production use

### Platform-Specific Notes

#### Linux
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev python3-pip

# CentOS/RHEL
sudo yum install python3-devel python3-pip
```

#### macOS
```bash
# Using Homebrew
brew install python
```

#### Windows
- Install Python from python.org
- Use PowerShell or Command Prompt
- Consider using Windows Subsystem for Linux (WSL)

## Configuration

### Environment Variables

Create a `.env` file in your project directory:

```bash
# ATLAS Configuration
ATLAS_LOG_LEVEL=INFO
ATLAS_CACHE_SIZE=1000
ATLAS_GRAPH_FORMAT=graphml
ATLAS_DATA_DIR=./atlas_data
ATLAS_TEMP_DIR=./atlas_temp
```

### Configuration File

Create `atlas_config.yaml`:

```yaml
# ATLAS Configuration
atlas:
  auto_pattern_inference: true
  enable_dynamic_typing: true
  max_expansion_depth: 10
  enable_quality_metrics: true
  log_level: "INFO"

# Database settings
database:
  engine: "sqlite"
  path: "./atlas.db"

# Visualization settings
visualization:
  default_backend: "matplotlib"
  figure_size: [12, 8]
  dpi: 100
```

## Verification

### Basic Functionality Test

```python
from atlas import ATLASEngine, Entity, Pattern

# Create ATLAS engine
atlas = ATLASEngine()

# Create a simple entity
entity = Entity("test_entity", attributes={"name": "Test"})
atlas.add_entity(entity.id, entity.to_dict())

# Verify
print(f"ATLAS installed successfully! Entities: {len(atlas.entities)}")
```

### Run Built-in Tests

```bash
# Run comprehensive test suite
python -m examples.basic_test

# Run with visualization tests (if viz dependencies installed)  
python -m examples.comprehensive_demo
```

### Test Visualization (Optional)
```python
try:
    from atlas.visualization.graph_viz import GraphVisualizer
    print("✓ Visualization modules available")
except ImportError:
    print("⚠ Visualization modules not available")
```

## Next Steps

1. **Read the Documentation**: Check `README.md` for system overview
2. **Run Examples**: Explore `examples/` directory
3. **Read the Paper**: See `ATLAS_paper.md` for theoretical background
4. **Build Your Knowledge Base**: Start with `examples/basic_test.py`
5. **Explore Advanced Features**: Try `examples/comprehensive_demo.py`

## Getting Help

- **Documentation**: See `doc/` directory
- **Examples**: See `examples/` directory  
- **Issues**: Open GitHub issues for bugs
- **Discussions**: Use GitHub discussions for questions

## License

MIT License - see LICENSE file for details. 