# Contributing to ATLAS

We welcome contributions to ATLAS! This guide explains how to contribute to the project, whether you're fixing bugs, adding features, improving documentation, or helping with community support.

## Getting Started

### Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](code-of-conduct.md). Please read it before contributing.

### Ways to Contribute

There are many ways to contribute to ATLAS:

- **Report bugs** and request features
- **Submit code** improvements and new features
- **Improve documentation** and examples
- **Help with testing** and quality assurance
- **Provide community support** and answer questions
- **Share use cases** and success stories

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/atlas.git
   cd atlas
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv atlas-dev
   source atlas-dev/bin/activate  # On Windows: atlas-dev\Scripts\activate
   ```

4. **Install development dependencies**:
   ```bash
   pip install -e .[dev,viz,all]
   ```

5. **Set up pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

6. **Run tests** to verify setup:
   ```bash
   pytest tests/
   ```

### Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following our coding standards
3. **Add tests** for new functionality
4. **Update documentation** as needed
5. **Run the test suite**:
   ```bash
   pytest tests/
   flake8 src/
   black src/ tests/
   mypy src/
   ```

6. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** on GitHub

## Coding Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black default)
- **Imports**: Use absolute imports, group by standard/third-party/local
- **Docstrings**: Use Google-style docstrings
- **Type hints**: Required for all public functions and methods

### Code Formatting

We use automated tools to maintain consistent formatting:

```bash
# Format code with Black
black src/ tests/

# Sort imports with isort
isort src/ tests/

# Check style with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/
```

### Example Code Style

```python
from typing import Dict, List, Optional, Union
import logging

from atlas.core import ATLASEngine
from atlas.entities import Entity


class ExampleClass:
    """Example class demonstrating ATLAS coding standards.
    
    This class shows proper formatting, type hints, and documentation
    style for ATLAS contributions.
    
    Args:
        name: The name of the example instance.
        config: Optional configuration dictionary.
        
    Attributes:
        name: The instance name.
        logger: Logger instance for this class.
    """
    
    def __init__(
        self, 
        name: str, 
        config: Optional[Dict[str, Union[str, int]]] = None
    ) -> None:
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
    def process_entities(self, entities: List[Entity]) -> Dict[str, int]:
        """Process a list of entities and return statistics.
        
        Args:
            entities: List of Entity objects to process.
            
        Returns:
            Dictionary containing processing statistics.
            
        Raises:
            ValueError: If entities list is empty.
        """
        if not entities:
            raise ValueError("Entities list cannot be empty")
            
        stats = {"total": len(entities), "processed": 0}
        
        for entity in entities:
            if self._process_single_entity(entity):
                stats["processed"] += 1
                
        return stats
        
    def _process_single_entity(self, entity: Entity) -> bool:
        """Process a single entity (private method).
        
        Args:
            entity: Entity to process.
            
        Returns:
            True if processing succeeded, False otherwise.
        """
        try:
            # Processing logic here
            return True
        except Exception as e:
            self.logger.error(f"Failed to process entity {entity.id}: {e}")
            return False
```

## Testing Guidelines

### Test Structure

We use pytest for testing with the following structure:

```
tests/
├── unit/           # Unit tests for individual components
├── integration/    # Integration tests for component interaction
├── fixtures/       # Test data and fixtures
└── conftest.py     # Shared test configuration
```

### Writing Tests

1. **Test naming**: Use descriptive names that explain what is being tested
2. **Test organization**: Group related tests in classes
3. **Fixtures**: Use pytest fixtures for common test data
4. **Assertions**: Use specific assertions with clear error messages

### Example Test

```python
import pytest
from atlas import ATLASEngine, Entity, Pattern


class TestEntityManagement:
    """Test suite for entity management functionality."""
    
    @pytest.fixture
    def atlas_engine(self):
        """Create a fresh ATLAS engine for testing."""
        return ATLASEngine()
        
    @pytest.fixture
    def sample_entity(self):
        """Create a sample entity for testing."""
        return Entity(
            entity_id="test_entity",
            attributes={"name": "Test", "type": "sample"},
            patterns=["test_pattern"]
        )
        
    def test_add_entity_success(self, atlas_engine, sample_entity):
        """Test successful entity addition."""
        # Act
        atlas_engine.add_entity(sample_entity.id, sample_entity.to_dict())
        
        # Assert
        assert sample_entity.id in atlas_engine.entities
        assert atlas_engine.entities[sample_entity.id]["attributes"]["name"] == "Test"
        
    def test_add_duplicate_entity_raises_error(self, atlas_engine, sample_entity):
        """Test that adding duplicate entity raises appropriate error."""
        # Arrange
        atlas_engine.add_entity(sample_entity.id, sample_entity.to_dict())
        
        # Act & Assert
        with pytest.raises(ValueError, match="Entity already exists"):
            atlas_engine.add_entity(sample_entity.id, sample_entity.to_dict())
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_entities.py

# Run with coverage
pytest --cov=atlas tests/

# Run with verbose output
pytest -v

# Run only failed tests from last run
pytest --lf
```

## Documentation Guidelines

### Documentation Types

We maintain several types of documentation:

1. **API Documentation**: Docstrings in code
2. **User Guides**: Step-by-step instructions
3. **Tutorials**: Learning-oriented content
4. **Reference**: Comprehensive technical details

### Writing Documentation

#### Docstring Standards

Use Google-style docstrings for all public functions, classes, and methods:

```python
def calculate_similarity(pattern1: Pattern, pattern2: Pattern) -> float:
    """Calculate similarity score between two patterns.
    
    This function compares two patterns based on their QKit overlap,
    inheritance relationships, and attribute similarity.
    
    Args:
        pattern1: First pattern for comparison.
        pattern2: Second pattern for comparison.
        
    Returns:
        Similarity score between 0.0 and 1.0, where 1.0 indicates
        identical patterns.
        
    Raises:
        ValueError: If either pattern is None or invalid.
        
    Example:
        >>> pattern1 = Pattern("person", qkit=["name", "age"])
        >>> pattern2 = Pattern("researcher", qkit=["name", "field"])
        >>> similarity = calculate_similarity(pattern1, pattern2)
        >>> print(f"Similarity: {similarity:.2f}")
        Similarity: 0.33
    """
```

#### Markdown Documentation

For user guides and tutorials:

1. **Use clear headings** to organize content
2. **Include code examples** with proper syntax highlighting
3. **Add cross-references** to related documentation
4. **Provide practical examples** that users can follow
5. **Keep language clear and concise**

### Building Documentation

```bash
# Install documentation dependencies
pip install -e .[docs]

# Build documentation locally
cd docs/
make html

# View documentation
open build/html/index.html
```

## Submitting Changes

### Pull Request Process

1. **Ensure your branch is up to date**:
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run the full test suite**:
   ```bash
   pytest tests/
   flake8 src/
   black --check src/ tests/
   mypy src/
   ```

3. **Update documentation** if needed

4. **Create a Pull Request** with:
   - Clear title describing the change
   - Detailed description of what was changed and why
   - Reference to any related issues
   - Screenshots for UI changes (if applicable)

### Pull Request Template

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated

## Related Issues
Fixes #(issue number)

## Additional Notes
Any additional information or context about the changes.
```

### Review Process

1. **Automated checks** must pass (CI/CD pipeline)
2. **Code review** by at least one maintainer
3. **Documentation review** for user-facing changes
4. **Testing verification** for new features
5. **Final approval** and merge by maintainer

## Bug Reports

### Before Reporting

1. **Search existing issues** to avoid duplicates
2. **Try the latest version** to see if the bug is already fixed
3. **Gather relevant information** about your environment

### Bug Report Template

```markdown
## Bug Description
A clear and concise description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
A clear description of what you expected to happen.

## Actual Behavior
A clear description of what actually happened.

## Environment
- OS: [e.g. Ubuntu 20.04, Windows 10, macOS 12.0]
- Python version: [e.g. 3.9.7]
- ATLAS version: [e.g. 1.0.0]
- Dependencies: [relevant package versions]

## Additional Context
Add any other context about the problem here, including:
- Error messages or stack traces
- Screenshots (if applicable)
- Sample code that reproduces the issue
```

## Feature Requests

### Before Requesting

1. **Check existing issues** and discussions
2. **Consider the scope** - is this a core feature or plugin?
3. **Think about alternatives** - can existing features solve the problem?

### Feature Request Template

```markdown
## Feature Description
A clear and concise description of the feature you'd like to see.

## Problem Statement
What problem does this feature solve? What use case does it address?

## Proposed Solution
Describe the solution you'd like to see implemented.

## Alternatives Considered
Describe any alternative solutions or features you've considered.

## Additional Context
Add any other context, mockups, or examples about the feature request.

## Implementation Notes
If you have ideas about how this could be implemented, share them here.
```

## Community Support

### Helping Others

Ways to help the ATLAS community:

1. **Answer questions** in GitHub Discussions
2. **Review pull requests** from other contributors
3. **Improve documentation** based on user feedback
4. **Share examples** and use cases
5. **Report bugs** you encounter
6. **Test new features** and provide feedback

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions, ideas, and general discussion
- **Documentation**: Comprehensive guides and references
- **Code Reviews**: Technical discussions on pull requests

## Recognition

We value all contributions to ATLAS! Contributors are recognized through:

- **Contributors list** in the repository
- **Release notes** mentioning significant contributions
- **Community highlights** for exceptional contributions
- **Maintainer status** for long-term contributors

## Getting Help

If you need help with contributing:

1. **Read the documentation** thoroughly
2. **Search existing issues** and discussions
3. **Ask questions** in GitHub Discussions
4. **Join community calls** (if available)
5. **Contact maintainers** directly for complex issues

## License

By contributing to ATLAS, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

*Thank you for contributing to ATLAS! Your efforts help make knowledge management more accessible and powerful for everyone.* 