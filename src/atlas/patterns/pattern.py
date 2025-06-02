"""
Pattern class - Core pattern language implementation for ATLAS.

Patterns are subclasses of the Entity class, representing abstract phenomena
and objects which other Entity objects might instantiate or exemplify.
"""

import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import uuid

from ..entities.entity import Entity, EntityMetadata

logger = logging.getLogger(__name__)


class Pattern(Entity):
    """
    Pattern class representing abstract phenomena and objects.
    
    Patterns are subclasses of Entity that define abstract templates
    which other entities might instantiate or exemplify. They include
    QKits (question kits) and parent-child relationships.
    """
    
    def __init__(
        self,
        pattern_id: Optional[str] = None,
        qkit: Optional[List[str]] = None,
        parents: Optional[List[str]] = None,
        children: Optional[List[str]] = None,
        attributes: Optional[Dict[str, Any]] = None,
        patterns: Optional[List[str]] = None,
        metadata: Optional[EntityMetadata] = None
    ):
        """
        Initialize a Pattern.
        
        Args:
            pattern_id: Unique identifier for the pattern
            qkit: List of iQuery references representing expected questions
            parents: List of parent pattern IDs
            children: List of child pattern IDs
            attributes: Additional pattern attributes
            patterns: List of pattern IDs this pattern conforms to
            metadata: Entity metadata for tracking and provenance
        """
        # Initialize parent Entity
        super().__init__(
            entity_id=pattern_id,
            attributes=attributes,
            patterns=patterns,
            metadata=metadata
        )
        
        # Pattern-specific properties
        self.qkit: List[str] = qkit or []  # iQuery references
        self.parents: List[str] = parents or []  # Parent patterns
        self.children: List[str] = children or []  # Child patterns
        
        # Pattern usage tracking
        self.instances: Set[str] = set()  # Entities that instantiate this pattern
        self.derivations: Set[str] = set()  # Patterns derived from this one
        
        # Pattern metrics
        self.usage_count: int = 0
        self.effectiveness_score: Optional[float] = None
        
        logger.info(f"Created pattern: {self.id}")
    
    def add_qkit_item(self, iquery_id: str) -> bool:
        """
        Add an iQuery to the pattern's QKit.
        
        Args:
            iquery_id: The iQuery identifier to add
            
        Returns:
            True if iQuery was added, False if already exists
        """
        try:
            if iquery_id not in self.qkit:
                self.qkit.append(iquery_id)
                self.metadata.updated_at = datetime.now()
                self.metadata.version += 1
                logger.debug(f"Added iQuery {iquery_id} to pattern {self.id} QKit")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to add iQuery to pattern {self.id} QKit: {e}")
            return False
    
    def remove_qkit_item(self, iquery_id: str) -> bool:
        """Remove an iQuery from the pattern's QKit."""
        try:
            if iquery_id in self.qkit:
                self.qkit.remove(iquery_id)
                self.metadata.updated_at = datetime.now()
                self.metadata.version += 1
                logger.debug(f"Removed iQuery {iquery_id} from pattern {self.id} QKit")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove iQuery from pattern {self.id} QKit: {e}")
            return False
    
    def add_parent(self, parent_id: str) -> bool:
        """
        Add a parent pattern.
        
        Args:
            parent_id: The parent pattern identifier
            
        Returns:
            True if parent was added, False if already exists
        """
        try:
            if parent_id not in self.parents:
                self.parents.append(parent_id)
                self.metadata.updated_at = datetime.now()
                self.metadata.version += 1
                logger.debug(f"Added parent {parent_id} to pattern {self.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to add parent to pattern {self.id}: {e}")
            return False
    
    def remove_parent(self, parent_id: str) -> bool:
        """Remove a parent pattern."""
        try:
            if parent_id in self.parents:
                self.parents.remove(parent_id)
                self.metadata.updated_at = datetime.now()
                self.metadata.version += 1
                logger.debug(f"Removed parent {parent_id} from pattern {self.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove parent from pattern {self.id}: {e}")
            return False
    
    def add_child(self, child_id: str) -> bool:
        """
        Add a child pattern.
        
        Args:
            child_id: The child pattern identifier
            
        Returns:
            True if child was added, False if already exists
        """
        try:
            if child_id not in self.children:
                self.children.append(child_id)
                self.metadata.updated_at = datetime.now()
                self.metadata.version += 1
                logger.debug(f"Added child {child_id} to pattern {self.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to add child to pattern {self.id}: {e}")
            return False
    
    def remove_child(self, child_id: str) -> bool:
        """Remove a child pattern."""
        try:
            if child_id in self.children:
                self.children.remove(child_id)
                self.metadata.updated_at = datetime.now()
                self.metadata.version += 1
                logger.debug(f"Removed child {child_id} from pattern {self.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove child from pattern {self.id}: {e}")
            return False
    
    def add_instance(self, entity_id: str) -> bool:
        """
        Register an entity as an instance of this pattern.
        
        Args:
            entity_id: The entity that instantiates this pattern
            
        Returns:
            True if instance was registered
        """
        try:
            if entity_id not in self.instances:
                self.instances.add(entity_id)
                self.usage_count += 1
                logger.debug(f"Registered entity {entity_id} as instance of pattern {self.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to register instance for pattern {self.id}: {e}")
            return False
    
    def remove_instance(self, entity_id: str) -> bool:
        """Unregister an entity as an instance of this pattern."""
        try:
            if entity_id in self.instances:
                self.instances.remove(entity_id)
                self.usage_count = max(0, self.usage_count - 1)
                logger.debug(f"Unregistered entity {entity_id} from pattern {self.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to unregister instance for pattern {self.id}: {e}")
            return False
    
    def add_derivation(self, pattern_id: str) -> bool:
        """
        Register another pattern as derived from this one.
        
        Args:
            pattern_id: The derived pattern identifier
            
        Returns:
            True if derivation was registered
        """
        try:
            if pattern_id not in self.derivations:
                self.derivations.add(pattern_id)
                logger.debug(f"Registered pattern {pattern_id} as derivation of {self.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to register derivation for pattern {self.id}: {e}")
            return False
    
    def get_all_ancestors(self) -> Set[str]:
        """
        Get all ancestor patterns (recursive parent traversal).
        Note: This method would require access to the pattern registry
        for full implementation. Currently returns immediate parents.
        """
        return set(self.parents)
    
    def get_all_descendants(self) -> Set[str]:
        """
        Get all descendant patterns (recursive child traversal).
        Note: This method would require access to the pattern registry
        for full implementation. Currently returns immediate children.
        """
        return set(self.children)
    
    def is_ancestor_of(self, pattern_id: str) -> bool:
        """Check if this pattern is an ancestor of another pattern."""
        return pattern_id in self.get_all_descendants()
    
    def is_descendant_of(self, pattern_id: str) -> bool:
        """Check if this pattern is a descendant of another pattern."""
        return pattern_id in self.get_all_ancestors()
    
    def calculate_effectiveness_score(self) -> float:
        """
        Calculate effectiveness score based on usage and feedback.
        
        Returns:
            Effectiveness score between 0.0 and 1.0
        """
        try:
            # Simple effectiveness calculation - can be enhanced
            base_score = min(self.usage_count / 100.0, 0.6)  # Usage component
            instance_score = min(len(self.instances) / 50.0, 0.3)  # Instance diversity
            derivation_score = min(len(self.derivations) / 10.0, 0.1)  # Derivation utility
            
            self.effectiveness_score = base_score + instance_score + derivation_score
            return self.effectiveness_score
            
        except Exception as e:
            logger.error(f"Failed to calculate effectiveness score for pattern {self.id}: {e}")
            return 0.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get usage and effectiveness statistics for this pattern."""
        return {
            'usage_count': self.usage_count,
            'instance_count': len(self.instances),
            'derivation_count': len(self.derivations),
            'qkit_size': len(self.qkit),
            'parent_count': len(self.parents),
            'child_count': len(self.children),
            'effectiveness_score': self.effectiveness_score or self.calculate_effectiveness_score()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pattern to dictionary representation."""
        base_dict = super().to_dict()
        base_dict.update({
            'qkit': self.qkit,
            'parents': self.parents,
            'children': self.children,
            'instances': list(self.instances),
            'derivations': list(self.derivations),
            'usage_count': self.usage_count,
            'effectiveness_score': self.effectiveness_score,
            'statistics': self.get_statistics()
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Pattern':
        """Create pattern from dictionary representation."""
        # Extract base entity data
        metadata = EntityMetadata(
            created_at=datetime.fromisoformat(data['metadata']['created_at']),
            updated_at=datetime.fromisoformat(data['metadata']['updated_at']),
            version=data['metadata']['version'],
            source=data['metadata']['source'],
            quality_score=data['metadata']['quality_score'],
            tags=set(data['metadata']['tags'])
        )
        
        # Create pattern
        pattern = cls(
            pattern_id=data['id'],
            qkit=data['qkit'],
            parents=data['parents'],
            children=data['children'],
            attributes=data['attributes'],
            patterns=data['patterns'],
            metadata=metadata
        )
        
        # Restore pattern-specific data
        pattern.instances = set(data.get('instances', []))
        pattern.derivations = set(data.get('derivations', []))
        pattern.usage_count = data.get('usage_count', 0)
        pattern.effectiveness_score = data.get('effectiveness_score')
        
        # Restore entity-specific data
        pattern._anomalies = data.get('anomalies', {})
        pattern._exceptions = data.get('exceptions', {})
        pattern._pending_rfis = set(data.get('pending_rfis', []))
        
        return pattern
    
    def __str__(self) -> str:
        return (f"Pattern(id='{self.id}', qkit={len(self.qkit)}, "
                f"parents={len(self.parents)}, children={len(self.children)})")
    
    def __repr__(self) -> str:
        return (f"Pattern(id='{self.id}', qkit={self.qkit}, parents={self.parents}, "
                f"children={self.children}, instances={len(self.instances)})") 