"""
Animation visualization module for ATLAS.

Provides comprehensive animation capabilities for visualizing dynamic
knowledge graph evolution, pattern discovery, query execution, and system growth.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple, Union
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.figure import Figure
import networkx as nx
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict
import io
import base64

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

logger = logging.getLogger(__name__)


class AnimationVisualizer:
    """
    Comprehensive animation visualization for ATLAS knowledge management system.
    
    Provides various animation types including network growth, pattern discovery,
    query execution visualization, and temporal analysis animations.
    """
    
    def __init__(self, atlas_engine=None, pattern_engine=None):
        """
        Initialize the AnimationVisualizer.
        
        Args:
            atlas_engine: Optional ATLAS engine instance
            pattern_engine: Optional pattern engine instance
        """
        self.atlas_engine = atlas_engine
        self.pattern_engine = pattern_engine
        
        # Animation configuration
        self.frame_duration = 500  # milliseconds
        self.dpi = 100
        self.figsize = (12, 8)
        
        # Color schemes for animations
        self.node_colors = {
            'entity': '#4CAF50',
            'pattern': '#2196F3', 
            'query': '#FF9800',
            'attribute': '#9C27B0',
            'new': '#F44336',
            'active': '#FFC107',
            'complete': '#4CAF50'
        }
        
        logger.info("AnimationVisualizer initialized")
    
    def animate_network_growth(
        self,
        time_steps: int = 30,
        figsize: Tuple[int, int] = (12, 8),
        save_path: Optional[str] = None,
        interval: int = 500
    ) -> Optional[animation.FuncAnimation]:
        """
        Create an animation showing network growth over time.
        
        Args:
            time_steps: Number of animation frames
            figsize: Figure size tuple
            save_path: Optional path to save the animation
            interval: Frame interval in milliseconds
            
        Returns:
            Matplotlib animation object
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        try:
            fig, ax = plt.subplots(figsize=figsize)
            
            # Get current graph
            full_graph = self.atlas_engine.graph.copy()
            nodes = list(full_graph.nodes())
            edges = list(full_graph.edges())
            
            if not nodes:
                ax.text(0.5, 0.5, 'No nodes to animate', ha='center', va='center')
                return None
            
            # Create animation frames data
            frames_data = []
            for step in range(time_steps):
                # Calculate how many nodes/edges to show
                node_fraction = (step + 1) / time_steps
                edge_fraction = (step + 1) / time_steps
                
                current_nodes = nodes[:int(len(nodes) * node_fraction)]
                current_edges = [e for e in edges[:int(len(edges) * edge_fraction)]
                               if e[0] in current_nodes and e[1] in current_nodes]
                
                frames_data.append((current_nodes, current_edges))
            
            # Calculate layout for full graph (consistent positioning)
            pos = nx.spring_layout(full_graph, k=1, iterations=50)
            
            def animate_frame(frame_num):
                ax.clear()
                
                current_nodes, current_edges = frames_data[frame_num]
                
                if current_nodes:
                    # Create subgraph for current frame
                    frame_graph = full_graph.subgraph(current_nodes).copy()
                    
                    # Add edges that exist in current frame
                    frame_graph.clear_edges()
                    frame_graph.add_edges_from(current_edges)
                    
                    # Get node colors based on type
                    node_colors = []
                    for node in current_nodes:
                        node_data = full_graph.nodes[node]
                        node_type = node_data.get('node_type', 'entity')
                        node_colors.append(self.node_colors.get(node_type, '#CCCCCC'))
                    
                    # Draw network
                    current_pos = {node: pos[node] for node in current_nodes}
                    
                    nx.draw_networkx_nodes(
                        frame_graph, current_pos, ax=ax,
                        node_color=node_colors,
                        node_size=300,
                        alpha=0.8
                    )
                    
                    if current_edges:
                        nx.draw_networkx_edges(
                            frame_graph, current_pos, ax=ax,
                            edge_color='gray',
                            alpha=0.6,
                            arrows=True,
                            arrowsize=20
                        )
                    
                    # Add labels for important nodes
                    important_nodes = [node for node in current_nodes[:5]]
                    if important_nodes:
                        labels = {node: node[:8] + '...' if len(node) > 8 else node 
                                for node in important_nodes}
                        nx.draw_networkx_labels(frame_graph, current_pos, labels, ax=ax, font_size=8)
                
                ax.set_title(f'Network Growth Animation (Step {frame_num + 1}/{time_steps})\n'
                           f'Nodes: {len(current_nodes)}, Edges: {len(current_edges)}',
                           fontsize=14, fontweight='bold')
                ax.axis('off')
                
                # Add metrics text
                max_edges = max(1.0, len(current_nodes) * (len(current_nodes) - 1) / 2.0)
                metrics_text = f'Density: {len(current_edges) / max_edges:.3f}'
                ax.text(0.02, 0.98, metrics_text, transform=ax.transAxes, 
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"),
                       verticalalignment='top')
            
            # Create animation
            anim = animation.FuncAnimation(
                fig, animate_frame, frames=time_steps,
                interval=interval, repeat=True, blit=False
            )
            
            if save_path:
                writer = animation.PillowWriter(fps=2)
                anim.save(save_path, writer=writer, dpi=self.dpi)
                logger.info(f"Network growth animation saved to {save_path}")
            
            return anim
            
        except Exception as e:
            logger.error(f"Failed to create network growth animation: {e}")
            raise
    
    def animate_pattern_discovery(
        self,
        time_steps: int = 20,
        figsize: Tuple[int, int] = (12, 8),
        save_path: Optional[str] = None,
        interval: int = 600
    ) -> Optional[animation.FuncAnimation]:
        """
        Create an animation showing pattern discovery process.
        
        Args:
            time_steps: Number of animation frames
            figsize: Figure size tuple
            save_path: Optional path to save the animation
            interval: Frame interval in milliseconds
            
        Returns:
            Matplotlib animation object
        """
        if not self.atlas_engine or not self.pattern_engine:
            raise ValueError("Both ATLAS engine and pattern engine required")
        
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
            
            # Get patterns
            patterns = {}
            for node_id in self.atlas_engine.graph.nodes():
                node_data = self.atlas_engine.graph.nodes[node_id]
                if node_data.get('node_type') == 'pattern':
                    patterns[node_id] = node_data
            
            if not patterns:
                ax1.text(0.5, 0.5, 'No patterns to animate', ha='center', va='center')
                ax2.text(0.5, 0.5, 'No data available', ha='center', va='center')
                return None
            
            pattern_list = list(patterns.keys())
            
            # Simulate pattern discovery timeline
            discovery_timeline = []
            for step in range(time_steps):
                step_patterns = pattern_list[:int(len(pattern_list) * (step + 1) / time_steps)]
                discovery_timeline.append(step_patterns)
            
            def animate_discovery(frame_num):
                ax1.clear()
                ax2.clear()
                
                current_patterns = discovery_timeline[frame_num]
                
                # Left plot: Pattern hierarchy
                if current_patterns:
                    pattern_graph = nx.DiGraph()
                    
                    for pattern_id in current_patterns:
                        pattern_graph.add_node(pattern_id)
                        pattern_data = patterns[pattern_id]
                        
                        # Add hierarchy edges
                        for parent in pattern_data.get('parents', []):
                            if parent in current_patterns:
                                pattern_graph.add_edge(parent, pattern_id)
                    
                    if pattern_graph.nodes():
                        pos = nx.spring_layout(pattern_graph, k=2, iterations=30)
                        
                        # Color nodes by discovery order
                        node_colors = []
                        for node in pattern_graph.nodes():
                            discovery_order = pattern_list.index(node) / len(pattern_list)
                            node_colors.append(plt.cm.viridis(discovery_order))
                        
                        nx.draw_networkx_nodes(
                            pattern_graph, pos, ax=ax1,
                            node_color=node_colors,
                            node_size=400,
                            alpha=0.8
                        )
                        
                        if pattern_graph.edges():
                            nx.draw_networkx_edges(
                                pattern_graph, pos, ax=ax1,
                                edge_color='gray',
                                alpha=0.6,
                                arrows=True,
                                arrowsize=20
                            )
                        
                        # Add pattern labels
                        labels = {node: node[:6] + '...' if len(node) > 6 else node 
                                for node in pattern_graph.nodes()}
                        nx.draw_networkx_labels(pattern_graph, pos, labels, ax=ax1, font_size=8)
                
                ax1.set_title(f'Pattern Discovery Progress\n'
                            f'Discovered: {len(current_patterns)}/{len(pattern_list)} patterns',
                            fontsize=12, fontweight='bold')
                ax1.axis('off')
                
                # Right plot: Discovery metrics
                if current_patterns:
                    metrics_data = []
                    for pattern_id in current_patterns:
                        pattern_data = patterns[pattern_id]
                        qkit_size = len(pattern_data.get('qkit', []))
                        usage_count = len(pattern_data.get('instances', []))
                        metrics_data.append({
                            'pattern': pattern_id[:8],
                            'qkit_size': qkit_size,
                            'usage': usage_count
                        })
                    
                    df = pd.DataFrame(metrics_data)
                    
                    # Bar plot of QKit sizes
                    bars = ax2.bar(range(len(df)), df['qkit_size'], 
                                  color=self.node_colors['pattern'], alpha=0.7)
                    ax2.set_xlabel('Pattern Index')
                    ax2.set_ylabel('QKit Size')
                    ax2.set_title('Pattern Complexity (QKit Size)')
                    
                    # Add usage count as text
                    for i, (bar, usage) in enumerate(zip(bars, df['usage'])):
                        ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.1,
                               f'U:{usage}', ha='center', va='bottom', fontsize=8)
                
                # Add timeline indicator
                progress = (frame_num + 1) / time_steps
                fig.suptitle(f'Pattern Discovery Animation (Step {frame_num + 1}/{time_steps})\n'
                           f'Progress: {progress:.1%}', fontsize=14, fontweight='bold')
            
            # Create animation
            anim = animation.FuncAnimation(
                fig, animate_discovery, frames=time_steps,
                interval=interval, repeat=True, blit=False
            )
            
            if save_path:
                writer = animation.PillowWriter(fps=1.5)
                anim.save(save_path, writer=writer, dpi=self.dpi)
                logger.info(f"Pattern discovery animation saved to {save_path}")
            
            return anim
            
        except Exception as e:
            logger.error(f"Failed to create pattern discovery animation: {e}")
            raise
    
    def animate_query_execution(
        self,
        query_steps: int = 15,
        figsize: Tuple[int, int] = (12, 8),
        save_path: Optional[str] = None,
        interval: int = 400
    ) -> Optional[animation.FuncAnimation]:
        """
        Create an animation showing query execution process.
        
        Args:
            query_steps: Number of query execution steps to simulate
            figsize: Figure size tuple
            save_path: Optional path to save the animation
            interval: Frame interval in milliseconds
            
        Returns:
            Matplotlib animation object
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        try:
            fig, ax = plt.subplots(figsize=figsize)
            
            # Get graph data
            graph = self.atlas_engine.graph.copy()
            
            if not graph.nodes():
                ax.text(0.5, 0.5, 'No nodes for query simulation', ha='center', va='center')
                return None
            
            # Calculate layout
            pos = nx.spring_layout(graph, k=1, iterations=50)
            
            # Simulate query execution steps
            nodes = list(graph.nodes())
            query_simulation = []
            
            # Simulate search expansion from a random starting node
            start_node = np.random.choice(nodes)
            visited = set()
            current_frontier = {start_node}
            
            for step in range(query_steps):
                step_data = {
                    'visited': visited.copy(),
                    'frontier': current_frontier.copy(),
                    'results': set()
                }
                
                # Add current frontier to visited
                visited.update(current_frontier)
                
                # Expand frontier
                new_frontier = set()
                for node in current_frontier:
                    neighbors = set(graph.neighbors(node))
                    new_frontier.update(neighbors - visited)
                
                # Simulate finding results (some nodes become results)
                if step > query_steps // 3:  # Start finding results after initial exploration
                    potential_results = list(current_frontier)
                    if potential_results:
                        num_results = min(2, len(potential_results))
                        results = set(np.random.choice(potential_results, num_results, replace=False))
                        step_data['results'] = results
                
                current_frontier = new_frontier
                query_simulation.append(step_data)
                
                if not new_frontier:  # No more nodes to explore
                    break
            
            def animate_query(frame_num):
                ax.clear()
                
                if frame_num >= len(query_simulation):
                    frame_num = len(query_simulation) - 1
                
                step_data = query_simulation[frame_num]
                visited = step_data['visited']
                frontier = step_data['frontier']
                results = step_data['results']
                
                # Color nodes based on query status
                node_colors = []
                node_sizes = []
                
                for node in graph.nodes():
                    if node in results:
                        node_colors.append(self.node_colors['complete'])  # Green for results
                        node_sizes.append(500)
                    elif node in frontier:
                        node_colors.append(self.node_colors['active'])    # Yellow for current frontier
                        node_sizes.append(400)
                    elif node in visited:
                        node_colors.append(self.node_colors['pattern'])   # Blue for visited
                        node_sizes.append(300)
                    else:
                        node_colors.append('#CCCCCC')                     # Gray for unvisited
                        node_sizes.append(200)
                
                # Draw network
                nx.draw_networkx_nodes(
                    graph, pos, ax=ax,
                    node_color=node_colors,
                    node_size=node_sizes,
                    alpha=0.8
                )
                
                nx.draw_networkx_edges(
                    graph, pos, ax=ax,
                    edge_color='lightgray',
                    alpha=0.5,
                    arrows=True,
                    arrowsize=15
                )
                
                # Highlight search path edges
                if visited:
                    search_edges = []
                    for node in visited:
                        for neighbor in graph.neighbors(node):
                            if neighbor in visited:
                                search_edges.append((node, neighbor))
                    
                    if search_edges:
                        nx.draw_networkx_edges(
                            graph, pos, edgelist=search_edges, ax=ax,
                            edge_color='orange',
                            alpha=0.8,
                            width=2,
                            arrows=True,
                            arrowsize=15
                        )
                
                # Add legend
                legend_elements = [
                    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.node_colors['complete'],
                              markersize=10, label=f'Results ({len(results)})'),
                    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.node_colors['active'],
                              markersize=10, label=f'Frontier ({len(frontier)})'),
                    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=self.node_colors['pattern'],
                              markersize=10, label=f'Visited ({len(visited)})'),
                    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#CCCCCC',
                              markersize=10, label='Unvisited')
                ]
                ax.legend(handles=legend_elements, loc='upper right')
                
                ax.set_title(f'Query Execution Animation (Step {frame_num + 1}/{len(query_simulation)})\n'
                           f'Exploring knowledge graph to find relevant results',
                           fontsize=12, fontweight='bold')
                ax.axis('off')
            
            # Create animation
            anim = animation.FuncAnimation(
                fig, animate_query, frames=len(query_simulation),
                interval=interval, repeat=True, blit=False
            )
            
            if save_path:
                writer = animation.PillowWriter(fps=2.5)
                anim.save(save_path, writer=writer, dpi=self.dpi)
                logger.info(f"Query execution animation saved to {save_path}")
            
            return anim
            
        except Exception as e:
            logger.error(f"Failed to create query execution animation: {e}")
            raise
    
    def create_interactive_timeline(
        self,
        time_window_days: int = 30,
        figsize: Tuple[int, int] = (14, 8),
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Create an interactive timeline visualization showing system activity.
        
        Args:
            time_window_days: Number of days to simulate
            figsize: Figure size tuple
            save_path: Optional path to save the figure
            
        Returns:
            Matplotlib figure object
        """
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
            
            # Generate timeline data
            dates = pd.date_range(start=datetime.now() - timedelta(days=time_window_days),
                                 end=datetime.now(), freq='D')
            
            # Simulate system activity data
            np.random.seed(42)
            entity_creations = np.random.poisson(3, len(dates))
            pattern_discoveries = np.random.poisson(1, len(dates))
            query_executions = np.random.poisson(8, len(dates))
            system_events = np.random.poisson(2, len(dates))
            
            # Cumulative data
            cum_entities = np.cumsum(entity_creations)
            cum_patterns = np.cumsum(pattern_discoveries)
            cum_queries = np.cumsum(query_executions)
            
            # 1. Daily activity timeline
            ax1.plot(dates, entity_creations, 'o-', label='Entities Created', 
                    color=self.node_colors['entity'], markersize=4)
            ax1.plot(dates, pattern_discoveries, 's-', label='Patterns Discovered', 
                    color=self.node_colors['pattern'], markersize=4)
            ax1.plot(dates, query_executions, '^-', label='Queries Executed', 
                    color=self.node_colors['query'], markersize=4)
            
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Daily Count')
            ax1.set_title('Daily System Activity Timeline')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis='x', rotation=45)
            
            # 2. Cumulative growth
            ax2.plot(dates, cum_entities, label='Total Entities', 
                    color=self.node_colors['entity'], linewidth=2)
            ax2.plot(dates, cum_patterns, label='Total Patterns', 
                    color=self.node_colors['pattern'], linewidth=2)
            ax2.plot(dates, cum_queries, label='Total Queries', 
                    color=self.node_colors['query'], linewidth=2)
            
            ax2.set_xlabel('Date')
            ax2.set_ylabel('Cumulative Count')
            ax2.set_title('Cumulative System Growth')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            ax2.tick_params(axis='x', rotation=45)
            
            # 3. Activity heatmap (by day of week and hour)
            # Simulate hourly data for recent week
            hours = range(24)
            days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            
            # Create activity matrix
            activity_matrix = np.random.exponential(2, (7, 24))
            # Add patterns: higher activity during work hours and weekdays
            for day in range(5):  # Weekdays
                for hour in range(9, 18):  # Work hours
                    activity_matrix[day, hour] *= 1.5
            
            im = ax3.imshow(activity_matrix, cmap='YlOrRd', aspect='auto')
            ax3.set_xticks(range(0, 24, 2))
            ax3.set_xticklabels([f'{h}:00' for h in range(0, 24, 2)])
            ax3.set_yticks(range(7))
            ax3.set_yticklabels(days_of_week)
            ax3.set_xlabel('Hour of Day')
            ax3.set_ylabel('Day of Week')
            ax3.set_title('Activity Heatmap (Recent Week)')
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax3, shrink=0.8)
            cbar.set_label('Activity Level')
            
            # 4. Event distribution pie chart
            event_types = ['Entity Operations', 'Pattern Analysis', 'Query Processing', 'System Maintenance']
            event_counts = [np.sum(entity_creations), np.sum(pattern_discoveries), 
                           np.sum(query_executions), np.sum(system_events)]
            colors = [self.node_colors['entity'], self.node_colors['pattern'], 
                     self.node_colors['query'], self.node_colors['active']]
            
            wedges, texts, autotexts = ax4.pie(event_counts, labels=event_types, colors=colors,
                                              autopct='%1.1f%%', startangle=90)
            ax4.set_title('Event Distribution (Total)')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
                logger.info(f"Interactive timeline saved to {save_path}")
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create interactive timeline: {e}")
            raise
    
    def animate_system_metrics(
        self,
        time_steps: int = 25,
        figsize: Tuple[int, int] = (14, 8),
        save_path: Optional[str] = None,
        interval: int = 300
    ) -> Optional[animation.FuncAnimation]:
        """
        Create an animation showing system metrics evolution.
        
        Args:
            time_steps: Number of animation frames
            figsize: Figure size tuple
            save_path: Optional path to save the animation
            interval: Frame interval in milliseconds
            
        Returns:
            Matplotlib animation object
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
            
            # Simulate metrics evolution
            np.random.seed(42)
            
            # Generate baseline metrics from current system
            base_metrics = self.atlas_engine.get_metrics()
            base_entities = base_metrics.get('entities_created', 10)
            base_patterns = base_metrics.get('patterns_created', 5)
            base_relationships = base_metrics.get('relationships_added', 15)
            
            # Simulate growth over time
            entity_growth = [base_entities + int(i * 2 + np.random.poisson(1)) for i in range(time_steps)]
            pattern_growth = [base_patterns + int(i * 0.5 + np.random.poisson(0.3)) for i in range(time_steps)]
            relationship_growth = [base_relationships + int(i * 3 + np.random.poisson(2)) for i in range(time_steps)]
            
            # Calculate derived metrics
            density_evolution = []
            complexity_evolution = []
            efficiency_evolution = []
            
            for step in range(time_steps):
                entities = entity_growth[step]
                patterns = pattern_growth[step]
                relationships = relationship_growth[step]
                
                # Network density (simplified calculation)
                max_possible_edges = entities * (entities - 1) / 2
                density = min(1.0, relationships / max(1, max_possible_edges))
                density_evolution.append(density)
                
                # System complexity (patterns per entity ratio)
                complexity = patterns / max(1, entities)
                complexity_evolution.append(complexity)
                
                # Efficiency (relationships per pattern)
                efficiency = relationships / max(1, patterns)
                efficiency_evolution.append(efficiency)
            
            def animate_metrics(frame_num):
                for ax in [ax1, ax2, ax3, ax4]:
                    ax.clear()
                
                # Current step data
                steps = range(frame_num + 1)
                current_entities = entity_growth[:frame_num + 1]
                current_patterns = pattern_growth[:frame_num + 1]
                current_relationships = relationship_growth[:frame_num + 1]
                current_density = density_evolution[:frame_num + 1]
                current_complexity = complexity_evolution[:frame_num + 1]
                current_efficiency = efficiency_evolution[:frame_num + 1]
                
                # 1. Component growth
                ax1.plot(steps, current_entities, 'o-', color=self.node_colors['entity'], 
                        label='Entities', linewidth=2, markersize=6)
                ax1.plot(steps, current_patterns, 's-', color=self.node_colors['pattern'], 
                        label='Patterns', linewidth=2, markersize=6)
                ax1.plot(steps, current_relationships, '^-', color=self.node_colors['query'], 
                        label='Relationships', linewidth=2, markersize=6)
                
                ax1.set_xlabel('Time Step')
                ax1.set_ylabel('Count')
                ax1.set_title('System Component Growth')
                ax1.legend()
                ax1.grid(True, alpha=0.3)
                
                # 2. Network density
                ax2.plot(steps, current_density, 'o-', color='purple', linewidth=2, markersize=6)
                ax2.set_xlabel('Time Step')
                ax2.set_ylabel('Density')
                ax2.set_title('Network Density Evolution')
                ax2.set_ylim(0, 1)
                ax2.grid(True, alpha=0.3)
                
                # 3. System complexity
                ax3.plot(steps, current_complexity, 's-', color='orange', linewidth=2, markersize=6)
                ax3.set_xlabel('Time Step')
                ax3.set_ylabel('Patterns per Entity')
                ax3.set_title('System Complexity Trend')
                ax3.grid(True, alpha=0.3)
                
                # 4. Current metrics bar chart
                if frame_num < len(current_entities):
                    metrics = ['Entities', 'Patterns', 'Relationships']
                    values = [current_entities[-1], current_patterns[-1], current_relationships[-1]]
                    colors = [self.node_colors['entity'], self.node_colors['pattern'], self.node_colors['query']]
                    
                    bars = ax4.bar(metrics, values, color=colors, alpha=0.7)
                    ax4.set_ylabel('Count')
                    ax4.set_title(f'Current Metrics (Step {frame_num + 1})')
                    
                    # Add value labels on bars
                    for bar, value in zip(bars, values):
                        ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
                               f'{value}', ha='center', va='bottom', fontweight='bold')
                
                plt.suptitle(f'System Metrics Evolution (Step {frame_num + 1}/{time_steps})', 
                           fontsize=14, fontweight='bold')
                plt.tight_layout()
            
            # Create animation
            anim = animation.FuncAnimation(
                fig, animate_metrics, frames=time_steps,
                interval=interval, repeat=True, blit=False
            )
            
            if save_path:
                writer = animation.PillowWriter(fps=3)
                anim.save(save_path, writer=writer, dpi=self.dpi)
                logger.info(f"System metrics animation saved to {save_path}")
            
            return anim
            
        except Exception as e:
            logger.error(f"Failed to create system metrics animation: {e}")
            raise
    
    def create_comprehensive_animation_suite(
        self,
        output_dir: str,
        suite_name: str = "atlas_animations"
    ) -> Dict[str, Any]:
        """
        Create a comprehensive suite of all available animations.
        
        Args:
            output_dir: Directory to save all animations
            suite_name: Base name for animation files
            
        Returns:
            Dictionary with animation creation results
        """
        import os
        from pathlib import Path
        
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            results = {
                'created_animations': [],
                'failed_animations': [],
                'total_size_mb': 0,
                'creation_time': datetime.now().isoformat()
            }
            
            # Animation configurations
            animations_config = [
                {
                    'name': 'network_growth',
                    'func': self.animate_network_growth,
                    'params': {'time_steps': 30, 'interval': 400},
                    'description': 'Network growth over time'
                },
                {
                    'name': 'pattern_discovery',
                    'func': self.animate_pattern_discovery,
                    'params': {'time_steps': 20, 'interval': 600},
                    'description': 'Pattern discovery process'
                },
                {
                    'name': 'query_execution',
                    'func': self.animate_query_execution,
                    'params': {'query_steps': 15, 'interval': 400},
                    'description': 'Query execution visualization'
                },
                {
                    'name': 'system_metrics',
                    'func': self.animate_system_metrics,
                    'params': {'time_steps': 25, 'interval': 300},
                    'description': 'System metrics evolution'
                }
            ]
            
            # Create static visualizations (non-animated)
            static_configs = [
                {
                    'name': 'interactive_timeline',
                    'func': self.create_interactive_timeline,
                    'params': {'time_window_days': 30},
                    'description': 'Interactive timeline visualization'
                }
            ]
            
            logger.info(f"Creating comprehensive animation suite in {output_path}")
            
            # Create animations
            for config in animations_config:
                try:
                    file_path = output_path / f"{suite_name}_{config['name']}.gif"
                    
                    anim = config['func'](
                        save_path=str(file_path),
                        **config['params']
                    )
                    
                    if anim and file_path.exists():
                        file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                        results['created_animations'].append({
                            'name': config['name'],
                            'file_path': str(file_path),
                            'description': config['description'],
                            'size_mb': round(file_size, 2)
                        })
                        results['total_size_mb'] += file_size
                        logger.info(f"Created {config['name']} animation ({file_size:.2f} MB)")
                    
                except Exception as e:
                    logger.error(f"Failed to create {config['name']} animation: {e}")
                    results['failed_animations'].append({
                        'name': config['name'],
                        'error': str(e)
                    })
            
            # Create static visualizations
            for config in static_configs:
                try:
                    file_path = output_path / f"{suite_name}_{config['name']}.png"
                    
                    fig = config['func'](
                        save_path=str(file_path),
                        **config['params']
                    )
                    
                    if fig and file_path.exists():
                        file_size = file_path.stat().st_size / (1024 * 1024)  # MB
                        results['created_animations'].append({
                            'name': config['name'],
                            'file_path': str(file_path),
                            'description': config['description'],
                            'size_mb': round(file_size, 2),
                            'type': 'static'
                        })
                        results['total_size_mb'] += file_size
                        logger.info(f"Created {config['name']} visualization ({file_size:.2f} MB)")
                    
                    plt.close(fig)  # Clean up
                    
                except Exception as e:
                    logger.error(f"Failed to create {config['name']} visualization: {e}")
                    results['failed_animations'].append({
                        'name': config['name'],
                        'error': str(e)
                    })
            
            # Create summary report
            summary_path = output_path / f"{suite_name}_summary.json"
            with open(summary_path, 'w') as f:
                import json
                json.dump(results, f, indent=2)
            
            logger.info(f"Animation suite completed: {len(results['created_animations'])} successful, "
                       f"{len(results['failed_animations'])} failed, {results['total_size_mb']:.2f} MB total")
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to create comprehensive animation suite: {e}")
            raise 