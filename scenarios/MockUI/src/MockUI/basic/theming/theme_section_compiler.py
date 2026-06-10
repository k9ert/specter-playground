#!/usr/bin/env python3
"""
Theme Section Compiler for Specter UI Theming System:
    BaseClass for the individual compilers for the different theme sections
    (color palette, font palette, etc).

    IntermediateClass -> do not instantiate directly, but subclass for each
    theme section type
"""

if '.' in __name__:
    from ..templates.settings_file_compiler import SettingsFileCompiler, read_cstring
else:
    # Running as a script or loaded without package context
    # Add basic/ to sys.path so templates.settings_file_compiler is importable directly.
    import sys as _sys, pathlib as _pathlib
    _sys.path.insert(0, str(_pathlib.Path(__file__).parent.parent))
    from templates.settings_file_compiler import SettingsFileCompiler, read_cstring

class ThemeSectionCompiler(SettingsFileCompiler):
    """Compiler for Specter UI theme sections (color palette, font palette, etc)."""

    JSON_FILE_PREFIX = "specter_ui_theme_"
    SETTINGS_NAME_DESC = "theme name (alphanumeric + underscore, non-empty string)"

    _ALNUM = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'

    def validate_settings_name(self, name):
        """Theme section name must be a non-empty alphanumeric (+ underscore) string."""
        return isinstance(name, str) and len(name) > 0 and all(c in self._ALNUM for c in name)

    def _get_name_for_binary_header(self, settings_name, metadata):
        """Store the human-readable name in the binary header."""
        return metadata.get('name')

    def validate_metadata_and_extract_settings_name(self, metadata):
        """
        Validate _metadata dict and return the theme name.
        Checks that 'name' is present and matches the stripped filename.
        Returns the theme name string, or None on error.
        """
        name = metadata.get('name')
        if not name:
            print("Error: Missing 'name' in _metadata section")
            print("Please add: \"name\": \"YourThemeName\" to the _metadata section")
            return None
        name = name.lower()
        if not self.validate_settings_name(name):
            print(f"Error: Invalid name '{name}' in _metadata (must be a {self.SETTINGS_NAME_DESC})")
            return None
        return name

    def handle_extra_keys_from_json(self, binary_file_path, extra_keys):
        """Warn about extra section entries not present in the key mapping."""
        print(f"Warning: Found {len(extra_keys)} extra entry/entries not in key mapping:")
        for key in sorted(extra_keys):
            print(f"  - '{key}' (will be ignored)")