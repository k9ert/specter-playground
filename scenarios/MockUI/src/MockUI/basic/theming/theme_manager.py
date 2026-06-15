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

from .theme_compiler import ThemeCompiler, SpecterStylePalette, ColorMode
from ..templates.settings_file_compiler import collect_int_constants
from ..templates.settings_file_manager import SettingFileManager


class ThemeManager(SettingFileManager):
    COMPILER = ThemeCompiler()
    KEYS_CLASS = SpecterStylePalette
    SETTINGS_DIR = "/themes"
    DEFAULT_SETTING_FILE = "specter"

    mode = ColorMode.DARK  # Default to dark mode; can be changed by user

    def __init__(self):
        self.current_colors_file = None
        self.default_colors_file = None
        self.current_fonts_file = None
        self.default_fonts_file = None
        super().__init__()
        if self.current_file is not None:
            self._preload_styles()

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

                if colors_file_name not in binary_files:
                    print(f"Warning: Colors file '{colors_file}' not found for theme '{theme_name}' (skipping theme)")
                    all_found = False

                if fonts_file_name not in binary_files:
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

    # ── External GUI interface ────────────────────────────────────────────────

    def set_theme(self, theme_name, mode=None):
        """Set active theme (and optionally mode) by name. Returns True on success."""
        if self.set_setting(theme_name):
            success = True
            if mode is not None:
                success = self.set_mode(mode, load_on_change=False)
            self._preload_styles()
            return success
        return False

    def set_mode(self, mode, load_on_change=True):
        """Set the current color mode (dark/light) and persist it."""
        if mode in (ColorMode.LIGHT, ColorMode.DARK):
            if mode != self.mode:
                self.mode = mode
                self._save_settings_preference()
                if load_on_change:
                    self._preload_styles()
            return True
        print(f"Error: Invalid color mode '{mode}' (must be a ColorMode constant)")
        return False

    def get_style(self, style_key):
        """Return ``lv.style_t`` for *style_key*, using the cache when available."""
        cache = getattr(self, '_style_cache', None)
        if cache is not None and style_key in cache:
            return cache[style_key]
        return self.get_setting(style_key)
    
    def __getitem__(self, key):
        """Allow theme_manager['KEY']"""
        return self.get_style(key)

    def __call__(self, key):
        """Allow theme_manager('KEY')"""
        return self.get_style(key)    

    def apply_style(self, obj, keys, selector=0):
        """Apply one or more SPECTER_STYLES keys to an LVGL widget.

        Args:
            obj:      LVGL widget (any object with ``add_style``).
            keys:     A single int (``SPECTER_STYLES.*``) or
                      string (``"BG.INVISIBLE"``) or
                      a list of ints or strings.
                    
            selector: LVGL part/state selector (default 0 = MAIN/DEFAULT).
        """
        if isinstance(keys, int):
            keys = [keys]
        if isinstance(keys, str):
            # resolve e.g. "BG.INVISIBLE" to the corresponding integer key
            keys = [self.COMPILER.str_to_style_ind(keys)]
        for key in keys:
            if isinstance(key, str):
                key = self.COMPILER.str_to_style_ind(key)
            style = self.get_style(key)
            if style is not None:
                obj.add_style(style, selector)

    def remove_style(self, obj, keys, selector=0):
        """Remove one or more SPECTER_STYLES keys from an LVGL widget."""
        if isinstance(keys, int):
            keys = [keys]
        if isinstance(keys, str):
            # resolve e.g. "BG.INVISIBLE" to the corresponding integer key
            keys = [self.COMPILER.str_to_style_ind(keys)]
        for key in keys:
            if isinstance(key, str):
                key = self.COMPILER.str_to_style_ind(key)
            style = self.get_style(key)
            if style is not None:
                obj.remove_style(style, selector)

    def reset_style(self, obj, selector=0):
        """Remove all styles from an LVGL widget for the given selector."""
        obj.set_style_list(selector, None)

    def get_color(self, palette_idx):
        """Return an ``lv.color`` from the current theme's color palette."""
        return self.COMPILER.read_color_from_binary(self.current_colors_file, palette_idx, mode=self.mode)
    
    def get_font(self, palette_idx):
        """Return an ``lv.font`` from the current theme's font palette."""
        return self.COMPILER.read_font_from_binary(self.current_fonts_file, palette_idx)

    # ── SettingFileManager overrides ──────────────────────────────────────────

    def set_setting(self, theme_name):
        """Resolve and assign all three binary paths for *theme_name*."""
        if theme_name not in self.available_files:
            print(f"Error: Theme '{theme_name}' not found in available themes: {self.available_files}")
            return False

        (new_colors_file, new_fonts_file, new_style_file) = self.COMPILER.get_binary_filenames(theme_name, self.FLASH_DIR)
        (default_colors_file, default_fonts_file, default_style_file) = self.COMPILER.get_binary_filenames(self.DEFAULT_SETTING_FILE, self.FLASH_DIR)

        for file2test in [new_colors_file, new_fonts_file, default_colors_file, default_fonts_file]:
            try:
                os.stat(file2test)
            except OSError:
                print(f"Error: Required binary file '{file2test}' not found for theme '{theme_name}'")
                return False

        if super().set_setting(theme_name):
            self.current_colors_file = new_colors_file
            self.default_colors_file = default_colors_file
            self.current_fonts_file = new_fonts_file
            self.default_fonts_file = default_fonts_file
            return True
        return False

    def get_setting(self, style_key):
        """Read one ``lv.style_t`` live from binary — try current, fall back to default."""
        value, _err = self.COMPILER.read_setting_from_binary(
            self.current_colors_file, self.current_fonts_file,
            self.current_file, style_key, self.mode)
        if value is None:
            value, _err = self.COMPILER.read_setting_from_binary(
                self.default_colors_file, self.default_fonts_file,
                self.default_file, style_key, self.mode)
        return value

    # ── Persistence hooks (SettingFileManager) ────────────────────────────────

    def _build_preference_data(self):
        data = super()._build_preference_data()
        data['mode'] = self.mode
        return data

    def _apply_loaded_preference(self, config):
        mode = config.get('mode', ColorMode.DARK)
        if mode in (ColorMode.DARK, ColorMode.LIGHT):
            self.mode = mode

    # ── Style cache (internal) ────────────────────────────────────────────────

    def _preload_styles(self):
        """Load every SPECTER_STYLES entry into an in-memory cache.

        Reads all styles from binary once and stores the resulting ``lv.style_t``
        objects by integer key.  Called by ``SpecterGui`` after ``set_theme()``
        / ``set_mode()`` and before the first screen render.
        """
        if (self.current_colors_file is None or 
            self.current_file is None or
            self.current_fonts_file is None):
            return
        all_indices = collect_int_constants(SpecterStylePalette, recursive=True)
        self._style_cache = {}
        for name, idx in all_indices.items():
            style = self.get_setting(idx)
            if style is not None:
                self._style_cache[idx] = style


# ── Module-level shortcuts ────────────────────────────────────────────────────

def get_theme_manager():
    """Return the global ThemeManager singleton."""
    return ThemeManager.get_instance()

def apply_style(obj, keys, selector=0):
    return get_theme_manager().apply_style(obj, keys, selector)

def remove_style(obj, keys, selector=0):
    return get_theme_manager().remove_style(obj, keys, selector)

def reset_style(obj, selector=0):
    return get_theme_manager().reset_style(obj, selector)

def get_style(style_key):
    return get_theme_manager().get_style(style_key)

def get_color(palette_idx):
    return get_theme_manager().get_color(palette_idx)

def get_font(palette_idx):
    return get_theme_manager().get_font(palette_idx)
