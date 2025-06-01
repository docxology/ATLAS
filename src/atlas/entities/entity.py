"""
Entity class - Core object in the ATLAS system.

Entities are the fundamental objects within the ATLAS system.
They can represent any identifiable object and are assigned attributes and patterns.
"""

import logging
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


@dataclass
class EntityMetadata:
    """Metadata for entity tracking and provenance."""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: int = 1
    source: Optional[str] = None
    quality_score: Optional[float] = None
    tags: Set[str] = field(default_factory=set)


class Entity:
    """
    Fundamental object within the ATLAS system.
    
    Entities can represent any identifiable object and are assigned
    attributes and patterns. They support dynamic typing through
    pattern assignment and flexible attribute management.
    """
    
    def __init__(
        self,
        entity_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        patterns: Optional[List[str]] = None,
        metadata: Optional[EntityMetadata] = None
    ):
        """
        Initialize an Entity.
        
        Args:
            entity_id: Unique identifier for the entity
            attributes: Dictionary of entity attributes
            patterns: List of pattern IDs this entity conforms to
            metadata: Entity metadata for tracking and provenance
        """
        self.id = entity_id or str(uuid.uuid4())
        self.attributes: Dict[str, Any] = attributes or {}
        self.patterns: List[str] = patterns or []
        self.metadata = metadata or EntityMetadata()
        
        # Internal tracking
        self._anomalies: Dict[str, str] = {}  # iQuery ID -> reason
        self._exceptions: Dict[str, str] = {}  # iQuery ID -> reason
        self._pending_rfis: Set[str] = set()  # Pending requests for information
        
        logger.info(f"Created entity: {self.id}")
    
    def add_attribute(self, key: str, value: Any, overwrite: bool = True) -> bool:
        """
        Add or update an attribute.
        
        Args:
            key: Attribute key
            value: Attribute value
            overwrite: Whether to overwrite existing attributes
            
        Returns:
            True if attribute was added/updated, False otherwise
        """
        try:
            if key in self.attributes and not overwrite:
                logger.warning(f"Attribute {key} already exists for entity {self.id}")
                return False
            
            self.attributes[key] = value
            self.metadata.updated_at = datetime.now()
            self.metadata.version += 1
            
            logger.debug(f"Added attribute {key} to entity {self.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add attribute {key} to entity {self.id}: {e}")
            return False
    
    def remove_attribute(self, key: str) -> bool:
        """Remove an attribute."""
        try:
            if key in self.attributes:
                del self.attributes[key]
                self.metadata.updated_at = datetime.now()
                self.metadata.version += 1
                logger.debug(f"Removed attribute {key} from entity {self.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove attribute {key} from entity {self.id}: {e}")
            return False
    
    def get_attribute(self, key: str, default: Any = None) -> Any:
        """Get an attribute value."""
        return self.attributes.get(key, default)
    
    def has_attribute(self, key: str) -> bool:
        """Check if entity has an attribute."""
        return key in self.attributes
    
    def add_pattern(self, pattern_id: str) -> bool:
        """
        Add a pattern to this entity.
        
        Args:
            pattern_id: Pattern identifier to add
            
        Returns:
            True if pattern was added, False if already exists
        """
        try:
            if pattern_id not in self.patterns:
                self.patterns.append(pattern_id)
                self.metadata.updated_at = datetime.now()
                self.metadata.version += 1
                logger.debug(f"Added pattern {pattern_id} to entity {self.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to add pattern {pattern_id} to entity {self.id}: {e}")
            return False
    
    def remove_pattern(self, pattern_id: str) -> bool:
        """Remove a pattern from this entity."""
        try:
            if pattern_id in self.patterns:
                self.patterns.remove(pattern_id)
                self.metadata.updated_at = datetime.now()
                self.metadata.version += 1
                logger.debug(f"Removed pattern {pattern_id} from entity {self.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove pattern {pattern_id} from entity {self.id}: {e}")
            return False
    
    def has_pattern(self, pattern_id: str) -> bool:
        """Check if entity has a specific pattern."""
        return pattern_id in self.patterns
    
    def mark_anomaly(self, iquery_id: str, reason: str = "") -> None:
        """
        Mark the entity as an anomaly to a specific iQuery.
        
        Args:
            iquery_id: The iQuery ID this entity is anomalous to
            reason: Optional reason for the anomaly
        """
        self._anomalies[iquery_id] = reason
        logger.info(f"Marked entity {self.id} as anomaly for iQuery {iquery_id}: {reason}")
    
    def mark_exception(self, iquery_id: str, reason: str = "") -> None:
        """
        Mark the entity as an exception in relation to a specific iQuery.
        
        Args:
            iquery_id: The iQuery ID this entity is an exception to
            reason: Optional reason for the exception
        """
        self._exceptions[iquery_id] = reason
        logger.info(f"Marked entity {self.id} as exception for iQuery {iquery_id}: {reason}")
    
    def call_rfis(self) -> Set[str]:
        """
        Call open requests for information from entity attributes with no values.
        
        Returns:
            Set of RFI identifiers that were called
        """
        rfis_called = set()
        
        # Find attributes with None or empty values
        for key, value in self.attributes.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                rfi_id = f"rfi_{self.id}_{key}_{uuid.uuid4().hex[:8]}"
                self._pending_rfis.add(rfi_id)
                rfis_called.add(rfi_id)
                logger.info(f"Called RFI {rfi_id} for attribute {key} of entity {self.id}")
        
        return rfis_called
    
    def resolve_rfi(self, rfi_id: str, value: Any) -> bool:
        """
        Resolve a pending RFI with a value.
        
        Args:
            rfi_id: The RFI identifier to resolve
            value: The value to set
            
        Returns:
            True if RFI was resolved, False otherwise
        """
        try:
            if rfi_id in self._pending_rfis:
                # Extract attribute key from RFI ID (assumes format rfi_{entity_id}_{attr_key}_{uuid})
                parts = rfi_id.split('_')
                if len(parts) >= 4:
                    attr_key = parts[2]
                    self.add_attribute(attr_key, value)
                    self._pending_rfis.remove(rfi_id)
                    logger.info(f"Resolved RFI {rfi_id} for entity {self.id}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to resolve RFI {rfi_id} for entity {self.id}: {e}")
            return False
    
    def get_anomalies(self) -> Dict[str, str]:
        """Get all anomalies marked for this entity."""
        return self._anomalies.copy()
    
    def get_exceptions(self) -> Dict[str, str]:
        """Get all exceptions marked for this entity."""
        return self._exceptions.copy()
    
    def get_pending_rfis(self) -> Set[str]:
        """Get all pending RFIs for this entity."""
        return self._pending_rfis.copy()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary representation."""
        return {
            'id': self.id,
            'attributes': self.attributes,
            'patterns': self.patterns,
            'metadata': {
                'created_at': self.metadata.created_at.isoformat(),
                'updated_at': self.metadata.updated_at.isoformat(),
                'version': self.metadata.version,
                'source': self.metadata.source,
                'quality_score': self.metadata.quality_score,
                'tags': list(self.metadata.tags)
            },
            'anomalies': self._anomalies,
            'exceptions': self._exceptions,
            'pending_rfis': list(self._pending_rfis)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Entity':
        """Create entity from dictionary representation."""
        metadata = EntityMetadata(
            created_at=datetime.fromisoformat(data['metadata']['created_at']),
            updated_at=datetime.fromisoformat(data['metadata']['updated_at']),
            version=data['metadata']['version'],
            source=data['metadata']['source'],
            quality_score=data['metadata']['quality_score'],
            tags=set(data['metadata']['tags'])
        )
        
        entity = cls(
            entity_id=data['id'],
            attributes=data['attributes'],
            patterns=data['patterns'],
            metadata=metadata
        )
        
        entity._anomalies = data.get('anomalies', {})
        entity._exceptions = data.get('exceptions', {})
        entity._pending_rfis = set(data.get('pending_rfis', []))
        
        return entity
    
    def __str__(self) -> str:
        return f"Entity(id='{self.id}', patterns={self.patterns}, attributes={len(self.attributes)})"
    
    def __repr__(self) -> str:
        return f"Entity(id='{self.id}', attributes={self.attributes}, patterns={self.patterns})" 