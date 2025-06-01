#!/usr/bin/env python3
"""
Simple script to run individual ATLAS tests and identify issues.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_basic_functionality():
    """Test basic ATLAS functionality."""
    print("🧪 Testing Basic ATLAS Functionality")
    print("-" * 40)
    
    try:
        from atlas.core.engine import ATLASEngine, ATLASConfig
        from atlas.entities.entity import Entity
        from atlas.patterns.pattern import Pattern
        
        # Test engine initialization
        config = ATLASConfig()
        atlas = ATLASEngine(config)
        print("✓ Engine initialization")
        
        # Test entity creation
        entity = Entity(entity_id="test_entity", attributes={"name": "Test"})
        atlas.add_entity(entity.id, entity.to_dict())
        print("✓ Entity creation")
        
        # Test pattern creation
        pattern = Pattern(pattern_id="test_pattern", qkit=["q1", "q2"])
        atlas.add_pattern(pattern.id, pattern.to_dict())
        print("✓ Pattern creation")
        
        # Test relationship
        atlas.add_relationship(entity.id, pattern.id, "conforms_to")
        print("✓ Relationship creation")
        
        # Test search
        results = atlas.query("test")
        print(f"✓ Search functionality ({len(results)} results)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_comprehensive_class():
    """Test the comprehensive test class."""
    print("\n🧪 Testing Comprehensive Test Class")
    print("-" * 40)
    
    try:
        from test_atlas_comprehensive import TestATLASEngineComprehensive
        
        # Create test instance
        test = TestATLASEngineComprehensive()
        test.setup_method()
        print("✓ Test class setup")
        
        # Run initialization test
        test.test_engine_initialization_comprehensive()
        print("✓ Engine initialization test")
        
        # Run entity operations test
        test.test_multiple_entity_operations()
        print("✓ Multiple entity operations test")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test runner."""
    print("🚀 ATLAS Test Diagnostics")
    print("=" * 50)
    
    success_count = 0
    total_tests = 2
    
    # Test basic functionality
    if test_basic_functionality():
        success_count += 1
    
    # Test comprehensive class
    if test_comprehensive_class():
        success_count += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 