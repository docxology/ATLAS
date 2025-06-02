"""
Integration system for ATLAS.

This module provides integrations with external knowledge management systems,
enabling import/export and bidirectional synchronization capabilities.
"""

from .obsidian import ObsidianIntegration

__all__ = ["ObsidianIntegration"] 