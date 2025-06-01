"""
PromptInterface class - System interoperability for ATLAS.

PromptInterfaces enable translation and data exchange between different
systems within the ATLAS framework without requiring shared standards.
"""

import logging
from typing import Dict, List, Any, Optional, Callable, Union
from abc import ABC, abstractmethod
import uuid

logger = logging.getLogger(__name__)


class PromptInterface(ABC):
    """
    Abstract base class for prompt interfaces in ATLAS.
    
    Prompt interfaces facilitate structured data exchange and can be
    used to request Entity objects of particular types from existing
    ATLAS instances or external systems.
    """
    
    def __init__(
        self,
        interface_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a PromptInterface.
        
        Args:
            interface_id: Unique identifier for the interface
            name: Human-readable name for the interface
            description: Description of what this interface does
            input_schema: Expected input data schema
            output_schema: Expected output data schema
        """
        self.id = interface_id or str(uuid.uuid4())
        self.name = name or f"PromptInterface_{self.id[:8]}"
        self.description = description or ""
        self.input_schema = input_schema or {}
        self.output_schema = output_schema or {}
        
        # Interface metadata
        self.usage_count = 0
        self.error_count = 0
        self.success_rate = 0.0
        
        logger.info(f"Created PromptInterface: {self.id}")
    
    @abstractmethod
    def transform(self, data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Transform input data according to the interface specification.
        
        Args:
            data: Input data to transform
            context: Optional context for transformation
            
        Returns:
            Transformed data according to output schema
        """
        pass
    
    @abstractmethod
    def validate_input(self, data: Any) -> bool:
        """
        Validate input data against the input schema.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def validate_output(self, data: Any) -> bool:
        """
        Validate output data against the output schema.
        
        Args:
            data: Data to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        pass
    
    def execute(self, data: Any, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the prompt interface with input data.
        
        Args:
            data: Input data
            context: Optional execution context
            
        Returns:
            Result dictionary with success status and transformed data or error
        """
        try:
            # Update usage metrics
            self.usage_count += 1
            
            # Validate input
            if not self.validate_input(data):
                self.error_count += 1
                return {
                    'success': False,
                    'error': 'Input validation failed',
                    'data': None
                }
            
            # Transform data
            result = self.transform(data, context)
            
            # Validate output
            if not self.validate_output(result):
                self.error_count += 1
                return {
                    'success': False,
                    'error': 'Output validation failed',
                    'data': None
                }
            
            # Update success rate
            self.success_rate = (self.usage_count - self.error_count) / self.usage_count
            
            return {
                'success': True,
                'error': None,
                'data': result
            }
            
        except Exception as e:
            self.error_count += 1
            self.success_rate = (self.usage_count - self.error_count) / self.usage_count
            logger.error(f"PromptInterface {self.id} execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get usage and performance statistics."""
        return {
            'usage_count': self.usage_count,
            'error_count': self.error_count,
            'success_rate': self.success_rate,
            'has_input_schema': bool(self.input_schema),
            'has_output_schema': bool(self.output_schema)
        }
    
    def __str__(self) -> str:
        return f"PromptInterface(id='{self.id}', name='{self.name}')"
    
    def __repr__(self) -> str:
        return f"PromptInterface(id='{self.id}', name='{self.name}', usage={self.usage_count})"


class SimpleTransformInterface(PromptInterface):
    """
    Simple implementation of PromptInterface with a transformation function.
    """
    
    def __init__(
        self,
        transform_func: Callable[[Any], Any],
        interface_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a SimpleTransformInterface.
        
        Args:
            transform_func: Function to transform input data
            interface_id: Unique identifier for the interface
            name: Human-readable name for the interface
            description: Description of what this interface does
            input_schema: Expected input data schema
            output_schema: Expected output data schema
        """
        super().__init__(interface_id, name, description, input_schema, output_schema)
        self.transform_func = transform_func
    
    def transform(self, data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """Transform data using the provided function."""
        return self.transform_func(data)
    
    def validate_input(self, data: Any) -> bool:
        """Basic input validation - always returns True unless schema is specified."""
        if not self.input_schema:
            return True
        # Simple type checking if schema specifies type
        expected_type = self.input_schema.get('type')
        if expected_type:
            return type(data).__name__ == expected_type
        return True
    
    def validate_output(self, data: Any) -> bool:
        """Basic output validation - always returns True unless schema is specified."""
        if not self.output_schema:
            return True
        # Simple type checking if schema specifies type
        expected_type = self.output_schema.get('type')
        if expected_type:
            return type(data).__name__ == expected_type
        return True


class HTTPPromptInterface(PromptInterface):
    """
    PromptInterface for HTTP-based data exchange.
    """
    
    def __init__(
        self,
        endpoint_url: str,
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        interface_id: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        input_schema: Optional[Dict[str, Any]] = None,
        output_schema: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an HTTPPromptInterface.
        
        Args:
            endpoint_url: URL for the HTTP endpoint
            method: HTTP method to use
            headers: Optional HTTP headers
            interface_id: Unique identifier for the interface
            name: Human-readable name for the interface
            description: Description of what this interface does
            input_schema: Expected input data schema
            output_schema: Expected output data schema
        """
        super().__init__(interface_id, name, description, input_schema, output_schema)
        self.endpoint_url = endpoint_url
        self.method = method.upper()
        self.headers = headers or {}
    
    def transform(self, data: Any, context: Optional[Dict[str, Any]] = None) -> Any:
        """Transform data via HTTP request."""
        try:
            import requests
            
            if self.method == "GET":
                response = requests.get(self.endpoint_url, params=data, headers=self.headers)
            elif self.method == "POST":
                response = requests.post(self.endpoint_url, json=data, headers=self.headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {self.method}")
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"HTTP request failed in interface {self.id}: {e}")
            raise
    
    def validate_input(self, data: Any) -> bool:
        """Validate input data for HTTP transmission."""
        try:
            import json
            # Check if data is JSON serializable
            json.dumps(data)
            return True
        except (TypeError, ValueError):
            return False
    
    def validate_output(self, data: Any) -> bool:
        """Basic output validation for HTTP responses."""
        # HTTP responses are typically dictionaries or lists
        return isinstance(data, (dict, list, str, int, float, bool))


# Factory functions for common interface patterns
def create_identity_interface(interface_id: Optional[str] = None) -> SimpleTransformInterface:
    """Create an identity transform interface (returns input unchanged)."""
    return SimpleTransformInterface(
        transform_func=lambda x: x,
        interface_id=interface_id,
        name="Identity Interface",
        description="Returns input data unchanged"
    )


def create_format_interface(
    format_func: Callable[[Any], str],
    interface_id: Optional[str] = None,
    name: Optional[str] = None
) -> SimpleTransformInterface:
    """Create a formatting interface."""
    return SimpleTransformInterface(
        transform_func=format_func,
        interface_id=interface_id,
        name=name or "Format Interface",
        description="Formats input data to string representation"
    ) 