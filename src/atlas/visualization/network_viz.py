"""
Network visualization module for ATLAS.

Provides advanced network analysis and visualization capabilities including
community detection, centrality analysis, and dynamic network exploration.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Set
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import networkx as nx
import numpy as np
import pandas as pd
from collections import defaultdict

logger = logging.getLogger(__name__)


class NetworkVisualizer:
    """
    Advanced network visualization and analysis for ATLAS systems.
    
    Provides network analysis methods including community detection,
    centrality measures, and dynamic network visualization.
    """
    
    def __init__(self, atlas_engine=None):
        """
        Initialize the NetworkVisualizer.
        
        Args:
            atlas_engine: Optional ATLAS engine instance
        """
        self.atlas_engine = atlas_engine
        
        # Color schemes for different network analysis
        self.network_colors = {
            'community': plt.cm.Set3,
            'centrality': plt.cm.viridis,
            'degree': plt.cm.plasma,
            'clustering': plt.cm.coolwarm
        }
        
        logger.info("NetworkVisualizer initialized")
    
    def analyze_network_structure(self) -> Dict[str, Any]:
        """
        Perform comprehensive network structure analysis.
        
        Returns:
            Dictionary with network analysis results
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        try:
            graph = self.atlas_engine.graph
            
            if not graph.nodes():
                return {'error': 'No nodes in graph'}
            
            analysis = {
                'basic_metrics': {
                    'nodes': graph.number_of_nodes(),
                    'edges': graph.number_of_edges(),
                    'density': nx.density(graph),
                    'is_connected': nx.is_weakly_connected(graph) if graph.is_directed() else nx.is_connected(graph)
                },
                'centrality_measures': {},
                'clustering': {},
                'communities': {},
                'paths': {}
            }
            
            # Calculate centrality measures (for smaller graphs with error handling)
            if graph.number_of_nodes() <= 500:
                centrality_measures = {
                    'degree_centrality': nx.degree_centrality(graph),
                    'betweenness_centrality': nx.betweenness_centrality(graph),
                    'closeness_centrality': nx.closeness_centrality(graph)
                }
                
                # Try eigenvector centrality with multiple strategies
                try:
                    centrality_measures['eigenvector_centrality'] = nx.eigenvector_centrality(
                        graph, max_iter=1000, tol=1e-06
                    )
                except nx.PowerIterationFailedConvergence:
                    try:
                        # Fallback with more iterations and different tolerance
                        centrality_measures['eigenvector_centrality'] = nx.eigenvector_centrality(
                            graph, max_iter=5000, tol=1e-04
                        )
                    except nx.PowerIterationFailedConvergence:
                        # Final fallback: use PageRank as approximation
                        logger.warning("Eigenvector centrality failed, using PageRank approximation")
                        centrality_measures['eigenvector_centrality'] = nx.pagerank(graph, max_iter=1000)
                except Exception as e:
                    logger.warning(f"Eigenvector centrality calculation failed: {e}")
                    centrality_measures['eigenvector_centrality'] = {}
                
                analysis['centrality_measures'] = centrality_measures
            
            # Clustering analysis
            if not graph.is_directed():
                analysis['clustering'] = {
                    'clustering_coefficient': nx.clustering(graph),
                    'average_clustering': nx.average_clustering(graph),
                    'transitivity': nx.transitivity(graph)
                }
            
            # Community detection
            if not graph.is_directed() and graph.number_of_nodes() > 1:
                try:
                    communities = nx.community.greedy_modularity_communities(graph)
                    analysis['communities'] = {
                        'community_count': len(communities),
                        'modularity': nx.community.modularity(graph, communities),
                        'community_sizes': [len(c) for c in communities]
                    }
                except:
                    analysis['communities'] = {'error': 'Community detection failed'}
            
            # Path analysis
            if graph.is_connected() if not graph.is_directed() else nx.is_weakly_connected(graph):
                try:
                    if graph.number_of_nodes() <= 100:  # Only for small graphs
                        if graph.is_directed():
                            analysis['paths'] = {
                                'average_shortest_path': nx.average_shortest_path_length(graph)
                            }
                        else:
                            analysis['paths'] = {
                                'average_shortest_path': nx.average_shortest_path_length(graph),
                                'diameter': nx.diameter(graph),
                                'radius': nx.radius(graph)
                            }
                except:
                    analysis['paths'] = {'error': 'Path analysis failed'}
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze network structure: {e}")
            return {'error': str(e)}
    
    def visualize_centrality_analysis(
        self,
        centrality_type: str = 'degree',
        figsize: Tuple[int, int] = (12, 8),
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Visualize centrality measures across the network.
        
        Args:
            centrality_type: Type of centrality ('degree', 'betweenness', 'closeness', 'eigenvector')
            figsize: Figure size tuple
            save_path: Optional path to save the figure
            
        Returns:
            Matplotlib figure object
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
            graph = self.atlas_engine.graph
            
            if not graph.nodes():
                ax1.text(0.5, 0.5, 'No nodes to analyze', ha='center', va='center')
                return fig
            
            # Calculate centrality
            if centrality_type == 'degree':
                centrality = nx.degree_centrality(graph)
            elif centrality_type == 'betweenness':
                centrality = nx.betweenness_centrality(graph)
            elif centrality_type == 'closeness':
                centrality = nx.closeness_centrality(graph)
            elif centrality_type == 'eigenvector':
                try:
                    centrality = nx.eigenvector_centrality(graph, max_iter=1000, tol=1e-06)
                except nx.PowerIterationFailedConvergence:
                    logger.warning("Eigenvector centrality failed to converge, using PageRank")
                    centrality = nx.pagerank(graph, max_iter=1000)
            else:
                raise ValueError(f"Unknown centrality type: {centrality_type}")
            
            # 1. Network visualization with centrality-based node sizing
            pos = nx.spring_layout(graph, k=1, iterations=50)
            
            node_sizes = [centrality[node] * 1000 + 100 for node in graph.nodes()]
            node_colors = [centrality[node] for node in graph.nodes()]
            
            nx.draw_networkx_nodes(
                graph, pos, ax=ax1,
                node_size=node_sizes,
                node_color=node_colors,
                cmap=self.network_colors['centrality'],
                alpha=0.7
            )
            
            nx.draw_networkx_edges(
                graph, pos, ax=ax1,
                edge_color='gray',
                alpha=0.3,
                arrows=True if graph.is_directed() else False
            )
            
            ax1.set_title(f'{centrality_type.title()} Centrality Network')
            ax1.axis('off')
            
            # 2. Centrality distribution histogram
            centrality_values = list(centrality.values())
            ax2.hist(centrality_values, bins=20, alpha=0.7, 
                    color=self.network_colors['centrality'](0.7), edgecolor='black')
            ax2.set_xlabel(f'{centrality_type.title()} Centrality')
            ax2.set_ylabel('Frequency')
            ax2.set_title('Centrality Distribution')
            ax2.axvline(np.mean(centrality_values), color='red', linestyle='--',
                       label=f'Mean: {np.mean(centrality_values):.3f}')
            ax2.legend()
            
            # 3. Top nodes by centrality
            top_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]
            if top_nodes:
                nodes, values = zip(*top_nodes)
                bars = ax3.barh(range(len(nodes)), values, 
                               color=self.network_colors['centrality'](0.7))
                ax3.set_yticks(range(len(nodes)))
                ax3.set_yticklabels([node[:15] + '...' if len(node) > 15 else node 
                                   for node in nodes])
                ax3.set_xlabel(f'{centrality_type.title()} Centrality')
                ax3.set_title(f'Top 10 Nodes by {centrality_type.title()} Centrality')
            
            # 4. Centrality correlation with degree
            degrees = dict(graph.degree())
            degree_values = [degrees[node] for node in graph.nodes()]
            centrality_values = [centrality[node] for node in graph.nodes()]
            
            ax4.scatter(degree_values, centrality_values, alpha=0.6,
                       color=self.network_colors['centrality'](0.7))
            ax4.set_xlabel('Node Degree')
            ax4.set_ylabel(f'{centrality_type.title()} Centrality')
            ax4.set_title(f'Degree vs {centrality_type.title()} Centrality')
            
            # Calculate correlation
            correlation = np.corrcoef(degree_values, centrality_values)[0, 1]
            ax4.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
                    transform=ax4.transAxes, va='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to visualize centrality analysis: {e}")
            raise
    
    def visualize_community_structure(
        self,
        figsize: Tuple[int, int] = (14, 8),
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Visualize community structure in the network.
        
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
            graph = self.atlas_engine.graph
            
            if not graph.nodes():
                ax1.text(0.5, 0.5, 'No nodes to analyze', ha='center', va='center')
                return fig
            
            # Convert to undirected for community detection
            if graph.is_directed():
                undirected_graph = graph.to_undirected()
            else:
                undirected_graph = graph
            
            # Detect communities
            try:
                communities = list(nx.community.greedy_modularity_communities(undirected_graph))
                modularity = nx.community.modularity(undirected_graph, communities)
            except:
                ax1.text(0.5, 0.5, 'Community detection failed', ha='center', va='center')
                return fig
            
            # 1. Network with community colors
            pos = nx.spring_layout(undirected_graph, k=1, iterations=50)
            
            # Assign colors to communities
            community_colors = {}
            color_map = plt.cm.Set3(np.linspace(0, 1, len(communities)))
            
            for i, community in enumerate(communities):
                for node in community:
                    community_colors[node] = color_map[i]
            
            node_colors = [community_colors.get(node, 'gray') for node in undirected_graph.nodes()]
            
            nx.draw_networkx_nodes(
                undirected_graph, pos, ax=ax1,
                node_color=node_colors,
                node_size=300,
                alpha=0.8
            )
            
            nx.draw_networkx_edges(
                undirected_graph, pos, ax=ax1,
                edge_color='gray',
                alpha=0.3
            )
            
            ax1.set_title(f'Community Structure (Modularity: {modularity:.3f})')
            ax1.axis('off')
            
            # 2. Community size distribution
            community_sizes = [len(c) for c in communities]
            ax2.hist(community_sizes, bins=max(1, len(set(community_sizes))), 
                    alpha=0.7, color='skyblue', edgecolor='black')
            ax2.set_xlabel('Community Size')
            ax2.set_ylabel('Frequency')
            ax2.set_title('Community Size Distribution')
            
            # 3. Modularity optimization curve (simulated)
            resolutions = np.linspace(0.5, 2.0, 20)
            modularities = []
            community_counts = []
            
            for resolution in resolutions:
                try:
                    temp_communities = nx.community.greedy_modularity_communities(
                        undirected_graph, resolution=resolution
                    )
                    temp_modularity = nx.community.modularity(undirected_graph, temp_communities)
                    modularities.append(temp_modularity)
                    community_counts.append(len(temp_communities))
                except:
                    modularities.append(0)
                    community_counts.append(0)
            
            ax3_twin = ax3.twinx()
            line1 = ax3.plot(resolutions, modularities, 'b-o', markersize=4, label='Modularity')
            line2 = ax3_twin.plot(resolutions, community_counts, 'r-s', markersize=4, label='Community Count')
            
            ax3.set_xlabel('Resolution Parameter')
            ax3.set_ylabel('Modularity', color='b')
            ax3_twin.set_ylabel('Number of Communities', color='r')
            ax3.set_title('Modularity vs Resolution')
            
            # Combine legends
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax3.legend(lines, labels, loc='upper right')
            
            # 4. Inter-community vs intra-community edges
            intra_edges = 0
            inter_edges = 0
            
            # Create node to community mapping
            node_to_community = {}
            for i, community in enumerate(communities):
                for node in community:
                    node_to_community[node] = i
            
            for edge in undirected_graph.edges():
                node1, node2 = edge
                if node_to_community.get(node1) == node_to_community.get(node2):
                    intra_edges += 1
                else:
                    inter_edges += 1
            
            edge_types = ['Intra-community', 'Inter-community']
            edge_counts = [intra_edges, inter_edges]
            colors = ['lightgreen', 'lightcoral']
            
            bars = ax4.bar(edge_types, edge_counts, color=colors, alpha=0.7)
            ax4.set_ylabel('Number of Edges')
            ax4.set_title('Edge Distribution')
            
            # Add percentage labels
            total_edges = intra_edges + inter_edges
            for bar, count in zip(bars, edge_counts):
                percentage = (count / total_edges) * 100 if total_edges > 0 else 0
                ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                        f'{percentage:.1f}%', ha='center', va='bottom')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to visualize community structure: {e}")
            raise
    
    def visualize_network_evolution(
        self,
        time_steps: int = 10,
        figsize: Tuple[int, int] = (16, 10),
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Visualize network evolution over time (simulated).
        
        Args:
            time_steps: Number of time steps to simulate
            figsize: Figure size tuple
            save_path: Optional path to save the figure
            
        Returns:
            Matplotlib figure object
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        try:
            fig = plt.figure(figsize=figsize)
            gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
            
            graph = self.atlas_engine.graph
            
            if not graph.nodes():
                ax = fig.add_subplot(gs[:, :])
                ax.text(0.5, 0.5, 'No nodes to analyze', ha='center', va='center')
                return fig
            
            # Simulate network growth over time
            initial_nodes = min(5, len(graph.nodes()))
            node_list = list(graph.nodes())
            edge_list = list(graph.edges())
            
            evolution_data = []
            
            for step in range(time_steps):
                # Calculate how many nodes/edges to include at this step
                node_fraction = (step + 1) / time_steps
                edge_fraction = (step + 1) / time_steps
                
                nodes_to_include = int(len(node_list) * node_fraction)
                edges_to_include = int(len(edge_list) * edge_fraction)
                
                # Create subgraph for this time step
                current_nodes = node_list[:nodes_to_include]
                current_edges = [e for e in edge_list[:edges_to_include] 
                               if e[0] in current_nodes and e[1] in current_nodes]
                
                step_graph = graph.subgraph(current_nodes).copy()
                
                # Calculate metrics
                step_data = {
                    'step': step,
                    'nodes': step_graph.number_of_nodes(),
                    'edges': step_graph.number_of_edges(),
                    'density': nx.density(step_graph) if step_graph.number_of_nodes() > 1 else 0,
                    'avg_degree': np.mean([d for n, d in step_graph.degree()]) if step_graph.nodes() else 0
                }
                
                # Add clustering coefficient for undirected graphs
                if not step_graph.is_directed() and step_graph.number_of_nodes() > 2:
                    step_data['clustering'] = nx.average_clustering(step_graph)
                else:
                    step_data['clustering'] = 0
                
                evolution_data.append(step_data)
            
            df = pd.DataFrame(evolution_data)
            
            # 1. Network size evolution (top left, 2 columns)
            ax1 = fig.add_subplot(gs[0, :2])
            ax1.plot(df['step'], df['nodes'], 'bo-', label='Nodes', markersize=6)
            ax1_twin = ax1.twinx()
            ax1_twin.plot(df['step'], df['edges'], 'ro-', label='Edges', markersize=6)
            
            ax1.set_xlabel('Time Step')
            ax1.set_ylabel('Number of Nodes', color='b')
            ax1_twin.set_ylabel('Number of Edges', color='r')
            ax1.set_title('Network Growth Over Time')
            ax1.grid(True, alpha=0.3)
            
            # Combine legends
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax1_twin.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            
            # 2. Network density evolution (top right)
            ax2 = fig.add_subplot(gs[0, 2])
            ax2.plot(df['step'], df['density'], 'go-', markersize=6)
            ax2.set_xlabel('Time Step')
            ax2.set_ylabel('Density')
            ax2.set_title('Network Density Evolution')
            ax2.grid(True, alpha=0.3)
            
            # 3. Average degree evolution (bottom left)
            ax3 = fig.add_subplot(gs[1, 0])
            ax3.plot(df['step'], df['avg_degree'], 'mo-', markersize=6)
            ax3.set_xlabel('Time Step')
            ax3.set_ylabel('Average Degree')
            ax3.set_title('Average Degree Evolution')
            ax3.grid(True, alpha=0.3)
            
            # 4. Clustering coefficient evolution (bottom middle)
            ax4 = fig.add_subplot(gs[1, 1])
            ax4.plot(df['step'], df['clustering'], 'co-', markersize=6)
            ax4.set_xlabel('Time Step')
            ax4.set_ylabel('Clustering Coefficient')
            ax4.set_title('Clustering Evolution')
            ax4.grid(True, alpha=0.3)
            
            # 5. Final network snapshot (bottom right)
            ax5 = fig.add_subplot(gs[1, 2])
            pos = nx.spring_layout(graph, k=0.5, iterations=30)
            
            # Color nodes by when they were added (simulated)
            node_colors = []
            for node in graph.nodes():
                # Simulate addition time based on node position in list
                add_time = node_list.index(node) / len(node_list)
                node_colors.append(add_time)
            
            nx.draw_networkx_nodes(
                graph, pos, ax=ax5,
                node_color=node_colors,
                node_size=100,
                cmap='viridis',
                alpha=0.8
            )
            
            nx.draw_networkx_edges(
                graph, pos, ax=ax5,
                edge_color='gray',
                alpha=0.3,
                arrows=True if graph.is_directed() else False
            )
            
            ax5.set_title('Final Network State')
            ax5.axis('off')
            
            plt.suptitle('Network Evolution Analysis', fontsize=16, fontweight='bold')
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to visualize network evolution: {e}")
            raise
    
    def export_network_analysis(self, output_path: str) -> Dict[str, Any]:
        """
        Export comprehensive network analysis results.
        
        Args:
            output_path: Base path for output files
            
        Returns:
            Dictionary with analysis results and file paths
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        try:
            # Perform comprehensive analysis
            analysis = self.analyze_network_structure()
            
            # Add visualization paths
            analysis['visualizations_generated'] = []
            
            # Generate centrality analysis
            centrality_fig = self.visualize_centrality_analysis()
            centrality_path = f"{output_path}_centrality.png"
            centrality_fig.savefig(centrality_path, dpi=300, bbox_inches='tight')
            analysis['visualizations_generated'].append(centrality_path)
            plt.close(centrality_fig)
            
            # Generate community analysis
            community_fig = self.visualize_community_structure()
            community_path = f"{output_path}_communities.png"
            community_fig.savefig(community_path, dpi=300, bbox_inches='tight')
            analysis['visualizations_generated'].append(community_path)
            plt.close(community_fig)
            
            # Generate evolution analysis
            evolution_fig = self.visualize_network_evolution()
            evolution_path = f"{output_path}_evolution.png"
            evolution_fig.savefig(evolution_path, dpi=300, bbox_inches='tight')
            analysis['visualizations_generated'].append(evolution_path)
            plt.close(evolution_fig)
            
            # Save analysis as JSON
            import json
            analysis_path = f"{output_path}_network_analysis.json"
            with open(analysis_path, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            
            logger.info(f"Network analysis exported to {analysis_path}")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to export network analysis: {e}")
            raise 