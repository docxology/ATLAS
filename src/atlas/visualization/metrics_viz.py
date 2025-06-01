"""
Metrics visualization module for ATLAS.

Provides comprehensive metrics visualization capabilities including
system performance, usage statistics, and quality analysis charts.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
import seaborn as sns
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MetricsVisualizer:
    """
    Comprehensive metrics visualization for ATLAS systems.
    
    Provides visualization methods for system performance metrics,
    usage statistics, and quality analysis.
    """
    
    def __init__(self, atlas_engine=None):
        """
        Initialize the MetricsVisualizer.
        
        Args:
            atlas_engine: Optional ATLAS engine instance
        """
        self.atlas_engine = atlas_engine
        
        # Color schemes for different metric types
        self.metric_colors = {
            'performance': '#3498db',    # Blue
            'usage': '#2ecc71',         # Green  
            'quality': '#e74c3c',       # Red
            'growth': '#f39c12',        # Orange
            'efficiency': '#9b59b6'     # Purple
        }
        
        logger.info("MetricsVisualizer initialized")
    
    def visualize_system_overview(
        self,
        figsize: Tuple[int, int] = (16, 10),
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Create a comprehensive system overview dashboard.
        
        Args:
            figsize: Figure size tuple
            save_path: Optional path to save the figure
            
        Returns:
            Matplotlib figure object
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        try:
            fig = plt.figure(figsize=figsize)
            gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
            
            # Get system metrics
            metrics = self.atlas_engine.get_metrics()
            
            # 1. Component counts (top left, 2x2)
            ax1 = fig.add_subplot(gs[0:2, 0:2])
            component_counts = {
                'Entities': metrics.get('entities_created', 0),
                'Patterns': metrics.get('patterns_created', 0),
                'Queries': metrics.get('queries_executed', 0),
                'Relationships': metrics.get('relationships_added', 0)
            }
            
            colors = list(self.metric_colors.values())[:len(component_counts)]
            wedges, texts, autotexts = ax1.pie(
                component_counts.values(),
                labels=component_counts.keys(),
                colors=colors,
                autopct='%1.1f%%',
                startangle=90
            )
            ax1.set_title('System Component Distribution', fontsize=12, fontweight='bold')
            
            # 2. Network metrics (top right)
            ax2 = fig.add_subplot(gs[0, 2:])
            network_metrics = [
                ('Nodes', metrics.get('total_nodes', 0)),
                ('Edges', metrics.get('total_edges', 0)),
                ('Components', metrics.get('connected_components', 0))
            ]
            
            metrics_names = [m[0] for m in network_metrics]
            metrics_values = [m[1] for m in network_metrics]
            bars = ax2.bar(metrics_names, metrics_values, color=self.metric_colors['performance'])
            ax2.set_title('Network Topology Metrics', fontweight='bold')
            ax2.set_ylabel('Count')
            
            # Add value labels on bars
            for bar, value in zip(bars, metrics_values):
                ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                        f'{value}', ha='center', va='bottom')
            
            # 3. Graph density and connectivity (middle right)
            ax3 = fig.add_subplot(gs[1, 2:])
            density = metrics.get('graph_density', 0)
            ax3.bar(['Graph Density'], [density], color=self.metric_colors['quality'])
            ax3.set_ylabel('Density')
            ax3.set_ylim(0, 1)
            ax3.set_title('Graph Connectivity', fontweight='bold')
            ax3.text(0, density + 0.05, f'{density:.3f}', ha='center', va='bottom')
            
            # 4. System activity timeline (bottom, full width)
            ax4 = fig.add_subplot(gs[2, :])
            
            # Generate sample activity data (in real implementation, this would come from logs)
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), 
                                 end=datetime.now(), freq='D')
            
            # Simulate activity data
            np.random.seed(42)  # For reproducible results
            entities_created = np.random.poisson(2, len(dates))
            patterns_created = np.random.poisson(1, len(dates))
            queries_executed = np.random.poisson(5, len(dates))
            
            ax4.plot(dates, entities_created, label='Entities Created', 
                    color=self.metric_colors['usage'], marker='o', markersize=3)
            ax4.plot(dates, patterns_created, label='Patterns Created', 
                    color=self.metric_colors['growth'], marker='s', markersize=3)
            ax4.plot(dates, queries_executed, label='Queries Executed', 
                    color=self.metric_colors['performance'], marker='^', markersize=3)
            
            ax4.set_xlabel('Date')
            ax4.set_ylabel('Daily Count')
            ax4.set_title('System Activity Timeline (Last 30 Days)', fontweight='bold')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            
            # Format dates
            ax4.tick_params(axis='x', rotation=45)
            
            plt.suptitle('ATLAS System Overview Dashboard', fontsize=16, fontweight='bold')
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create system overview: {e}")
            raise
    
    def visualize_performance_metrics(
        self,
        figsize: Tuple[int, int] = (14, 8),
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Visualize system performance metrics.
        
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
            
            # Get query performance data (simulated for demonstration)
            np.random.seed(42)
            query_times = np.random.lognormal(0, 1, 100)  # Log-normal distribution for query times
            query_success_rates = np.random.beta(8, 2, 50)  # Beta distribution for success rates
            
            # 1. Query execution time distribution
            ax1.hist(query_times, bins=20, alpha=0.7, color=self.metric_colors['performance'], 
                    edgecolor='black')
            ax1.set_xlabel('Execution Time (seconds)')
            ax1.set_ylabel('Frequency')
            ax1.set_title('Query Execution Time Distribution')
            ax1.axvline(np.mean(query_times), color='red', linestyle='--', 
                       label=f'Mean: {np.mean(query_times):.2f}s')
            ax1.legend()
            
            # 2. Success rate over time
            dates = pd.date_range(start=datetime.now() - timedelta(days=50), 
                                 end=datetime.now(), periods=len(query_success_rates))
            ax2.plot(dates, query_success_rates, color=self.metric_colors['quality'], 
                    marker='o', markersize=4)
            ax2.set_xlabel('Date')
            ax2.set_ylabel('Success Rate')
            ax2.set_title('Query Success Rate Over Time')
            ax2.set_ylim(0, 1)
            ax2.grid(True, alpha=0.3)
            ax2.tick_params(axis='x', rotation=45)
            
            # 3. System load metrics
            hours = np.arange(24)
            load_data = np.random.normal(50, 15, 24)  # Simulated hourly load
            load_data = np.clip(load_data, 0, 100)  # Ensure values are between 0-100
            
            bars = ax3.bar(hours, load_data, color=self.metric_colors['efficiency'], alpha=0.7)
            ax3.set_xlabel('Hour of Day')
            ax3.set_ylabel('System Load (%)')
            ax3.set_title('Average System Load by Hour')
            ax3.set_xticks(range(0, 24, 4))
            
            # Color bars based on load level
            for i, bar in enumerate(bars):
                if load_data[i] > 80:
                    bar.set_color('red')
                elif load_data[i] > 60:
                    bar.set_color('orange')
            
            # 4. Memory and resource usage
            resource_types = ['Memory', 'CPU', 'Storage', 'Network']
            current_usage = np.random.uniform(20, 90, len(resource_types))
            max_capacity = np.full(len(resource_types), 100)
            
            x = np.arange(len(resource_types))
            width = 0.35
            
            bars1 = ax4.bar(x - width/2, current_usage, width, label='Current Usage',
                           color=self.metric_colors['usage'], alpha=0.7)
            bars2 = ax4.bar(x + width/2, max_capacity, width, label='Capacity',
                           color='lightgray', alpha=0.5)
            
            ax4.set_xlabel('Resource Type')
            ax4.set_ylabel('Usage (%)')
            ax4.set_title('Resource Utilization')
            ax4.set_xticks(x)
            ax4.set_xticklabels(resource_types)
            ax4.legend()
            
            # Add percentage labels
            for i, bar in enumerate(bars1):
                ax4.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2,
                        f'{current_usage[i]:.1f}%', ha='center', va='bottom')
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to visualize performance metrics: {e}")
            raise
    
    def visualize_quality_metrics(
        self,
        figsize: Tuple[int, int] = (12, 8),
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Visualize data quality and confidence metrics.
        
        Args:
            figsize: Figure size tuple
            save_path: Optional path to save the figure
            
        Returns:
            Matplotlib figure object
        """
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)
            
            # Simulate quality metrics data
            np.random.seed(42)
            
            # 1. Data quality scores distribution
            quality_scores = np.random.beta(3, 1, 200)  # Beta distribution skewed toward high quality
            ax1.hist(quality_scores, bins=20, alpha=0.7, color=self.metric_colors['quality'],
                    edgecolor='black')
            ax1.set_xlabel('Quality Score')
            ax1.set_ylabel('Frequency')
            ax1.set_title('Data Quality Score Distribution')
            ax1.axvline(np.mean(quality_scores), color='darkred', linestyle='--',
                       label=f'Mean: {np.mean(quality_scores):.2f}')
            ax1.legend()
            
            # 2. Confidence scores by component type
            component_types = ['Entities', 'Patterns', 'Queries', 'Attributes']
            confidence_means = np.random.uniform(0.6, 0.9, len(component_types))
            confidence_stds = np.random.uniform(0.05, 0.15, len(component_types))
            
            bars = ax2.bar(component_types, confidence_means, 
                          yerr=confidence_stds, capsize=5,
                          color=self.metric_colors['quality'], alpha=0.7)
            ax2.set_ylabel('Average Confidence Score')
            ax2.set_title('Confidence by Component Type')
            ax2.set_ylim(0, 1)
            
            # Add value labels
            for bar, mean in zip(bars, confidence_means):
                ax2.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.02,
                        f'{mean:.2f}', ha='center', va='bottom')
            
            # 3. Quality trends over time
            dates = pd.date_range(start=datetime.now() - timedelta(days=30), 
                                 end=datetime.now(), freq='D')
            
            # Simulate quality trend with slight improvement over time
            base_quality = 0.7
            trend = np.linspace(0, 0.1, len(dates))
            noise = np.random.normal(0, 0.05, len(dates))
            quality_trend = np.clip(base_quality + trend + noise, 0, 1)
            
            ax3.plot(dates, quality_trend, color=self.metric_colors['quality'], 
                    marker='o', markersize=3, linewidth=2)
            ax3.set_xlabel('Date')
            ax3.set_ylabel('Average Quality Score')
            ax3.set_title('Quality Trend Over Time')
            ax3.set_ylim(0, 1)
            ax3.grid(True, alpha=0.3)
            ax3.tick_params(axis='x', rotation=45)
            
            # Add trend line
            z = np.polyfit(range(len(dates)), quality_trend, 1)
            p = np.poly1d(z)
            ax3.plot(dates, p(range(len(dates))), "--", color='red', alpha=0.7,
                    label=f'Trend (slope: {z[0]:.4f}/day)')
            ax3.legend()
            
            # 4. Anomaly detection summary
            anomaly_types = ['Data Outliers', 'Pattern Violations', 'Consistency Issues', 'Missing Values']
            anomaly_counts = np.random.poisson(5, len(anomaly_types))
            severity_high = np.random.poisson(1, len(anomaly_types))
            severity_medium = anomaly_counts - severity_high - np.random.poisson(1, len(anomaly_types))
            severity_low = anomaly_counts - severity_high - severity_medium
            severity_low = np.clip(severity_low, 0, None)  # Ensure non-negative
            
            x = np.arange(len(anomaly_types))
            width = 0.6
            
            p1 = ax4.bar(x, severity_high, width, label='High Severity', color='red', alpha=0.8)
            p2 = ax4.bar(x, severity_medium, width, bottom=severity_high, 
                        label='Medium Severity', color='orange', alpha=0.8)
            p3 = ax4.bar(x, severity_low, width, 
                        bottom=severity_high + severity_medium,
                        label='Low Severity', color='yellow', alpha=0.8)
            
            ax4.set_xlabel('Anomaly Type')
            ax4.set_ylabel('Count')
            ax4.set_title('Anomaly Detection Summary')
            ax4.set_xticks(x)
            ax4.set_xticklabels(anomaly_types, rotation=45, ha='right')
            ax4.legend()
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to visualize quality metrics: {e}")
            raise
    
    def create_metrics_comparison(
        self,
        metrics_data: Dict[str, Dict[str, float]],
        figsize: Tuple[int, int] = (12, 6),
        save_path: Optional[str] = None
    ) -> Figure:
        """
        Create a comparison chart for multiple metric categories.
        
        Args:
            metrics_data: Dictionary with categories as keys and metric dicts as values
            figsize: Figure size tuple
            save_path: Optional path to save the figure
            
        Returns:
            Matplotlib figure object
        """
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
            
            if not metrics_data:
                ax1.text(0.5, 0.5, 'No metrics data provided', ha='center', va='center')
                ax2.text(0.5, 0.5, 'No metrics data provided', ha='center', va='center')
                return fig
            
            # Convert to DataFrame for easier plotting
            df = pd.DataFrame(metrics_data).T
            
            # 1. Heatmap of all metrics
            im = ax1.imshow(df.values, cmap='RdYlGn', aspect='auto', vmin=0, vmax=1)
            ax1.set_xticks(range(len(df.columns)))
            ax1.set_yticks(range(len(df.index)))
            ax1.set_xticklabels(df.columns, rotation=45, ha='right')
            ax1.set_yticklabels(df.index)
            ax1.set_title('Metrics Heatmap')
            
            # Add text annotations
            for i in range(len(df.index)):
                for j in range(len(df.columns)):
                    value = df.iloc[i, j]
                    if pd.notna(value):
                        text = ax1.text(j, i, f'{value:.2f}', ha='center', va='center',
                                      color='white' if value < 0.5 else 'black')
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax1)
            cbar.set_label('Score', rotation=270, labelpad=20)
            
            # 2. Radar chart for metric comparison
            categories = list(df.index)
            if len(df.columns) > 0:
                # Use first metric set for radar chart
                values = df.iloc[:, 0].values
                
                # Number of variables
                N = len(categories)
                
                # Compute angle for each axis
                angles = [n / float(N) * 2 * np.pi for n in range(N)]
                angles += angles[:1]  # Complete the circle
                
                # Add values for completing the circle
                values = np.concatenate((values, [values[0]]))
                
                # Create radar chart
                ax2 = plt.subplot(1, 2, 2, projection='polar')
                ax2.plot(angles, values, 'o-', linewidth=2, 
                        color=self.metric_colors['performance'])
                ax2.fill(angles, values, alpha=0.25, 
                        color=self.metric_colors['performance'])
                
                # Add labels
                ax2.set_xticks(angles[:-1])
                ax2.set_xticklabels(categories)
                ax2.set_ylim(0, 1)
                ax2.set_title(f'Metrics Profile: {df.columns[0]}', pad=20)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            
            return fig
            
        except Exception as e:
            logger.error(f"Failed to create metrics comparison: {e}")
            raise
    
    def export_metrics_report(
        self,
        output_path: str,
        include_charts: bool = True
    ) -> Dict[str, Any]:
        """
        Generate and export a comprehensive metrics report.
        
        Args:
            output_path: Base path for output files
            include_charts: Whether to include visualization charts
            
        Returns:
            Dictionary with report summary and file paths
        """
        if not self.atlas_engine:
            raise ValueError("ATLAS engine not provided")
        
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'system_metrics': self.atlas_engine.get_metrics(),
                'charts_generated': [],
                'summary': {}
            }
            
            # Generate summary statistics
            metrics = report['system_metrics']
            report['summary'] = {
                'total_components': (metrics.get('entities_created', 0) + 
                                   metrics.get('patterns_created', 0) + 
                                   metrics.get('queries_executed', 0)),
                'network_density': metrics.get('graph_density', 0),
                'connectivity_score': 1.0 if metrics.get('connected_components', 1) == 1 else 0.5,
                'activity_level': min(1.0, metrics.get('relationships_added', 0) / 100.0)
            }
            
            if include_charts:
                # Generate overview chart
                overview_fig = self.visualize_system_overview()
                overview_path = f"{output_path}_overview.png"
                overview_fig.savefig(overview_path, dpi=300, bbox_inches='tight')
                report['charts_generated'].append(overview_path)
                plt.close(overview_fig)
                
                # Generate performance chart
                performance_fig = self.visualize_performance_metrics()
                performance_path = f"{output_path}_performance.png"
                performance_fig.savefig(performance_path, dpi=300, bbox_inches='tight')
                report['charts_generated'].append(performance_path)
                plt.close(performance_fig)
                
                # Generate quality chart
                quality_fig = self.visualize_quality_metrics()
                quality_path = f"{output_path}_quality.png"
                quality_fig.savefig(quality_path, dpi=300, bbox_inches='tight')
                report['charts_generated'].append(quality_path)
                plt.close(quality_fig)
            
            # Save report as JSON
            import json
            report_path = f"{output_path}_report.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Metrics report exported to {report_path}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to export metrics report: {e}")
            raise 