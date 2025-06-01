"""
PatternEngine - Advanced pattern management and analysis for ATLAS.

The PatternEngine provides sophisticated pattern matching, inheritance,
and analysis capabilities for the ATLAS pattern language system.
"""

import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
import networkx as nx

from .pattern import Pattern

logger = logging.getLogger(__name__)


class PatternEngine:
    """
    Advanced pattern management and analysis engine.
    
    The PatternEngine provides pattern matching, inheritance analysis,
    pattern discovery, and optimization capabilities for ATLAS patterns.
    """
    
    def __init__(self):
        """Initialize the PatternEngine."""
        self.patterns: Dict[str, Pattern] = {}
        self.pattern_graph = nx.DiGraph()
        
        # Pattern analysis caches
        self._inheritance_cache: Dict[str, Set[str]] = {}
        self._similarity_cache: Dict[Tuple[str, str], float] = {}
        
        # Pattern discovery state
        self.pattern_clusters: Dict[str, Set[str]] = defaultdict(set)
        self.emerging_patterns: List[Dict[str, Any]] = []
        
        logger.info("PatternEngine initialized")
    
    def add_pattern(self, pattern: Pattern) -> bool:
        """
        Add a pattern to the engine.
        
        Args:
            pattern: Pattern instance to add
            
        Returns:
            True if pattern was added successfully
        """
        try:
            self.patterns[pattern.id] = pattern
            
            # Add to pattern graph
            self.pattern_graph.add_node(pattern.id, pattern=pattern)
            
            # Add parent-child relationships
            for parent_id in pattern.parents:
                if parent_id in self.patterns:
                    self.pattern_graph.add_edge(parent_id, pattern.id, relation='parent_of')
            
            for child_id in pattern.children:
                if child_id in self.patterns:
                    self.pattern_graph.add_edge(pattern.id, child_id, relation='parent_of')
            
            # Clear caches
            self._clear_caches()
            
            logger.info(f"Added pattern {pattern.id} to engine")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add pattern {pattern.id}: {e}")
            return False
    
    def remove_pattern(self, pattern_id: str) -> bool:
        """Remove a pattern from the engine."""
        try:
            if pattern_id in self.patterns:
                del self.patterns[pattern_id]
                
                # Remove from graph
                if self.pattern_graph.has_node(pattern_id):
                    self.pattern_graph.remove_node(pattern_id)
                
                # Clear caches
                self._clear_caches()
                
                logger.info(f"Removed pattern {pattern_id} from engine")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove pattern {pattern_id}: {e}")
            return False
    
    def get_pattern_hierarchy(self, pattern_id: str) -> Dict[str, Set[str]]:
        """
        Get the complete hierarchy for a pattern.
        
        Args:
            pattern_id: Pattern identifier
            
        Returns:
            Dictionary with 'ancestors' and 'descendants' sets
        """
        if pattern_id not in self.patterns:
            return {'ancestors': set(), 'descendants': set()}
        
        try:
            ancestors = set()
            descendants = set()
            
            # Get all ancestors (recursive)
            for ancestor in nx.ancestors(self.pattern_graph, pattern_id):
                ancestors.add(ancestor)
            
            # Get all descendants (recursive)
            for descendant in nx.descendants(self.pattern_graph, pattern_id):
                descendants.add(descendant)
            
            return {
                'ancestors': ancestors,
                'descendants': descendants
            }
            
        except Exception as e:
            logger.error(f"Failed to get hierarchy for pattern {pattern_id}: {e}")
            return {'ancestors': set(), 'descendants': set()}
    
    def calculate_pattern_similarity(self, pattern1_id: str, pattern2_id: str) -> float:
        """
        Calculate similarity between two patterns.
        
        Args:
            pattern1_id: First pattern identifier
            pattern2_id: Second pattern identifier
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Handle self-similarity case
        if pattern1_id == pattern2_id:
            return 1.0
        
        cache_key: Tuple[str, str] = tuple(sorted([pattern1_id, pattern2_id]))
        if cache_key in self._similarity_cache:
            return self._similarity_cache[cache_key]
        
        if pattern1_id not in self.patterns or pattern2_id not in self.patterns:
            return 0.0
        
        try:
            pattern1 = self.patterns[pattern1_id]
            pattern2 = self.patterns[pattern2_id]
            
            # QKit similarity
            qkit1_set = set(pattern1.qkit)
            qkit2_set = set(pattern2.qkit)
            qkit_intersection = len(qkit1_set & qkit2_set)
            qkit_union = len(qkit1_set | qkit2_set)
            qkit_similarity = qkit_intersection / qkit_union if qkit_union > 0 else 1.0  # If both empty, consider similar
            
            # Attribute similarity
            attrs1_keys = set(pattern1.attributes.keys())
            attrs2_keys = set(pattern2.attributes.keys())
            attr_intersection = len(attrs1_keys & attrs2_keys)
            attr_union = len(attrs1_keys | attrs2_keys)
            attr_similarity = attr_intersection / attr_union if attr_union > 0 else 1.0  # If both empty, consider similar
            
            # Hierarchy similarity
            hier1 = self.get_pattern_hierarchy(pattern1_id)
            hier2 = self.get_pattern_hierarchy(pattern2_id)
            hier_intersection = len(hier1['ancestors'] & hier2['ancestors'])
            hier_union = len(hier1['ancestors'] | hier2['ancestors'])
            hier_similarity = hier_intersection / hier_union if hier_union > 0 else 1.0  # If both empty, consider similar
            
            # Weighted average
            similarity = (0.5 * qkit_similarity + 0.3 * attr_similarity + 0.2 * hier_similarity)
            
            # Cache result
            self._similarity_cache[cache_key] = similarity
            
            return similarity
            
        except Exception as e:
            logger.error(f"Failed to calculate similarity between {pattern1_id} and {pattern2_id}: {e}")
            return 0.0
    
    def find_similar_patterns(self, pattern_id: str, threshold: float = 0.7) -> List[Tuple[str, float]]:
        """
        Find patterns similar to the given pattern.
        
        Args:
            pattern_id: Pattern to find similarities for
            threshold: Minimum similarity threshold
            
        Returns:
            List of (pattern_id, similarity_score) tuples
        """
        if pattern_id not in self.patterns:
            return []
        
        similar_patterns = []
        
        for other_id in self.patterns:
            if other_id != pattern_id:
                similarity = self.calculate_pattern_similarity(pattern_id, other_id)
                if similarity >= threshold:
                    similar_patterns.append((other_id, similarity))
        
        # Sort by similarity descending
        similar_patterns.sort(key=lambda x: x[1], reverse=True)
        
        return similar_patterns
    
    def detect_pattern_clusters(self, similarity_threshold: float = 0.6) -> Dict[str, Set[str]]:
        """
        Detect clusters of similar patterns.
        
        Args:
            similarity_threshold: Minimum similarity for clustering
            
        Returns:
            Dictionary mapping cluster IDs to sets of pattern IDs
        """
        try:
            # Create similarity graph
            similarity_graph = nx.Graph()
            similarity_graph.add_nodes_from(self.patterns.keys())
            
            # Add edges for similar patterns
            for pattern1_id in self.patterns:
                for pattern2_id in self.patterns:
                    if pattern1_id < pattern2_id:  # Avoid duplicates
                        similarity = self.calculate_pattern_similarity(pattern1_id, pattern2_id)
                        if similarity >= similarity_threshold:
                            similarity_graph.add_edge(pattern1_id, pattern2_id, weight=similarity)
            
            # Find connected components as clusters
            clusters = {}
            for i, component in enumerate(nx.connected_components(similarity_graph)):
                cluster_id = f"cluster_{i}"
                clusters[cluster_id] = component
            
            self.pattern_clusters = clusters
            return clusters
            
        except Exception as e:
            logger.error(f"Failed to detect pattern clusters: {e}")
            return {}
    
    def suggest_pattern_merges(self, similarity_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Suggest pattern merges based on high similarity.
        
        Args:
            similarity_threshold: Minimum similarity for merge suggestion
            
        Returns:
            List of merge suggestions with pattern pairs and reasons
        """
        suggestions = []
        
        for pattern1_id in self.patterns:
            similar = self.find_similar_patterns(pattern1_id, similarity_threshold)
            for pattern2_id, similarity in similar:
                if pattern1_id < pattern2_id:  # Avoid duplicates
                    suggestion = {
                        'pattern1': pattern1_id,
                        'pattern2': pattern2_id,
                        'similarity': similarity,
                        'reason': f"High similarity ({similarity:.2f}) suggests potential merge",
                        'common_qkit': list(set(self.patterns[pattern1_id].qkit) & 
                                          set(self.patterns[pattern2_id].qkit)),
                        'common_attributes': list(set(self.patterns[pattern1_id].attributes.keys()) & 
                                                set(self.patterns[pattern2_id].attributes.keys()))
                    }
                    suggestions.append(suggestion)
        
        return suggestions
    
    def analyze_pattern_usage(self) -> Dict[str, Any]:
        """
        Analyze pattern usage across the system.
        
        Returns:
            Dictionary with usage statistics and insights
        """
        try:
            total_patterns = len(self.patterns)
            total_usage = sum(pattern.usage_count for pattern in self.patterns.values())
            
            # Most used patterns
            most_used = sorted(
                [(pid, p.usage_count) for pid, p in self.patterns.items()],
                key=lambda x: x[1], reverse=True
            )[:10]
            
            # Least used patterns
            least_used = sorted(
                [(pid, p.usage_count) for pid, p in self.patterns.items()],
                key=lambda x: x[1]
            )[:10]
            
            # Orphaned patterns (no parents or children)
            orphaned = [
                pid for pid, pattern in self.patterns.items()
                if not pattern.parents and not pattern.children
            ]
            
            # Root patterns (no parents)
            root_patterns = [
                pid for pid, pattern in self.patterns.items()
                if not pattern.parents
            ]
            
            # Leaf patterns (no children)
            leaf_patterns = [
                pid for pid, pattern in self.patterns.items()
                if not pattern.children
            ]
            
            return {
                'total_patterns': total_patterns,
                'total_usage': total_usage,
                'average_usage': total_usage / total_patterns if total_patterns > 0 else 0,
                'most_used_patterns': most_used,
                'least_used_patterns': least_used,
                'orphaned_patterns': orphaned,
                'root_patterns': root_patterns,
                'leaf_patterns': leaf_patterns,
                'hierarchy_depth': nx.dag_longest_path_length(self.pattern_graph) if self.pattern_graph.nodes else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze pattern usage: {e}")
            return {}
    
    def optimize_pattern_hierarchy(self) -> List[Dict[str, Any]]:
        """
        Suggest optimizations for the pattern hierarchy.
        
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        try:
            # Detect cycles
            if not nx.is_directed_acyclic_graph(self.pattern_graph):
                cycles = list(nx.simple_cycles(self.pattern_graph))
                for cycle in cycles:
                    suggestions.append({
                        'type': 'cycle_detected',
                        'patterns': cycle,
                        'priority': 'high',
                        'description': f"Circular dependency detected: {' -> '.join(cycle)}"
                    })
            
            # Find redundant relationships
            for pattern_id in self.patterns:
                pattern = self.patterns[pattern_id]
                for parent_id in pattern.parents:
                    # Check if parent is also ancestor through another path
                    hierarchy = self.get_pattern_hierarchy(pattern_id)
                    indirect_ancestors = hierarchy['ancestors'] - set(pattern.parents)
                    if parent_id in indirect_ancestors:
                        suggestions.append({
                            'type': 'redundant_relationship',
                            'pattern': pattern_id,
                            'parent': parent_id,
                            'priority': 'medium',
                            'description': f"Direct parent {parent_id} is also indirect ancestor"
                        })
            
            # Find isolated patterns
            for pattern_id in self.patterns:
                if (self.pattern_graph.in_degree(pattern_id) == 0 and 
                    self.pattern_graph.out_degree(pattern_id) == 0):
                    suggestions.append({
                        'type': 'isolated_pattern',
                        'pattern': pattern_id,
                        'priority': 'low',
                        'description': f"Pattern {pattern_id} has no relationships"
                    })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Failed to optimize pattern hierarchy: {e}")
            return []
    
    def _clear_caches(self) -> None:
        """Clear internal caches."""
        self._inheritance_cache.clear()
        self._similarity_cache.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            'pattern_count': len(self.patterns),
            'graph_nodes': self.pattern_graph.number_of_nodes(),
            'graph_edges': self.pattern_graph.number_of_edges(),
            'cache_sizes': {
                'inheritance': len(self._inheritance_cache),
                'similarity': len(self._similarity_cache)
            },
            'cluster_count': len(self.pattern_clusters),
            'emerging_patterns': len(self.emerging_patterns)
        } 