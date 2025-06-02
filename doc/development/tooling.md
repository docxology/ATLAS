# Development Tooling Guide

This guide covers the development tools, machine-readable specifications, and automation capabilities that support ATLAS development and integration.

## Machine-Readable Specifications

ATLAS provides comprehensive machine-readable specifications to support automation, validation, and integration:

### Configuration Schema

**File**: [`doc/schemas/atlas-config.schema.json`](../schemas/atlas-config.schema.json)

The configuration JSON Schema provides comprehensive validation for ATLAS runtime configuration, enabling:

- **IDE Support**: IntelliSense and auto-completion in VS Code, JetBrains IDEs
- **Validation**: Automatic validation of configuration files
- **Documentation**: Self-documenting configuration options
- **Tooling**: Integration with configuration management tools

**Usage Examples**:

```bash
# Validate configuration with ajv-cli
npx ajv-cli validate -s doc/schemas/atlas-config.schema.json -d atlas-config.yaml

# Generate TypeScript types
npx json-schema-to-typescript doc/schemas/atlas-config.schema.json > atlas-config.d.ts
```

**IDE Configuration** (VS Code):
```json
{
  "yaml.schemas": {
    "doc/schemas/atlas-config.schema.json": "atlas-config.yaml"
  }
}
```

### OpenAPI Specification

**File**: [`doc/schemas/atlas-api.openapi.yaml`](../schemas/atlas-api.openapi.yaml)

The OpenAPI 3.0 specification defines the future REST API interface, supporting:

- **API Documentation**: Automatic generation of API docs
- **Client Generation**: Generate client libraries in multiple languages
- **Mock Servers**: Create mock APIs for testing
- **Validation**: Request/response validation

**Usage Examples**:

```bash
# Generate API documentation
npx @redocly/cli build-docs doc/schemas/atlas-api.openapi.yaml

# Generate Python client
openapi-generator generate -i doc/schemas/atlas-api.openapi.yaml -g python -o atlas-client-python

# Generate TypeScript client
openapi-generator generate -i doc/schemas/atlas-api.openapi.yaml -g typescript-axios -o atlas-client-ts

# Run mock server
npx @stoplight/prism mock doc/schemas/atlas-api.openapi.yaml
```

### Build and Test Schema

**File**: [`doc/schemas/atlas-build.schema.json`](../schemas/atlas-build.schema.json)

The build schema standardizes build automation, testing, and CI/CD configuration, supporting:

- **Dependency Management**: Core, visualization, development, and documentation dependencies
- **Testing Configuration**: Framework setup, coverage targets, and test markers
- **Quality Tools**: Code formatters, linters, and type checkers
- **CI/CD Pipelines**: Multi-platform testing and deployment automation

**Usage Examples**:
```bash
# Validate build configuration
ajv-cli validate -s doc/schemas/atlas-build.schema.json -d build-config.json

# Generate CI/CD pipeline from schema
python tools/generate-pipeline.py --schema doc/schemas/atlas-build.schema.json
```

### Deployment Schema

**File**: [`doc/schemas/atlas-deployment.schema.json`](../schemas/atlas-deployment.schema.json)

The deployment schema defines container orchestration and infrastructure automation, covering:

- **Application Deployment**: Container images, resource limits, scaling configuration
- **Database Configuration**: Engine selection, storage, backup policies
- **Security Settings**: RBAC, pod security, network policies
- **Monitoring**: Health checks, metrics collection, logging configuration

**Usage Examples**:
```bash
# Validate deployment configuration
ajv-cli validate -s doc/schemas/atlas-deployment.schema.json -d k8s-config.json

# Generate Kubernetes manifests
helm template atlas-chart --values deployment-config.yaml

# Generate Docker Compose from schema
python tools/generate-compose.py --config deployment-config.yaml
```

### System Metadata

**File**: [`doc/metadata/system-metadata.json`](../metadata/system-metadata.json)

Comprehensive machine-readable system information including:

- **Architecture**: Component descriptions and dependencies
- **Capabilities**: Feature maturity and performance characteristics
- **Performance**: Scalability limits and resource requirements
- **Development**: Build tools, CI/CD pipelines, and release processes
- **Integrations**: Supported databases and external systems

**Usage Examples**:

```python
import json

# Load system metadata
with open('doc/metadata/system-metadata.json') as f:
    metadata = json.load(f)

# Check component dependencies
for component in metadata['architecture']['core_components']:
    print(f"{component['name']}: {component['dependencies']}")

# Validate system requirements
min_memory = metadata['performance']['resource_requirements']['minimum']['memory']
print(f"Minimum memory requirement: {min_memory}")
```

### Configuration Templates

**File**: [`doc/templates/atlas-config.yaml`](../templates/atlas-config.yaml)

Production-ready configuration templates with:

- **Complete Examples**: All configuration sections with documentation
- **Environment-specific**: Development, testing, and production variants
- **Best Practices**: Recommended settings and optimizations
- **Comments**: Inline documentation for all options

**Usage Examples**:

```bash
# Copy template for new deployment
cp doc/templates/atlas-config.yaml atlas-config.yaml

# Extract specific configuration section
yq eval '.atlas' doc/templates/atlas-config.yaml > atlas-core-config.yaml

# Merge with environment-specific overrides
yq eval-all 'select(fileIndex == 0) * select(fileIndex == 1)' \
  doc/templates/atlas-config.yaml env/production.yaml > production-config.yaml
```

## Development Tools

### Build and Packaging

**setuptools** (`setup.py`):
```python
# Install in development mode with all optional dependencies
pip install -e ".[dev,viz,all]"

# Build distribution packages
python setup.py sdist bdist_wheel

# Upload to PyPI
twine upload dist/*
```

**pip-tools** (dependency management):
```bash
# Generate locked requirements
pip-compile --extra dev --extra viz setup.py

# Update dependencies
pip-compile --upgrade --extra dev --extra viz setup.py

# Sync environment
pip-sync requirements.txt
```

### Testing Framework

**pytest** with comprehensive test configuration:

```bash
# Run all tests with coverage
pytest tests/ --cov=atlas --cov-report=html --cov-report=term

# Run specific test categories
pytest tests/unit/ -v                    # Unit tests only
pytest tests/integration/ -v            # Integration tests only
pytest tests/test_*performance* -v      # Performance tests only

# Run tests with specific markers
pytest -m "not slow" tests/             # Skip slow tests
pytest -m "integration" tests/          # Run only integration tests
```

**Test Configuration** (`pytest.ini`):
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    performance: marks tests as performance tests
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
```

### Code Quality Tools

**Black** (code formatting):
```bash
# Format all Python files
black src/ tests/ examples/

# Check formatting without changes
black --check src/ tests/ examples/

# Format with specific line length
black --line-length 88 src/
```

**flake8** (linting):
```bash
# Run linting
flake8 src/ tests/ examples/

# With specific configuration
flake8 --max-line-length=88 --extend-ignore=E203,W503 src/
```

**mypy** (type checking):
```bash
# Type check with mypy
mypy src/atlas/

# Generate mypy report
mypy --html-report mypy-report src/atlas/
```

### Documentation Tools

**Sphinx** (documentation generation):
```bash
# Generate API documentation
sphinx-apidoc -o docs/source src/atlas

# Build HTML documentation
sphinx-build -b html docs/source docs/build

# Build PDF documentation
sphinx-build -b latex docs/source docs/latex
```

**MkDocs** (alternative documentation):
```bash
# Serve documentation locally
mkdocs serve

# Build static documentation
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

## Automation and CI/CD

### GitHub Actions Workflow

**File**: `.github/workflows/ci.yml`
```yaml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v3
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        pip install -e ".[dev,test]"
    
    - name: Run tests
      run: |
        pytest tests/ --cov=atlas --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  quality:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: pip install black flake8 mypy
    
    - name: Check formatting
      run: black --check src/ tests/
    
    - name: Run linting
      run: flake8 src/ tests/
    
    - name: Type checking
      run: mypy src/atlas/

  docs:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v3
      with:
        python-version: 3.9
    
    - name: Install documentation dependencies
      run: pip install -r doc/requirements.txt
    
    - name: Build documentation
      run: sphinx-build -b html doc/source doc/build
    
    - name: Deploy to GitHub Pages
      if: github.ref == 'refs/heads/main'
      uses: peaceiris/actions-gh-pages@v3
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: doc/build
```

### Pre-commit Hooks

**File**: `.pre-commit-config.yaml`
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.950
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.2.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
```

**Setup**:
```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## Integration Tools

### Database Schema Migration

**Alembic** (for SQLAlchemy/PostgreSQL):
```bash
# Initialize migrations
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Add entity tables"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

### Container Support

**Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY setup.py .
RUN pip install -e .

EXPOSE 8080

CMD ["python", "-m", "atlas.server"]
```

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  atlas:
    build: .
    ports:
      - "8080:8080"
    environment:
      - ATLAS_LOG_LEVEL=INFO
      - ATLAS_DATABASE_ENGINE=postgresql
    depends_on:
      - postgres
  
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: atlas
      POSTGRES_USER: atlas
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Performance Monitoring

**prometheus.yml** (metrics collection):
```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'atlas'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: /metrics
```

**Grafana Dashboard** (visualization):
```json
{
  "dashboard": {
    "title": "ATLAS System Metrics",
    "panels": [
      {
        "title": "Entity Count",
        "type": "stat",
        "targets": [
          {"expr": "atlas_entities_total"}
        ]
      },
      {
        "title": "Query Performance",
        "type": "graph",
        "targets": [
          {"expr": "rate(atlas_query_duration_seconds[5m])"}
        ]
      }
    ]
  }
}
```

## Development Workflows

### Feature Development

1. **Setup Development Environment**:
   ```bash
   git clone https://github.com/atlas-team/atlas.git
   cd atlas
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -e ".[dev,viz,all]"
   pre-commit install
   ```

2. **Create Feature Branch**:
   ```bash
   git checkout -b feature/new-functionality
   ```

3. **Development Cycle**:
   ```bash
   # Write code and tests
   # Run tests
   pytest tests/

   # Check code quality
   black src/ tests/
   flake8 src/ tests/
   mypy src/atlas/

   # Update documentation
   # Commit changes
   git add .
   git commit -m "Add new functionality"
   ```

4. **Integration Testing**:
   ```bash
   # Run full test suite
   pytest tests/ --cov=atlas

   # Test with different Python versions
   tox

   # Test documentation build
   sphinx-build -b html doc/source doc/build
   ```

### Release Process

1. **Version Bump**:
   ```bash
   # Update version in setup.py
   # Update CHANGELOG.md
   # Commit version changes
   git add setup.py CHANGELOG.md
   git commit -m "Bump version to 1.1.0"
   ```

2. **Create Release**:
   ```bash
   # Tag release
   git tag v1.1.0
   git push origin v1.1.0

   # Build packages
   python setup.py sdist bdist_wheel

   # Upload to PyPI
   twine upload dist/*
   ```

3. **Documentation Deployment**:
   ```bash
   # Build and deploy documentation
   sphinx-build -b html doc/source doc/build
   # Deploy to hosting platform
   ```

## Troubleshooting Development Issues

### Common Problems

1. **Import Errors**:
   ```bash
   # Check PYTHONPATH
   echo $PYTHONPATH
   
   # Install in development mode
   pip install -e .
   ```

2. **Test Failures**:
   ```bash
   # Run specific test with verbose output
   pytest tests/test_specific.py::test_function -v -s
   
   # Debug with pdb
   pytest tests/test_specific.py::test_function --pdb
   ```

3. **Documentation Build Issues**:
   ```bash
   # Clear build cache
   rm -rf doc/build/
   
   # Rebuild with warnings as errors
   sphinx-build -W -b html doc/source doc/build
   ```

### Performance Debugging

```python
# Profile code execution
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative').print_stats(10)
```

```bash
# Memory profiling with memory_profiler
pip install memory_profiler
python -m memory_profiler examples/memory_test.py

# Line profiling with line_profiler  
pip install line_profiler
kernprof -l -v examples/performance_test.py
```

---

*This tooling guide provides comprehensive support for ATLAS development. For specific tool configuration, see the individual configuration files in the repository.* 