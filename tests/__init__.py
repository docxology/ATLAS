"""
ATLAS Test Suite Package

This package provides comprehensive testing for the ATLAS Knowledge Management System.
It includes unit tests, integration tests, and performance tests organized modularly.

Test Organization:
- unit/: Individual component tests
- integration/: Component interaction tests  
- fixtures/: Shared test data and utilities
- Main test files: Comprehensive system-level tests

Usage:
    from tests import get_test_files, run_all_tests
    test_files = get_test_files()
    results = run_all_tests()
"""

__version__ = "1.0.0"
__author__ = "ATLAS Development Team"

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import subprocess

# Add src to path for imports if not already added
project_root = Path(__file__).parent.parent
src_path = project_root / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


class TestSuiteManager:
    """Manages the ATLAS test suite execution and discovery."""
    
    def __init__(self):
        self.tests_dir = Path(__file__).parent
        self.project_root = self.tests_dir.parent
        self.test_categories = {
            'unit': 'unit/',
            'integration': 'integration/',
            'comprehensive': 'test_atlas_comprehensive.py',
            'system': 'test_atlas_system.py',
            'performance': 'test_atlas_performance.py',
            'edge_cases': 'test_edge_cases.py',
            'coverage': 'test_comprehensive_coverage.py'
        }
    
    def get_test_files(self) -> Dict[str, Any]:
        """
        Discover available test files in the tests directory.
        
        Returns:
            Dict mapping test categories to file paths
        """
        test_files: Dict[str, Any] = {}
        
        # Check main test files
        for category, filename in self.test_categories.items():
            if category in ['unit', 'integration']:
                # Directory-based tests
                test_dir = self.tests_dir / filename
                if test_dir.exists() and test_dir.is_dir():
                    test_files_in_dir = list(test_dir.glob('test_*.py'))
                    if test_files_in_dir:
                        test_files[category] = test_files_in_dir
            else:
                # Single file tests
                file_path = self.tests_dir / filename
                if file_path.exists():
                    test_files[category] = file_path
        
        return test_files
    
    def get_available_test_categories(self) -> List[str]:
        """Get list of available test categories."""
        test_files = self.get_test_files()
        return list(test_files.keys())
    
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
                timeout=30,
                cwd=str(self.project_root)
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def run_test_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Run a single test file and return results.
        
        Args:
            file_path: Path to the test file
            
        Returns:
            Dict with test execution results
        """
        result = {
            'name': file_path.name,
            'path': str(file_path),
            'status': 'FAILED',
            'error': None,
            'duration': 0.0,
            'output': ''
        }
        
        import time
        start_time = time.time()
        
        try:
            process_result = subprocess.run(
                [sys.executable, str(file_path)],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                cwd=str(self.project_root)
            )
            
            result['duration'] = time.time() - start_time
            result['output'] = process_result.stdout
            
            if process_result.returncode == 0:
                result['status'] = 'PASSED'
            else:
                result['error'] = f"Exit code {process_result.returncode}"
                if process_result.stderr:
                    result['error'] += f": {process_result.stderr}"
                    
        except subprocess.TimeoutExpired:
            result['duration'] = time.time() - start_time
            result['error'] = "Test execution timed out"
        except Exception as e:
            result['duration'] = time.time() - start_time
            result['error'] = f"Execution error: {str(e)}"
        
        return result
    
    def get_test_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the test infrastructure.
        
        Returns:
            Dictionary with test infrastructure summary
        """
        test_files = self.get_test_files()
        summary: Dict[str, Any] = {
            'total_categories': len(test_files),
            'categories': {},
            'syntax_valid': {},
            'total_files': 0
        }
        
        for category, files in test_files.items():
            if isinstance(files, list):
                # Multiple files (unit/integration tests)
                file_count = len(files)
                valid_files = sum(1 for f in files if self.run_syntax_check(f))
                summary['categories'][category] = file_count
                summary['syntax_valid'][category] = valid_files
                summary['total_files'] += file_count
            else:
                # Single file
                summary['categories'][category] = 1
                summary['syntax_valid'][category] = 1 if self.run_syntax_check(files) else 0
                summary['total_files'] += 1
        
        return summary


# Create global instance
_test_manager = TestSuiteManager()

# Export main functions for easy access
def get_test_files() -> Dict[str, Any]:
    """Get all test files organized by category."""
    return _test_manager.get_test_files()

def get_available_test_categories() -> List[str]:
    """Get list of available test categories."""
    return _test_manager.get_available_test_categories()

def get_test_summary() -> Dict[str, Any]:
    """Get a summary of the test infrastructure."""
    return _test_manager.get_test_summary()

def run_syntax_check(file_path: Path) -> bool:
    """Check if a Python file has valid syntax."""
    return _test_manager.run_syntax_check(file_path)

def run_test_file(file_path: Path) -> Dict[str, Any]:
    """Run a single test file and return results."""
    return _test_manager.run_test_file(file_path)

def run_all_tests(output_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Run all available tests and return comprehensive results.
    
    Args:
        output_dir: Optional directory to save results
        
    Returns:
        Dict with comprehensive test results
    """
    import time
    from datetime import datetime
    
    start_time = time.time()
    test_files = get_test_files()
    
    results: Dict[str, Any] = {
        'timestamp': datetime.now().isoformat(),
        'summary': get_test_summary(),
        'test_results': {},
        'overall_success': True,
        'total_duration': 0.0,
        'total_passed': 0,
        'total_failed': 0
    }
    
    # Initialize counters
    total_passed = 0
    total_failed = 0
    
    # Run tests by category
    for category, files in test_files.items():
        category_results = []
        
        if isinstance(files, list):
            # Multiple files (unit/integration)
            for file_path in files:
                if _test_manager.run_syntax_check(file_path):
                    result = _test_manager.run_test_file(file_path)
                    category_results.append(result)
                    
                    if result['status'] == 'PASSED':
                        total_passed += 1
                    else:
                        total_failed += 1
                        results['overall_success'] = False
        else:
            # Single file
            if _test_manager.run_syntax_check(files):
                result = _test_manager.run_test_file(files)
                category_results.append(result)
                
                if result['status'] == 'PASSED':
                    total_passed += 1
                else:
                    total_failed += 1
                    results['overall_success'] = False
        
        results['test_results'][category] = category_results
    
    # Update results with final counts
    results['total_passed'] = total_passed
    results['total_failed'] = total_failed
    results['total_duration'] = time.time() - start_time
    
    # Save results if output directory provided
    if output_dir:
        _save_test_results(results, output_dir)
    
    return results

def _save_test_results(results: Dict[str, Any], output_dir: Path) -> None:
    """Save test results to output directory."""
    import json
    
    output_dir.mkdir(parents=True, exist_ok=True)
    results_file = output_dir / 'test_results.json'
    
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

# Export main functions
__all__ = [
    'get_test_files',
    'get_available_test_categories', 
    'get_test_summary',
    'run_syntax_check',
    'run_test_file',
    'run_all_tests',
    'TestSuiteManager'
] 