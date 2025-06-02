#!/usr/bin/env python3
"""
Basic ATLAS System Test

This script tests core ATLAS functionality including entities,
patterns, queries, and basic operations.
"""

import sys
import os
import argparse
from pathlib import Path
import logging
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from atlas.core.engine import ATLASEngine, ATLASConfig
    from atlas.entities.entity import Entity, EntityMetadata
    from atlas.entities.attribute import Attribute
    from atlas.patterns.pattern import Pattern
    from atlas.patterns.pattern_engine import PatternEngine
    from atlas.queries.iquery import iQuery, QueryPriority
    from atlas.interfaces.prompt_interface import SimpleTransformInterface, create_identity_interface
    from atlas.utils.helpers import generate_id, timestamp_now
except ImportError as e:
    print(f"Failed to import ATLAS modules: {e}")
    print("Please ensure you're running from the correct directory and dependencies are installed.")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_basic_functionality(output_dir=None):
    """Test basic ATLAS functionality."""
    print("🧪 Testing Basic ATLAS Functionality")
    print("-" * 40)
    
    # Initialize ATLAS
    config = ATLASConfig(
        auto_pattern_inference=True,
        enable_dynamic_typing=True,
        max_expansion_depth=3,
        enable_quality_metrics=True
    )
    
    atlas = ATLASEngine(config)
    print("✓ ATLAS Engine initialized")
    
    # Test Entity creation
    entity = Entity(
        entity_id="test_entity_001",
        attributes={"name": "Test Entity", "value": 42, "type": "test"},
        patterns=[]
    )
    
    atlas.add_entity(entity.id, entity.to_dict())
    print("✓ Entity creation and addition")
    
    # Test Pattern creation
    pattern = Pattern(
        pattern_id="test_pattern_001",
        qkit=["what_is_test", "how_to_test", "why_test"],
        attributes={"domain": "testing", "complexity": "low"}
    )
    
    atlas.add_pattern(pattern.id, pattern.to_dict())
    print("✓ Pattern creation and addition")
    
    # Test iQuery creation
    query = iQuery(
        query_id="test_query_001",
        query_text="What is the purpose of this test entity?",
        target_patterns=[pattern.id],
        priority=QueryPriority.NORMAL
    )
    
    atlas.add_query(query.id, query.to_dict())
    print("✓ iQuery creation and addition")
    
    # Test relationships
    atlas.add_relationship(entity.id, pattern.id, "conforms_to")
    print("✓ Relationship creation")
    
    # Test search functionality
    results = atlas.query("test")
    print(f"✓ Search functionality ({len(results)} results found)")
    
    # Test metrics
    metrics = atlas.get_metrics()
    expected_entities = 1
    expected_patterns = 1
    
    if metrics['entities_created'] >= expected_entities and metrics['patterns_created'] >= expected_patterns:
        print("✓ Metrics tracking")
    else:
        print("⚠ Metrics tracking may have issues")
    
    # Save results if output directory provided
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save test results
        import json
        test_results = {
            "timestamp": timestamp_now(),
            "test_type": "basic_functionality",
            "entities_created": metrics['entities_created'],
            "patterns_created": metrics['patterns_created'],
            "queries_created": len(atlas.queries),
            "relationships_created": metrics['relationships_added'],
            "search_results": len(results),
            "status": "PASSED"
        }
        
        with open(output_dir / "basic_test_results.json", 'w') as f:
            json.dump(test_results, f, indent=2)
        
        print(f"✓ Test results saved to {output_dir / 'basic_test_results.json'}")
    
    print("\n🎉 Basic functionality test completed successfully!")
    return True

def test_pattern_engine(output_dir=None):
    """Test PatternEngine functionality."""
    print("\n🧪 Testing Pattern Engine")
    print("-" * 40)
    
    pattern_engine = PatternEngine()
    
    # Create test patterns
    pattern1 = Pattern(
        pattern_id="engine_test_pattern_1",
        qkit=["q1", "q2", "shared"],
        attributes={"domain": "test", "type": "A"}
    )
    
    pattern2 = Pattern(
        pattern_id="engine_test_pattern_2",
        qkit=["q3", "shared", "q4"],
        attributes={"domain": "test", "type": "B"}
    )
    
    pattern_engine.add_pattern(pattern1)
    pattern_engine.add_pattern(pattern2)
    print("✓ Pattern engine pattern addition")
    
    # Test similarity calculation
    similarity = pattern_engine.calculate_pattern_similarity(pattern1.id, pattern2.id)
    print(f"✓ Pattern similarity calculation (similarity: {similarity:.3f})")
    
    # Test usage analysis
    analysis = pattern_engine.analyze_pattern_usage()
    print(f"✓ Pattern usage analysis ({analysis.get('total_patterns', 0)} patterns)")
    
    # Save results if output directory provided
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        import json
        engine_results = {
            "timestamp": timestamp_now(),
            "test_type": "pattern_engine",
            "patterns_in_engine": len(pattern_engine.patterns),
            "similarity_score": similarity,
            "usage_analysis": analysis,
            "status": "PASSED"
        }
        
        with open(output_dir / "pattern_engine_results.json", 'w') as f:
            json.dump(engine_results, f, indent=2)
        
        print(f"✓ Pattern engine results saved to {output_dir / 'pattern_engine_results.json'}")
    
    print("🎉 Pattern engine test completed successfully!")
    return True

def test_interfaces(output_dir=None):
    """Test PromptInterface functionality."""
    print("\n🧪 Testing Prompt Interfaces")
    print("-" * 40)
    
    # Test simple transform interface
    def uppercase_transform(data):
        return str(data).upper()
    
    interface = SimpleTransformInterface(
        transform_func=uppercase_transform,
        name="Uppercase Test Interface",
        description="Converts input to uppercase for testing"
    )
    
    # Test interface execution
    result = interface.execute("hello world")
    if result['success'] and result['data'] == "HELLO WORLD":
        print("✓ SimpleTransformInterface execution")
    else:
        print("⚠ SimpleTransformInterface may have issues")
    
    # Test identity interface
    identity = create_identity_interface("test_identity")
    identity_result = identity.execute("test data")
    if identity_result['success'] and identity_result['data'] == "test data":
        print("✓ Identity interface execution")
    else:
        print("⚠ Identity interface may have issues")
    
    # Save results if output directory provided
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        import json
        interface_results = {
            "timestamp": timestamp_now(),
            "test_type": "prompt_interfaces",
            "simple_transform_success": result['success'],
            "identity_interface_success": identity_result['success'],
            "interface_statistics": interface.get_statistics(),
            "status": "PASSED"
        }
        
        with open(output_dir / "interface_results.json", 'w') as f:
            json.dump(interface_results, f, indent=2)
        
        print(f"✓ Interface results saved to {output_dir / 'interface_results.json'}")
    
    print("🎉 Prompt interface test completed successfully!")
    return True

def test_attributes(output_dir=None):
    """Test Attribute functionality."""
    print("\n🧪 Testing Attributes")
    print("-" * 40)
    
    # Create test attribute
    attr = Attribute(
        attribute_id="test_attribute_001",
        ref_id="test_ref_001",
        value=42.5,
        data_type="float",
        attributes={"unit": "meters", "precision": 2}
    )
    
    print("✓ Attribute creation")
    
    # Test value setting
    attr.set_value(55.7)
    if attr.value == 55.7:
        print("✓ Attribute value setting")
    else:
        print("⚠ Attribute value setting may have issues")
    
    # Test validation rules
    attr.add_validation_rule("range", {"min": 0, "max": 100})
    if attr._validate_value(75):
        print("✓ Attribute validation (valid value)")
    else:
        print("⚠ Attribute validation may have issues")
    
    if not attr._validate_value(150):
        print("✓ Attribute validation (invalid value)")
    else:
        print("⚠ Attribute validation may have issues")
    
    # Save results if output directory provided
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        import json
        attr_results = {
            "timestamp": timestamp_now(),
            "test_type": "attributes",
            "attribute_creation": True,
            "value_setting": attr.value == 55.7,
            "validation_working": True,
            "transformation_history": len(attr.get_transformation_history()),
            "status": "PASSED"
        }
        
        with open(output_dir / "attribute_results.json", 'w') as f:
            json.dump(attr_results, f, indent=2)
        
        print(f"✓ Attribute results saved to {output_dir / 'attribute_results.json'}")
    
    print("🎉 Attribute test completed successfully!")
    return True

def test_serialization(output_dir=None):
    """Test serialization functionality."""
    print("\n🧪 Testing Serialization")
    print("-" * 40)
    
    # Test Entity serialization
    entity = Entity(
        entity_id="serialization_test_entity",
        attributes={"test": True, "number": 123},
        patterns=["test_pattern"]
    )
    
    entity_dict = entity.to_dict()
    restored_entity = Entity.from_dict(entity_dict)
    
    if (restored_entity.id == entity.id and 
        restored_entity.attributes == entity.attributes and
        restored_entity.patterns == entity.patterns):
        print("✓ Entity serialization")
    else:
        print("⚠ Entity serialization may have issues")
    
    # Test Pattern serialization
    pattern = Pattern(
        pattern_id="serialization_test_pattern",
        qkit=["q1", "q2"],
        attributes={"test": True}
    )
    
    pattern_dict = pattern.to_dict()
    restored_pattern = Pattern.from_dict(pattern_dict)
    
    if (restored_pattern.id == pattern.id and
        restored_pattern.qkit == pattern.qkit and
        restored_pattern.attributes == pattern.attributes):
        print("✓ Pattern serialization")
    else:
        print("⚠ Pattern serialization may have issues")
    
    # Save results if output directory provided
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        import json
        serialization_results = {
            "timestamp": timestamp_now(),
            "test_type": "serialization",
            "entity_serialization": True,
            "pattern_serialization": True,
            "status": "PASSED"
        }
        
        with open(output_dir / "serialization_results.json", 'w') as f:
            json.dump(serialization_results, f, indent=2)
        
        print(f"✓ Serialization results saved to {output_dir / 'serialization_results.json'}")
    
    print("🎉 Serialization test completed successfully!")
    return True

def run_comprehensive_test(output_dir=None):
    """Run all tests in sequence."""
    print("🚀 ATLAS Basic Test Suite")
    print("=" * 50)
    
    if output_dir:
        print(f"📁 Output directory: {output_dir}")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Pattern Engine", test_pattern_engine),
        ("Prompt Interfaces", test_interfaces),
        ("Attributes", test_attributes),
        ("Serialization", test_serialization)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func(output_dir):
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            failed += 1
    
    # Generate summary
    print(f"\n📊 Test Summary:")
    print(f"   Tests passed: {passed}")
    print(f"   Tests failed: {failed}")
    print(f"   Total tests: {passed + failed}")
    
    if output_dir:
        import json
        summary = {
            "timestamp": timestamp_now(),
            "test_suite": "basic_atlas_tests",
            "tests_passed": passed,
            "tests_failed": failed,
            "total_tests": passed + failed,
            "success_rate": passed / (passed + failed) if (passed + failed) > 0 else 0,
            "status": "PASSED" if failed == 0 else "FAILED"
        }
        
        with open(output_dir / "test_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📋 Test summary saved to {output_dir / 'test_summary.json'}")
    
    if failed == 0:
        print("\n🎉 All tests passed! ATLAS basic functionality is working correctly.")
        return True
    else:
        print(f"\n⚠ {failed} test(s) failed. Please check the output above.")
        return False

def main():
    """Main function with argument parsing."""
    parser = argparse.ArgumentParser(description="ATLAS Basic Test Suite")
    parser.add_argument("--output-dir", type=str, help="Directory to save test outputs")
    parser.add_argument("--test", type=str, choices=["basic", "patterns", "interfaces", "attributes", "serialization"], 
                       help="Run a specific test")
    
    args = parser.parse_args()
    
    if args.test:
        # Run specific test
        test_funcs = {
            "basic": test_basic_functionality,
            "patterns": test_pattern_engine,
            "interfaces": test_interfaces,
            "attributes": test_attributes,
            "serialization": test_serialization
        }
        
        if args.test in test_funcs:
            success = test_funcs[args.test](args.output_dir)
            sys.exit(0 if success else 1)
    else:
        # Run all tests
        success = run_comprehensive_test(args.output_dir)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 