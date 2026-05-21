#!/usr/bin/env python3
"""
i18n Synchronization Tool for Specter UI

Build-time tool that keeps JSON language files consistent with source code:
1. Identifies missing / obsolete i18n strings in the English (master) language file
2. Synchronizes other language files with the English master
3. Generates detailed logs of all changes made

Usage:
    python sync_i18n.py [--dry-run] [--source-dir PATH] [--languages-dir PATH] [--log-dir PATH]

Options:
    --dry-run         Show what would be changed without making actual changes
    --source-dir      Directory to search for Python source files
                      (default: scenarios/MockUI relative to repo root)
    --languages-dir   Directory containing JSON language files
                      (default: scenarios/MockUI/src/MockUI/i18n/languages relative to repo root)
    --log-dir         Directory to write log files
                      (default: build/ relative to repo root)

Key detection patterns recognised in source code:
    t("KEY") / t('KEY')
    i18n["KEY"] / i18n['KEY']
    i18n("KEY") / i18n('KEY')
    i18n_manager["KEY"] / i18n_manager['KEY']
    i18n_manager("KEY") / i18n_manager('KEY')
    i18n_manager.t("KEY") / i18n_manager.t('KEY')
    TITLE_KEY = "KEY"  (GenericMenu subclass class attribute)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple


# ---------------------------------------------------------------------------
# Bootstrap: resolve repo root and make lang_compiler importable without
# requiring the caller to set up PYTHONPATH.
# ---------------------------------------------------------------------------
_SCRIPT_DIR = Path(__file__).resolve().parent   # …/tools/
_REPO_ROOT = _SCRIPT_DIR.parent                 # …/specter-playground/
_I18N_PKG_DIR = _REPO_ROOT / "scenarios" / "MockUI" / "src" / "MockUI" / "i18n"

sys.path.insert(0, str(_I18N_PKG_DIR))

from lang_compiler import (          # noqa: E402  (import after sys.path tweak)
    extract_language_code_from_filename,
    JSON_FILE_PREFIX,
    JSON_FILE_SUFFIX,
    FILL_PLACEHOLDER,
)


class I18nSynchronizer:
    """Manages synchronization of JSON language files with source code."""

    def __init__(
        self,
        languages_dir: str,
        source_dir: str,
        log_dir: str,
        languages_to_sync: List[str] = None,
        dry_run: bool = False,
    ):
        self.languages_dir = Path(languages_dir)
        self.source_dir = Path(source_dir)
        self.log_dir = Path(log_dir)
        self.languages_to_sync = languages_to_sync
        self.dry_run = dry_run

        self.english_file = self.languages_dir / "specter_ui_en.json"

        # All patterns that constitute an i18n key lookup in source code.
        # Double- and single-quote variants are both handled.
        #
        #   t("KEY") / t('KEY')
        #   i18n["KEY"] / i18n['KEY']
        #   i18n("KEY") / i18n('KEY')
        #   i18n_manager["KEY"] / i18n_manager['KEY']
        #   i18n_manager("KEY") / i18n_manager('KEY')
        #   i18n_manager.t("KEY") / i18n_manager.t('KEY')  ← captured by the
        #       generic t() pattern since we match the .t(…) suffix
        #   TITLE_KEY = "KEY"  (GenericMenu subclass class attribute)
        _dq = r'"([^"]+)"'   # double-quoted key capture group
        _sq = r"'([^']+)'"   # single-quoted key capture group
        self.i18n_patterns = [
            re.compile(r't\(' + _dq + r'\)'),
            re.compile(r"t\(" + _sq + r"\)"),
            re.compile(r'i18n(?:_manager)?\[' + _dq + r'\]'),
            re.compile(r"i18n(?:_manager)?\[" + _sq + r"\]"),
            re.compile(r'i18n(?:_manager)?\(' + _dq + r'\)'),
            re.compile(r"i18n(?:_manager)?\(" + _sq + r"\)"),
            # GenericMenu subclasses declare the title key as a class attribute
            # instead of calling t("KEY") directly — scan for that pattern too.
            re.compile(r'TITLE_KEY\s*=\s*' + _dq),
            re.compile(r"TITLE_KEY\s*=\s*" + _sq),
            re.compile(r'"(HELP_[A-Z0-9_]+)"'),  # for help texts, HELP_ keys are passed as argument and resolved later
            re.compile(r'"(TOUR_[A-Z0-9_]+)"'),  # for tour texts, TOUR_ keys are passed as argument and resolved later
        ]

        # Tracks which per-file log files have already been initialised
        # (header written).  Master log is initialised in _init_logs().
        self._initialized_file_logs: Set[str] = set()

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------

    # Every write uses the open/write/close pattern so partial logs are
    # preserved even if the process crashes mid-run.

    def _master_log_path(self) -> Path:
        return self.log_dir / "i18n_sync_master.log"

    def _file_log_path(self, filename: str) -> Path:
        return self.log_dir / f"i18n_sync_{filename.replace('.json', '')}.log"

    def _append_to_log(self, log_path: Path, line: str) -> None:
        """Append *line* to *log_path*, opening and closing the file each time."""
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def _init_logs(self) -> None:
        """
        Create log files with a header (including a dry-run notice when
        applicable).  Called once at the very start of run() so that headers
        are always the first thing in the file.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dry_banner = "*** DRY RUN — no changes will be made ***\n" if self.dry_run else ""

        with open(self._master_log_path(), "w", encoding="utf-8") as f:
            f.write(f"i18n Synchronization Log — {timestamp}\n")
            if dry_banner:
                f.write(dry_banner)
            f.write("=" * 60 + "\n\n")

    def _ensure_file_log(self, filename: str) -> None:
        """Initialise the per-file log with a header on first use."""
        if filename in self._initialized_file_logs:
            return
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dry_banner = "*** DRY RUN — no changes will be made ***\n" if self.dry_run else ""
        with open(self._file_log_path(filename), "w", encoding="utf-8") as f:
            f.write(f"i18n Synchronization Log for {filename} — {timestamp}\n")
            if dry_banner:
                f.write(dry_banner)
            f.write("=" * 60 + "\n\n")
        self._initialized_file_logs.add(filename)

    def log_master(self, message: str) -> None:
        """Print *message* and immediately append it to the master log file."""
        stamped = f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
        print(message)
        self._append_to_log(self._master_log_path(), stamped)

    def log_file(self, filename: str, message: str) -> None:
        """Immediately append *message* to the per-file log (not printed)."""
        self._ensure_file_log(filename)
        stamped = f"[{datetime.now().strftime('%H:%M:%S')}] {message}"
        self._append_to_log(self._file_log_path(filename), stamped)

    # ------------------------------------------------------------------
    # Source scanning
    # ------------------------------------------------------------------

    def find_i18n_keys_in_source(self) -> Set[str]:
        """Scan Python source files for i18n key usage and return all found keys."""
        self.log_master("Scanning source files for i18n keys...")
        keys_found: Set[str] = set()

        python_files = list(self.source_dir.rglob("*.py"))

        # Filter out files that are unlikely to contain UI-level i18n calls
        skip_patterns = [
            "/test", "/tests", "test_",
            "/tools/", "/build/", "/__pycache__/",
            "/batch_convert_", "/c_to_python_", "/generate_python_icons",
            "btc_icons.py", "_test.py",
        ]
        ui_files = [
            fp for fp in python_files
            if not any(pat in str(fp) for pat in skip_patterns)
        ]

        for file_path in ui_files:
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception as e:
                self.log_master(f"Warning: Could not read {file_path}: {e}")
                continue

            for pattern in self.i18n_patterns:
                for key in pattern.findall(content):
                    # Reject obvious false positives: keys must follow the
                    # SCREAMING_SNAKE_CASE convention used throughout this project.
                    if (
                        key.isupper()
                        and "_" in key
                        and len(key) > 2
                        and " " not in key
                        and not key.startswith(".")
                        and not key.startswith("#")
                    ):
                        keys_found.add(key)

        self.log_master(
            f"Found {len(keys_found)} unique i18n keys in {len(ui_files)} UI files"
        )
        return keys_found

    # ------------------------------------------------------------------
    # English master file helpers
    # ------------------------------------------------------------------

    def load_english_translations(self) -> Dict[str, str]:
        """Load and return the translations dict from the English master file."""
        if not self.english_file.exists():
            raise FileNotFoundError(
                f"English translation file not found: {self.english_file}"
            )
        with open(self.english_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("translations", {})

    def save_english_translations(self, translations: Dict[str, str]):
        """Persist *translations* back into the English master file, preserving metadata."""
        with open(self.english_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["translations"] = translations
        if not self.dry_run:
            with open(self.english_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def sync_english_master(self) -> Tuple[Set[str], Set[str]]:
        """
        Synchronize the English master file with source code usage.

        - Adds missing keys with FILL_PLACEHOLDER as value.
        - Removes obsolete keys that are no longer referenced in source.

        Returns:
            (missing_keys, obsolete_keys)
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

        updated = english_translations.copy()
        for key in missing_keys:
            updated[key] = FILL_PLACEHOLDER
        for key in obsolete_keys:
            del updated[key]

        if missing_keys or obsolete_keys:
            self.log_master("Updating English master file...")
            self.save_english_translations(updated)
        else:
            self.log_master("English master file is already in sync")

        return missing_keys, obsolete_keys

    # ------------------------------------------------------------------
    # Language file helpers
    # ------------------------------------------------------------------

    def get_language_files(self) -> List[Path]:
        """
        Return all non-English language files in languages_dir that pass the
        project's filename naming conventions (validated via lang_compiler).
        """
        language_files: List[Path] = []
        candidate_glob = f"{JSON_FILE_PREFIX}*{JSON_FILE_SUFFIX}"

        for file_path in sorted(self.languages_dir.glob(candidate_glob)):
            if file_path.name == "specter_ui_en.json":
                continue  # English master is handled separately

            lang_code = extract_language_code_from_filename(file_path.name)
            if lang_code is None:
                self.log_master(
                    f"Warning: Skipping '{file_path.name}' — "
                    "does not follow naming conventions (expected specter_ui_XX.json)"
                )
                continue

            language_files.append(file_path)

        return language_files

    def load_language_file(self, file_path: Path) -> Dict:
        """Load and return the translations dict from a non-English language file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("translations", {})

    def save_language_file(self, file_path: Path, translations: Dict):
        """Persist *translations* back into *file_path*, preserving metadata."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["translations"] = translations
        if not self.dry_run:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def sync_language_file(self, file_path: Path, english_translations: Dict[str, str]):
        """
        Synchronize a single non-English language file against the English master.

        For each key in the English master:
        - Key already present as ``{"text": …, "ref_en": …}`` dict  → update
          ref_en if English text changed, otherwise leave intact.
        - Key present as a plain string  → migrate to dict format with a warning.
          This handles manually authored files or files copied from the English
          master before running sync for the first time.
        - Key missing entirely  → add with FILL_PLACEHOLDER text.

        Keys only present in the language file (obsolete) are removed.
        """
        filename = file_path.name
        self.log_master(f"Synchronizing {filename}...")

        lang_translations = self.load_language_file(file_path)
        updated: Dict = {}
        added_keys: List[str] = []
        updated_ref_keys: List[str] = []
        migrated_format_keys: List[str] = []
        removed_keys: List[str] = []

        for en_key, en_text in english_translations.items():
            if en_key in lang_translations:
                existing = lang_translations[en_key]

                if isinstance(existing, dict):
                    if existing.get("ref_en") != en_text:
                        # English source text changed — flag for re-translation
                        updated[en_key] = {
                            "text": existing.get("text", FILL_PLACEHOLDER),
                            "ref_en": en_text,
                        }
                        updated_ref_keys.append(en_key)
                        self.log_file(
                            filename,
                            f"Updated English reference for {en_key}: "
                            f"'{existing.get('ref_en', '')}' -> '{en_text}'",
                        )
                    else:
                        updated[en_key] = existing  # no change needed
                else:
                    # Plain string format — migrate to the standard dict format.
                    # This is defensive; it can happen when a new language file is
                    # created by copy-pasting from specter_ui_en.json.
                    self.log_master(
                        f"Warning: '{en_key}' in {filename} uses plain string format — "
                        "migrating to {text, ref_en} format. "
                        "Please verify the translation value is correct."
                    )
                    updated[en_key] = {
                        "text": existing if existing else FILL_PLACEHOLDER,
                        "ref_en": en_text,
                    }
                    migrated_format_keys.append(en_key)
                    self.log_file(filename, f"Migrated plain string format for {en_key}")
            else:
                # New key — add stub for translator
                updated[en_key] = {"text": FILL_PLACEHOLDER, "ref_en": en_text}
                added_keys.append(en_key)
                self.log_file(filename, f"Added new key {en_key}")

        # Keys only in the language file are obsolete
        for key in set(lang_translations.keys()) - set(english_translations.keys()):
            removed_keys.append(key)
            self.log_file(filename, f"Removed obsolete key {key}")

        total_changes = (
            len(added_keys)
            + len(updated_ref_keys)
            + len(migrated_format_keys)
            + len(removed_keys)
        )

        if total_changes > 0:
            self.save_language_file(file_path, updated)
            self.log_master(f"Changes made to {filename}:")
            if added_keys:
                self.log_master(f"  Added keys: {len(added_keys)}")
                for key in sorted(added_keys):
                    self.log_master(f"    + {key}")
            if updated_ref_keys:
                self.log_master(f"  Updated English references: {len(updated_ref_keys)}")
                for key in sorted(updated_ref_keys):
                    self.log_master(f"    ~ {key}")
            if migrated_format_keys:
                self.log_master(f"  Migrated plain-string → dict format: {len(migrated_format_keys)}")
                for key in sorted(migrated_format_keys):
                    self.log_master(f"    * {key}")
            if removed_keys:
                self.log_master(f"  Removed obsolete keys: {len(removed_keys)}")
                for key in sorted(removed_keys):
                    self.log_master(f"    - {key}")
        else:
            self.log_master(f"  No changes needed for {filename}")

    def sync_all_language_files(self):
        """Synchronize all non-English language files against the English master."""
        
        self.log_master("=== Synchronizing language files ===")

        english_translations = self.load_english_translations()
        language_files = self.get_language_files()

        sync_all = not self.languages_to_sync
        if not language_files:
            self.log_master("No language files found to synchronize")
            return

        for file_path in language_files:
            lang_code = extract_language_code_from_filename(file_path.name)
            if sync_all or (lang_code in self.languages_to_sync):
                self.log_master(f"=== Language file: {lang_code.upper()} ===")
                self.sync_language_file(file_path, english_translations)

    # ------------------------------------------------------------------
    # Log output
    # ------------------------------------------------------------------

    def _finalize_logs(self) -> None:
        """Append a completion footer to all log files that were written."""
        if self.dry_run:
            footer = "=== Dry run completed — no changes were made ==="
        else:
            footer = "=== Synchronization completed successfully ==="

        self._append_to_log(self._master_log_path(), f"\n[{datetime.now().strftime('%H:%M:%S')}] {footer}\n")
        for filename in self._initialized_file_logs:
            self._append_to_log(
                self._file_log_path(filename),
                f"\n[{datetime.now().strftime('%H:%M:%S')}] {footer}\n",
            )

        self.log_master(f"Logs written to {self.log_dir}")

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------

    def run(self):
        """Run the full synchronization process."""
        # Initialise log files first — headers (incl. dry-run notice) go to disk
        # before any work starts, so even a hard crash leaves a readable log.
        self._init_logs()

        self.log_master("Starting i18n synchronization...")
        self.log_master(f"  Languages directory : {self.languages_dir}")
        self.log_master(f"  Source directory    : {self.source_dir}")
        self.log_master(f"  Log directory       : {self.log_dir}")
        self.log_master(f"  Languages to sync   : {', '.join(self.languages_to_sync) if self.languages_to_sync else 'All'}")
        self.log_master(f"  Dry run             : {self.dry_run}")
        self.log_master("")


        sync_all = not self.languages_to_sync
        try:
            if sync_all or ("en" in self.languages_to_sync):
                self.sync_english_master()
            if sync_all or any(lang != "en" for lang in self.languages_to_sync):
                self.sync_all_language_files()
            self.log_master("")
            self.log_master("i18n synchronization completed successfully!")
            self._finalize_logs()
        except Exception as e:
            self.log_master(f"Error during synchronization: {e}")
            self._append_to_log(
                self._master_log_path(),
                f"\n[{datetime.now().strftime('%H:%M:%S')}] === ABORTED with error: {e} ===\n",
            )
            raise


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Synchronize i18n JSON language files with source code. "
            "Build-time tool — run from the repo root or via Makefile."
        )
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making actual changes",
    )
    parser.add_argument(
        "--only-lang",
        default=None,
        type=str,
        help=(
            "Which language file to synchronize (e.g., 'de' for specter_ui_de.json); comma separated — if not set, all language files are synchronized"
        ),
    )
    parser.add_argument(
        "--source-dir",
        type=str,
        help=(
            "Directory to search for Python source files "
            "(default: scenarios/MockUI relative to repo root)"
        ),
    )
    parser.add_argument(
        "--languages-dir",
        type=str,
        help=(
            "Directory containing JSON language files "
            "(default: scenarios/MockUI/src/MockUI/i18n/languages relative to repo root)"
        ),
    )
    parser.add_argument(
        "--log-dir",
        type=str,
        help="Directory to write log files (default: build/ relative to repo root)",
    )

    args = parser.parse_args()

    default_languages_dir = _REPO_ROOT / "scenarios" / "MockUI" / "src" / "MockUI" / "i18n" / "languages"
    default_source_dir = _REPO_ROOT / "scenarios" / "MockUI"
    default_log_dir = _REPO_ROOT / "build"

    languages_dir = args.languages_dir or str(default_languages_dir)
    source_dir = args.source_dir or str(default_source_dir)
    log_dir = args.log_dir or str(default_log_dir)

    languages_to_sync = args.only_lang.split(",") if args.only_lang else None


    # Validate inputs
    if not Path(languages_dir).exists():
        print(f"Error: languages directory does not exist: {languages_dir}")
        sys.exit(1)

    if not Path(source_dir).exists():
        print(f"Error: source directory does not exist: {source_dir}")
        sys.exit(1)

    english_file = Path(languages_dir) / "specter_ui_en.json"
    if not english_file.exists():
        print(f"Error: English master file does not exist: {english_file}")
        sys.exit(1)

    # Ensure log directory exists
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Ensure languages are given as language codes
    if languages_to_sync:
        for lang in languages_to_sync:
            if not re.match(r"^[a-zA-Z]{2}$", lang):
                print(f"Error: Invalid language code '{lang}' in --only-lang. Expected format: 'en', 'de', etc. (or uppercase 'EN', 'DE', etc.)")
                sys.exit(1)

    synchronizer = I18nSynchronizer(languages_dir, source_dir, log_dir, languages_to_sync, args.dry_run)
    synchronizer.run()


if __name__ == "__main__":
    main()
