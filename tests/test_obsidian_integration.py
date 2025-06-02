"""
Tests for Obsidian Integration

This module tests the Obsidian integration functionality including
parsing vaults, importing/exporting data, and synchronization.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import pytest

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from atlas.integrations.obsidian import (
        ObsidianIntegration, ObsidianParser, ObsidianNote, ObsidianVault
    )
    from atlas.core.engine import ATLASEngine, ATLASConfig
    from atlas.entities.entity import Entity
    from atlas.patterns.pattern import Pattern
    from atlas.queries.iquery import iQuery, QueryPriority
    OBSIDIAN_AVAILABLE = True
except ImportError as e:
    print(f"Obsidian integration not available: {e}")
    OBSIDIAN_AVAILABLE = False


@pytest.mark.skipif(not OBSIDIAN_AVAILABLE, reason="Obsidian integration not available")
class TestObsidianParser:
    """Test the ObsidianParser functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = ObsidianParser()
        self.test_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_parser_initialization(self):
        """Test parser initialization."""
        assert self.parser is not None
        assert hasattr(self.parser, 'wiki_link_pattern')
        assert hasattr(self.parser, 'tag_pattern')
        assert hasattr(self.parser, 'frontmatter_pattern')
    
    def test_parse_simple_note(self):
        """Test parsing a simple note without frontmatter."""
        note_content = """# Test Note

This is a simple note with [[linked note]] and #tag.

Some more content here.
"""
        note_file = self.test_dir / "test_note.md"
        with open(note_file, 'w', encoding='utf-8') as f:
            f.write(note_content)
        
        note = self.parser.parse_note(note_file)
        
        assert note.title == "test_note"
        assert "linked note" in note.wiki_links
        assert "tag" in note.tags
        assert "This is a simple note" in note.content
        assert note.frontmatter == {}
    
    def test_parse_note_with_frontmatter(self):
        """Test parsing a note with YAML frontmatter."""
        note_content = """---
title: My Test Note
tags:
  - important
  - project
created: 2023-01-01T10:00:00
modified: 2023-01-02T15:30:00
---

# My Test Note

This note has frontmatter and links to [[another note]].

It also has #inline-tag and content.
"""
        note_file = self.test_dir / "frontmatter_note.md"
        with open(note_file, 'w', encoding='utf-8') as f:
            f.write(note_content)
        
        note = self.parser.parse_note(note_file)
        
        assert note.title == "frontmatter_note"  # Uses filename, not frontmatter title
        assert "another note" in note.wiki_links
        assert "important" in note.tags
        assert "project" in note.tags
        assert "inline-tag" in note.tags
        assert note.frontmatter['title'] == "My Test Note"
        assert "This note has frontmatter" in note.content
    
    def test_parse_note_with_aliases(self):
        """Test parsing notes with wiki link aliases."""
        note_content = """# Note with Aliases

This note links to [[Target Note|Display Name]] and [[Another Note]].
"""
        note_file = self.test_dir / "alias_note.md"
        with open(note_file, 'w', encoding='utf-8') as f:
            f.write(note_content)
        
        note = self.parser.parse_note(note_file)
        
        assert "Target Note" in note.wiki_links
        assert "Another Note" in note.wiki_links
    
    def test_parse_vault_structure(self):
        """Test parsing a complete vault structure."""
        # Create test vault structure
        (self.test_dir / "folder1").mkdir()
        (self.test_dir / "folder2").mkdir()
        (self.test_dir / "Templates").mkdir()
        
        # Create test notes
        notes = [
            ("note1.md", "# Note 1\nThis is note 1 with [[note2]].\n#tag1"),
            ("folder1/note2.md", "# Note 2\nThis is note 2.\n#tag2"),
            ("folder2/note3.md", "# Note 3\nThis links to [[note1]].\n#tag1 #tag3"),
            ("Templates/template.md", "# Template\nThis is a template.\n")
        ]
        
        for path, content in notes:
            file_path = self.test_dir / path
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        vault = self.parser.parse_vault(self.test_dir)
        
        assert len(vault.notes) == 3  # Templates excluded
        assert "note1" in vault.notes
        assert "note2" in vault.notes
        assert "note3" in vault.notes
        assert len(vault.templates) == 1


@pytest.mark.skipif(not OBSIDIAN_AVAILABLE, reason="Obsidian integration not available")
class TestObsidianIntegration:
    """Test the main ObsidianIntegration functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.atlas = ATLASEngine()
        self.integration = ObsidianIntegration(self.atlas)
        self.test_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_integration_initialization(self):
        """Test integration initialization."""
        assert self.integration.atlas is not None
        assert self.integration.parser is not None
        assert isinstance(self.integration.imported_notes, dict)
        assert isinstance(self.integration.exported_files, set)
    
    def test_import_simple_vault(self):
        """Test importing a simple vault."""
        # Create test vault
        (self.test_dir / "Notes").mkdir()
        
        notes = [
            ("note1.md", "# Note 1\nContent about science.\n#science"),
            ("Notes/note2.md", "# Note 2\nContent about technology.\n#technology"),
            ("note3.md", "# Note 3\nLinks to [[note1]] and [[note2]].\n#science #technology")
        ]
        
        for path, content in notes:
            file_path = self.test_dir / path
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        # Import vault
        stats = self.integration.import_vault(self.test_dir)
        
        assert stats['notes_processed'] == 3
        assert stats['entities_created'] == 3
        assert stats['patterns_created'] >= 2  # At least science and technology tags
        assert stats['relationships_created'] >= 2  # Wiki links
        
        # Check that entities were created
        assert len(self.atlas.entities) == 3
        
        # Check that patterns were created
        assert len(self.atlas.patterns) >= 2
    
    def test_export_to_vault(self):
        """Test exporting ATLAS data to a vault."""
        # Add test data to ATLAS
        entity = Entity(
            entity_id="test_entity",
            attributes={
                "title": "Test Entity",
                "content": "This is test content.",
                "domain": "testing"
            },
            patterns=["test_pattern"]
        )
        
        pattern = Pattern(
            pattern_id="test_pattern",
            qkit=["what_is_test", "how_to_test"],
            attributes={"domain": "testing", "description": "A test pattern"}
        )
        
        query = iQuery(
            query_id="test_query",
            query_text="What is testing?",
            target_patterns=["test_pattern"],
            priority=QueryPriority.NORMAL
        )
        
        self.atlas.add_entity(entity.id, entity.to_dict())
        self.atlas.add_pattern(pattern.id, pattern.to_dict())
        self.atlas.add_query(query.id, query.to_dict())
        
        # Export to vault
        output_dir = self.test_dir / "export"
        stats = self.integration.export_to_vault(output_dir)
        
        assert stats['entities_exported'] >= 1
        assert stats['patterns_exported'] >= 1
        assert stats['files_created'] >= 3  # At least entity, pattern, and index
        
        # Check that files were created
        assert (output_dir / "ATLAS_Export" / "Entities").exists()
        assert (output_dir / "ATLAS_Export" / "Patterns").exists()
        assert (output_dir / "ATLAS_Export" / "README.md").exists()
    
    def test_bidirectional_sync(self):
        """Test bidirectional synchronization."""
        # Create test vault with notes
        (self.test_dir / "vault").mkdir()
        test_note = """---
title: Sync Test Note
tags: [sync, test]
---

# Sync Test Note

This note will be synchronized with ATLAS.
"""
        with open(self.test_dir / "vault" / "sync_note.md", 'w') as f:
            f.write(test_note)
        
        # Perform bidirectional sync
        stats = self.integration.sync_vault(
            self.test_dir / "vault", 
            sync_mode='bidirectional'
        )
        
        assert 'import_stats' in stats
        assert 'export_stats' in stats
        assert stats['mode'] == 'bidirectional'
    
    def test_integration_with_real_patterns(self):
        """Test integration with realistic pattern creation."""
        # Create vault with hierarchical tags
        notes = [
            ("ai_overview.md", "# AI Overview\nArtificial Intelligence overview.\n#ai #technology"),
            ("machine_learning.md", "# Machine Learning\nML is part of [[ai_overview]].\n#ai/ml #technology"),
            ("deep_learning.md", "# Deep Learning\nDL is part of [[machine_learning]].\n#ai/ml/dl #technology"),
        ]
        
        for path, content in notes:
            file_path = self.test_dir / path
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        stats = self.integration.import_vault(self.test_dir)
        
        # Should create hierarchical patterns from nested tags
        assert stats['patterns_created'] >= 4  # ai, technology, ai/ml, ai/ml/dl
        
        # Check that patterns were created
        patterns = self.atlas.patterns
        pattern_ids = list(patterns.keys())
        assert any('ai' in p_id for p_id in pattern_ids)
        assert any('technology' in p_id for p_id in pattern_ids)
    
    def test_export_note_format(self):
        """Test the format of exported notes."""
        # Add entity with comprehensive data
        entity = Entity(
            entity_id="detailed_entity",
            attributes={
                "title": "Detailed Entity",
                "content": "This is detailed content with **markdown**.",
                "tags": ["important", "detailed"],
                "created_date": "2023-01-01T10:00:00",
                "custom_field": "custom_value"
            },
            patterns=["detailed_pattern"]
        )
        
        self.atlas.add_entity(entity.id, entity.to_dict())
        
        # Export to vault
        output_dir = self.test_dir / "format_test"
        self.integration.export_to_vault(output_dir)
        
        # Read exported file
        entity_files = list((output_dir / "ATLAS_Export" / "Entities").glob("*.md"))
        assert len(entity_files) > 0
        
        content = entity_files[0].read_text(encoding='utf-8')
        
        # Check frontmatter
        assert '---' in content
        assert 'type: entity' in content
        assert 'entity_id: detailed_entity' in content
        
        # Check content structure
        assert '# Detailed Entity' in content
        assert '## Metadata' in content
        assert 'This is detailed content' in content


@pytest.mark.skipif(not OBSIDIAN_AVAILABLE, reason="Obsidian integration not available")
class TestObsidianEdgeCases:
    """Test edge cases and error handling."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.integration = ObsidianIntegration()
        self.test_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Clean up test fixtures."""
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_empty_vault(self):
        """Test importing an empty vault."""
        stats = self.integration.import_vault(self.test_dir)
        
        assert stats['notes_processed'] == 0
        assert stats['entities_created'] == 0
        assert stats['patterns_created'] == 0
        assert stats['relationships_created'] == 0
    
    def test_malformed_frontmatter(self):
        """Test handling malformed YAML frontmatter."""
        malformed_note = """---
title: Test
invalid_yaml: [unclosed list
tags: test
---

# Test Note

Content here.
"""
        note_file = self.test_dir / "malformed.md"
        with open(note_file, 'w') as f:
            f.write(malformed_note)
        
        # Should not crash
        stats = self.integration.import_vault(self.test_dir)
        assert stats['notes_processed'] == 1
    
    def test_special_characters_in_filenames(self):
        """Test handling special characters in note names."""
        special_notes = [
            ("note with spaces.md", "# Note with Spaces\nContent.\n"),
            ("note-with-dashes.md", "# Note with Dashes\nContent.\n"),
            ("note_with_underscores.md", "# Note with Underscores\nContent.\n"),
        ]
        
        for filename, content in special_notes:
            note_file = self.test_dir / filename
            with open(note_file, 'w') as f:
                f.write(content)
        
        stats = self.integration.import_vault(self.test_dir)
        assert stats['notes_processed'] == 3
        assert stats['entities_created'] == 3
    
    def test_broken_wiki_links(self):
        """Test handling broken wiki links."""
        note_content = """# Test Note

This note has a broken link to [[Non-existent Note]].
And a working link to [[working_note]].
"""
        working_note = """# Working Note

This note exists.
"""
        
        with open(self.test_dir / "test_note.md", 'w') as f:
            f.write(note_content)
        
        with open(self.test_dir / "working_note.md", 'w') as f:
            f.write(working_note)
        
        stats = self.integration.import_vault(self.test_dir)
        
        # Should create entities for both notes
        assert stats['notes_processed'] == 2
        assert stats['entities_created'] == 2
        # Should only create relationship for working link
        assert stats['relationships_created'] == 1


def test_integration_stats():
    """Test getting integration statistics."""
    if not OBSIDIAN_AVAILABLE:
        pytest.skip("Obsidian integration not available")
    
    integration = ObsidianIntegration()
    stats = integration.get_integration_stats()
    
    assert 'imported_notes' in stats
    assert 'exported_files' in stats
    assert 'atlas_entities' in stats
    assert 'atlas_patterns' in stats
    assert 'atlas_queries' in stats


if __name__ == "__main__":
    # Run basic tests
    if OBSIDIAN_AVAILABLE:
        print("Running Obsidian integration tests...")
        
        # Create a simple test
        test_parser = TestObsidianParser()
        test_parser.setup_method()
        
        try:
            test_parser.test_parser_initialization()
            print("✓ Parser initialization test passed")
            
            test_parser.test_parse_simple_note()
            print("✓ Simple note parsing test passed")
            
            print("🎉 Basic Obsidian integration tests completed successfully!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
            
        finally:
            test_parser.teardown_method()
    else:
        print("❌ Obsidian integration not available for testing") 