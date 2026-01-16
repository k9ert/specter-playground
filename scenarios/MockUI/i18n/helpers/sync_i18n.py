#!/usr/bin/env python3
"""
i18n Synchronization Tool for Specter UI

This tool helps maintain consistency between language files and source code:
1. Identifies missing/obsolete i18n strings in the English (master) language file
2. Synchronizes other language files with the English master file
3. Generates detailed logs of all changes made

Usage:
    python sync_i18n.py [--dry-run] [--source-dir path] [--i18n-dir path]
    
Options:
    --dry-run      Show what would be changed without making actual changes
    --source-dir   Directory to search for source files (default: parent of i18n dir)
    --i18n-dir     Directory containing i18n files (default: auto-detected)
    --log-dir      Directory to write log files (default: same as i18n-dir)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, List, Tuple, Any


class I18nSynchronizer:
    """Manages synchronization of i18n files and source code."""
    
    def __init__(self, i18n_dir: str, source_dir: str, log_dir: str, dry_run: bool = False):
        self.i18n_dir = Path(i18n_dir)
        self.source_dir = Path(source_dir)
        self.log_dir = Path(log_dir)
        self.dry_run = dry_run
        
        self.english_file = self.i18n_dir / "specter_ui_en.json"
        self.dummy_text = "<FILL>"
        
        # Pattern to match t("KEY") in source code
        self.i18n_pattern = re.compile(r't\("([^"]+)"\)')
        
        # Logs for tracking changes
        self.master_log = []
        self.file_logs = {}
        
    def log_master(self, message: str):
        """Add message to master log."""
        self.master_log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        print(message)
    
    def log_file(self, filename: str, message: str):
        """Add message to file-specific log."""
        if filename not in self.file_logs:
            self.file_logs[filename] = []
        self.file_logs[filename].append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def find_i18n_keys_in_source(self) -> Set[str]:
        """Scan source files for i18n key usage."""
        self.log_master("Scanning source files for i18n keys...")
        keys_found = set()
        
        # Search for Python files in the source directory
        python_files = list(self.source_dir.rglob("*.py"))
        
        # Filter out files that are not likely to contain UI code
        ui_files = []
        for file_path in python_files:
            # Skip test files, tool scripts, and build artifacts
            path_str = str(file_path)
            skip_patterns = [
                '/test', '/tests', 'test_',
                '/tools/', '/build/', '/__pycache__/',
                '/batch_convert_', '/c_to_python_', '/generate_python_icons',
                'btc_icons.py', '_test.py'
            ]
            
            if not any(pattern in path_str for pattern in skip_patterns):
                ui_files.append(file_path)
        
        for file_path in ui_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    matches = self.i18n_pattern.findall(content)
                    for key in matches:
                        # Filter out obvious false positives
                        if (key.isupper() and '_' in key and 
                            len(key) > 2 and 
                            not key.startswith('.') and
                            not key.startswith('#') and
                            ' ' not in key):
                            keys_found.add(key)
            except Exception as e:
                self.log_master(f"Warning: Could not read {file_path}: {e}")
        
        self.log_master(f"Found {len(keys_found)} unique i18n keys in {len(ui_files)} UI files")
        return keys_found
    
    def load_english_translations(self) -> Dict[str, str]:
        """Load the English (master) translation file."""
        if not self.english_file.exists():
            raise FileNotFoundError(f"English translation file not found: {self.english_file}")
            
        with open(self.english_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return data.get('translations', {})
    
    def save_english_translations(self, translations: Dict[str, str]):
        """Save the English (master) translation file."""
        if not self.english_file.exists():
            raise FileNotFoundError(f"English translation file not found: {self.english_file}")
            
        # Load existing data to preserve metadata
        with open(self.english_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data['translations'] = translations
        
        if not self.dry_run:
            with open(self.english_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def sync_english_master(self) -> Tuple[Set[str], Set[str]]:
        """
        Synchronize English master file with source code usage.
        Returns (missing_keys, obsolete_keys).
        """
        self.log_master("=== Synchronizing English master file ===")
        
        source_keys = self.find_i18n_keys_in_source()
        english_translations = self.load_english_translations()
        english_keys = set(english_translations.keys())
        
        missing_keys = source_keys - english_keys
        obsolete_keys = english_keys - source_keys
        
        self.log_master(f"Missing keys in English file: {len(missing_keys)}")
        for key in sorted(missing_keys):
            self.log_master(f"  + {key}")
            
        self.log_master(f"Obsolete keys in English file: {len(obsolete_keys)}")
        for key in sorted(obsolete_keys):
            self.log_master(f"  - {key}")
        
        # Update English translations
        updated_translations = english_translations.copy()
        
        # Add missing keys with dummy text
        for key in missing_keys:
            updated_translations[key] = self.dummy_text
            
        # Remove obsolete keys
        for key in obsolete_keys:
            del updated_translations[key]
            
        if missing_keys or obsolete_keys:
            self.log_master(f"Updating English master file...")
            self.save_english_translations(updated_translations)
        else:
            self.log_master("English master file is already in sync")
            
        return missing_keys, obsolete_keys
    
    def get_language_files(self) -> List[Path]:
        """Get all non-English language files."""
        pattern = "specter_ui_*.json"
        language_files = []
        
        for file_path in self.i18n_dir.glob(pattern):
            if file_path.name != "specter_ui_en.json":
                language_files.append(file_path)
                
        return sorted(language_files)
    
    def load_language_file(self, file_path: Path) -> Dict[str, Dict[str, str]]:
        """Load a non-English language file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return data.get('translations', {})
    
    def save_language_file(self, file_path: Path, translations: Dict[str, Dict[str, str]]):
        """Save a non-English language file."""
        # Load existing data to preserve metadata
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data['translations'] = translations
        
        if not self.dry_run:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    def sync_language_file(self, file_path: Path, english_translations: Dict[str, str]):
        """Synchronize a single non-English language file with English master."""
        filename = file_path.name
        self.log_master(f"Synchronizing {filename}...")
        
        lang_translations = self.load_language_file(file_path)
        updated_translations = {}
        
        # Track different types of changes
        added_keys = []
        updated_ref_keys = []
        converted_format_keys = []
        removed_keys = []
        
        for en_key, en_text in english_translations.items():
            if en_key in lang_translations:
                # Key exists in both - check if English reference is up to date
                existing = lang_translations[en_key]
                if isinstance(existing, dict):
                    if existing.get('ref_en') != en_text:
                        # English reference text has changed
                        updated_translations[en_key] = {
                            'text': existing.get('text', self.dummy_text),
                            'ref_en': en_text
                        }
                        updated_ref_keys.append(en_key)
                        self.log_file(filename, f"Updated English reference for {en_key}: '{existing.get('ref_en', '')}' -> '{en_text}'")
                    else:
                        # No change needed
                        updated_translations[en_key] = existing
                else:
                    # Old format - convert to new format
                    updated_translations[en_key] = {
                        'text': existing if existing else self.dummy_text,
                        'ref_en': en_text
                    }
                    converted_format_keys.append(en_key)
                    self.log_file(filename, f"Converted format for {en_key}")
            else:
                # Key only in English - add dummy entry
                updated_translations[en_key] = {
                    'text': self.dummy_text,
                    'ref_en': en_text
                }
                added_keys.append(en_key)
                self.log_file(filename, f"Added new key {en_key}")
        
        # Check for keys only in language file (should be removed)
        lang_only_keys = set(lang_translations.keys()) - set(english_translations.keys())
        removed_keys = list(lang_only_keys)
        for key in lang_only_keys:
            self.log_file(filename, f"Removed obsolete key {key}")
        
        # Log summary of changes
        total_changes = len(added_keys) + len(updated_ref_keys) + len(converted_format_keys) + len(removed_keys)
        
        if total_changes > 0:
            self.log_master(f"Changes made to {filename}:")
            if added_keys:
                self.log_master(f"  Added keys: {len(added_keys)}")
                for key in sorted(added_keys):
                    self.log_master(f"    + {key}")
            if updated_ref_keys:
                self.log_master(f"  Updated English references: {len(updated_ref_keys)}")
                for key in sorted(updated_ref_keys):
                    self.log_master(f"    ~ {key}")
            if converted_format_keys:
                self.log_master(f"  Converted format: {len(converted_format_keys)}")
                for key in sorted(converted_format_keys):
                    self.log_master(f"    * {key}")
            if removed_keys:
                self.log_master(f"  Removed obsolete keys: {len(removed_keys)}")
                for key in sorted(removed_keys):
                    self.log_master(f"    - {key}")
            
            self.save_language_file(file_path, updated_translations)
        else:
            self.log_master(f"  No changes needed for {filename}")
    
    def sync_all_language_files(self):
        """Synchronize all non-English language files with English master."""
        self.log_master("=== Synchronizing language files ===")
        
        english_translations = self.load_english_translations()
        language_files = self.get_language_files()
        
        if not language_files:
            self.log_master("No language files found to synchronize")
            return
        
        for file_path in language_files:
            self.sync_language_file(file_path, english_translations)
    
    def write_log_files(self):
        """Write log files to disk."""
        if self.dry_run:
            self.log_master("=== Dry run completed - no changes were made ===")
            return
            
        self.log_master("Writing log files...")
        
        # Write master log
        master_log_path = self.log_dir / "i18n_sync_master.log"
        with open(master_log_path, 'w', encoding='utf-8') as f:
            f.write(f"i18n Synchronization Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            for line in self.master_log:
                f.write(line + "\n")
        
        # Write file-specific logs
        for filename, log_lines in self.file_logs.items():
            file_log_path = self.log_dir / f"i18n_sync_{filename.replace('.json', '')}.log"
            with open(file_log_path, 'w', encoding='utf-8') as f:
                f.write(f"i18n Synchronization Log for {filename} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                for line in log_lines:
                    f.write(line + "\n")
        
        self.log_master(f"Logs written to {self.log_dir}")
    
    def run(self):
        """Run the full synchronization process."""
        self.log_master(f"Starting i18n synchronization...")
        self.log_master(f"i18n directory: {self.i18n_dir}")
        self.log_master(f"Source directory: {self.source_dir}")
        self.log_master(f"Dry run: {self.dry_run}")
        self.log_master("")
        
        try:
            # Step 1: Sync English master file
            self.sync_english_master()
            
            # Step 2: Sync all language files
            self.sync_all_language_files()
            
            # Step 3: Write logs
            self.write_log_files()
            
            self.log_master("")
            self.log_master("i18n synchronization completed successfully!")
            
        except Exception as e:
            self.log_master(f"Error during synchronization: {e}")
            raise


def main():
    parser = argparse.ArgumentParser(description="Synchronize i18n files with source code")
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making actual changes')
    parser.add_argument('--source-dir', type=str,
                       help='Directory to search for source files')
    parser.add_argument('--i18n-dir', type=str,
                       help='Directory containing i18n files')
    parser.add_argument('--log-dir', type=str,
                       help='Directory to write log files')
    
    args = parser.parse_args()
    
    # Auto-detect directories if not specified
    script_dir = Path(__file__).parent
    default_i18n_dir = script_dir.parent  # Parent of helpers directory
    default_source_dir = default_i18n_dir.parent.parent  # scenarios/MockUI
    
    i18n_dir = args.i18n_dir or str(default_i18n_dir)
    source_dir = args.source_dir or str(default_source_dir)
    log_dir = args.log_dir or i18n_dir
    
    # Validate directories
    if not Path(i18n_dir).exists():
        print(f"Error: i18n directory does not exist: {i18n_dir}")
        sys.exit(1)
    
    if not Path(source_dir).exists():
        print(f"Error: source directory does not exist: {source_dir}")
        sys.exit(1)
    
    english_file = Path(i18n_dir) / "specter_ui_en.json"
    if not english_file.exists():
        print(f"Error: English master file does not exist: {english_file}")
        sys.exit(1)
    
    # Create log directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    
    # Run synchronization
    synchronizer = I18nSynchronizer(i18n_dir, source_dir, log_dir, args.dry_run)
    synchronizer.run()


if __name__ == "__main__":
    main()