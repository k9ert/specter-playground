#!/usr/bin/env python3
"""
Language Compiler for Specter UI i18n System

Converts JSON language files to efficient binary format for flash storage.
Generates translation key mappings for runtime lookups.
"""

if '.' in __name__:
    from ..templates.settings_file_compiler import SettingsFileCompiler, read_cstring
else:
    # Running as a script or loaded without package context
    # Add basic/templates to sys.path and import the module directly.
    # This avoids importing templates/__init__.py, which pulls GUI modules
    # (including lvgl) that are unavailable in host-side build tools.
    import sys as _sys, pathlib as _pathlib
    _sys.path.insert(0, str(_pathlib.Path(__file__).parent.parent / "templates"))
    from settings_file_compiler import SettingsFileCompiler, read_cstring


class LangCompiler(SettingsFileCompiler):
    """Compiler for Specter UI language (i18n) files."""

    BINARY_FILE_PREFIX = "lang_"
    BINARY_FILE_SUFFIX = ".bin"
    JSON_FILE_PREFIX = "specter_ui_"
    JSON_FILE_SUFFIX = ".json"
    MAGIC_BYTES = b"LANG"
    SETTINGS_NAME_DESC = "2-letter language code (e.g. 'en', 'de')"
    SETTINGS_KEY = "translations"

    # Used by sync_i18n.py when adding a new key not yet translated.
    # i18n_manager.t() recognises this value and falls back to the default language.
    FILL_PLACEHOLDER = "<FILL>"

    def validate_settings_name(self, name):
        """Language code must be exactly 2 alphabetic characters."""
        return isinstance(name, str) and len(name) == 2 and name.isalpha()

    def reconstruct_setting_from_binary(self, f):
        """Read a null-terminated UTF-8 string from file handle."""
        return read_cstring(f)

    def convert_setting_to_binary(self, value):
        """
        Encode a translation value and return it as a bytearray.

        Supports two JSON formats:
          - Simple string  (default language):   "Hello"
          - Object with text field (other langs): {"text": "Hallo", "ref_en": "Hello"}
        """
        if isinstance(value, str):
            text = value
        elif isinstance(value, dict):
            text = value.get('text', '')
        else:
            text = ''
        return text.encode('utf-8') + b'\x00'  # Null-terminated string

    def validate_metadata_and_extract_settings_name(self, metadata):
        """
        Validate _metadata dict and return the language code.
        Checks that 'language_code' is present and matches the filename code.
        Returns the language code string, or None on error.
        """
        lang_code = metadata.get('language_code')
        if not lang_code:
            print("Error: Missing 'language_code' in _metadata section")
            print("Please add: \"language_code\": \"XX\" to the _metadata section")
            return None
        lang_code = lang_code.lower()
        if not self.validate_settings_name(lang_code):
            print(f"Error: Invalid language_code '{lang_code}' in _metadata (must be 2 letters)")
            return None
        return lang_code

    def _get_name_for_binary_header(self, settings_name, metadata):
        """Store the human-readable language name (e.g. 'English') in the header."""
        return metadata.get('language_name', settings_name)

    def handle_extra_keys_from_json(self, binary_file_path, extra_keys):
        """Warn about extra translation keys not present in the key mapping."""
        print(f"Warning: Found {len(extra_keys)} extra translation(s) not in key mapping:")
        for key in sorted(extra_keys):
            print(f"  - '{key}' (will be ignored)")
        print("These keys may need to be added to the default language file.")


def main():
    """Command line interface for the language compiler."""
    LangCompiler().main()


if __name__ == "__main__":
    main()
