"""
Pattern management system for ATLAS.

This module provides the Pattern class and related functionality
for managing pattern languages within the ATLAS framework.
"""

from .pattern import Pattern
from .pattern_engine import PatternEngine

__all__ = ["Pattern", "PatternEngine"] 