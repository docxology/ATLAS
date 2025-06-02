---
title: Python Best Practices
tags: [python, programming, bestpractices, software]
---

# Python Best Practices

Essential practices for writing clean, maintainable Python code.

## Code Style and Formatting

### PEP 8 Guidelines
- Use 4 spaces for indentation
- Line length max 79 characters
- Meaningful variable and function names
- Consistent naming conventions

### Tools
- **Black**: Automatic code formatting
- **Flake8**: Style guide enforcement
- **isort**: Import statement organization

## Project Structure

```
project/
├── src/
│   └── package/
│       ├── __init__.py
│       ├── core/
│       └── utils/
├── tests/
├── docs/
├── requirements.txt
├── setup.py
└── README.md
```

## Documentation

#documentation

### Docstrings
```python
def calculate_similarity(text1: str, text2: str) -> float:
    \"\"\"
    Calculate similarity between two text strings.
    
    Args:
        text1: First text string
        text2: Second text string
        
    Returns:
        Similarity score between 0.0 and 1.0
        
    Raises:
        ValueError: If input strings are empty
    \"\"\"
    pass
```

### Type Hints
- Use type annotations for function parameters and return values
- Import from `typing` module for complex types
- Use `Optional[Type]` for nullable parameters

## Testing

#testing

### Unit Testing
- Use `pytest` framework
- Test edge cases and error conditions
- Aim for high test coverage
- Mock external dependencies

### Test Structure
```python
def test_function_with_valid_input():
    # Arrange
    input_data = "test"
    expected = "result"
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    assert result == expected
```

## Error Handling

### Exception Practices
- Use specific exception types
- Handle exceptions at appropriate levels
- Provide meaningful error messages
- Use context managers for resource management

## Performance Optimization

#performance

### Profiling
- Use `cProfile` for performance analysis
- Identify bottlenecks with line profilers
- Memory profiling with `memory_profiler`

### Common Optimizations
- List comprehensions vs loops
- Generator expressions for memory efficiency
- Caching with `functools.lru_cache`
- Vectorization with NumPy

## Security Considerations

- Input validation and sanitization
- Avoid `eval()` and `exec()`
- Use parameterized queries for databases
- Handle secrets properly

## Related Notes

- [[01 - Areas/Software Development]]
- [[API Design Patterns]]
- [[Database Design]]
- [[Git Workflow]]

## Tools and Libraries

- **Development**: `black`, `flake8`, `mypy`, `pre-commit`
- **Testing**: `pytest`, `coverage`, `tox`
- **Documentation**: `sphinx`, `mkdocs`
- **Virtual Environments**: `venv`, `conda`, `poetry`