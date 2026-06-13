#!/usr/bin/env python3
"""
Color Palette Compiler for Specter UI Theming System

Converts JSON color palette sections in theme json files to efficient binary format for flash storage.
Generates color key mappings for runtime lookups.
"""

if '.' in __name__:
    from .theme_section_compiler import ThemeSectionCompiler, read_cstring
    from .theme_schema import SpecterColorPalette
else:
    import sys as _sys, pathlib as _pathlib
    _sys.path.insert(0, str(_pathlib.Path(__file__).parent.parent))  # basic/
    _sys.path.insert(0, str(_pathlib.Path(__file__).parent))         # theming/
    from theme_section_compiler import ThemeSectionCompiler, read_cstring
    from theme_schema import SpecterColorPalette

try:
    import lvgl as lv
except ImportError:
    lv = None

# ─────────────────────────────────────────────────────────────────────────────
# Colour helpers
# ─────────────────────────────────────────────────────────────────────────────

def is_hex_RGB_color(value):
    """Validate that a string is in the format "#RRGGBB" where RR, GG, BB are hexadecimal digits."""
    return ( isinstance(value, str) and 
             len(value) == 7 and 
             value.startswith('#') and 
             all(c in '0123456789abcdefABCDEF' for c in value[1:])
            )

def to_lv_color(spec):
    """Normalise a colour *spec* into an ``lv.color_t``.

    Accepts an already-built ``lv.color_t`` (returned as-is), an int hex value
    (``0xRRGGBB``), or a ``"0xRRGGBB"`` / ``"#RRGGBB"`` string.
    """
    if isinstance(spec, str):
        if spec.startswith("#"):
            return lv.color_hex(int(spec[1:], 16))
        if spec.lower().startswith("0x"):
            return lv.color_hex(int(spec[2:], 16))
        return lv.color_hex(int(spec, 16))
    if isinstance(spec, int):
        return lv.color_hex(spec)
    return spec  # assume it is already an lv.color_t

def to_hex_color_str(color):
    """Return *color* as a ``"#RRGGBB"`` hex string.

    Accepts either an ``lv.color_t`` object or a hex string
    (``"0xRRGGBB"`` or ``"#RRGGBB"``)
    """
    if isinstance(color, str):
        val = int(color[1:], 16) if color.startswith("#") else int(color, 16)
        return "#{:06X}".format(val)
    c32 = lv.color_to32(color)
    return "#{:02X}{:02X}{:02X}".format(c32.ch.red, c32.ch.green, c32.ch.blue)

def shade(lv_color, level):
    """Return *lv_color* lightened (level > 0) or darkened (level < 0).

    level: integer from -8 to +8 (inclusive) - each step is ~12% toward black or white.

    Material/Vuetify-style: each step mixes ~12% toward white (lighten) or black
    (darken).  ``level == 0`` returns the colour unchanged.
    """
    if not level:
        return lv_color
    ratio = min(255, abs(level) * 30)   # ~12% per step (30/255)
    if level > 0:
        return lv_color.lighten(ratio)
    else:
        return lv_color.darken(ratio)

class ColorMode:
    """Enum for color mode (light/dark) in dual-variant palette entries."""
    LIGHT = "light"
    DARK = "dark"


def color_ref_to_palette_idx(name):
    """Map a colour palette name like 'primary' to SpecterColorPalette int.
    Returns None if unknown."""
    val = getattr(SpecterColorPalette, name.upper(), None)
    if isinstance(val, int):
        return val
    return None

class ColorPaletteCompiler(ThemeSectionCompiler):
    """Compiler for Specter UI color palette (theming) files."""

    # --- Section-specific attributes ---
    BINARY_FILE_PREFIX = "colors_"
    MAGIC_BYTES = b"COLR"
    SETTINGS_KEY = "colors"

    def convert_setting_to_binary(self, entry):
        """
        Encode a color entry and return it as a bytearray.

        Expects JSON format:
          {
            "text": "#RRGGBB",
            or
            "text" : { "dark": "#RRGGBB", "light": "#RRGGBB" }
          }
        """
        if isinstance(entry, dict):
            value_dark = entry.get('dark', None)
            value_light = entry.get('light', None)
            if not value_dark and not value_light:
                value = ''
            else:
                if not value_dark:
                    value_dark = value_light
                elif not value_light:
                    value_light = value_dark
                value = "d" + to_hex_color_str(value_dark) + "l" + to_hex_color_str(value_light)
        elif isinstance(entry, str):
            value = to_hex_color_str(entry)
        else:
            value = ''

        return (value.encode('utf-8') + b'\x00')


    def _resolve_color_string(self, raw_str, mode):
        """Helper to resolve a raw color string (single or dual-variant) to an lv.color_t for the given mode."""
        if raw_str.startswith("d") and "l" in raw_str:
            dark_part  = raw_str.split("d")[1].split("l")[0]
            light_part = raw_str.split("l")[1]
            color_str = dark_part if mode == ColorMode.DARK else light_part
        else:
            color_str = raw_str
        if not is_hex_RGB_color(color_str):
            return None
        return to_lv_color(color_str)

    def reconstruct_setting_from_binary(self, f, mode=None):
        """Read a null-terminated UTF-8 string from file handle.

        Without *mode*: returns the raw encoded color string as stored in binary:
          "#RRGGBB"               — single (mode-independent) color
          "d#RRGGBBl#RRGGBB"     — dual-variant (dark / light)
          None                    — invalid / empty entry

        With *mode* (ColorMode.DARK or ColorMode.LIGHT): applies mode selection
        and returns the resolved lv.color_t directly, or None on error.
        """
        color_str = read_cstring(f)
        if not color_str:
            return None
        # Validate format
        if color_str.startswith("d") and "l" in color_str:
            raw_str = color_str
        elif is_hex_RGB_color(color_str):
            raw_str = color_str
        else:
            return None  # invalid format

        if mode is None:
            return raw_str  # caller will apply mode later
        else:
            return self._resolve_color_string(raw_str, mode)

    def read_setting_from_binary(self, file_path, key_index, mode=ColorMode.DARK):
        """Read one color entry and return (lv.color_t, None) or (None, error_str).

        Overrides the base class method to add the optional *mode* argument.
        Calls super() to navigate the file and get the raw encoded string, then
        applies mode resolution to produce an lv.color_t.
        """
        raw_str, err = super().read_setting_from_binary(file_path, key_index)
        if err:
            return (None, err)
        if raw_str is None:
            return (None, "missing")
        # Resolve the raw color string to an lv.color_t for the given mode
        lv_color = self._resolve_color_string(raw_str, mode)
        if lv_color is None:
            return (None, "decode_error")
        return (lv_color, None)


    # --- END: Section-specific overrides ---

def main():
    """Command line interface for the palette compiler."""
    ColorPaletteCompiler().main()

if __name__ == "__main__":
    main()