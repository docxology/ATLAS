"""
ATLAS Engine - Core orchestration system for the ATLAS framework.

The ATLASEngine manages entities, patterns, queries, and provides the main
interface for interacting with the ATLAS knowledge management system.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Union
from dataclasses import dataclass, field
import networkx as nx
from collections import defaultdict
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ATLASConfig:
    """Configuration settings for ATLAS engine."""
    auto_pattern_inference: bool = True
    enable_dynamic_typing: bool = True
    max_expansion_depth: int = 10
    enable_quality_metrics: bool = True
    log_level: str = "INFO"


class ATLASEngine:
    """
    Core ATLAS engine that orchestrates all system components.
    
    The ATLASEngine provides a unified interface for managing entities,
    patterns, queries, and their relationships within the ATLAS framework.
    """
    
    def __init__(self, config: Optional[ATLASConfig] = None):
        """Initialize the ATLAS engine."""
        self.config = config or ATLASConfig()
        self.graph = nx.DiGraph()
        
        # Component registries
        self.entities: Dict[str, Any] = {}
        self.patterns: Dict[str, Any] = {}
        self.queries: Dict[str, Any] = {}
        self.attributes: Dict[str, Any] = {}
        self.interfaces: Dict[str, Any] = {}
        
        # Relationship tracking
        self.relationships: Dict[str, List[tuple]] = defaultdict(list)
        
        # Performance and quality metrics
        self.metrics = {
            'entities_created': 0,
            'patterns_created': 0,
            'queries_executed': 0,
            'relationships_added': 0
        }
        
        logger.info("ATLAS Engine initialized with config: %s", self.config)
    
    def add_entity(self, entity_id: str, entity_data: Dict[str, Any]) -> bool:
        """
        Add an entity to the ATLAS system.
        
        Args:
            entity_id: Unique identifier for the entity
            entity_data: Entity data including attributes and patterns
            
        Returns:
            True if entity was added successfully, False otherwise
        """
        try:
            if entity_id in self.entities:
                logger.warning(f"Entity {entity_id} already exists, updating...")
            
            # Store entity data
            self.entities[entity_id] = entity_data
            
            # Add to graph
            self.graph.add_node(entity_id, node_type='entity', **entity_data)
            
            # Update metrics
            self.metrics['entities_created'] += 1
            
            logger.info(f"Added entity: {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add entity {entity_id}: {e}")
            return False
    
    def add_pattern(self, pattern_id: str, pattern_data: Dict[str, Any]) -> bool:
        """
        Add a pattern to the ATLAS system.
        
        Args:
            pattern_id: Unique identifier for the pattern
            pattern_data: Pattern data including qkit, parents, children
            
        Returns:
            True if pattern was added successfully, False otherwise
        """
        try:
            if pattern_id in self.patterns:
                logger.warning(f"Pattern {pattern_id} already exists, updating...")
            
            # Store pattern data
            self.patterns[pattern_id] = pattern_data
            
            # Add to graph
            self.graph.add_node(pattern_id, node_type='pattern', **pattern_data)
            
            # Handle parent-child relationships
            for parent_id in pattern_data.get('parents', []):
                self.add_relationship(parent_id, pattern_id, 'parent_of')
            
            for child_id in pattern_data.get('children', []):
                self.add_relationship(pattern_id, child_id, 'parent_of')
            
            # Update metrics
            self.metrics['patterns_created'] += 1
            
            logger.info(f"Added pattern: {pattern_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add pattern {pattern_id}: {e}")
            return False
    
    def add_query(self, query_id: str, query_data: Dict[str, Any]) -> bool:
        """
        Add an iQuery to the ATLAS system.
        
        Args:
            query_id: Unique identifier for the query
            query_data: Query data including ref_id and prompts
            
        Returns:
            True if query was added successfully, False otherwise
        """
        try:
            if query_id in self.queries:
                logger.warning(f"Query {query_id} already exists, updating...")
            
            # Store query data
            self.queries[query_id] = query_data
            
            # Add to graph
            self.graph.add_node(query_id, node_type='query', **query_data)
            
            logger.info(f"Added query: {query_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add query {query_id}: {e}")
            return False
    
    def add_relationship(self, source_id: str, target_id: str, relationship_type: str) -> bool:
        """
        Add a relationship between two nodes in the ATLAS system.
        
        Args:
            source_id: Source node identifier
            target_id: Target node identifier
            relationship_type: Type of relationship
            
        Returns:
            True if relationship was added successfully, False otherwise
        """
        try:
            # Ensure both nodes exist in graph before adding edge
            if not self.graph.has_node(source_id):
                # Add source node if it exists in any registry
                if source_id in self.entities:
                    self.graph.add_node(source_id, node_type='entity', **self.entities[source_id])
                elif source_id in self.patterns:
                    self.graph.add_node(source_id, node_type='pattern', **self.patterns[source_id])
                elif source_id in self.queries:
                    self.graph.add_node(source_id, node_type='query', **self.queries[source_id])
                else:
                    logger.warning(f"Source node {source_id} not found in any registry")
                    return False
            
            if not self.graph.has_node(target_id):
                # Add target node if it exists in any registry
                if target_id in self.entities:
                    self.graph.add_node(target_id, node_type='entity', **self.entities[target_id])
                elif target_id in self.patterns:
                    self.graph.add_node(target_id, node_type='pattern', **self.patterns[target_id])
                elif target_id in self.queries:
                    self.graph.add_node(target_id, node_type='query', **self.queries[target_id])
                else:
                    logger.warning(f"Target node {target_id} not found in any registry")
                    return False
            
            # Add edge to graph
            self.graph.add_edge(source_id, target_id, relationship_type=relationship_type)
            
            # Track relationship
            self.relationships[source_id].append((target_id, relationship_type))
            
            # Update metrics
            self.metrics['relationships_added'] += 1
            
            logger.info(f"Added relationship: {source_id} --[{relationship_type}]--> {target_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add relationship {source_id} -> {target_id}: {e}")
            return False
    
    def query(self, query_string: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a query against the ATLAS system.
        
        Args:
            query_string: Query to execute
            context: Optional context for the query
            
        Returns:
            List of results matching the query
        """
        try:
            # Update metrics
            self.metrics['queries_executed'] += 1
            
            # Simple implementation - can be extended with sophisticated query processing
            results = []
            
            # Search entities
            for entity_id, entity_data in self.entities.items():
                if self._matches_query(entity_data, query_string):
                    results.append({
                        'id': entity_id,
                        'type': 'entity',
                        'data': entity_data,
                        'relevance_score': self._calculate_relevance(entity_data, query_string)
                    })
            
            # Search patterns
            for pattern_id, pattern_data in self.patterns.items():
                if self._matches_query(pattern_data, query_string):
                    results.append({
                        'id': pattern_id,
                        'type': 'pattern',
                        'data': pattern_data,
                        'relevance_score': self._calculate_relevance(pattern_data, query_string)
                    })
            
            # Search queries
            for query_id, query_data in self.queries.items():
                if self._matches_query(query_data, query_string):
                    results.append({
                        'id': query_id,
                        'type': 'query',
                        'data': query_data,
                        'relevance_score': self._calculate_relevance(query_data, query_string)
                    })
            
            # Sort by relevance score
            results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
            
            logger.info(f"Query '{query_string}' returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return []
    
    def _matches_query(self, data: Dict[str, Any], query_string: str) -> bool:
        """Enhanced query matching logic."""
        query_lower = query_string.lower()
        
        # Check in all string values
        for key, value in data.items():
            if isinstance(value, str) and query_lower in value.lower():
                return True
            elif isinstance(value, (list, dict)):
                if query_lower in str(value).lower():
                    return True
            elif key.lower() == query_lower:  # Exact key match
                return True
        
        return False
    
    def _calculate_relevance(self, data: Dict[str, Any], query_string: str) -> float:
        """Calculate relevance score for search results."""
        query_lower = query_string.lower()
        score = 0.0
        
        for key, value in data.items():
            if isinstance(value, str):
                # Exact match gets higher score
                if query_lower == value.lower():
                    score += 1.0
                elif query_lower in value.lower():
                    score += 0.5
                    
            # Key match
            if query_lower == key.lower():
                score += 0.3
            elif query_lower in key.lower():
                score += 0.1
        
        return score
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node by its ID."""
        try:
            if node_id in self.entities:
                return {'type': 'entity', 'data': self.entities[node_id]}
            elif node_id in self.patterns:
                return {'type': 'pattern', 'data': self.patterns[node_id]}
            elif node_id in self.queries:
                return {'type': 'query', 'data': self.queries[node_id]}
            return None
        except Exception as e:
            logger.error(f"Failed to get node {node_id}: {e}")
            return None
    
    def get_relationships(self, node_id: str, relationship_type: Optional[str] = None) -> List[tuple]:
        """Get relationships for a node."""
        try:
            relationships = self.relationships.get(node_id, [])
            if relationship_type:
                return [(target, rtype) for target, rtype in relationships if rtype == relationship_type]
            return relationships
        except Exception as e:
            logger.error(f"Failed to get relationships for {node_id}: {e}")
            return []
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance and usage metrics."""
        return {
            **self.metrics,
            'total_nodes': len(self.graph.nodes),
            'total_edges': len(self.graph.edges),
            'graph_density': nx.density(self.graph),
            'connected_components': nx.number_weakly_connected_components(self.graph)
        }
    
    def export_graph(self, format: str = 'graphml') -> str:
        """Export the ATLAS graph in various formats."""
        try:
            if format == 'graphml':
                return '\n'.join(nx.generate_graphml(self.graph))
            elif format == 'gexf':
                return '\n'.join(nx.generate_gexf(self.graph))
            else:
                raise ValueError(f"Unsupported format: {format}")
        except Exception as e:
            logger.error(f"Failed to export graph: {e}")
            return ""
    
    def clear(self) -> None:
        """Clear all data from the ATLAS engine."""
        self.graph.clear()
        self.entities.clear()
        self.patterns.clear()
        self.queries.clear()
        self.attributes.clear()
        self.interfaces.clear()
        self.relationships.clear()
        
        # Reset metrics
        for key in self.metrics:
            self.metrics[key] = 0
        
        logger.info("ATLAS engine cleared") 