"""
MockUI theming package — public API for widget factories.
"""

from .theme_schema import SpecterColorPalette, SpecterFontPalette, SpecterStylePalette
from .color_palette_compiler import to_lv_color, to_hex_color_str, ColorMode
from .theme_manager import apply_style, remove_style, reset_style, get_theme_manager, ThemeManager, get_style, get_color, get_font
from ..templates.settings_file_compiler import collect_int_constants as get_palette_entries

__all__ = [
    'SpecterColorPalette', 'SpecterFontPalette', 'SpecterStylePalette', 'ColorMode',
    'get_palette_entries',
    'apply_style', 'remove_style', 'reset_style', 'get_theme_manager', 'ThemeManager',
    'get_style', 'get_color', 'get_font',
    'to_lv_color', 'to_hex_color_str',
]
