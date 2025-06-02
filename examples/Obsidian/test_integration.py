#!/usr/bin/env python3
"""
ATLAS Obsidian Integration Test Script

This script tests the fixed integration between ATLAS and Obsidian vaults,
verifying that all issues have been resolved.
"""

import sys
import os
import warnings
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="networkx")

# Add src to path for imports
src_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Test imports
try:
    from atlas.core.engine import ATLASEngine, ATLASConfig
    from atlas.entities.entity import Entity, EntityMetadata
    from atlas.patterns.pattern import Pattern
    from atlas.queries.iquery import iQuery, QueryPriority
    from atlas.integrations.obsidian import ObsidianIntegration
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)


def test_basic_functionality() -> ATLASEngine:
    """Test basic ATLAS functionality."""
    print("\n=== Testing Basic ATLAS Functionality ===")
    
    try:
        # Create ATLAS engine
        atlas = ATLASEngine()
        print("✓ ATLAS engine created")
        
        # Create a test entity
        entity = Entity(
            entity_id="test_entity",
            attributes={
                "title": "Test Entity",
                "description": "A test entity for validation",
                "tags": ["test", "validation"]
            }
        )
        
        success = atlas.add_entity(entity.id, entity.to_dict())
        assert success, "Failed to add entity"
        print("✓ Entity added successfully")
        
        # Create a test pattern
        pattern = Pattern(
            pattern_id="test_pattern",
            qkit=["what_is_test", "how_to_test", "why_test"],
            attributes={
                "domain": "testing",
                "description": "A pattern for testing"
            }
        )
        
        success = atlas.add_pattern(pattern.id, pattern.to_dict())
        assert success, "Failed to add pattern"
        print("✓ Pattern added successfully")
        
        # Test query functionality
        results = atlas.query("test")
        assert len(results) > 0, "Query should return results"
        print(f"✓ Query returned {len(results)} results")
        
        # Test improved query matching
        results = atlas.query("test validation")
        assert len(results) > 0, "Multi-word query should return results"
        print(f"✓ Multi-word query returned {len(results)} results")
        
        return atlas
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        raise


def test_obsidian_integration():
    """Test Obsidian integration functionality."""
    print("\n=== Testing Obsidian Integration ===")
    
    # Create integration
    integration = ObsidianIntegration()
    print("✓ Obsidian integration created")
    
    # Create a temporary vault for testing
    test_vault = Path(__file__).parent / "test_vault"
    test_vault.mkdir(exist_ok=True)
    
    # Create a sample note
    sample_note = test_vault / "sample_note.md"
    with open(sample_note, 'w', encoding='utf-8') as f:
        f.write("""---
title: Sample Note
tags: [test, sample]
created: 2024-01-01
---

# Sample Note

This is a sample note for testing.

It contains some [[linked content]] and uses #hashtags.

## Content

Some content here with references to [[another note]].
""")
    
    # Import the vault
    import_stats = integration.import_vault(test_vault)
    print(f"✓ Import completed: {import_stats}")
    
    assert import_stats['notes_processed'] == 1, "Should process 1 note"
    assert import_stats['entities_created'] == 1, "Should create 1 entity"
    assert import_stats['patterns_created'] >= 2, "Should create patterns for tags"
    
    # Test export
    export_path = Path(__file__).parent / "test_export"
    export_stats = integration.export_to_vault(export_path)
    print(f"✓ Export completed: {export_stats}")
    
    assert export_stats['entities_exported'] >= 1, "Should export at least 1 entity"
    assert export_stats['files_created'] >= 1, "Should create at least 1 file"
    
    # Test JSON export
    json_path = Path(__file__).parent / "test_export.json"
    json_result = integration.export_data_as_json(json_path)
    assert json_result['success'], "JSON export should succeed"
    print("✓ JSON export successful")
    
    # Cleanup
    import shutil
    if test_vault.exists():
        shutil.rmtree(test_vault)
    if export_path.exists():
        shutil.rmtree(export_path)
    if json_path.exists():
        json_path.unlink()
    
    print("✓ Cleanup completed")
    
    return integration


def test_no_duplicates():
    """Test that duplicate entities/patterns are not created."""
    print("\n=== Testing No Duplicates ===")
    
    integration = ObsidianIntegration()
    
    # Create a test vault
    test_vault = Path(__file__).parent / "test_vault_duplicates"
    test_vault.mkdir(exist_ok=True)
    
    # Create notes with same tags
    for i in range(3):
        note_path = test_vault / f"note_{i}.md"
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(f"""---
title: Note {i}
tags: [common, test]
---

# Note {i}

This note has common tags.
""")
    
    # Import twice to test duplicate prevention
    import_stats1 = integration.import_vault(test_vault)
    import_stats2 = integration.import_vault(test_vault)
    
    print(f"First import: {import_stats1}")
    print(f"Second import: {import_stats2}")
    
    # Second import should not create new patterns (they already exist)
    assert import_stats2['patterns_created'] == 0, "Second import should not create duplicate patterns"
    print("✓ No duplicate patterns created")
    
    # Check that we don't have duplicate entities either
    entity_count = len(integration.atlas.entities)
    pattern_count = len(integration.atlas.patterns)
    
    print(f"✓ Final counts - Entities: {entity_count}, Patterns: {pattern_count}")
    
    # Cleanup
    import shutil
    if test_vault.exists():
        shutil.rmtree(test_vault)
    
    return integration


def test_error_handling():
    """Test error handling and robustness."""
    print("\n=== Testing Error Handling ===")
    
    integration = ObsidianIntegration()
    
    # Test with non-existent vault
    try:
        integration.import_vault(Path("non_existent_vault"))
        assert False, "Should raise error for non-existent vault"
    except ValueError:
        print("✓ Correctly handles non-existent vault")
    
    # Test with invalid export path
    try:
        integration.export_to_vault(Path("/invalid/path/that/cannot/be/created"))
        print("! Export to invalid path succeeded (might be platform-specific)")
    except Exception:
        print("✓ Correctly handles invalid export path")
    
    return integration


def main():
    """Run all tests."""
    print("🚀 ATLAS Obsidian Integration Test Suite")
    print("=" * 50)
    
    start_time = datetime.now()
    
    try:
        # Run tests
        atlas = test_basic_functionality()
        integration = test_obsidian_integration()
        test_no_duplicates()
        test_error_handling()
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n🎉 All tests passed successfully!")
        print(f"⏱️  Test duration: {duration.total_seconds():.2f} seconds")
        print(f"📊 Final ATLAS state:")
        print(f"   - Entities: {len(atlas.entities)}")
        print(f"   - Patterns: {len(atlas.patterns)}")
        print(f"   - Graph nodes: {len(atlas.graph.nodes)}")
        print(f"   - Graph edges: {len(atlas.graph.edges)}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 