"""
Helper functions and utilities for ATLAS.

Common utility functions used throughout the ATLAS system for
ID generation, time handling, data manipulation, and more.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import copy


def generate_id(prefix: str = "", length: int = 8) -> str:
    """
    Generate a unique identifier.
    
    Args:
        prefix: Optional prefix for the ID
        length: Length of the random portion
        
    Returns:
        Unique identifier string
    """
    random_part = str(uuid.uuid4()).replace('-', '')[:length]
    return f"{prefix}_{random_part}" if prefix else random_part


def timestamp_now() -> str:
    """
    Get current timestamp in ISO format.
    
    Returns:
        Current timestamp as ISO string
    """
    return datetime.now().isoformat()


def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary (takes precedence)
        
    Returns:
        Merged dictionary
    """
    result = copy.deepcopy(dict1)
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    
    return result


def safe_get(data: Union[Dict, List], key_path: str, default: Any = None) -> Any:
    """
    Safely get a nested value from a dictionary or list using dot notation.
    
    Args:
        data: Dictionary or list to traverse
        key_path: Dot-separated path (e.g., "user.profile.name" or "items.0.id")
        default: Default value if path not found
        
    Returns:
        Value at the specified path or default
    """
    try:
        keys = key_path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list):
                index = int(key)
                current = current[index]
            else:
                return default
        
        return current
        
    except (KeyError, IndexError, ValueError, TypeError):
        return default


def flatten_dict(data: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """
    Flatten a nested dictionary.
    
    Args:
        data: Dictionary to flatten
        parent_key: Parent key for recursion
        sep: Separator for keys
        
    Returns:
        Flattened dictionary
    """
    items = []
    
    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep).items())
        else:
            items.append((new_key, value))
    
    return dict(items)


def unflatten_dict(data: Dict[str, Any], sep: str = '.') -> Dict[str, Any]:
    """
    Unflatten a dictionary with dot-separated keys.
    
    Args:
        data: Flattened dictionary
        sep: Separator used in keys
        
    Returns:
        Nested dictionary
    """
    result = {}
    
    for key, value in data.items():
        keys = key.split(sep)
        current = result
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    return result


def validate_id(entity_id: str) -> bool:
    """
    Validate an entity ID format.
    
    Args:
        entity_id: ID to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not entity_id or not isinstance(entity_id, str):
        return False
    
    # Basic validation - ID should not be empty and should not contain problematic characters
    invalid_chars = [' ', '\n', '\t', '\r']
    return not any(char in entity_id for char in invalid_chars)


def sanitize_string(text: str, max_length: int = 1000) -> str:
    """
    Sanitize a string for safe storage and display.
    
    Args:
        text: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(text, str):
        text = str(text)
    
    # Remove control characters and limit length
    sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    return sanitized[:max_length] if len(sanitized) > max_length else sanitized


def calculate_metrics(values: List[Union[int, float]]) -> Dict[str, float]:
    """
    Calculate basic statistical metrics for a list of values.
    
    Args:
        values: List of numeric values
        
    Returns:
        Dictionary with metrics (mean, median, std, min, max)
    """
    if not values:
        return {'mean': 0.0, 'median': 0.0, 'std': 0.0, 'min': 0.0, 'max': 0.0}
    
    try:
        sorted_values = sorted(values)
        n = len(values)
        
        # Mean
        mean = sum(values) / n
        
        # Median
        if n % 2 == 0:
            median = (sorted_values[n//2 - 1] + sorted_values[n//2]) / 2
        else:
            median = sorted_values[n//2]
        
        # Standard deviation
        variance = sum((x - mean) ** 2 for x in values) / n
        std = variance ** 0.5
        
        return {
            'mean': mean,
            'median': median,
            'std': std,
            'min': min(values),
            'max': max(values),
            'count': n
        }
        
    except Exception:
        return {'mean': 0.0, 'median': 0.0, 'std': 0.0, 'min': 0.0, 'max': 0.0, 'count': 0}


def chunk_list(data: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split a list into chunks of specified size.
    
    Args:
        data: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    if chunk_size <= 0:
        return [data]
    
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison and searching.
    
    Args:
        text: Text to normalize
        
    Returns:
        Normalized text
    """
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase and strip whitespace
    normalized = text.lower().strip()
    
    # Replace multiple whitespace with single space
    import re
    normalized = re.sub(r'\s+', ' ', normalized)
    
    return normalized 