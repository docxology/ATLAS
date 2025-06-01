#!/usr/bin/env python3
"""
ATLAS Test Configuration

This module provides configuration and discovery utilities for the ATLAS test suite.
It handles test discovery and provides a unified interface for running tests.
"""

import os
import sys
import subprocess
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

# Add src to path for imports if not already added
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)


class TestConfig:
    """Configuration class for ATLAS test suite."""
    
    def __init__(self):
        self.tests_dir = Path(__file__).parent
        self.test_categories = [
            'unit',
            'integration', 
            'comprehensive',
            'performance',
            'system',
            'edge_cases',
            'coverage'
        ]
        self._test_files_cache: Optional[Dict[str, Any]] = None
    
    def get_test_files(self) -> Dict[str, Any]:
        """
        Get all test files organized by category.
        
        Returns:
            Dict mapping categories to file paths
        """
        if self._test_files_cache is not None:
            return self._test_files_cache
        
        test_files: Dict[str, Any] = {}
        
        # Check for main test files
        main_test_files = {
            'comprehensive': 'test_atlas_comprehensive.py',
            'system': 'test_atlas_system.py',
            'performance': 'test_atlas_performance.py',
            'edge_cases': 'test_edge_cases.py',
            'coverage': 'test_comprehensive_coverage.py'
        }
        
        for category, filename in main_test_files.items():
            file_path = self.tests_dir / filename
            if file_path.exists():
                test_files[category] = file_path
        
        # Check for unit tests
        unit_dir = self.tests_dir / 'unit'
        if unit_dir.exists():
            unit_files = list(unit_dir.glob('test_*.py'))
            if unit_files:
                test_files['unit'] = unit_files
        
        # Check for integration tests  
        integration_dir = self.tests_dir / 'integration'
        if integration_dir.exists():
            integration_files = list(integration_dir.glob('test_*.py'))
            if integration_files:
                test_files['integration'] = integration_files
        
        self._test_files_cache = test_files
        return test_files
    
    def run_syntax_check(self, file_path: Path) -> bool:
        """
        Check if a Python file has valid syntax.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            True if syntax is valid, False otherwise
        """
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', str(file_path)],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False
    
    def can_import_pytest(self) -> bool:
        """Check if pytest is available."""
        try:
            result = subprocess.run(
                [sys.executable, '-c', 'import pytest'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def run_file_with_python(self, file_path: Path, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run a Python file and return execution results.
        
        Args:
            file_path: Path to the Python file to run
            args: Optional command line arguments
            
        Returns:
            Dict with execution results
        """
        cmd = [sys.executable, str(file_path)]
        if args:
            cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=str(file_path.parent.parent)  # Run from project root
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'file': str(file_path)
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': 'Test execution timed out',
                'file': str(file_path)
            }
        except Exception as e:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': f'Execution error: {str(e)}',
                'file': str(file_path)
            }
    
    def run_pytest_on_directory(self, directory: Path, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """
        Run pytest on a directory.
        
        Args:
            directory: Directory to run pytest on
            output_file: Optional file to save XML results
            
        Returns:
            Dict with pytest results
        """
        if not self.can_import_pytest():
            return {
                'success': False,
                'error': 'pytest not available'
            }
        
        cmd = [sys.executable, '-m', 'pytest', str(directory), '-v', '--tb=short']
        
        if output_file:
            cmd.extend(['--junitxml', str(output_file)])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout
                cwd=str(directory.parent.parent)  # Run from project root
            )
            
            return {
                'success': result.returncode == 0,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'directory': str(directory)
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': 'Pytest execution timed out',
                'directory': str(directory)
            }
        except Exception as e:
            return {
                'success': False,
                'returncode': -1,
                'stdout': '',
                'stderr': f'Pytest execution error: {str(e)}',
                'directory': str(directory)
            }
    
    def get_test_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive summary of the test infrastructure.
        
        Returns:
            Dict with test infrastructure summary
        """
        test_files = self.get_test_files()
        
        summary = {
            'total_categories': len(test_files),
            'categories': {},
            'syntax_check': {},
            'pytest_available': self.can_import_pytest(),
            'test_files_found': {},
            'total_files': 0
        }
        
        for category, files in test_files.items():
            if isinstance(files, list):
                # Multiple files
                file_count = len(files)
                valid_files = []
                invalid_files = []
                
                for file_path in files:
                    if self.run_syntax_check(file_path):
                        valid_files.append(str(file_path))
                    else:
                        invalid_files.append(str(file_path))
                
                summary['categories'][category] = file_count
                summary['syntax_check'][category] = {
                    'valid': len(valid_files),
                    'invalid': len(invalid_files),
                    'valid_files': valid_files,
                    'invalid_files': invalid_files
                }
                summary['test_files_found'][category] = [str(f) for f in files]
                summary['total_files'] += file_count
                
            else:
                # Single file
                is_valid = self.run_syntax_check(files)
                summary['categories'][category] = 1
                summary['syntax_check'][category] = {
                    'valid': 1 if is_valid else 0,
                    'invalid': 0 if is_valid else 1,
                    'valid_files': [str(files)] if is_valid else [],
                    'invalid_files': [] if is_valid else [str(files)]
                }
                summary['test_files_found'][category] = str(files)
                summary['total_files'] += 1
        
        return summary
    
    def run_all_tests(self, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Run all available tests using the best available method.
        
        Args:
            output_dir: Optional directory to save results
            
        Returns:
            Dict with comprehensive test results
        """
        results = {
            'timestamp': self._get_timestamp(),
            'summary': self.get_test_summary(),
            'test_results': {},
            'overall_success': True
        }
        
        test_files = self.get_test_files()
        
        # Try pytest first if available
        if self.can_import_pytest() and test_files:
            pytest_result = self.run_pytest_on_directory(
                self.tests_dir,
                output_dir / 'pytest_results.xml' if output_dir else None
            )
            results['test_results']['pytest'] = pytest_result
            
            if not pytest_result['success']:
                results['overall_success'] = False
        
        # Run individual test files
        for category, files in test_files.items():
            category_results = []
            
            if isinstance(files, list):
                for file_path in files:
                    if self.run_syntax_check(file_path):
                        result = self.run_file_with_python(file_path)
                        category_results.append(result)
                        if not result['success']:
                            results['overall_success'] = False
            else:
                if self.run_syntax_check(files):
                    result = self.run_file_with_python(files)
                    category_results.append(result)
                    if not result['success']:
                        results['overall_success'] = False
            
            results['test_results'][category] = category_results
        
        # Save results if output directory provided
        if output_dir:
            self._save_results(results, output_dir)
        
        return results
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _save_results(self, results: Dict[str, Any], output_dir: Path) -> None:
        """Save test results to output directory."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results_file = output_dir / 'test_config_results.json'
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)


# Global test configuration instance
test_config = TestConfig()

# Convenience functions for easy access
def get_test_files() -> Dict[str, Any]:
    """Get all test files."""
    return test_config.get_test_files()

def get_test_summary() -> Dict[str, Any]:
    """Get test summary."""
    return test_config.get_test_summary()

def run_all_tests(output_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Run all tests."""
    return test_config.run_all_tests(output_dir)

def can_import_pytest() -> bool:
    """Check if pytest is available."""
    return test_config.can_import_pytest() 