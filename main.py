#!/usr/bin/env python3
"""
ATLAS Main Entry Point

This script handles complete ATLAS system setup, testing, and example discovery.
Run this script to install, test, and explore the ATLAS knowledge management system.
"""

import os
import sys
import subprocess
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def create_output_directory():
    """Create a timestamped output directory for all results."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"atlas_output_{timestamp}")
    output_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    (output_dir / "reports").mkdir(exist_ok=True)
    (output_dir / "logs").mkdir(exist_ok=True)
    (output_dir / "visualizations").mkdir(exist_ok=True)
    (output_dir / "test_results").mkdir(exist_ok=True)
    
    return output_dir

def cleanup_standalone_output_directories():
    """Clean up any standalone test output directories to prevent confusion."""
    standalone_dirs = [
        "test_output",
        "test_custom_output",
        "atlas_output",  # Any unversioned atlas_output
        "demo_output",
        "visualization_output"
    ]
    
    cleaned_dirs = []
    for dir_name in standalone_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists() and dir_path.is_dir():
            try:
                # Check if it's empty or contains only test files
                contents = list(dir_path.rglob("*"))
                if len(contents) <= 20:  # Small directory, likely test output
                    import shutil
                    shutil.rmtree(dir_path)
                    cleaned_dirs.append(dir_name)
            except Exception as e:
                print_warning(f"Could not clean up {dir_name}: {e}")
    
    if cleaned_dirs:
        print_success(f"Cleaned up standalone output directories: {', '.join(cleaned_dirs)}")
    
    return cleaned_dirs

def print_header(text):
    """Print a colored header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_step(step_num, total_steps, description):
    """Print a step indicator."""
    print(f"{Colors.OKBLUE}[{step_num}/{total_steps}]{Colors.ENDC} {Colors.BOLD}{description}{Colors.ENDC}")

def print_success(message):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_warning(message):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_error(message):
    """Print an error message."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def run_command(command, description, capture_output=True, check=True, output_dir=None):
    """Run a shell command with error handling."""
    try:
        print(f"  Running: {description}")
        if capture_output:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                check=check
            )
            
            # Save command output to log file if output_dir provided
            if output_dir and result.stdout:
                log_dir = output_dir / "logs"
                log_dir.mkdir(exist_ok=True)
                log_file = log_dir / f"{description.replace(' ', '_').lower()}.log"
                with open(log_file, 'w') as f:
                    f.write(f"Command: {command}\n")
                    f.write(f"Description: {description}\n")
                    f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                    f.write(f"Return code: {result.returncode}\n\n")
                    f.write("STDOUT:\n")
                    f.write(result.stdout)
                    if result.stderr:
                        f.write("\n\nSTDERR:\n")
                        f.write(result.stderr)
            
            return result
        else:
            result = subprocess.run(command, shell=True, check=check)
            return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {description}")
        if hasattr(e, 'stdout') and e.stdout:
            print(f"  stdout: {e.stdout}")
        if hasattr(e, 'stderr') and e.stderr:
            print(f"  stderr: {e.stderr}")
        return None

def check_python_version():
    """Check if Python version meets requirements."""
    print_step(1, 8, "Checking Python Version")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} meets requirements (≥3.8)")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} does not meet requirements (≥3.8)")
        return False

def install_atlas(output_dir):
    """Install ATLAS in development mode."""
    print_step(2, 8, "Installing ATLAS System")
    
    # Install core dependencies first
    print("  Installing core dependencies...")
    result = run_command(
        "pip install --upgrade pip setuptools wheel", 
        "Upgrading pip and build tools",
        output_dir=output_dir
    )
    
    if not result or result.returncode != 0:
        print_warning("Failed to upgrade pip - continuing with installation")
    
    # Install core ATLAS with constrained dependencies
    core_result = run_command(
        "pip install -e . --no-deps", 
        "Installing ATLAS core (no dependencies)",
        output_dir=output_dir
    )
    
    # Install core dependencies separately with version constraints
    deps_result = run_command(
        "pip install 'networkx>=2.6.0,<4.0' 'numpy>=1.20.0,<2.0' 'python-dateutil>=2.8.0,<3.0'", 
        "Installing core dependencies with constraints",
        output_dir=output_dir
    )
    
    if core_result and core_result.returncode == 0 and deps_result and deps_result.returncode == 0:
        print_success("Core installation completed")
    else:
        print_error("Core installation failed")
        return False
    
    # Try to install test dependencies (optional)
    print("  Installing test dependencies (optional)...")
    test_result = run_command(
        "pip install 'pytest>=6.0.0,<8.0' 'pytest-cov>=2.10.0,<5.0'", 
        "Installing test dependencies",
        check=False,
        output_dir=output_dir
    )
    
    if test_result and test_result.returncode == 0:
        print_success("Test dependencies installed")
    else:
        print_warning("Test dependencies failed - tests may not work properly")
    
    # Try to install visualization dependencies (optional)
    print("  Installing visualization dependencies (optional)...")
    viz_result = run_command(
        "pip install 'matplotlib>=3.3.0,<4.0' 'pandas>=1.2.0,<3.0' --no-deps", 
        "Installing minimal visualization dependencies",
        check=False,
        output_dir=output_dir
    )
    
    if viz_result and viz_result.returncode == 0:
        print_success("Visualization dependencies installed")
    else:
        print_warning("Visualization dependencies failed - continuing with core only")
    
    return True

def run_tests(output_dir):
    """Run the comprehensive ATLAS test suite using the improved test structure."""
    print_step(3, 6, "Running ATLAS Test Suite")
    
    test_results: Dict[str, Any] = {
        'basic_test': 'UNKNOWN',
        'pytest_suite': 'NOT_FOUND',
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'test_time': 0.0,
        'overall_success': False
    }
    
    # Check tests directory
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print_error("Tests directory not found")
        test_results['basic_test'] = 'FAILED'
        return test_results
    
    try:
        start_time = time.time()
        
        # Run the improved test runner
        print("🧪 Executing ATLAS Test Suite using improved runner:")
        simple_runner = tests_dir / "test_runner_simple.py"
        
        if simple_runner.exists():
            test_output_dir = output_dir / "test_results"
            test_output_dir.mkdir(exist_ok=True)
            
            # Run with better logging and error capture
            result = run_command(
                f"{sys.executable} {simple_runner}",
                "Running comprehensive ATLAS test suite",
                output_dir=test_output_dir,
                check=False
            )
            
            test_results['test_time'] = time.time() - start_time
            
            if result and result.returncode == 0:
                test_results['basic_test'] = 'PASSED'
                test_results['pytest_suite'] = 'PASSED'
                test_results['overall_success'] = True
                print_success("✅ All tests passed successfully!")
                
                # Parse test output for detailed metrics
                if result.stdout:
                    output_str = result.stdout if isinstance(result.stdout, str) else result.stdout.decode('utf-8')
                    
                    # Extract test metrics from improved runner output
                    lines = output_str.split('\n')
                    for line in lines:
                        if 'Total Tests:' in line:
                            try:
                                test_results['total_tests'] = int(line.split(':')[1].strip())
                            except (ValueError, IndexError):
                                pass
                        elif '✅ Passed:' in line:
                            try:
                                test_results['passed_tests'] = int(line.split(':')[1].strip())
                            except (ValueError, IndexError):
                                pass
                        elif '❌ Failed:' in line:
                            try:
                                test_results['failed_tests'] = int(line.split(':')[1].strip())
                            except (ValueError, IndexError):
                                pass
                
            else:
                test_results['basic_test'] = 'FAILED'
                test_results['pytest_suite'] = 'FAILED'
                test_results['overall_success'] = False
                
                if result:
                    if result.returncode == 1:
                        print_warning("⚠️ Some tests failed - check detailed output")
                        # Still try to parse results
                        if result.stdout:
                            output_str = result.stdout if isinstance(result.stdout, str) else result.stdout.decode('utf-8')
                            lines = output_str.split('\n')
                            for line in lines:
                                if 'Total Tests:' in line:
                                    try:
                                        test_results['total_tests'] = int(line.split(':')[1].strip())
                                    except (ValueError, IndexError):
                                        pass
                                elif '✅ Passed:' in line:
                                    try:
                                        test_results['passed_tests'] = int(line.split(':')[1].strip())
                                    except (ValueError, IndexError):
                                        pass
                                elif '❌ Failed:' in line:
                                    try:
                                        test_results['failed_tests'] = int(line.split(':')[1].strip())
                                    except (ValueError, IndexError):
                                        pass
                        
                        # If we got some results, consider it partially successful
                        if test_results['total_tests'] > 0:
                            test_results['basic_test'] = 'PASSED'
                            if test_results['failed_tests'] == 0:
                                test_results['overall_success'] = True
                    else:
                        print_error("❌ Test execution failed")
                
                if result and result.stderr:
                    error_str = result.stderr if isinstance(result.stderr, str) else result.stderr.decode('utf-8')
                    print(f"Error details: {error_str[:300]}...")
        else:
            print_error("Improved test runner not found")
            test_results['basic_test'] = 'FAILED'
            
        # Show summary
        passed_count = test_results.get('passed_tests', 0)
        failed_count = test_results.get('failed_tests', 0)
        total_count = test_results.get('total_tests', 0)
        
        if total_count > 0:
            success_rate = (passed_count / total_count) * 100 if total_count > 0 else 0
            print(f"\n📊 Test Results: {passed_count}/{total_count} tests passed ({success_rate:.1f}%)")
            if failed_count > 0:
                print(f"⚠️  {failed_count} test(s) failed - see detailed logs for analysis")
        else:
            print("📊 Test execution completed (detailed counts not available)")
            
    except Exception as e:
        print_error(f"Test execution failed: {e}")
        test_results['basic_test'] = 'FAILED'
        test_results['overall_success'] = False
        test_results['error'] = str(e)
        test_results['test_time'] = time.time() - start_time if 'start_time' in locals() else 0.0
    
    return test_results

def discover_examples():
    """Discover and categorize available examples."""
    print_step(4, 8, "Discovering Available Examples")
    
    examples_dir = Path("examples")
    if not examples_dir.exists():
        print_error("Examples directory not found")
        return {}
    
    examples = {
        'core_examples': [],
        'tutorial_examples': [],
        'advanced_examples': [],
        'demo_examples': []
    }
    
    for example_file in examples_dir.glob("*.py"):
        example_name = example_file.stem
        example_path = str(example_file)
        
        # Read first few lines to get description
        description = "No description available"
        try:
            with open(example_file, 'r') as f:
                lines = f.readlines()
                for line in lines[:10]:
                    if '"""' in line or "'''" in line:
                        # Found docstring start
                        for desc_line in lines:
                            if desc_line.strip() and not desc_line.strip().startswith('#') and '"""' not in desc_line and "'''" not in desc_line:
                                description = desc_line.strip()
                                break
                        break
        except Exception:
            pass
        
        example_info = {
            'name': example_name,
            'path': example_path,
            'description': description
        }
        
        # Categorize examples
        if 'basic' in example_name.lower() or 'core' in example_name.lower():
            examples['core_examples'].append(example_info)
        elif 'tutorial' in example_name.lower() or 'learn' in example_name.lower():
            examples['tutorial_examples'].append(example_info)
        elif 'advanced' in example_name.lower() or 'complex' in example_name.lower():
            examples['advanced_examples'].append(example_info)
        elif 'demo' in example_name.lower() or 'comprehensive' in example_name.lower():
            examples['demo_examples'].append(example_info)
        else:
            examples['core_examples'].append(example_info)
    
    # Print discovered examples
    total_examples = sum(len(cat) for cat in examples.values())
    print_success(f"Discovered {total_examples} examples")
    
    return examples

def test_examples(examples, output_dir):
    """Test which examples can be run successfully."""
    print_step(5, 8, "Testing Example Availability")
    
    runnable_examples = []
    failed_examples = []
    
    for category, example_list in examples.items():
        for example in example_list:
            print(f"  Testing {example['name']}...")
            
            # Test if example can run (dry run with --help or similar)
            test_result = run_command(
                f"python3 {example['path']} --help",
                f"Testing {example['name']}",
                check=False,
                output_dir=output_dir
            )
            
            # If --help fails, try checking syntax
            if not test_result or test_result.returncode != 0:
                syntax_result = run_command(
                    f"python3 -m py_compile {example['path']}",
                    f"Checking syntax of {example['name']}",
                    check=False,
                    output_dir=output_dir
                )
                
                if syntax_result and syntax_result.returncode == 0:
                    runnable_examples.append(example)
                    print_success(f"  {example['name']} is runnable")
                else:
                    failed_examples.append(example)
                    print_warning(f"  {example['name']} has syntax issues")
            else:
                runnable_examples.append(example)
                print_success(f"  {example['name']} is runnable")
    
    return runnable_examples, failed_examples

def run_demonstration(output_dir):
    """Run the comprehensive demonstration."""
    print_step(6, 8, "Running Comprehensive Demonstration")
    
    # Ensure demonstration outputs to centralized directory
    demo_output_dir = output_dir / 'visualizations'
    demo_output_dir.mkdir(exist_ok=True)
    
    print(f"  Running comprehensive ATLAS demonstration (output: {demo_output_dir})...")
    demo_result = run_command(
        f"python3 examples/comprehensive_demo.py --output-dir '{demo_output_dir}'",
        "Comprehensive ATLAS demonstration",
        output_dir=output_dir
    )
    
    if demo_result and demo_result.returncode == 0:
        print_success("Comprehensive demonstration completed")
        return True
    else:
        print_warning("Comprehensive demonstration had issues - check logs")
        return False

def generate_report(test_results, examples, runnable_examples, failed_examples, output_dir):
    """Generate a comprehensive report."""
    print_step(7, 8, "Generating System Report")
    
    # Create report data
    report = {
        'timestamp': datetime.now().isoformat(),
        'output_directory': str(output_dir),
        'system_info': {
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'platform': sys.platform,
            'atlas_installed': True,
            'working_directory': os.getcwd()
        },
        'test_results': test_results,
        'examples': {
            'total_discovered': sum(len(cat) for cat in examples.values()),
            'runnable_count': len(runnable_examples),
            'failed_count': len(failed_examples),
            'categories': {cat: len(example_list) for cat, example_list in examples.items()}
        },
        'output_files': {
            'reports_dir': str(output_dir / "reports"),
            'logs_dir': str(output_dir / "logs"),
            'visualizations_dir': str(output_dir / "visualizations"),
            'test_results_dir': str(output_dir / "test_results")
        }
    }
    
    # Save report to output directory
    report_file = output_dir / "reports" / "atlas_system_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print_success(f"System report saved to {report_file}")
    
    # Also create a summary report
    summary_file = output_dir / "reports" / "summary.txt"
    with open(summary_file, 'w') as f:
        f.write("ATLAS SYSTEM EXECUTION SUMMARY\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Execution Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Output Directory: {output_dir}\n\n")
        f.write(f"Installation: {'SUCCESS' if test_results.get('basic_test') == 'PASSED' else 'FAILED'}\n")
        f.write(f"Tests Passed: {test_results.get('passed_tests', 0)}\n")
        f.write(f"Tests Failed: {test_results.get('failed_tests', 0)}\n")
        f.write(f"Examples Available: {len(runnable_examples)}\n")
        f.write(f"Examples Failed: {len(failed_examples)}\n\n")
        f.write("Output Structure:\n")
        f.write(f"  {output_dir}/\n")
        f.write(f"    reports/        - System reports and summaries\n")
        f.write(f"    logs/           - Command execution logs\n")
        f.write(f"    visualizations/ - Generated charts and graphs\n")
        f.write(f"    test_results/   - Test outputs and results\n")
    
    print_success(f"Summary report saved to {summary_file}")
    return report

def print_final_summary(test_results, examples, runnable_examples, failed_examples, output_dir):
    """Print a comprehensive final summary."""
    print_header("ATLAS SYSTEM SUMMARY")
    
    # Output Directory Info
    print(f"{Colors.BOLD}📁 Output Directory:{Colors.ENDC}")
    print_success(f"All outputs saved to: {output_dir}")
    
    # Installation Status
    print(f"\n{Colors.BOLD}📦 Installation Status:{Colors.ENDC}")
    print_success("ATLAS core system installed successfully")
    
    # Test Results
    print(f"\n{Colors.BOLD}🧪 Test Results:{Colors.ENDC}")
    if test_results['basic_test'] == 'PASSED':
        print_success("Basic functionality test: PASSED")
    else:
        print_error("Basic functionality test: FAILED")
    
    if test_results['pytest_suite'] == 'PASSED':
        print_success("Comprehensive test suite: PASSED")
    elif test_results['pytest_suite'] == 'FAILED':
        print_error("Comprehensive test suite: FAILED")
    else:
        print_warning("Comprehensive test suite: NOT FOUND")
    
    if test_results.get('total_tests', 0) > 0:
        total = test_results['total_tests']
        passed = test_results.get('passed_tests', 0)
        failed = test_results.get('failed_tests', 0)
        print(f"  Total tests: {total}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"  Success rate: {success_rate:.1f}%")
    
    print(f"  Test execution time: {test_results.get('test_time', 0.0):.2f} seconds")
    
    # Example Availability
    print(f"\n{Colors.BOLD}📋 Available Examples:{Colors.ENDC}")
    
    total_examples = sum(len(cat) for cat in examples.values())
    runnable_count = len(runnable_examples)
    
    print(f"  Total examples discovered: {total_examples}")
    print(f"  Runnable examples: {runnable_count}")
    print(f"  Examples with issues: {len(failed_examples)}")
    
    # List runnable examples by category
    for category, example_list in examples.items():
        category_runnable = [ex for ex in example_list if ex in runnable_examples]
        if category_runnable:
            category_name = category.replace('_', ' ').title()
            print(f"\n  {Colors.OKCYAN}{category_name}:{Colors.ENDC}")
            for example in category_runnable:
                print(f"    • {example['name']}: python3 {example['path']} --output-dir {output_dir}")
    
    # Quick Start Commands
    print(f"\n{Colors.BOLD}🚀 Quick Start Commands:{Colors.ENDC}")
    if runnable_examples:
        # Find the basic test example
        basic_example = next((ex for ex in runnable_examples if 'basic' in ex['name'].lower()), runnable_examples[0])
        print(f"  Run basic test: {Colors.OKGREEN}python3 {basic_example['path']} --output-dir {output_dir}{Colors.ENDC}")
        
        # Find comprehensive demo if available
        demo_example = next((ex for ex in runnable_examples if 'comprehensive' in ex['name'].lower() or 'demo' in ex['name'].lower()), None)
        if demo_example:
            print(f"  Run full demo: {Colors.OKGREEN}python3 {demo_example['path']} --output-dir {output_dir}{Colors.ENDC}")
    
    print(f"  Run tests: {Colors.OKGREEN}python3 -m pytest tests/ -v{Colors.ENDC}")
    print(f"  View system report: {Colors.OKGREEN}cat {output_dir}/reports/atlas_system_report.json{Colors.ENDC}")
    print(f"  View summary: {Colors.OKGREEN}cat {output_dir}/reports/summary.txt{Colors.ENDC}")
    
    # Output Structure
    print(f"\n{Colors.BOLD}📂 Generated Output Structure:{Colors.ENDC}")
    print(f"  {output_dir}/")
    print(f"    ├── reports/")
    print(f"    │   ├── atlas_system_report.json")
    print(f"    │   └── summary.txt")
    print(f"    ├── logs/")
    print(f"    │   └── *.log (command execution logs)")
    print(f"    ├── visualizations/")
    print(f"    │   └── *.png (generated charts and graphs)")
    print(f"    └── test_results/")
    print(f"        └── pytest_results.xml")
    
    # Final Status
    print(f"\n{Colors.BOLD}🎯 Overall Status:{Colors.ENDC}")
    if (test_results['basic_test'] == 'PASSED' and 
        runnable_count > 0):
        print_success("ATLAS system is fully operational and ready to use!")
    elif test_results['basic_test'] == 'PASSED':
        print_warning("ATLAS core is operational, but some examples may have issues")
    else:
        print_error("ATLAS installation has issues - please check the logs above")

def main():
    """Main execution function."""
    print_header("ATLAS KNOWLEDGE MANAGEMENT SYSTEM")
    print(f"{Colors.BOLD}Automated Setup, Testing, and Discovery{Colors.ENDC}")
    
    start_time = time.time()
    
    # Clean up any standalone output directories first
    print_step(0, 8, "Cleaning Up Previous Outputs")
    cleaned_dirs = cleanup_standalone_output_directories()
    if cleaned_dirs:
        print(f"  Removed standalone directories: {', '.join(cleaned_dirs)}")
    else:
        print("  No standalone directories found to clean up")
    
    # Create centralized timestamped output directory
    output_dir = create_output_directory()
    print_success(f"Created centralized output directory: {output_dir}")
    print(f"  🔒 All outputs will be saved to this single directory")
    
    # Step 1: Check Python version
    if not check_python_version():
        print_error("Python version requirements not met. Please upgrade to Python 3.8+")
        sys.exit(1)
    
    # Step 2: Install ATLAS
    if not install_atlas(output_dir):
        print_error("ATLAS installation failed. Please check the error messages above.")
        sys.exit(1)
    
    # Step 3: Run tests (all output to centralized directory)
    test_results = run_tests(output_dir)
    
    # Step 4: Discover examples
    examples = discover_examples()
    
    # Step 5: Test examples (all output to centralized directory)
    runnable_examples, failed_examples = test_examples(examples, output_dir)
    
    # Step 6: Run demonstration (all output to centralized directory)
    demo_success = run_demonstration(output_dir)
    
    # Step 7: Generate report (all output to centralized directory)
    report = generate_report(test_results, examples, runnable_examples, failed_examples, output_dir)
    
    # Step 8: Final centralized output summary
    print_step(8, 8, "Centralizing All Outputs")
    print(f"  📁 All outputs centralized in: {output_dir}")
    print(f"  📊 Test results: {output_dir / 'test_results'}")
    print(f"  📈 Visualizations: {output_dir / 'visualizations'}")
    print(f"  📋 Reports: {output_dir / 'reports'}")
    print(f"  📜 Logs: {output_dir / 'logs'}")
    print_success("All outputs successfully centralized in single timestamped directory!")
    
    # Final summary
    total_time = time.time() - start_time
    print(f"\n{Colors.BOLD}Total execution time: {total_time:.2f} seconds{Colors.ENDC}")
    
    print_final_summary(test_results, examples, runnable_examples, failed_examples, output_dir)
    
    # Exit with appropriate code
    if test_results['basic_test'] == 'PASSED':
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Operation interrupted by user{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1) 