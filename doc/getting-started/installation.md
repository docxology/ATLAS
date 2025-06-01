# Installation Guide

This guide will help you install and set up ATLAS on your system.

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM (8GB+ recommended)
- **Storage**: 1GB free space
- **Operating System**: Linux, macOS, or Windows

### Recommended Requirements
- **Python**: 3.10 or higher
- **Memory**: 8GB+ RAM
- **Storage**: 5GB+ free space
- **CPU**: Multi-core processor for better performance

## Installation Methods

### 1. Install from PyPI (Recommended)

```bash
# Install the latest stable version
pip install atlas-knowledge

# Verify installation
python -c "import atlas; print(atlas.__version__)"
```

### 2. Install from Source

```bash
# Clone the repository
git clone https://github.com/atlas-team/atlas.git
cd atlas

# Create a virtual environment
python -m venv atlas-env
source atlas-env/bin/activate  # On Windows: atlas-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Verify installation
python -c "import atlas; print('ATLAS installed successfully')"
```

### 3. Docker Installation

```bash
# Pull the official image
docker pull atlas/atlas-knowledge:latest

# Run ATLAS container
docker run -p 8080:8080 atlas/atlas-knowledge:latest

# Or build from source
git clone https://github.com/atlas-team/atlas.git
cd atlas
docker build -t atlas-knowledge .
```

## Optional Dependencies

ATLAS has several optional dependency groups that enable additional functionality:

### Visualization Dependencies

```bash
# Install visualization capabilities
pip install atlas-knowledge[viz]
```

Includes:
- `matplotlib>=3.5.0` - Basic plotting
- `plotly>=5.0.0` - Interactive visualizations
- `graphviz>=0.20.0` - Graph visualization
- `seaborn>=0.11.0` - Statistical visualizations

### Development Dependencies

```bash
# Install development tools
pip install atlas-knowledge[dev]
```

Includes:
- `pytest>=7.0.0` - Testing framework
- `black>=23.0.0` - Code formatting
- `mypy>=1.0.0` - Type checking
- `flake8>=6.0.0` - Code linting

### All Dependencies

```bash
# Install everything
pip install atlas-knowledge[all]
```

## Platform-Specific Instructions

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3 python3-pip python3-venv

# Install system dependencies for visualization
sudo apt install graphviz graphviz-dev

# Install ATLAS
pip3 install atlas-knowledge[all]
```

### macOS

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python

# Install Graphviz
brew install graphviz

# Install ATLAS
pip3 install atlas-knowledge[all]
```

### Windows

1. **Install Python**: Download from [python.org](https://python.org)
2. **Install Git**: Download from [git-scm.com](https://git-scm.com)
3. **Install Graphviz**: Download from [graphviz.org](https://graphviz.org)

```cmd
# In Command Prompt or PowerShell
pip install atlas-knowledge[all]
```

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
python -m atlas.examples.basic_test

# Run with visualization tests (if viz dependencies installed)
python -m atlas.examples.comprehensive_demo
```

## Troubleshooting

### Common Issues

#### ImportError: No module named 'atlas'

**Solution**: Ensure ATLAS is installed in the correct Python environment
```bash
pip list | grep atlas
```

#### Graphviz not found

**Solution**: Install Graphviz system package
```bash
# Ubuntu/Debian
sudo apt install graphviz

# macOS
brew install graphviz

# Windows: Download installer from graphviz.org
```

#### Permission denied errors

**Solution**: Use virtual environment
```bash
python -m venv atlas-env
source atlas-env/bin/activate
pip install atlas-knowledge
```

#### Memory errors with large datasets

**Solution**: Adjust configuration
```python
from atlas.core import ATLASConfig

config = ATLASConfig(
    max_expansion_depth=5,  # Reduce from default 10
    enable_quality_metrics=False  # Disable for performance
)
```

### Getting Help

- **GitHub Issues**: [github.com/atlas-team/atlas/issues](https://github.com/atlas-team/atlas/issues)
- **Documentation**: [atlas-knowledge.readthedocs.io](https://atlas-knowledge.readthedocs.io)
- **Community**: [atlas-knowledge.discourse.group](https://atlas-knowledge.discourse.group)

## Next Steps

- [Quick Start Tutorial](quickstart.md) - Build your first ATLAS system
- [Basic Concepts](concepts.md) - Understand ATLAS fundamentals
- [User Guide](../user-guide/index.md) - Complete usage documentation

---

*Installation successful? Try the [Quick Start Tutorial](quickstart.md) next!* 