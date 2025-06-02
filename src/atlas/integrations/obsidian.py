"""
Obsidian Integration for ATLAS

This module provides comprehensive integration with Obsidian vaults,
enabling bidirectional conversion between Obsidian markdown files
and ATLAS knowledge structures.
"""

import re
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, date
from pathlib import Path
from typing import Dict, Optional, Set, List, Any, Union

import yaml

from ..core.engine import ATLASEngine
from ..entities.entity import Entity, EntityMetadata
from ..patterns.pattern import Pattern

logger = logging.getLogger(__name__)


class ATLASJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle datetime and other special objects."""
    def default(self, obj: Any) -> Any:  # type: ignore
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)


@dataclass
class ObsidianNote:
    """Represents an Obsidian note with metadata and content."""
    title: str
    content: str
    file_path: Path
    frontmatter: Dict = field(default_factory=dict)
    wiki_links: Set[str] = field(default_factory=set)
    tags: Set[str] = field(default_factory=set)
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None

    def __post_init__(self):
        """Process note content after initialization."""
        if not self.created_date:
            self.created_date = datetime.now()
        if not self.modified_date:
            self.modified_date = datetime.now()


@dataclass
class ObsidianVault:
    """Represents an Obsidian vault structure."""
    name: str
    root_path: Path
    notes: Dict[str, ObsidianNote] = field(default_factory=dict)
    attachments: Set[Path] = field(default_factory=set)
    templates: Dict[str, str] = field(default_factory=dict)
    settings: Dict = field(default_factory=dict)


class ObsidianParser:
    """Parser for Obsidian markdown files and vault structures."""
    
    def __init__(self):
        """Initialize the Obsidian parser."""
        # Regex patterns for Obsidian syntax
        self.wiki_link_pattern = re.compile(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
        self.tag_pattern = re.compile(r'(?:^|\s)#([a-zA-Z0-9/_-]+)')
        self.frontmatter_pattern = re.compile(
            r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL
        )
        
    def parse_frontmatter(self, content: str) -> tuple[Dict, str]:
        """Parse YAML frontmatter from markdown content."""
        match = self.frontmatter_pattern.match(content)
        if match:
            try:
                frontmatter_data = yaml.safe_load(match.group(1))
                frontmatter = frontmatter_data if isinstance(frontmatter_data, dict) else {}
                content_without_frontmatter = content[match.end():]
                return frontmatter, content_without_frontmatter
            except yaml.YAMLError as e:
                logger.warning(f"Failed to parse YAML frontmatter: {e}")
                return {}, content
        return {}, content
        
    def extract_wiki_links(self, content: str) -> Set[str]:
        """Extract wiki-style links from content."""
        links = set()
        for match in self.wiki_link_pattern.finditer(content):
            link_target = match.group(1).strip()
            links.add(link_target)
        return links
        
    def extract_tags(self, content: str, frontmatter: Optional[Dict] = None) -> Set[str]:
        """Extract tags from content and frontmatter."""
        tags = set()
        
        # Extract from content
        for match in self.tag_pattern.finditer(content):
            tag = match.group(1)
            tags.add(tag)
            
        # Extract from frontmatter
        if frontmatter:
            fm_tags = frontmatter.get('tags', [])
            if isinstance(fm_tags, str):
                fm_tags = [fm_tags]
            elif isinstance(fm_tags, list):
                fm_tags = [str(tag) for tag in fm_tags]
            tags.update(fm_tags)
            
        return tags
        
    def parse_note(self, file_path: Path) -> ObsidianNote:
        """Parse a single Obsidian note file."""
        if not file_path.exists() or file_path.suffix.lower() != '.md':
            raise ValueError(f"Invalid note file: {file_path}")
            
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            raise
            
        frontmatter, clean_content = self.parse_frontmatter(content)
        
        # Extract components
        wiki_links = self.extract_wiki_links(clean_content)
        tags = self.extract_tags(clean_content, frontmatter)
        
        # Get file metadata
        try:
            stat = file_path.stat()
            created = datetime.fromtimestamp(stat.st_ctime)
            modified = datetime.fromtimestamp(stat.st_mtime)
        except Exception as e:
            logger.warning(f"Failed to get file stats for {file_path}: {e}")
            created = datetime.now()
            modified = datetime.now()
        
        return ObsidianNote(
            title=file_path.stem,
            content=clean_content,
            file_path=file_path,
            frontmatter=frontmatter,
            wiki_links=wiki_links,
            tags=tags,
            created_date=created,
            modified_date=modified
        )
        
    def parse_vault(self, vault_path: Path) -> ObsidianVault:
        """Parse an entire Obsidian vault."""
        if not vault_path.exists() or not vault_path.is_dir():
            raise ValueError(f"Invalid vault path: {vault_path}")
            
        vault = ObsidianVault(
            name=vault_path.name,
            root_path=vault_path
        )
        
        # Find and parse markdown files
        for md_file in vault_path.rglob('*.md'):
            # Skip system files and hidden files
            if md_file.name.startswith('.'):
                continue
                
            try:
                note = self.parse_note(md_file)
                vault.notes[note.title] = note
                logger.debug(f"Parsed note: {note.title}")
            except Exception as e:
                logger.warning(f"Could not parse {md_file}: {e}")
                
        # Find attachments
        attachment_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.pdf',
                               '.mp4', '.mp3', '.wav', '.doc', '.docx'}
        for file_path in vault_path.rglob('*'):
            if (file_path.is_file() and 
                file_path.suffix.lower() in attachment_extensions):
                vault.attachments.add(file_path)
                
        # Load templates if they exist
        templates_dir = vault_path / 'Templates'
        if templates_dir.exists():
            for template_file in templates_dir.glob('*.md'):
                try:
                    template_content = template_file.read_text(encoding='utf-8')
                    vault.templates[template_file.stem] = template_content
                except Exception as e:
                    logger.warning(f"Could not read template {template_file}: {e}")
                
        logger.info(f"Parsed vault '{vault.name}' with {len(vault.notes)} notes, "
                   f"{len(vault.attachments)} attachments, {len(vault.templates)} templates")
        return vault


class ObsidianIntegration:
    """Main integration class for Obsidian-ATLAS conversion."""
    
    def __init__(self, atlas_engine: Optional[ATLASEngine] = None):
        """Initialize the Obsidian integration."""
        self.atlas = atlas_engine or ATLASEngine()
        self.parser = ObsidianParser()
        self.imported_notes = {}
        self.exported_files = set()
        self.created_patterns = set()  # Track created patterns to avoid duplicates
        
    def import_vault(self, vault_path: Path, 
                    create_patterns_from_tags: bool = True,
                    create_entities_from_notes: bool = True,
                    link_related_content: bool = True) -> Dict:
        """Import an Obsidian vault into ATLAS."""
        vault = self.parser.parse_vault(vault_path)
        
        import_stats: Dict[str, Any] = {
            'notes_processed': 0,
            'entities_created': 0,
            'patterns_created': 0,
            'relationships_created': 0,
            'errors': []
        }
        
        # Create patterns from unique tags (avoid duplicates)
        if create_patterns_from_tags:
            all_tags = set()
            for note in vault.notes.values():
                all_tags.update(note.tags)
                
            for tag in all_tags:
                pattern_id = f"obsidian_tag_{tag.replace('/', '_').replace('-', '_')}"
                
                # Check if pattern already exists, but track attempts
                pattern_already_exists = (pattern_id in self.created_patterns or 
                                        pattern_id in self.atlas.patterns)
                
                if pattern_already_exists:
                    logger.debug(f"Pattern for tag '{tag}' already exists, skipping")
                    continue
                    
                try:
                    pattern = Pattern(
                        pattern_id=pattern_id,
                        qkit=[f"what_is_{tag.replace('/', '_')}", 
                              f"how_to_{tag.replace('/', '_')}", 
                              f"examples_of_{tag.replace('/', '_')}"],
                        attributes={
                            'source': 'obsidian',
                            'tag': tag,
                            'domain': tag.split('/')[0] if '/' in tag else tag,
                            'pattern_type': 'tag_based'
                        }
                    )
                    
                    if self.atlas.add_pattern(pattern.id, pattern.to_dict()):
                        self.created_patterns.add(pattern_id)
                        import_stats['patterns_created'] += 1
                        logger.debug(f"Created pattern for tag: {tag}")
                        
                except Exception as e:
                    import_stats['errors'].append(
                        f"Error creating pattern for tag '{tag}': {e}"
                    )
                    logger.error(f"Error creating pattern for tag '{tag}': {e}")
                    
        # Create entities from notes
        if create_entities_from_notes:
            for note in vault.notes.values():
                try:
                    entity_id = f"obsidian_note_{note.title.replace(' ', '_').replace('/', '_')}"
                    
                    # Check if entity already exists, but still count processing
                    if entity_id in self.atlas.entities:
                        logger.debug(f"Entity {entity_id} already exists, skipping")
                        import_stats['notes_processed'] += 1
                        continue
                    
                    # Determine patterns for this entity
                    note_patterns = []
                    if create_patterns_from_tags:
                        for tag in note.tags:
                            pattern_id = f"obsidian_tag_{tag.replace('/', '_').replace('-', '_')}"
                            if pattern_id in self.atlas.patterns:
                                note_patterns.append(pattern_id)
                            
                    # Create entity attributes
                    attributes = {
                        'title': note.title,
                        'content': note.content[:1000] + '...' if len(note.content) > 1000 else note.content,
                        'file_path': str(note.file_path),
                        'source': 'obsidian',
                        'tags': list(note.tags),
                        'wiki_links': list(note.wiki_links),
                        'created_date': note.created_date.isoformat() if note.created_date else None,
                        'modified_date': note.modified_date.isoformat() if note.modified_date else None,
                        'content_length': len(note.content),
                        'has_frontmatter': bool(note.frontmatter)
                    }
                    
                    # Add frontmatter as separate attributes
                    for key, value in note.frontmatter.items():
                        if key not in attributes:  # Don't overwrite existing
                            attributes[f"fm_{key}"] = value
                    
                    # Create metadata
                    metadata = EntityMetadata(
                        created_at=note.created_date or datetime.now(),
                        updated_at=note.modified_date or datetime.now(),
                        source='obsidian_import',
                        tags=note.tags
                    )
                    
                    entity = Entity(
                        entity_id=entity_id,
                        attributes=attributes,
                        patterns=note_patterns,
                        metadata=metadata
                    )
                    
                    if self.atlas.add_entity(entity.id, entity.to_dict()):
                        self.imported_notes[note.title] = entity_id
                        import_stats['entities_created'] += 1
                        import_stats['notes_processed'] += 1
                        logger.debug(f"Created entity for note: {note.title}")
                    
                except Exception as e:
                    import_stats['errors'].append(
                        f"Error creating entity for note '{note.title}': {e}"
                    )
                    logger.error(f"Error creating entity for note '{note.title}': {e}")
                    
        # Create relationships based on wiki links
        if link_related_content:
            for note in vault.notes.values():
                try:
                    source_entity_id = self.imported_notes.get(note.title)
                    if not source_entity_id:
                        continue
                        
                    for link in note.wiki_links:
                        target_entity_id = self.imported_notes.get(link)
                        if target_entity_id and source_entity_id != target_entity_id:
                            if self.atlas.add_relationship(
                                source_entity_id,
                                target_entity_id,
                                'references'
                            ):
                                import_stats['relationships_created'] += 1
                                
                except Exception as e:
                    import_stats['errors'].append(
                        f"Error creating relationships for '{note.title}': {e}"
                    )
                    logger.error(f"Error creating relationships for '{note.title}': {e}")
                    
        logger.info(f"Import completed: {import_stats}")
        return import_stats
        
    def export_to_vault(self, output_path: Path,
                       vault_name: str = "ATLAS_Export",
                       include_entities: bool = True,
                       include_patterns: bool = True,
                       create_index: bool = True) -> Dict[str, Any]:
        """Export ATLAS data to an Obsidian vault."""
        vault_path = output_path / vault_name
        vault_path.mkdir(parents=True, exist_ok=True)
        
        export_stats: Dict[str, Any] = {
            'files_created': 0,
            'entities_exported': 0,
            'patterns_exported': 0,
            'errors': []
        }
        
        # Export entities as notes
        if include_entities:
            entities_dir = vault_path / "Entities"
            entities_dir.mkdir(exist_ok=True)
            
            for entity_id, entity_data in self.atlas.entities.items():
                try:
                    self._export_entity_as_note(
                        entity_id, entity_data, entities_dir
                    )
                    export_stats['entities_exported'] = export_stats['entities_exported'] + 1
                    export_stats['files_created'] = export_stats['files_created'] + 1
                except Exception as e:
                    export_stats['errors'].append(
                        f"Error exporting entity '{entity_id}': {e}"
                    )
                    logger.error(f"Error exporting entity '{entity_id}': {e}")
                    
        # Export patterns as notes
        if include_patterns:
            patterns_dir = vault_path / "Patterns"
            patterns_dir.mkdir(exist_ok=True)
            
            for pattern_id, pattern_data in self.atlas.patterns.items():
                try:
                    self._export_pattern_as_note(
                        pattern_id, pattern_data, patterns_dir
                    )
                    export_stats['patterns_exported'] = export_stats['patterns_exported'] + 1
                    export_stats['files_created'] = export_stats['files_created'] + 1
                except Exception as e:
                    export_stats['errors'].append(
                        f"Error exporting pattern '{pattern_id}': {e}"
                    )
                    logger.error(f"Error exporting pattern '{pattern_id}': {e}")
                    
        # Create index file
        if create_index:
            try:
                self._create_vault_index(vault_path, export_stats)
                export_stats['files_created'] = export_stats['files_created'] + 1
            except Exception as e:
                export_stats['errors'].append(f"Error creating index: {e}")
                logger.error(f"Error creating index: {e}")
                
        logger.info(f"Export completed: {export_stats}")
        return export_stats
        
    def _export_entity_as_note(self, entity_id: str, entity_data: Dict[str, Any],
                              output_dir: Path) -> None:
        """Export a single entity as an Obsidian note."""
        # Create frontmatter
        frontmatter = {
            'type': 'entity',
            'entity_id': entity_id,
            'created': datetime.now().isoformat(),
            'tags': ['atlas-entity']
        }
        
        # Add entity attributes to frontmatter
        attributes = entity_data.get('attributes', {})
        if 'tags' in attributes:
            existing_tags = frontmatter.get('tags', [])
            if isinstance(existing_tags, list) and isinstance(attributes['tags'], list):
                existing_tags.extend(attributes['tags'])
                frontmatter['tags'] = existing_tags
            
        # Create content
        title = attributes.get('title', entity_id)
        content = f"# {title}\n\n"
        
        # Add description or content
        if 'content' in attributes:
            content += f"{attributes['content']}\n\n"
        elif 'description' in attributes:
            content += f"{attributes['description']}\n\n"
            
        # Add metadata section
        content += "## Metadata\n\n"
        for key, value in attributes.items():
            if key not in ['title', 'content', 'description', 'tags']:
                content += f"- **{key}**: {value}\n"
                
        # Add patterns section
        patterns = entity_data.get('patterns', [])
        if patterns:
            content += "\n## Related Patterns\n\n"
            for pattern in patterns:
                content += f"- [[{pattern}]]\n"
                
        # Add relationships section from graph
        try:
            relationships = self.atlas.get_relationships(entity_id)
            if relationships:
                content += "\n## Relationships\n\n"
                for target_id, rel_type in relationships:
                    target_data = self.atlas.get_node(target_id)
                    if target_data:
                        target_title = target_data.get('data', {}).get('attributes', {}).get('title', target_id)
                        content += f"- **{rel_type.replace('_', ' ').title()}**: [[{target_title}]]\n"
        except Exception as e:
            logger.warning(f"Could not get relationships for {entity_id}: {e}")
                
        # Write file
        safe_title = self._sanitize_filename(title)
        filename = f"{safe_title}.md"
        file_path = output_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("---\n")
                yaml.dump(frontmatter, f, default_flow_style=False)
                f.write("---\n\n")
                f.write(content)
                
            self.exported_files.add(file_path)
            logger.debug(f"Exported entity {entity_id} to {filename}")
        except Exception as e:
            logger.error(f"Failed to write entity file {filename}: {e}")
            raise
        
    def _export_pattern_as_note(self, pattern_id: str, pattern_data: Dict[str, Any],
                               output_dir: Path) -> None:
        """Export a single pattern as an Obsidian note."""
        # Create frontmatter
        frontmatter = {
            'type': 'pattern',
            'pattern_id': pattern_id,
            'created': datetime.now().isoformat(),
            'tags': ['atlas-pattern']
        }
        
        # Add pattern attributes to frontmatter
        attributes = pattern_data.get('attributes', {})
        if 'domain' in attributes:
            frontmatter['domain'] = attributes['domain']
            
        # Create content
        title = attributes.get('name', pattern_id)
        content = f"# {title}\n\n"
        
        # Add description
        if 'description' in attributes:
            content += f"{attributes['description']}\n\n"
            
        # Add qkit section
        qkit = pattern_data.get('qkit', [])
        if qkit:
            content += "## Key Questions (QKit)\n\n"
            for question in qkit:
                content += f"- {question}\n"
            content += "\n"
            
        # Add attributes section
        content += "## Pattern Attributes\n\n"
        for key, value in attributes.items():
            if key not in ['name', 'description']:
                content += f"- **{key}**: {value}\n"
                
        # Add related entities section
        related_entities = self._find_entities_using_pattern(pattern_id)
        if related_entities:
            content += "\n## Related Entities\n\n"
            for entity_id in related_entities:
                entity_data = self.atlas.entities.get(entity_id, {})
                entity_title = entity_data.get('attributes', {}).get(
                    'title', entity_id
                )
                content += f"- [[{entity_title}]]\n"
                
        # Write file
        safe_title = self._sanitize_filename(title)
        filename = f"{safe_title}.md"
        file_path = output_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("---\n")
                yaml.dump(frontmatter, f, default_flow_style=False)
                f.write("---\n\n")
                f.write(content)
                
            self.exported_files.add(file_path)
            logger.debug(f"Exported pattern {pattern_id} to {filename}")
        except Exception as e:
            logger.error(f"Failed to write pattern file {filename}: {e}")
            raise
        
    def _find_entities_using_pattern(self, pattern_id: str) -> List[str]:
        """Find entities that use a specific pattern."""
        related_entities = []
        for entity_id, entity_data in self.atlas.entities.items():
            entity_patterns = entity_data.get('patterns', [])
            if pattern_id in entity_patterns:
                related_entities.append(entity_id)
        return related_entities
        
    def _create_vault_index(self, vault_path: Path, export_stats: Dict[str, Any]) -> None:
        """Create an index file for the exported vault."""
        frontmatter = {
            'type': 'index',
            'created': datetime.now().isoformat(),
            'tags': ['atlas-index', 'navigation']
        }
        
        content = "# ATLAS Knowledge Vault\n\n"
        content += "This vault contains knowledge exported from ATLAS.\n\n"
        
        # Add export statistics
        content += "## Export Statistics\n\n"
        content += f"- Entities exported: {export_stats['entities_exported']}\n"
        content += f"- Patterns exported: {export_stats['patterns_exported']}\n"
        content += f"- Total files created: {export_stats['files_created']}\n"
        content += f"- Export date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Add navigation sections
        entities_dir = vault_path / "Entities"
        if entities_dir.exists():
            content += "## Entities\n\n"
            for md_file in sorted(entities_dir.glob('*.md')):
                title = md_file.stem
                content += f"- [[{title}]]\n"
            content += "\n"
            
        patterns_dir = vault_path / "Patterns"
        if patterns_dir.exists():
            content += "## Patterns\n\n"
            for md_file in sorted(patterns_dir.glob('*.md')):
                title = md_file.stem
                content += f"- [[{title}]]\n"
            content += "\n"
            
        # Write index file
        index_path = vault_path / "README.md"
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write("---\n")
                yaml.dump(frontmatter, f, default_flow_style=False)
                f.write("---\n\n")
                f.write(content)
            logger.debug(f"Created vault index at {index_path}")
        except Exception as e:
            logger.error(f"Failed to write index file: {e}")
            raise
            
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize a filename for safe use across platforms."""
        # Replace problematic characters
        safe_chars = ".-_() "
        sanitized = ""
        for char in filename:
            if char.isalnum() or char in safe_chars:
                sanitized += char
            else:
                sanitized += "_"
        
        # Limit length and clean up
        sanitized = sanitized.strip()[:100]
        sanitized = re.sub(r'_+', '_', sanitized)  # Replace multiple underscores
        return sanitized
            
    def sync_vault(self, vault_path: Path, sync_mode: str = "bidirectional") -> Dict[str, Any]:
        """Synchronize an Obsidian vault with ATLAS data."""
        if sync_mode not in ["import", "export", "bidirectional"]:
            raise ValueError(
                "sync_mode must be 'import', 'export', or 'bidirectional'"
            )
            
        sync_stats: Dict[str, Any] = {
            'mode': sync_mode,
            'timestamp': datetime.now().isoformat(),
            'import_stats': {},
            'export_stats': {}
        }
        
        if sync_mode in ["import", "bidirectional"]:
            sync_stats['import_stats'] = self.import_vault(vault_path)
            
        if sync_mode in ["export", "bidirectional"]:
            sync_stats['export_stats'] = self.export_to_vault(
                vault_path.parent, vault_path.name
            )
            
        logger.info(f"Sync completed in {sync_mode} mode")
        return sync_stats
        
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get statistics about the integration state."""
        return {
            'imported_notes': len(self.imported_notes),
            'exported_files': len(self.exported_files),
            'created_patterns': len(self.created_patterns),
            'atlas_entities': len(self.atlas.entities),
            'atlas_patterns': len(self.atlas.patterns),
            'atlas_queries': len(self.atlas.queries),
            'atlas_metrics': self.atlas.get_metrics()
        }
        
    def export_data_as_json(self, output_path: Path) -> Dict[str, Any]:
        """Export ATLAS data as JSON with proper serialization."""
        export_data = {
            'metadata': {
                'export_timestamp': datetime.now().isoformat(),
                'atlas_version': '1.0.0',
                'total_entities': len(self.atlas.entities),
                'total_patterns': len(self.atlas.patterns),
                'total_queries': len(self.atlas.queries)
            },
            'entities': self.atlas.entities,
            'patterns': self.atlas.patterns,
            'queries': self.atlas.queries,
            'integration_stats': self.get_integration_stats()
        }
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, cls=ATLASJSONEncoder, indent=2)
            logger.info(f"Exported ATLAS data to {output_path}")
            return {'success': True, 'file_path': str(output_path)}
        except Exception as e:
            logger.error(f"Failed to export JSON data: {e}")
            return {'success': False, 'error': str(e)} 