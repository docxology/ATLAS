#!/usr/bin/env python3
"""
Setup script for ATLAS Knowledge Management System.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_file(filename):
    """Read file contents."""
    with open(os.path.join(os.path.dirname(__file__), filename), encoding='utf-8') as f:
        return f.read()

# Core dependencies that are essential for ATLAS to function
CORE_REQUIREMENTS = [
    "networkx>=2.6.0,<4.0",
    "numpy>=1.20.0,<2.0",  # Constraint to avoid compatibility issues
    "python-dateutil>=2.8.0,<3.0",
]

# Visualization dependencies (optional)
VIZ_REQUIREMENTS = [
    "matplotlib>=3.3.0,<4.0",
    "seaborn>=0.11.0,<1.0", 
    "pandas>=1.2.0,<3.0",
    "plotly>=5.0.0,<6.0",
]

# Development dependencies
DEV_REQUIREMENTS = [
    "pytest>=6.0.0,<8.0",
    "pytest-cov>=2.10.0,<5.0",
    "black>=20.8b1,<25.0",
    "flake8>=3.8.0,<7.0",
    "mypy>=0.812,<2.0",
]

# Testing-specific dependencies to avoid conflicts
TEST_REQUIREMENTS = [
    "pytest>=6.0.0,<8.0",
    "pytest-cov>=2.10.0,<5.0",
    # Avoid problematic dependencies that conflict with numpy
]

# All optional dependencies
EXTRAS_REQUIRE = {
    'viz': VIZ_REQUIREMENTS,
    'dev': DEV_REQUIREMENTS,
    'test': TEST_REQUIREMENTS,
    'all': VIZ_REQUIREMENTS + DEV_REQUIREMENTS,
}

setup(
    name="atlas-knowledge",
    version="1.0.0",
    author="ATLAS Development Team",
    author_email="atlas@example.com",
    description="A comprehensive knowledge management system based on modular composability",
    long_description=read_file("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/atlas-team/atlas",
    
    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Dependencies
    install_requires=CORE_REQUIREMENTS,
    extras_require=EXTRAS_REQUIRE,
    
    # Entry points
    entry_points={
        'console_scripts': [
            'atlas-demo=examples.basic_test:run_comprehensive_test',
            'atlas-full-demo=examples.comprehensive_demo:main',
        ],
    },
    
    # Package metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    
    # Additional metadata
    keywords="knowledge-management, graph-databases, pattern-recognition, information-retrieval",
    project_urls={
        "Bug Reports": "https://github.com/atlas-team/atlas/issues",
        "Source": "https://github.com/atlas-team/atlas",
        "Documentation": "https://atlas-knowledge.readthedocs.io/",
    },
    
    # Include additional files
    include_package_data=True,
    package_data={
        'atlas': ['*.md', '*.txt', '*.json'],
    },
    
    # Test configuration
    test_suite="tests",
    tests_require=DEV_REQUIREMENTS,
) 