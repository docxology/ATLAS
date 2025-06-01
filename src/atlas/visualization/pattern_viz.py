"""
Pattern visualization module for ATLAS.

Provides comprehensive pattern visualization capabilities including
hierarchy visualization, inheritance relationships, and pattern analysis charts.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Set
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
import networkx as nx
import numpy as np
import seaborn as sns
import pandas as pd
from collections import defaultdict

logger = logging.getLogger(__name__)


class PatternVisualizer:
    """
    Comprehensive pattern visualization for ATLAS pattern systems.
    
    Provides visualization methods for pattern hierarchies, effectiveness
    analysis, and pattern relationship exploration.
    """
    
    def __init__(self, atlas_engine=None, pattern_engine=None):
        """
        Initialize the PatternVisualizer.
        
        Args:
            atlas_engine: Optional ATLAS engine instance
            pattern_engine: Optional pattern engine instance
        """
        self.atlas_engine = atlas_engine
        self.pattern_engine = pattern_engine
        
        # Color schemes for different visualization types
        self.hierarchy_colors = {
            'root': '#ff6b6b',       # Red
            'intermediate': '#4ecdc4', # Teal
            'leaf': '#45b7d1',       # Blue
            'orphan': '#96ceb4'      # Green
        }
        
        # Pattern effectiveness color gradient
        self.effectiveness_colormap = plt.cm.RdYlGn
        
        logger.info("PatternVisualizer initialized")
    
    def visualize_pattern_hierarchy(
        self,
        layout: str = 'hierarchical',
        figsize: Tuple[int, int] = (14, 10),
        save_path: Optional[str] = None,
        show_qkit_size: bool = True
    ) -> Figure:
        """
        Visualize the complete pattern hierarchy.
        
        Args:
            layout: Layout style ('hierarchical', 'circular', 'spring')
            figsize: Figure size tuple
            save_path: Optional path to save the figure
            show_qkit_size: Whether to size nodes by QKit size
            
        Returns:
            Matplotlib figure object
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        try:
            fig, ax = plt.subplots(figsize=figsize)
            
            # Build pattern graph
            pattern_graph = nx.DiGraph()
            patterns = {}
            
            # Collect pattern data
            for node_id in self.atlas_engine.graph.nodes():
                node_data = self.atlas_engine.graph.nodes[node_id]
                if node_data.get('node_type') == 'pattern':
                    patterns[node_id] = node_data
                    pattern_graph.add_node(node_id)
            
            # Add hierarchy edges
            for pattern_id, pattern_data in patterns.items():
                parents = pattern_data.get('parents', [])
                children = pattern_data.get('children', [])
                
                for parent_id in parents:
                    if parent_id in patterns:
                        pattern_graph.add_edge(parent_id, pattern_id)
                
                for child_id in children:
                    if child_id in patterns:
                        pattern_graph.add_edge(pattern_id, child_id)
            
            if not pattern_graph.nodes():
                ax.text(0.5, 0.5, 'No patterns to display', 
                       ha='center', va='center', transform=ax.transAxes)
                return fig
            
            # Calculate layout
            if layout == 'hierarchical':
                # Use graphviz_layout if available, otherwise fall back to spring
                try:
                    pos = nx.nx_agraph.graphviz_layout(pattern_graph, prog='dot')
                except:
                    pos = nx.spring_layout(pattern_graph, k=2, iterations=50)
            elif layout == 'circular':
                pos = nx.circular_layout(pattern_graph)
            else:
                pos = nx.spring_layout(pattern_graph, k=2, iterations=50)
            
            # Categorize nodes
            node_categories = {}
            for node in pattern_graph.nodes():
                in_degree = pattern_graph.in_degree(node)
                out_degree = pattern_graph.out_degree(node)
                
                if in_degree == 0 and out_degree > 0:
                    node_categories[node] = 'root'
                elif in_degree > 0 and out_degree > 0:
                    node_categories[node] = 'intermediate'
                elif in_degree > 0 and out_degree == 0:
                    node_categories[node] = 'leaf'
                else:
                    node_categories[node] = 'orphan'
            
            # Prepare node attributes
            node_colors = [self.hierarchy_colors[node_categories[node]] for node in pattern_graph.nodes()]
            
            if show_qkit_size:
                node_sizes = []
                for node in pattern_graph.nodes():
                    qkit_size = len(patterns[node].get('qkit', []))
                    node_sizes.append(max(200, min(800, qkit_size * 100 + 200)))
            else:
                node_sizes = [400] * len(pattern_graph.nodes())
            
            # Draw the graph
            nx.draw_networkx_nodes(
                pattern_graph, pos, ax=ax,
                node_color=node_colors,
                node_size=node_sizes,
                alpha=0.8
            )
            
            nx.draw_networkx_edges(
                pattern_graph, pos, ax=ax,
                edge_color='gray',
                alpha=0.6,
                arrows=True,
                arrowsize=20,
                arrowstyle='->'
            )
            
            # Add labels
            labels = {node: node[:12] + '...' if len(node) > 12 else node 
                     for node in pattern_graph.nodes()}
            nx.draw_networkx_labels(pattern_graph, pos, labels, ax=ax, font_size=8)
            
            # Create legend
            legend_elements = [
                mpatches.Patch(color=color, label=category.title())
                for category, color in self.hierarchy_colors.items()
            ]
            ax.legend(handles=legend_elements, loc='upper right', title='Pattern Types')
            
            ax.set_title(f'Pattern Hierarchy ({layout} layout)', fontsize=14, fontweight='bold')
            ax.axis('off')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to visualize pattern hierarchy: {e}")
            raise
    
    def visualize_pattern_effectiveness(
        self,
        figsize: Tuple[int, int] = (12, 8),
        save_path: Optional[str] = None,
        min_usage: int = 1
    ) -> Figure:
        """
        Visualize pattern effectiveness and usage metrics.
        
        Args:
            figsize: Figure size tuple
            save_path: Optional path to save the figure
            min_usage: Minimum usage count to include
            
        Returns:
            Matplotlib figure object
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
            
            # Collect pattern metrics
            pattern_data = []
            for node_id in self.atlas_engine.graph.nodes():
                node_data = self.atlas_engine.graph.nodes[node_id]
                if node_data.get('node_type') == 'pattern':
                    usage_count = node_data.get('usage_count', 0)
                    if usage_count >= min_usage:
                        effectiveness = node_data.get('effectiveness_score', 0.0)
                        qkit_size = len(node_data.get('qkit', []))
                        instance_count = len(node_data.get('instances', []))
                        
                        pattern_data.append({
                            'id': node_id,
                            'usage_count': usage_count,
                            'effectiveness_score': effectiveness,
                            'qkit_size': qkit_size,
                            'instance_count': instance_count
                        })
            
            if not pattern_data:
                for ax in [ax1, ax2, ax3, ax4]:
                    ax.text(0.5, 0.5, 'No pattern data available', 
                           ha='center', va='center', transform=ax.transAxes)
                return fig
            
            df = pd.DataFrame(pattern_data)
            
            # Plot 1: Usage vs Effectiveness scatter
            scatter = ax1.scatter(
                df['usage_count'], 
                df['effectiveness_score'],
                c=df['qkit_size'],
                cmap='viridis',
                alpha=0.6,
                s=60
            )
            ax1.set_xlabel('Usage Count')
            ax1.set_ylabel('Effectiveness Score')
            ax1.set_title('Pattern Usage vs Effectiveness')
            plt.colorbar(scatter, ax=ax1, label='QKit Size')
            
            # Plot 2: Top patterns by effectiveness
            top_patterns = df.nlargest(10, 'effectiveness_score')
            bars = ax2.barh(
                range(len(top_patterns)),
                top_patterns['effectiveness_score'],
                color=self.effectiveness_colormap(top_patterns['effectiveness_score'])
            )
            ax2.set_yticks(range(len(top_patterns)))
            ax2.set_yticklabels([p[:15] + '...' if len(p) > 15 else p 
                                for p in top_patterns['id']])
            ax2.set_xlabel('Effectiveness Score')
            ax2.set_title('Top 10 Most Effective Patterns')
            
            # Plot 3: Usage distribution histogram
            ax3.hist(df['usage_count'], bins=20, alpha=0.7, color='skyblue', edgecolor='black')
            ax3.set_xlabel('Usage Count')
            ax3.set_ylabel('Frequency')
            ax3.set_title('Pattern Usage Distribution')
            
            # Plot 4: QKit size vs Instance count
            ax4.scatter(
                df['qkit_size'], 
                df['instance_count'],
                alpha=0.6,
                c='coral',
                s=60
            )
            ax4.set_xlabel('QKit Size')
            ax4.set_ylabel('Instance Count')
            ax4.set_title('QKit Size vs Instance Count')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to visualize pattern effectiveness: {e}")
            raise
    
    def visualize_pattern_inheritance_tree(
        self,
        root_pattern_id: str,
        max_depth: int = 5,
        figsize: Tuple[int, int] = (12, 8),
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Visualize inheritance tree starting from a root pattern.
        
        Args:
            root_pattern_id: ID of the root pattern
            max_depth: Maximum depth to traverse
            figsize: Figure size tuple
            save_path: Optional path to save the figure
            
        Returns:
            Matplotlib figure object
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        try:
            fig, ax = plt.subplots(figsize=figsize)
            
            # Build inheritance tree
            tree = nx.DiGraph()
            patterns = {}
            
            # Get all patterns
            for node_id in self.atlas_engine.graph.nodes():
                node_data = self.atlas_engine.graph.nodes[node_id]
                if node_data.get('node_type') == 'pattern':
                    patterns[node_id] = node_data
            
            if root_pattern_id not in patterns:
                ax.text(0.5, 0.5, f'Root pattern {root_pattern_id} not found', 
                       ha='center', va='center', transform=ax.transAxes)
                return fig
            
            # Traverse inheritance tree
            def add_children(pattern_id, current_depth):
                if current_depth >= max_depth:
                    return
                
                if pattern_id in patterns:
                    tree.add_node(pattern_id, depth=current_depth)
                    children = patterns[pattern_id].get('children', [])
                    
                    for child_id in children:
                        if child_id in patterns:
                            tree.add_edge(pattern_id, child_id)
                            add_children(child_id, current_depth + 1)
            
            add_children(root_pattern_id, 0)
            
            if not tree.nodes():
                ax.text(0.5, 0.5, 'No inheritance tree found', 
                       ha='center', va='center', transform=ax.transAxes)
                return fig
            
            # Calculate hierarchical layout
            pos = {}
            depth_nodes = defaultdict(list)
            
            # Group nodes by depth
            for node in tree.nodes():
                depth = tree.nodes[node].get('depth', 0)
                depth_nodes[depth].append(node)
            
            # Position nodes
            for depth, nodes in depth_nodes.items():
                y = -depth
                x_positions = np.linspace(-len(nodes)/2, len(nodes)/2, len(nodes))
                for i, node in enumerate(nodes):
                    pos[node] = (x_positions[i], y)
            
            # Color nodes by depth
            node_colors = []
            for node in tree.nodes():
                depth = tree.nodes[node].get('depth', 0)
                color_intensity = min(1.0, depth / max_depth)
                node_colors.append(plt.cm.viridis(color_intensity))
            
            # Draw the tree
            nx.draw_networkx_nodes(
                tree, pos, ax=ax,
                node_color=node_colors,
                node_size=500,
                alpha=0.8
            )
            
            nx.draw_networkx_edges(
                tree, pos, ax=ax,
                edge_color='gray',
                alpha=0.6,
                arrows=True,
                arrowsize=20
            )
            
            labels = {node: node[:10] + '...' if len(node) > 10 else node 
                     for node in tree.nodes()}
            nx.draw_networkx_labels(tree, pos, labels, ax=ax, font_size=9)
            
            ax.set_title(f'Inheritance Tree: {root_pattern_id}', fontsize=14, fontweight='bold')
            ax.axis('off')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to visualize inheritance tree: {e}")
            raise
    
    def visualize_pattern_similarity_matrix(
        self,
        figsize: Tuple[int, int] = (10, 8),
        save_path: Optional[str] = None,
        max_patterns: int = 20
    ) -> Figure:
        """
        Visualize pattern similarity as a heatmap matrix.
        
        Args:
            figsize: Figure size tuple
            save_path: Optional path to save the figure
            max_patterns: Maximum number of patterns to include
            
        Returns:
            Matplotlib figure object
        """
        if not self.atlas_engine or not self.pattern_engine:
            raise ValueError("Both ATLAS engine and pattern engine required")
        
        try:
            fig, ax = plt.subplots(figsize=figsize)
            
            # Get pattern IDs
            pattern_ids = list(self.pattern_engine.patterns.keys())[:max_patterns]
            
            if len(pattern_ids) < 2:
                ax.text(0.5, 0.5, 'Need at least 2 patterns for similarity matrix', 
                       ha='center', va='center', transform=ax.transAxes)
                return fig
            
            # Calculate similarity matrix
            similarity_matrix = np.zeros((len(pattern_ids), len(pattern_ids)))
            
            for i, pattern1_id in enumerate(pattern_ids):
                for j, pattern2_id in enumerate(pattern_ids):
                    if i == j:
                        similarity_matrix[i, j] = 1.0
                    else:
                        similarity = self.pattern_engine.calculate_pattern_similarity(
                            pattern1_id, pattern2_id
                        )
                        similarity_matrix[i, j] = similarity
            
            # Create heatmap
            im = ax.imshow(similarity_matrix, cmap='RdYlBu_r', aspect='auto', vmin=0, vmax=1)
            
            # Set ticks and labels
            ax.set_xticks(range(len(pattern_ids)))
            ax.set_yticks(range(len(pattern_ids)))
            ax.set_xticklabels([p[:12] + '...' if len(p) > 12 else p for p in pattern_ids], 
                              rotation=45, ha='right')
            ax.set_yticklabels([p[:12] + '...' if len(p) > 12 else p for p in pattern_ids])
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.set_label('Similarity Score', rotation=270, labelpad=20)
            
            # Add text annotations
            for i in range(len(pattern_ids)):
                for j in range(len(pattern_ids)):
                    text = ax.text(j, i, f'{similarity_matrix[i, j]:.2f}',
                                 ha='center', va='center',
                                 color='white' if similarity_matrix[i, j] < 0.5 else 'black',
                                 fontsize=8)
            
            ax.set_title('Pattern Similarity Matrix', fontsize=14, fontweight='bold')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to visualize pattern similarity matrix: {e}")
            raise
    
    def visualize_qkit_analysis(
        self,
        figsize: Tuple[int, int] = (14, 8),
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Visualize QKit analysis across patterns.
        
        Args:
            figsize: Figure size tuple
            save_path: Optional path to save the figure
            
        Returns:
            Matplotlib figure object
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
            
            # Collect QKit data
            qkit_sizes = []
            qkit_overlaps = defaultdict(int)
            all_qkit_items = set()
            pattern_qkits = {}
            
            for node_id in self.atlas_engine.graph.nodes():
                node_data = self.atlas_engine.graph.nodes[node_id]
                if node_data.get('node_type') == 'pattern':
                    qkit = node_data.get('qkit', [])
                    qkit_sizes.append(len(qkit))
                    pattern_qkits[node_id] = set(qkit)
                    all_qkit_items.update(qkit)
            
            if not qkit_sizes:
                for ax in [ax1, ax2, ax3, ax4]:
                    ax.text(0.5, 0.5, 'No QKit data available', 
                           ha='center', va='center', transform=ax.transAxes)
                return fig
            
            # Plot 1: QKit size distribution
            ax1.hist(qkit_sizes, bins=max(1, len(set(qkit_sizes))), 
                    alpha=0.7, color='lightblue', edgecolor='black')
            ax1.set_xlabel('QKit Size')
            ax1.set_ylabel('Number of Patterns')
            ax1.set_title('QKit Size Distribution')
            
            # Plot 2: QKit overlap analysis
            overlap_counts = []
            pattern_pairs = list(pattern_qkits.keys())
            for i, pattern1 in enumerate(pattern_pairs):
                for pattern2 in pattern_pairs[i+1:]:
                    overlap = len(pattern_qkits[pattern1] & pattern_qkits[pattern2])
                    if overlap > 0:
                        overlap_counts.append(overlap)
            
            if overlap_counts:
                ax2.hist(overlap_counts, bins=max(1, len(set(overlap_counts))), 
                        alpha=0.7, color='lightcoral', edgecolor='black')
                ax2.set_xlabel('Number of Shared QKit Items')
                ax2.set_ylabel('Number of Pattern Pairs')
                ax2.set_title('QKit Overlap Distribution')
            else:
                ax2.text(0.5, 0.5, 'No QKit overlaps found', ha='center', va='center')
            
            # Plot 3: Most common QKit items
            qkit_item_counts = defaultdict(int)
            for qkit in pattern_qkits.values():
                for item in qkit:
                    qkit_item_counts[item] += 1
            
            if qkit_item_counts:
                common_items = sorted(qkit_item_counts.items(), 
                                    key=lambda x: x[1], reverse=True)[:10]
                if common_items:
                    items, counts = zip(*common_items)
                    ax3.barh(range(len(items)), counts, color='lightgreen')
                    ax3.set_yticks(range(len(items)))
                    ax3.set_yticklabels([item[:20] + '...' if len(item) > 20 else item 
                                        for item in items])
                    ax3.set_xlabel('Usage Count')
                    ax3.set_title('Most Common QKit Items')
            
            # Plot 4: Pattern complexity vs QKit size
            if len(pattern_qkits) > 1:
                complexity_scores = []
                sizes = []
                for pattern_id, qkit in pattern_qkits.items():
                    # Simple complexity based on unique vs total items
                    unique_ratio = len(qkit) / max(1, len(all_qkit_items))
                    complexity_scores.append(unique_ratio)
                    sizes.append(len(qkit))
                
                ax4.scatter(sizes, complexity_scores, alpha=0.6, color='purple')
                ax4.set_xlabel('QKit Size')
                ax4.set_ylabel('Uniqueness Ratio')
                ax4.set_title('Pattern Complexity Analysis')
            else:
                ax4.text(0.5, 0.5, 'Need more patterns for complexity analysis', 
                        ha='center', va='center')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to visualize QKit analysis: {e}")
            raise 