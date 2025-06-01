"""
Attribute class - Specialized entity for managing attribute metadata.

Attributes within the ATLAS system are extensions of the Entity class,
carrying Reference IDs and their own attributes and patterns.
"""

import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import uuid

from .entity import Entity, EntityMetadata

logger = logging.getLogger(__name__)


class Attribute(Entity):
    """
    Attribute class extending Entity with reference ID management.
    
    Attributes can be shared between systems and linked via common
    Reference IDs despite differing ontology or split despite
    overlaps in ontology.
    """
    
    def __init__(
        self,
        attribute_id: Optional[str] = None,
        ref_id: Optional[str] = None,
        value: Any = None,
        data_type: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        patterns: Optional[List[str]] = None,
        metadata: Optional[EntityMetadata] = None
    ):
        """
        Initialize an Attribute.
        
        Args:
            attribute_id: Unique identifier for the attribute
            ref_id: Reference ID for cross-system linking
            value: The attribute value
            data_type: Type of the attribute value
            attributes: Additional metadata attributes
            patterns: List of pattern IDs this attribute conforms to
            metadata: Entity metadata for tracking and provenance
        """
        # Initialize parent Entity
        super().__init__(
            entity_id=attribute_id,
            attributes=attributes,
            patterns=patterns,
            metadata=metadata
        )
        
        # Attribute-specific properties
        self.ref_id = ref_id or str(uuid.uuid4())
        self.value = value
        self.data_type = data_type or self._infer_data_type(value)
        
        # Additional attribute metadata
        self.validation_rules: Dict[str, Any] = {}
        self.transformation_history: List[Dict[str, Any]] = []
        self.linked_attributes: Set[str] = set()  # Related attribute IDs
        
        logger.info(f"Created attribute: {self.id} with ref_id: {self.ref_id}")
    
    def _infer_data_type(self, value: Any) -> str:
        """Infer data type from value."""
        if value is None:
            return "null"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, str):
            return "string"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        else:
            return "unknown"
    
    def set_value(self, new_value: Any, track_history: bool = True) -> bool:
        """
        Set a new value for the attribute.
        
        Args:
            new_value: The new value to set
            track_history: Whether to track the value change in history
            
        Returns:
            True if value was set successfully, False otherwise
        """
        try:
            old_value = self.value
            old_type = self.data_type
            
            # Apply validation rules if any
            if not self._validate_value(new_value):
                logger.warning(f"Value validation failed for attribute {self.id}")
                return False
            
            # Track transformation history
            if track_history and old_value != new_value:
                self.transformation_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'old_value': old_value,
                    'new_value': new_value,
                    'old_type': old_type,
                    'new_type': self._infer_data_type(new_value)
                })
            
            # Set new value and type
            self.value = new_value
            self.data_type = self._infer_data_type(new_value)
            
            # Update metadata
            self.metadata.updated_at = datetime.now()
            self.metadata.version += 1
            
            logger.debug(f"Updated value for attribute {self.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set value for attribute {self.id}: {e}")
            return False
    
    def _validate_value(self, value: Any) -> bool:
        """
        Validate a value against defined validation rules.
        
        Args:
            value: The value to validate
            
        Returns:
            True if value is valid, False otherwise
        """
        try:
            for rule_name, rule_config in self.validation_rules.items():
                if not self._apply_validation_rule(value, rule_name, rule_config):
                    logger.warning(f"Validation rule '{rule_name}' failed for attribute {self.id}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Validation error for attribute {self.id}: {e}")
            return False
    
    def _apply_validation_rule(self, value: Any, rule_name: str, rule_config: Dict[str, Any]) -> bool:
        """Apply a specific validation rule."""
        try:
            if rule_name == "type":
                expected_type = rule_config.get("expected")
                return self._infer_data_type(value) == expected_type
            
            elif rule_name == "range":
                if isinstance(value, (int, float)):
                    min_val = rule_config.get("min")
                    max_val = rule_config.get("max")
                    if min_val is not None and value < min_val:
                        return False
                    if max_val is not None and value > max_val:
                        return False
                return True
            
            elif rule_name == "length":
                if isinstance(value, (str, list, dict)):
                    min_len = rule_config.get("min")
                    max_len = rule_config.get("max")
                    length = len(value)
                    if min_len is not None and length < min_len:
                        return False
                    if max_len is not None and length > max_len:
                        return False
                return True
            
            elif rule_name == "pattern":
                if isinstance(value, str):
                    import re
                    pattern = rule_config.get("regex")
                    if pattern is not None:
                        return re.match(pattern, value) is not None
                return True
            
            elif rule_name == "enum":
                allowed_values = rule_config.get("values", [])
                return value in allowed_values
            
            # Default: rule passes
            return True
            
        except Exception as e:
            logger.error(f"Error applying validation rule {rule_name}: {e}")
            return False
    
    def add_validation_rule(self, rule_name: str, rule_config: Dict[str, Any]) -> bool:
        """
        Add a validation rule for this attribute.
        
        Args:
            rule_name: Name of the validation rule
            rule_config: Configuration for the rule
            
        Returns:
            True if rule was added successfully
        """
        try:
            self.validation_rules[rule_name] = rule_config
            logger.debug(f"Added validation rule '{rule_name}' to attribute {self.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add validation rule to attribute {self.id}: {e}")
            return False
    
    def remove_validation_rule(self, rule_name: str) -> bool:
        """Remove a validation rule."""
        try:
            if rule_name in self.validation_rules:
                del self.validation_rules[rule_name]
                logger.debug(f"Removed validation rule '{rule_name}' from attribute {self.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove validation rule from attribute {self.id}: {e}")
            return False
    
    def link_attribute(self, attribute_id: str) -> bool:
        """
        Link this attribute to another attribute.
        
        Args:
            attribute_id: ID of the attribute to link to
            
        Returns:
            True if link was established, False if already linked
        """
        try:
            if attribute_id in self.linked_attributes:
                logger.debug(f"Attribute {attribute_id} already linked to {self.id}")
                return False  # Already linked
            
            self.linked_attributes.add(attribute_id)
            logger.debug(f"Linked attribute {self.id} to {attribute_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to link attribute {self.id} to {attribute_id}: {e}")
            return False
    
    def unlink_attribute(self, attribute_id: str) -> bool:
        """Unlink this attribute from another attribute."""
        try:
            if attribute_id in self.linked_attributes:
                self.linked_attributes.remove(attribute_id)
                logger.debug(f"Unlinked attribute {self.id} from {attribute_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to unlink attribute {self.id} from {attribute_id}: {e}")
            return False
    
    def get_transformation_history(self) -> List[Dict[str, Any]]:
        """Get the complete transformation history."""
        return self.transformation_history.copy()
    
    def clear_transformation_history(self) -> None:
        """Clear the transformation history."""
        self.transformation_history.clear()
        logger.debug(f"Cleared transformation history for attribute {self.id}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert attribute to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            'ref_id': self.ref_id,
            'value': self.value,
            'data_type': self.data_type,
            'validation_rules': self.validation_rules,
            'transformation_history': self.transformation_history,
            'linked_attributes': list(self.linked_attributes)
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Attribute':
        """Create attribute from dictionary representation."""
        # Extract base entity data
        metadata = EntityMetadata(
            created_at=datetime.fromisoformat(data['metadata']['created_at']),
            updated_at=datetime.fromisoformat(data['metadata']['updated_at']),
            version=data['metadata']['version'],
            source=data['metadata']['source'],
            quality_score=data['metadata']['quality_score'],
            tags=set(data['metadata']['tags'])
        )
        
        # Create attribute
        attribute = cls(
            attribute_id=data['id'],
            ref_id=data['ref_id'],
            value=data['value'],
            data_type=data['data_type'],
            attributes=data['attributes'],
            patterns=data['patterns'],
            metadata=metadata
        )
        
        # Restore attribute-specific data
        attribute.validation_rules = data.get('validation_rules', {})
        attribute.transformation_history = data.get('transformation_history', [])
        attribute.linked_attributes = set(data.get('linked_attributes', []))
        
        # Restore entity-specific data
        attribute._anomalies = data.get('anomalies', {})
        attribute._exceptions = data.get('exceptions', {})
        attribute._pending_rfis = set(data.get('pending_rfis', []))
        
        return attribute
    
    def __str__(self) -> str:
        return f"Attribute(id='{self.id}', ref_id='{self.ref_id}', value={self.value}, type={self.data_type})"
    
    def __repr__(self) -> str:
        return (f"Attribute(id='{self.id}', ref_id='{self.ref_id}', value={self.value}, "
                f"data_type='{self.data_type}', patterns={self.patterns})") 