#!/usr/bin/env python3
"""
Font Palette Compiler for Specter UI Theming System

Converts JSON font palette sections in theme json files to efficient binary format for flash storage.
Generates font key mappings for runtime lookups.
"""

if '.' in __name__:
    from .theme_section_compiler import ThemeSectionCompiler
    from .theme_schema import SpecterFontPalette
    from ..utils.generic_utils import resolve_obj
else:
    import sys as _sys, pathlib as _pathlib
    _sys.path.insert(0, str(_pathlib.Path(__file__).parent.parent))  # basic/
    _sys.path.insert(0, str(_pathlib.Path(__file__).parent))          # theming/
    _sys.path.insert(0, str(_pathlib.Path(__file__).parent.parent / "utils"))  # utils/
    from theme_section_compiler import ThemeSectionCompiler
    from theme_schema import SpecterFontPalette
    from generic_utils import resolve_obj

try:
    import lvgl as lv
    if '.' in __name__:
        from ..fonts.font_manager import font_manager
    else:
        import sys as _sys, pathlib as _pathlib
        _sys.path.insert(0, str(_pathlib.Path(__file__).parent.parent))
        from fonts.font_manager import font_manager
except ImportError:
    lv = None
    font_manager = None


def font_ref_to_palette_idx(name):
    """Map a font palette name like 'TEXT' to SpecterFontPalette int.
    Returns None if unknown."""
    result = resolve_obj(name, SpecterFontPalette)
    if isinstance(result, int):
        return result
    return None

class FontPaletteCompiler(ThemeSectionCompiler):
    """Compiler for Specter UI font palette (theming) files."""

    # --- Section-specific attributes ---
    BINARY_FILE_PREFIX = "fonts_"
    MAGIC_BYTES = b"FONT"

    SETTINGS_KEY = "fonts"

    def convert_setting_to_binary(self, entry):
        """
        Encode a font entry and return it as a bytearray.

        Expects JSON format:
          {
            "text": "fontname:fontsize",
          }
        """
        if isinstance(entry, str):
            parts = entry.split(":")
            if len(parts) == 2:
                font_name = parts[0].strip()
                font_size = parts[1].strip()
                value = f"{font_name}:{font_size}"
        else:
            value = ''

        return (value.encode('utf-8') + b'\x00')


    def reconstruct_setting_from_binary(self, f):
        """Read a null-terminated UTF-8 string from file handle.

        Returns the raw "fontname:fontsize" string for structural validation,
        or None if the entry is missing or malformed.
        """
        result = bytearray()
        while True:
            byte = f.read(1)
            if not byte or byte == b'\x00':
                break
            result.extend(byte)

        font_str = result.decode('utf-8')
        if ":" in font_str:
            font_name, font_size_str = font_str.split(":", 1)
            if font_name.strip() and font_size_str.strip().isdigit():
                return font_str
        return None  # invalid entry format

    def read_setting_from_binary(self, file_path, key_index):
        """Read one font entry and return (lv.font, None) or (None, error_str)."""
        raw_str, err = super().read_setting_from_binary(file_path, key_index)
        if err:
            return (None, err)
        if raw_str is None:
            return (None, "missing")
        if font_manager is None:
            return (None, "font_manager not available")
        font = font_manager.get_font(raw_str.strip())
        return (font, None) if font is not None else (None, "could not resolve " + raw_str)

    # --- END: Section-specific overrides ---

def main():
    """Command line interface for the palette compiler."""
    FontPaletteCompiler().main()


if __name__ == "__main__":
    main()