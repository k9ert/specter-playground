"""
Theme Manager for Specter UI.

Handles loading, validating, and providing themes from efficient binary format.
Supports fallback to default theme for missing entries.
Enables runtime loading of new themes via JSON to binary conversion.


Scans the flash themes directory for theme data (binary), validates and registers
each theme with the theming framework, and persists the user's selected theme +
colour mode across reboots.

Naming convention
-----------------
Theme identity is the **display name** — the ``"name"`` field inside the JSON
file. 
The name must be one alphanumeric word (e.g. ``specter``).
The JSON file must be named ``specter_ui_theme_<filename>.json``
(e.g. ``specter_ui_theme_specter.json``).  

Files that violate this rule are skipped during scanning.
"""

import os

from .theme_compiler import ThemeCompiler, SPECTER_STYLES, ColorMode
from ..templates.settings_file_manager import SettingFileManager


class ThemeManager(SettingFileManager):
    COMPILER = ThemeCompiler()
    KEYS_CLASS = SPECTER_STYLES
    SETTINGS_DIR = "/themes"
    DEFAULT_SETTING_FILE = "specter"

    mode = ColorMode.DARK  # Default to dark mode; can be changed by user

    def __init__(self):
        self.current_colors_file = None
        self.default_colors_file = None
        self.current_fonts_file = None
        self.default_fonts_file = None
        super().__init__()

    @property
    def current_styles_file(self):
        return self.current_file

    def _scan_available_files(self):
        # super will check for fitting styles binaries and extract their names from them.
        # afterwards we still need to check if also the fitting colors and fonts binaries 
        # are present for each theme, otherwise we have to remove it again.
        super()._scan_available_files()
        try: 
            binary_files = os.listdir(self.FLASH_DIR)
            to_remove = []
            for theme_name in self.available_files:
                all_found = True
                colors_file, fonts_file, styles_file = self.COMPILER.get_binary_filenames(theme_name, self.FLASH_DIR)
                
                colors_file_name = self.COMPILER._path_basename(colors_file)
                fonts_file_name = self.COMPILER._path_basename(fonts_file)

                if (not colors_file_name in binary_files or 
                    theme_name != self.COMPILER._color_compiler.extract_settings_name_from_binary_file(colors_file)):
                    print(f"Warning: Colors file '{colors_file}' not found for theme '{theme_name}' (skipping theme)")
                    all_found = False

                if (not fonts_file_name in binary_files or 
                    theme_name != self.COMPILER._font_compiler.extract_settings_name_from_binary_file(fonts_file)):
                    print(f"Warning: Fonts file '{fonts_file}' not found for theme '{theme_name}' (skipping theme)")
                    all_found = False

                if not all_found:
                    to_remove.append(theme_name)

            for name in to_remove:
                self.available_files.remove(name)

        except Exception as e:
            print(f"Error scanning theme files: {e}")
            self.available_files = []

        #have to verify the default theme survived as well
        if self.DEFAULT_SETTING_FILE not in self.available_files:
            print(f"CRITICAL ERROR: Default theme '{self.DEFAULT_SETTING_FILE}' not found in {self.FLASH_DIR}!")
            print("This indicates a build system problem - the default theme should be embedded in firmware.")

    def set_theme(self, theme_name, mode=None):
        if self.set_setting(theme_name):
            if mode is not None:
                self.set_mode(mode)
            return True
        return False

    def set_setting(self, theme_name):
        """Set the current theme and color mode."""
        if theme_name not in self.available_files:
            print(f"Error: Theme '{theme_name}' not found in available themes: {self.available_files}")
            return False

        (new_colors_file, new_fonts_file, new_style_file) = self.COMPILER.get_binary_filenames(theme_name, self.FLASH_DIR)
        (default_colors_file, default_fonts_file, default_style_file) = self.COMPILER.get_binary_filenames(self.DEFAULT_SETTING_FILE, self.FLASH_DIR)
        
        #check if the files exist before setting. Style file is checked by set_setting
        for file2test in [new_colors_file, new_fonts_file, default_colors_file, default_fonts_file]:
             try:
                os.stat(file2test)
             except OSError as e:
                print(f"Error: Required binary file '{file2test}' not found for theme '{theme_name}'")
                return False

        if super().set_setting(theme_name):
            self.current_colors_file = new_colors_file
            self.default_colors_file = default_colors_file
            self.current_fonts_file = new_fonts_file
            self.default_fonts_file = default_fonts_file
            return True
        return False
    
    def set_mode(self, mode):
        """Set the current color mode (light/dark)."""
        if mode in (ColorMode.LIGHT, ColorMode.DARK):
            self.mode = mode
            self._save_settings_preference()
            return True
        print(f"Error: Invalid color mode '{mode}' (must be a ColorMode enum value)")
        return False

    def _build_preference_data(self):
        data = super()._build_preference_data()
        data['mode'] = self.mode
        return data

    def _apply_loaded_preference(self, config):
        mode = config.get('mode', ColorMode.DARK)
        if mode in (ColorMode.DARK, ColorMode.LIGHT):
            self.mode = mode

    def get_setting(self, style_key):
        # Try to read from current settings file
        value, error = self.COMPILER.read_setting_from_binary(self.current_colors_file,
                                                              self.current_fonts_file,
                                                              self.current_file,
                                                              style_key,
                                                              self.mode)
        
        # If not found in current settings, try default settings
        if value is None:
            value, error = self.COMPILER.read_setting_from_binary(self.default_colors_file,
                                                                  self.default_fonts_file,
                                                                  self.default_file,
                                                                  style_key,
                                                                  self.mode)
        
        return value

# --- Module-level convenience API (unchanged from before) ---

def get_theme_manager():
    """Get the global ThemeManager singleton."""
    return ThemeManager.get_instance()
