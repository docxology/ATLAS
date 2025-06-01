"""
Graph visualization module for ATLAS.

Provides comprehensive graph visualization capabilities including
network topology, entity relationships, and system structure visualization.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Set
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import networkx as nx
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd

logger = logging.getLogger(__name__)


class GraphVisualizer:
    """
    Comprehensive graph visualization for ATLAS systems.
    
    Provides multiple visualization methods for different aspects
    of the ATLAS knowledge graph and system relationships.
    """
    
    def __init__(self, atlas_engine=None):
        """
        Initialize the GraphVisualizer.
        
        Args:
            atlas_engine: Optional ATLAS engine instance
        """
        self.atlas_engine = atlas_engine
        self.color_schemes = {
            'entity': '#1f77b4',      # Blue
            'pattern': '#ff7f0e',     # Orange
            'query': '#2ca02c',       # Green
            'attribute': '#d62728',   # Red
            'prompt_interface': '#9467bd'  # Purple
        }
        
        # Layout algorithms available
        self.layouts = {
            'spring': nx.spring_layout,
            'circular': nx.circular_layout,
            'random': nx.random_layout,
            'shell': nx.shell_layout,
            'spectral': nx.spectral_layout,
            'kamada_kawai': nx.kamada_kawai_layout
        }
        
        logger.info("GraphVisualizer initialized")
    
    def visualize_network_topology(
        self, 
        layout: str = 'spring',
        figsize: Tuple[int, int] = (12, 8),
        save_path: Optional[str] = None,
        show_labels: bool = True,
        node_size_attr: Optional[str] = None
    ) -> Figure:
        """
        Visualize the overall network topology of the ATLAS system.
        
        Args:
            layout: Layout algorithm to use
            figsize: Figure size tuple
            save_path: Optional path to save the figure
            show_labels: Whether to show node labels
            node_size_attr: Attribute to use for node sizing
            
        Returns:
            Matplotlib figure object
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        try:
            fig, ax = plt.subplots(figsize=figsize)
            graph = self.atlas_engine.graph
            
            if not graph.nodes():
                ax.text(0.5, 0.5, 'No nodes to display', 
                       ha='center', va='center', transform=ax.transAxes)
                return fig
            
            # Calculate layout
            if layout in self.layouts:
                pos = self.layouts[layout](graph)
            else:
                pos = nx.spring_layout(graph)
            
            # Prepare node attributes
            node_colors = []
            node_sizes = []
            
            for node in graph.nodes():
                node_data = graph.nodes[node]
                node_type = node_data.get('node_type', 'unknown')
                node_colors.append(self.color_schemes.get(node_type, '#cccccc'))
                
                if node_size_attr and node_size_attr in node_data:
                    size = node_data[node_size_attr]
                    node_sizes.append(max(100, min(1000, size * 100)))
                else:
                    node_sizes.append(300)
            
            # Draw the graph
            nx.draw_networkx_nodes(
                graph, pos, ax=ax,
                node_color=node_colors,
                node_size=node_sizes,
                alpha=0.7
            )
            
            nx.draw_networkx_edges(
                graph, pos, ax=ax,
                edge_color='gray',
                alpha=0.5,
                arrows=True,
                arrowsize=20
            )
            
            if show_labels:
                labels = {node: node[:10] + '...' if len(node) > 10 else node 
                         for node in graph.nodes()}
                nx.draw_networkx_labels(graph, pos, labels, ax=ax, font_size=8)
            
            # Create legend
            legend_elements = [
                mpatches.Patch(color=color, label=node_type.title())
                for node_type, color in self.color_schemes.items()
            ]
            ax.legend(handles=legend_elements, loc='upper right')
            
            ax.set_title(f'ATLAS Network Topology ({layout} layout)', fontsize=14, fontweight='bold')
            ax.axis('off')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to visualize network topology: {e}")
            raise
    
    def visualize_entity_relationships(
        self,
        entity_id: str,
        depth: int = 2,
        layout: str = 'spring',
        figsize: Tuple[int, int] = (10, 8),
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Visualize relationships for a specific entity.
        
        Args:
            entity_id: ID of the entity to visualize
            depth: Depth of relationships to include
            layout: Layout algorithm to use
            figsize: Figure size tuple
            save_path: Optional path to save the figure
            
        Returns:
            Matplotlib figure object
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        try:
            fig, ax = plt.subplots(figsize=figsize)
            graph = self.atlas_engine.graph
            
            if entity_id not in graph.nodes():
                ax.text(0.5, 0.5, f'Entity {entity_id} not found', 
                       ha='center', va='center', transform=ax.transAxes)
                return fig
            
            # Get subgraph with entities within specified depth
            nodes_to_include = {entity_id}
            current_level = {entity_id}
            
            for _ in range(depth):
                next_level = set()
                for node in current_level:
                    # Add neighbors (both predecessors and successors)
                    next_level.update(graph.predecessors(node))
                    next_level.update(graph.successors(node))
                
                nodes_to_include.update(next_level)
                current_level = next_level
            
            subgraph = graph.subgraph(nodes_to_include)
            
            # Calculate layout
            if layout in self.layouts:
                pos = self.layouts[layout](subgraph)
            else:
                pos = nx.spring_layout(subgraph)
            
            # Color nodes by type and highlight target entity
            node_colors = []
            for node in subgraph.nodes():
                if node == entity_id:
                    node_colors.append('#ff0000')  # Red for target entity
                else:
                    node_data = subgraph.nodes[node]
                    node_type = node_data.get('node_type', 'unknown')
                    node_colors.append(self.color_schemes.get(node_type, '#cccccc'))
            
            # Draw the graph
            nx.draw_networkx_nodes(
                subgraph, pos, ax=ax,
                node_color=node_colors,
                node_size=400,
                alpha=0.8
            )
            
            nx.draw_networkx_edges(
                subgraph, pos, ax=ax,
                edge_color='gray',
                alpha=0.6,
                arrows=True,
                arrowsize=20
            )
            
            labels = {node: node[:8] + '...' if len(node) > 8 else node 
                     for node in subgraph.nodes()}
            nx.draw_networkx_labels(subgraph, pos, labels, ax=ax, font_size=9)
            
            ax.set_title(f'Entity Relationships: {entity_id} (depth={depth})', 
                        fontsize=12, fontweight='bold')
            ax.axis('off')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to visualize entity relationships: {e}")
            raise
    
    def create_interactive_network(
        self,
        width: int = 1000,
        height: int = 700,
        save_path: Optional[str] = None
    ) -> go.Figure:
        """
        Create an interactive network visualization using Plotly.
        
        Args:
            width: Figure width in pixels
            height: Figure height in pixels
            save_path: Optional path to save the HTML file
            
        Returns:
            Plotly figure object
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        try:
            graph = self.atlas_engine.graph
            
            if not graph.nodes():
                # Return empty figure
                fig = go.Figure()
                fig.add_annotation(
                    text="No nodes to display",
                    xref="paper", yref="paper",
                    x=0.5, y=0.5, xanchor='center', yanchor='middle',
                    showarrow=False
                )
                return fig
            
            # Calculate layout
            pos = nx.spring_layout(graph, k=1, iterations=50)
            
            # Prepare edge traces
            edge_x = []
            edge_y = []
            edge_info = []
            
            for edge in graph.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                
                edge_data = graph.edges[edge]
                relationship_type = edge_data.get('relationship_type', 'related')
                edge_info.append(f"{edge[0]} → {edge[1]} ({relationship_type})")
            
            # Create edge trace
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                mode='lines'
            )
            
            # Prepare node traces
            node_x = []
            node_y = []
            node_text = []
            node_colors = []
            node_sizes = []
            
            for node in graph.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                
                node_data = graph.nodes[node]
                node_type = node_data.get('node_type', 'unknown')
                
                # Create hover text
                hover_text = f"<b>{node}</b><br>"
                hover_text += f"Type: {node_type}<br>"
                
                # Add additional attributes to hover text
                for key, value in node_data.items():
                    if key != 'node_type' and len(str(value)) < 100:
                        hover_text += f"{key}: {value}<br>"
                
                node_text.append(hover_text)
                node_colors.append(self.color_schemes.get(node_type, '#cccccc'))
                
                # Calculate node size based on connections
                degree = graph.degree(node)
                node_sizes.append(max(10, min(50, degree * 5 + 15)))
            
            # Create node trace
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=[node[:10] + '...' if len(node) > 10 else node for node in graph.nodes()],
                textposition="middle center",
                hovertext=node_text,
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    line=dict(width=2, color='white'),
                    opacity=0.8
                )
            )
            
            # Create figure
            fig = go.Figure(data=[edge_trace, node_trace],
                           layout=go.Layout(
                               title='Interactive ATLAS Network',
                               title_font_size=16,
                               showlegend=False,
                               hovermode='closest',
                               margin=dict(b=20,l=5,r=5,t=40),
                               annotations=[ dict(
                                   text="Click and drag to explore the network",
                                   showarrow=False,
                                   xref="paper", yref="paper",
                                   x=0.005, y=-0.002,
                                   xanchor='left', yanchor='bottom',
                                   font=dict(color="#888", size=12)
                               )],
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               width=width,
                               height=height
                           ))
            
            if save_path:
                fig.write_html(save_path)
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create interactive network: {e}")
            raise
    
    def visualize_component_distribution(
        self,
        figsize: Tuple[int, int] = (12, 6),
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Visualize the distribution of different component types.
        
        Args:
            figsize: Figure size tuple
            save_path: Optional path to save the figure
            
        Returns:
            Matplotlib figure object
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
            
            # Count component types
            type_counts = {}
            for node in self.atlas_engine.graph.nodes():
                node_data = self.atlas_engine.graph.nodes[node]
                node_type = node_data.get('node_type', 'unknown')
                type_counts[node_type] = type_counts.get(node_type, 0) + 1
            
            if not type_counts:
                ax1.text(0.5, 0.5, 'No data to display', ha='center', va='center')
                ax2.text(0.5, 0.5, 'No data to display', ha='center', va='center')
                return fig
            
            # Pie chart
            colors = [self.color_schemes.get(t, '#cccccc') for t in type_counts.keys()]
            wedges, texts, autotexts = ax1.pie(
                type_counts.values(),
                labels=type_counts.keys(),
                colors=colors,
                autopct='%1.1f%%',
                startangle=90
            )
            ax1.set_title('Component Type Distribution', fontweight='bold')
            
            # Bar chart
            bars = ax2.bar(type_counts.keys(), type_counts.values(), color=colors)
            ax2.set_title('Component Type Counts', fontweight='bold')
            ax2.set_ylabel('Count')
            ax2.tick_params(axis='x', rotation=45)
            
            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to visualize component distribution: {e}")
            raise
    
    def export_graph_formats(self, base_path: str) -> Dict[str, str]:
        """
        Export the graph in multiple formats.
        
        Args:
            base_path: Base path for export files (without extension)
            
        Returns:
            Dictionary mapping format names to file paths
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        exported_files = {}
        
        try:
            graph = self.atlas_engine.graph
            
            # GraphML format
            graphml_path = f"{base_path}.graphml"
            nx.write_graphml(graph, graphml_path)
            exported_files['graphml'] = graphml_path
            
            # GEXF format
            gexf_path = f"{base_path}.gexf"
            nx.write_gexf(graph, gexf_path)
            exported_files['gexf'] = gexf_path
            
            # Edge list
            edgelist_path = f"{base_path}.edgelist"
            nx.write_edgelist(graph, edgelist_path, data=True)
            exported_files['edgelist'] = edgelist_path
            
            # Adjacency list
            adjlist_path = f"{base_path}.adjlist"
            nx.write_adjlist(graph, adjlist_path)
            exported_files['adjlist'] = adjlist_path
            
            logger.info(f"Exported graph in {len(exported_files)} formats")
            return exported_files
            
        except Exception as e:
            logger.error(f"Failed to export graph formats: {e}")
            return {}
    
    def generate_graph_statistics(self) -> Dict[str, Any]:
        """
        Generate comprehensive graph statistics.
        
        Returns:
            Dictionary with various graph metrics and statistics
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        try:
            graph = self.atlas_engine.graph
            
            if not graph.nodes():
                return {'error': 'No nodes in graph'}
            
            stats = {
                'basic_metrics': {
                    'node_count': graph.number_of_nodes(),
                    'edge_count': graph.number_of_edges(),
                    'density': nx.density(graph),
                    'is_directed': graph.is_directed()
                },
                'connectivity': {
                    'is_connected': nx.is_weakly_connected(graph) if graph.is_directed() else nx.is_connected(graph),
                    'connected_components': nx.number_weakly_connected_components(graph) if graph.is_directed() else nx.number_connected_components(graph)
                },
                'centrality': {},
                'node_types': {}
            }
            
            # Calculate centrality measures (sample if graph is large)
            if graph.number_of_nodes() <= 1000:
                stats['centrality'] = {
                    'degree_centrality': nx.degree_centrality(graph),
                    'betweenness_centrality': nx.betweenness_centrality(graph),
                    'closeness_centrality': nx.closeness_centrality(graph)
                }
            
            # Node type distribution
            type_counts = {}
            for node in graph.nodes():
                node_data = graph.nodes[node]
                node_type = node_data.get('node_type', 'unknown')
                type_counts[node_type] = type_counts.get(node_type, 0) + 1
            
            stats['node_types'] = type_counts
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to generate graph statistics: {e}")
            return {'error': str(e)} 