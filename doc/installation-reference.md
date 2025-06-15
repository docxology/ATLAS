# Installation Reference

This file provides the canonical installation commands for ATLAS. All documentation should reference this file rather than duplicating installation instructions.

## Core Installation

```bash
# Basic installation (minimal dependencies)
pip install -e .
```

## Installation with Optional Dependencies

```bash
# With visualization capabilities
pip install -e ".[viz]"

# With development tools
pip install -e ".[dev]"

# With all optional dependencies
pip install -e ".[all]"
```

## Production Installation

```bash
# From PyPI (when released)
pip install atlas-knowledge

# From GitHub (development version)
pip install git+https://github.com/atlas-team/atlas.git
```

## Development Setup

```bash
# Full development environment
pip install -e ".[dev,viz,all]"

# Install pre-commit hooks
pre-commit install
```

## Dependency Constraints

Core dependencies with version constraints:
- `networkx>=2.6.0,<4.0`
- `numpy>=1.20.0,<2.0`
- `python-dateutil>=2.8.0,<3.0`

Visualization dependencies:
- `matplotlib>=3.3.0,<4.0`
- `seaborn>=0.11.0,<1.0`
- `pandas>=1.2.0,<3.0`
- `plotly>=5.0.0,<6.0`

Development dependencies:
- `pytest>=6.0.0,<8.0`
- `pytest-cov>=2.10.0,<5.0`
- `black>=20.8b1,<25.0`
- `flake8>=3.8.0,<7.0`
- `mypy>=0.812,<2.0`

## Troubleshooting {#troubleshooting}

- **Import errors**: Ensure `pip install -e .` was run from the project root
- **Missing dependencies**: Use `pip install atlas-knowledge[all]` for all features
- **Visualization issues**: Install optional dependencies with `pip install -e ".[viz]"`

---

**Note**: For detailed installation instructions and troubleshooting, see [INSTALL.md](INSTALL.md). 