"""
iQuery class - Itemized query management for ATLAS.

The iQuery class manages and facilitates the resolution of requests
for information and leverages the latent information in such requests.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Callable
from datetime import datetime
import uuid
from enum import Enum

logger = logging.getLogger(__name__)


class QueryStatus(Enum):
    """Status of an iQuery."""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QueryPriority(Enum):
    """Priority levels for query execution."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


class iQuery:
    """
    Itemized query class for managing information requests.
    
    iQueries manage and facilitate the resolution of requests for
    information and leverage the latent information in such requests
    through dynamic typing and prompt interfaces.
    """
    
    def __init__(
        self,
        query_id: Optional[str] = None,
        ref_id: Optional[str] = None,
        query_text: Optional[str] = None,
        prompts: Optional[List[str]] = None,
        target_patterns: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
        priority: QueryPriority = QueryPriority.NORMAL
    ):
        """
        Initialize an iQuery.
        
        Args:
            query_id: Unique identifier for the query
            ref_id: Reference ID for cross-system linking
            query_text: The actual query text or description
            prompts: List of prompt interface IDs to use
            target_patterns: Patterns this query is expected to reveal
            context: Additional context for query execution
            priority: Priority level for execution
        """
        self.id = query_id or str(uuid.uuid4())
        self.ref_id = ref_id or str(uuid.uuid4())
        self.query_text = query_text or ""
        self.prompts: List[str] = prompts or []
        self.target_patterns: List[str] = target_patterns or []
        self.context: Dict[str, Any] = context or {}
        self.priority = priority
        
        # Query execution state
        self.status = QueryStatus.PENDING
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error_message: Optional[str] = None
        
        # Results and responses
        self.results: List[Dict[str, Any]] = []
        self.response_entities: Set[str] = set()
        self.derived_patterns: Set[str] = set()
        
        # Query metadata
        self.execution_time: Optional[float] = None
        self.quality_score: Optional[float] = None
        self.confidence_score: Optional[float] = None
        
        logger.info(f"Created iQuery: {self.id}")
    
    def add_prompt(self, prompt_id: str) -> bool:
        """
        Add a prompt interface to this query.
        
        Args:
            prompt_id: The prompt interface identifier
            
        Returns:
            True if prompt was added, False if already exists
        """
        try:
            if prompt_id not in self.prompts:
                self.prompts.append(prompt_id)
                logger.debug(f"Added prompt {prompt_id} to iQuery {self.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to add prompt to iQuery {self.id}: {e}")
            return False
    
    def remove_prompt(self, prompt_id: str) -> bool:
        """Remove a prompt interface from this query."""
        try:
            if prompt_id in self.prompts:
                self.prompts.remove(prompt_id)
                logger.debug(f"Removed prompt {prompt_id} from iQuery {self.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove prompt from iQuery {self.id}: {e}")
            return False
    
    def add_target_pattern(self, pattern_id: str) -> bool:
        """
        Add a target pattern that this query is expected to reveal.
        
        Args:
            pattern_id: The pattern identifier
            
        Returns:
            True if pattern was added, False if already exists
        """
        try:
            if pattern_id not in self.target_patterns:
                self.target_patterns.append(pattern_id)
                logger.debug(f"Added target pattern {pattern_id} to iQuery {self.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to add target pattern to iQuery {self.id}: {e}")
            return False
    
    def set_context(self, key: str, value: Any) -> None:
        """Set a context variable for this query."""
        self.context[key] = value
        logger.debug(f"Set context {key} for iQuery {self.id}")
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context variable value."""
        return self.context.get(key, default)
    
    def start_execution(self) -> bool:
        """Mark the query as started."""
        try:
            if self.status == QueryStatus.PENDING:
                self.status = QueryStatus.EXECUTING
                self.started_at = datetime.now()
                logger.info(f"Started execution of iQuery {self.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to start iQuery {self.id}: {e}")
            return False
    
    def complete_execution(self, results: Optional[List[Dict[str, Any]]] = None) -> bool:
        """
        Mark the query as completed with optional results.
        
        Args:
            results: Optional results to add to the query
            
        Returns:
            True if query was completed successfully
        """
        try:
            if self.status == QueryStatus.EXECUTING:
                self.status = QueryStatus.COMPLETED
                self.completed_at = datetime.now()
                
                if self.started_at:
                    self.execution_time = (self.completed_at - self.started_at).total_seconds()
                
                if results:
                    self.results.extend(results)
                
                logger.info(f"Completed iQuery {self.id} in {self.execution_time}s")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to complete iQuery {self.id}: {e}")
            return False
    
    def fail_execution(self, error_message: str) -> bool:
        """
        Mark the query as failed with an error message.
        
        Args:
            error_message: Description of the failure
            
        Returns:
            True if query was marked as failed
        """
        try:
            self.status = QueryStatus.FAILED
            self.error_message = error_message
            self.completed_at = datetime.now()
            
            if self.started_at:
                self.execution_time = (self.completed_at - self.started_at).total_seconds()
            
            logger.error(f"iQuery {self.id} failed: {error_message}")
            return True
        except Exception as e:
            logger.error(f"Failed to mark iQuery {self.id} as failed: {e}")
            return False
    
    def cancel_execution(self) -> bool:
        """Cancel the query execution."""
        try:
            if self.status in [QueryStatus.PENDING, QueryStatus.EXECUTING]:
                self.status = QueryStatus.CANCELLED
                self.completed_at = datetime.now()
                
                if self.started_at:
                    self.execution_time = (self.completed_at - self.started_at).total_seconds()
                
                logger.info(f"Cancelled iQuery {self.id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to cancel iQuery {self.id}: {e}")
            return False
    
    def add_result(self, result: Dict[str, Any]) -> bool:
        """
        Add a result to this query.
        
        Args:
            result: Result data to add
            
        Returns:
            True if result was added successfully
        """
        try:
            self.results.append(result)
            
            # Extract entity IDs from results if present
            if 'entity_id' in result:
                self.response_entities.add(result['entity_id'])
            
            # Extract derived patterns if present
            if 'derived_patterns' in result:
                self.derived_patterns.update(result['derived_patterns'])
            
            logger.debug(f"Added result to iQuery {self.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add result to iQuery {self.id}: {e}")
            return False
    
    def clear_results(self) -> None:
        """Clear all results from this query."""
        self.results.clear()
        self.response_entities.clear()
        self.derived_patterns.clear()
        logger.debug(f"Cleared results for iQuery {self.id}")
    
    def calculate_quality_score(self) -> float:
        """
        Calculate quality score based on results and execution.
        
        Returns:
            Quality score between 0.0 and 1.0
        """
        try:
            if not self.results:
                return 0.0
            
            # Simple quality calculation - can be enhanced
            result_count_score = min(len(self.results) / 10.0, 0.4)
            entity_diversity_score = min(len(self.response_entities) / 5.0, 0.3)
            pattern_discovery_score = min(len(self.derived_patterns) / 3.0, 0.2)
            execution_efficiency_score = 0.1 if self.execution_time and self.execution_time < 5.0 else 0.0
            
            self.quality_score = (result_count_score + entity_diversity_score + 
                                pattern_discovery_score + execution_efficiency_score)
            return self.quality_score
            
        except Exception as e:
            logger.error(f"Failed to calculate quality score for iQuery {self.id}: {e}")
            return 0.0
    
    def calculate_confidence_score(self) -> float:
        """
        Calculate confidence score based on result consistency.
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        try:
            if not self.results:
                return 0.0
            
            # Simple confidence calculation - can be enhanced
            # This would typically involve checking result consistency,
            # source reliability, and validation against known patterns
            
            base_confidence = 0.5  # Default baseline
            result_consistency = 0.3 if len(self.results) > 1 else 0.1
            pattern_alignment = 0.2 if self.derived_patterns else 0.0
            
            self.confidence_score = base_confidence + result_consistency + pattern_alignment
            return min(self.confidence_score, 1.0)
            
        except Exception as e:
            logger.error(f"Failed to calculate confidence score for iQuery {self.id}: {e}")
            return 0.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get execution and performance statistics."""
        return {
            'status': self.status.value,
            'execution_time': self.execution_time,
            'result_count': len(self.results),
            'response_entity_count': len(self.response_entities),
            'derived_pattern_count': len(self.derived_patterns),
            'quality_score': self.quality_score or self.calculate_quality_score(),
            'confidence_score': self.confidence_score or self.calculate_confidence_score(),
            'priority': self.priority.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert iQuery to dictionary representation."""
        return {
            'id': self.id,
            'ref_id': self.ref_id,
            'query_text': self.query_text,
            'prompts': self.prompts,
            'target_patterns': self.target_patterns,
            'context': self.context,
            'priority': self.priority.value,
            'status': self.status.value,
            'results': self.results,
            'response_entities': list(self.response_entities),
            'derived_patterns': list(self.derived_patterns),
            'error_message': self.error_message,
            'statistics': self.get_statistics()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'iQuery':
        """Create iQuery from dictionary representation."""
        query = cls(
            query_id=data['id'],
            ref_id=data['ref_id'],
            query_text=data['query_text'],
            prompts=data['prompts'],
            target_patterns=data['target_patterns'],
            context=data['context'],
            priority=QueryPriority(data['priority'])
        )
        
        # Restore execution state
        query.status = QueryStatus(data['status'])
        query.results = data.get('results', [])
        query.response_entities = set(data.get('response_entities', []))
        query.derived_patterns = set(data.get('derived_patterns', []))
        query.error_message = data.get('error_message')
        
        # Restore timestamps if present in statistics
        stats = data.get('statistics', {})
        if stats.get('created_at'):
            query.created_at = datetime.fromisoformat(stats['created_at'])
        if stats.get('started_at'):
            query.started_at = datetime.fromisoformat(stats['started_at'])
        if stats.get('completed_at'):
            query.completed_at = datetime.fromisoformat(stats['completed_at'])
        
        query.execution_time = stats.get('execution_time')
        query.quality_score = stats.get('quality_score')
        query.confidence_score = stats.get('confidence_score')
        
        return query
    
    def __str__(self) -> str:
        return f"iQuery(id='{self.id}', status={self.status.value}, results={len(self.results)})"
    
    def __repr__(self) -> str:
        return (f"iQuery(id='{self.id}', query_text='{self.query_text}', "
                f"status={self.status.value}, prompts={len(self.prompts)})") 