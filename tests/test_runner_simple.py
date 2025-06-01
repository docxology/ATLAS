#!/usr/bin/env python3
"""
Improved test runner for ATLAS comprehensive tests without pytest dependency.
This runner provides detailed logging and handles test execution robustly.
"""

import sys
import os
import traceback
import time
import subprocess
from typing import List, Dict, Any, Union
from pathlib import Path
from datetime import datetime

# Add src and current directory to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(project_root))

def run_test_file(file_path) -> Dict[str, Any]:
    """Run a test file using subprocess with detailed logging."""
    result = {
        'name': os.path.basename(file_path) if isinstance(file_path, str) else file_path.name,
        'status': 'FAILED',
        'error': None,
        'duration': 0.0,
        'output': ''
    }
    
    start_time = time.time()
    print(f"  🧪 Running {result['name']}...", end=" ", flush=True)
    
    try:
        # Run the test file as a Python script with buffering disabled
        process_result = subprocess.run(
            [sys.executable, '-u', str(file_path)],  # -u for unbuffered output
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout for comprehensive tests
            cwd=str(project_root),  # Run from project root
            env={**os.environ, 'PYTHONPATH': f"{project_root / 'src'}:{project_root}"}
        )
        
        result['duration'] = time.time() - start_time
        result['output'] = process_result.stdout if process_result.stdout else ""
        
        if process_result.returncode == 0:
            result['status'] = 'PASSED'
            print(f"✅ PASSED ({result['duration']:.2f}s)")
        else:
            result['error'] = f"Exit code {process_result.returncode}"
            if process_result.stderr:
                result['error'] += f": {process_result.stderr[:500]}..."  # Limit error length
            print(f"❌ FAILED ({result['duration']:.2f}s)")
            print(f"    ⚠️  Error: {result['error']}")
        
    except subprocess.TimeoutExpired:
        result['duration'] = time.time() - start_time
        result['error'] = f"Test execution timed out after {result['duration']:.1f}s"
        print(f"⏰ TIMEOUT ({result['duration']:.2f}s)")
        
    except Exception as e:
        result['duration'] = time.time() - start_time
        result['error'] = f"Execution error: {str(e)}"
        print(f"💥 ERROR ({result['duration']:.2f}s)")
        print(f"    ⚠️  Error: {result['error']}")
    
    return result


def discover_test_files() -> Dict[str, Union[Path, List[Path]]]:
    """Discover test files with improved categorization."""
    test_files: Dict[str, Union[Path, List[Path]]] = {}
    tests_dir = Path(__file__).parent
    
    # Priority order for main test files
    main_test_files = [
        ("atlas_comprehensive", "test_atlas_comprehensive.py"),
        ("atlas_system", "test_atlas_system.py"), 
        ("comprehensive_coverage", "test_comprehensive_coverage.py"),
        ("edge_cases", "test_edge_cases.py"),
        ("atlas_performance", "test_atlas_performance.py")
    ]
    
    for category, filename in main_test_files:
        file_path = tests_dir / filename
        if file_path.exists():
            test_files[category] = file_path
    
    # Add unit tests
    unit_dir = tests_dir / 'unit'
    if unit_dir.exists():
        unit_files = list(unit_dir.glob('test_*.py'))
        if unit_files:
            test_files['unit_tests'] = unit_files
    
    # Add integration tests
    integration_dir = tests_dir / 'integration'
    if integration_dir.exists():
        integration_files = list(integration_dir.glob('test_*.py'))
        if integration_files:
            test_files['integration_tests'] = integration_files
    
    return test_files


def print_test_summary(all_results: List[Dict[str, Any]], total_time: float) -> None:
    """Print detailed test execution summary."""
    total_tests = len(all_results)
    passed_tests = len([r for r in all_results if r['status'] == 'PASSED'])
    failed_tests = len([r for r in all_results if r['status'] == 'FAILED'])
    
    print("\n" + "=" * 80)
    print("📊 ATLAS TEST EXECUTION SUMMARY")
    print("=" * 80)
    print(f"🕐 Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️  Total Duration: {total_time:.2f}s")
    print(f"📁 Working Directory: {os.getcwd()}")
    print()
    print(f"📋 Test Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   ✅ Passed: {passed_tests}")
    print(f"   ❌ Failed: {failed_tests}")
    if total_tests > 0:
        success_rate = (passed_tests / total_tests) * 100
        print(f"   📈 Success Rate: {success_rate:.1f}%")
    
    # Performance metrics
    if all_results:
        durations = [r['duration'] for r in all_results]
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        print(f"   ⚡ Average Test Duration: {avg_duration:.2f}s")
        print(f"   🔥 Longest Test Duration: {max_duration:.2f}s")
    
    # Failed tests details
    if failed_tests > 0:
        print(f"\n❌ FAILED TESTS DETAILS ({failed_tests}):")
        print("-" * 60)
        for result in all_results:
            if result['status'] == 'FAILED':
                print(f"  💀 {result['name']}")
                if result['error']:
                    print(f"     Error: {result['error'][:200]}...")
                print(f"     Duration: {result['duration']:.2f}s")
                print()
    
    # Success celebration
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("✨ ATLAS Knowledge Management System is functioning perfectly!")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed. Please review the errors above.")


def main():
    """Enhanced main test runner with comprehensive logging."""
    print("🚀 ATLAS COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("🧠 Advanced Testing System for Knowledge Management")
    print(f"📍 Location: {Path(__file__).parent}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    print()
    
    # Discover test files
    print("🔍 Discovering test files...")
    test_files = discover_test_files()
    
    if not test_files:
        print("❌ No test files found!")
        return 1
    
    print(f"✅ Discovered {len(test_files)} test categories:")
    for category, files in test_files.items():
        if isinstance(files, list):
            print(f"   📂 {category}: {len(files)} files")
        else:
            print(f"   📄 {category}: {files.name}")
    print()
    
    # Execute all tests
    all_results = []
    total_passed = 0
    total_failed = 0
    start_time = time.time()
    
    for category, files in test_files.items():
        print(f"🏃 Running {category.replace('_', ' ').title()} Tests")
        print("-" * 60)
        
        if isinstance(files, list):
            # Multiple files
            for file_path in files:
                result = run_test_file(file_path)
                all_results.append(result)
                if result['status'] == 'PASSED':
                    total_passed += 1
                else:
                    total_failed += 1
        else:
            # Single file
            result = run_test_file(files)
            all_results.append(result)
            if result['status'] == 'PASSED':
                total_passed += 1
            else:
                total_failed += 1
        
        print()  # Add spacing between categories

    total_time = time.time() - start_time
    
    # Print comprehensive summary
    print_test_summary(all_results, total_time)
    
    # Return appropriate exit code
    exit_code = 0 if total_failed == 0 else 1
    print(f"\n🚪 Exiting with code: {exit_code}")
    return exit_code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Unexpected error in test runner: {e}")
        traceback.print_exc()
        sys.exit(1) 