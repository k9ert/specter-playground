#!/usr/bin/env python3
"""
Theme Compiler for Specter UI Theming System

Orchestrates compilation of a full theme JSON file into three binary files
(colors, fonts, styles) and reconstructs all palette objects at runtime into 
lvgl style objects.

──────────────────────────────────────────────────────────────────────────────
Compile-time  (PC or device with SD card)
──────────────────────────────────────────────────────────────────────────────

    ThemeCompiler.json_to_binary(json_path, keys_class, output_dir)
    (keys_class can be set as None)

Given a theme JSON whose _metadata.name is e.g. <name>, the following
three binary files are written to *output_dir*:

    colors_<name>.bin   — color palette  (ColorPaletteCompiler.BINARY_FILE_PREFIX)
    fonts_<name>.bin    — font palette   (FontPaletteCompiler.BINARY_FILE_PREFIX)
    styles_<name>.bin   — style palette  (StylePaletteCompiler.BINARY_FILE_PREFIX)

The theme name is always lower-cased from _metadata.name.

Returns (colors_path, fonts_path, styles_path) on success, None on fatal error.

──────────────────────────────────────────────────────────────────────────────
Runtime
──────────────────────────────────────────────────────────────────────────────

    tc = ThemeCompiler()
    style = tc.read_setting_from_binary(
                    colors_path,
                    fonts_path,
                    styles_path,
                    SPECTER_STYLES.WIDGET.BUTTON,
                    mode=ColorMode.DARK) → lv.style_t

──────────────────────────────────────────────────────────────────────────────
Relationship to SettingsFileCompiler
──────────────────────────────────────────────────────────────────────────────

ThemeCompiler does NOT fully subclass SettingsFileCompiler.  The
SettingsFileCompiler contract is 1 JSON → 1 binary with per-entry integer
addressing; a theme maps 1 JSON → 3 binaries and reconstruction requires all
three simultaneously, with no meaningful single-entry key index.

A future SettingsFileManager that needs per-section access should work with
the three section compilers directly (ColorPaletteCompiler,
FontPaletteCompiler, StylePaletteCompiler) — each of those IS a full
SettingsFileCompiler subclass. 
However, 
    ThemeCompiler.json_to_binary() and
    ThemeCompiler.read_setting_from_binary() 
follow the same naming convention (return values might slightly differ from the
single-path return of the section compilers due to the need to handle multiple 
binaries simultaneously).
"""

import json
try:
    import lvgl as lv
except ImportError:
    lv = None


if '.' in __name__:
    from .theme_section_compiler import ThemeSectionCompiler
    from .theme_schema import SpecterColorPalette, SpecterFontPalette, SpecterStylePalette
    from ..templates.settings_file_compiler import collect_int_constants
    from .color_palette_compiler import (
        ColorPaletteCompiler, ColorMode, color_ref_to_palette_idx
    )
    from .font_palette_compiler import (
        FontPaletteCompiler, font_ref_to_palette_idx
    )
    from .style_palette_compiler import (
        StylePaletteCompiler, style_ref_to_palette_idx
    )
else:
    import sys as _sys, pathlib as _pathlib
    _sys.path.insert(0, str(_pathlib.Path(__file__).parent.parent / "templates"))
    _sys.path.insert(0, str(_pathlib.Path(__file__).parent.parent))
    _sys.path.insert(0, str(_pathlib.Path(__file__).parent))
    from theme_section_compiler import ThemeSectionCompiler
    from theme_schema import SpecterColorPalette, SpecterFontPalette, SpecterStylePalette
    from settings_file_compiler import collect_int_constants
    from color_palette_compiler import (
        ColorPaletteCompiler, ColorMode
    )
    from font_palette_compiler import (
        FontPaletteCompiler
    )
    from style_palette_compiler import (
        StylePaletteCompiler
    )


class ThemeCompiler(ThemeSectionCompiler):
    """
    Orchestrates theme compilation (JSON → binary) and reconstruction
    (binary → lv objects) for a complete Specter UI theme.

    Also acts as the *context* object consumed by StylePaletteCompiler.
    """

    #Helper class to hold context for StylePaletteCompiler during reconstruction.
    class ThemeCompilerContext:

        def __init__(self, theme_compiler, colors_path, fonts_path, styles_path, mode=ColorMode.DARK):
            if (theme_compiler is None or
                colors_path is None or 
                fonts_path is None or 
                styles_path is None):
                raise ValueError("ThemeCompilerContext requires theme_compiler, colors_path, fonts_path and styles_path")
            self._theme_compiler = theme_compiler
            self.colors_path = colors_path
            self.fonts_path = fonts_path
            self.styles_path = styles_path
            self.mode = mode

        @property
        def _color_compiler(self):
            return self._theme_compiler._color_compiler
        @property
        def _font_compiler(self):
            return self._theme_compiler._font_compiler
        @property
        def _style_compiler(self):
            return self._theme_compiler._style_compiler

        def str_to_style(self, key_str):
            """Helper to resolve a key string like "BG.INVISIBLE" to the corresponding integer index."""
            return self._theme_compiler._style_compiler.style_ref_to_palette_idx(key_str)

        # ── context interface (consumed by StylePaletteCompiler) ─────────────────
        def get_color(self, palette_idx):
            """Internal. Return lv.color_t for *palette_idx*, read from flash.
            Requires colors_path and mode to be set."""
            val, err = self._color_compiler.read_setting_from_binary(
                self.colors_path, palette_idx, mode=self.mode)
            if err:
                print("Warning: color index {} load error: {}".format(palette_idx, err))
                return None
            return val

        def get_font(self, palette_idx):
            """Internal. Return lv.font for *palette_idx*, read from flash.
            Requires fonts_path to be set."""
            val, err = self._font_compiler.read_setting_from_binary(
                self.fonts_path, palette_idx)
            if err:
                print("Warning: font index {} load error: {}".format(palette_idx, err))
                return None
            return val

        def get_style(self, style_idx):
            """Internal. Build and return lv.style_t for *style_idx* from flash.
            Returns a fresh object each call. Caller must keep reference alive.
            Requires colors_path, fonts_path and styles_path to be set."""
            result, err = self._style_compiler.read_setting_from_binary(
                self.styles_path, style_idx, context=self)
            if err:
                print("Warning: style index {} load error: {}".format(style_idx, err))
                return None
            return result

    # use Styles binaries as main anchors for binaries. JSON file prefix is
    # inherited from ThemeSectionCompiler for ThemeCompiler and all sub compiler
    BINARY_FILE_PREFIX = StylePaletteCompiler.BINARY_FILE_PREFIX  # "styles_"
    SETTINGS_KEY = StylePaletteCompiler.SETTINGS_KEY  # "styles"
    RECURSIVE_KEYS = True  # for validation, collect all nested style indices from SPECTER_STYLES

    def __init__(self):
        self._color_compiler = ColorPaletteCompiler()
        self._font_compiler = FontPaletteCompiler()
        self._style_compiler = StylePaletteCompiler()

    # ── compile-time ──────────────────────────────────────────────────────────

    def json_to_binary(self, json_path, keys_class, output_dir=None):
        """Compile a full theme JSON file into three binary files.

        Writes:
          <output_dir>/colors_<name>.bin
          <output_dir>/fonts_<name>.bin
          <output_dir>/styles_<name>.bin

        output_dir defaults to "." if not specified.

        After writing, attempts to reconstruct all styles as a compile-time
        validation. Prints a warning for each style that fails.

        Returns a 3-tuple of paths (colors, fonts, styles) on success, None on fatal error.
        """
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print("Error: could not read theme JSON '{}': {}".format(json_path, e))
            return None

        theme_name = data.get("_metadata", {}).get("name", "").lower()
        if not theme_name:
            print("Error: missing '_metadata.name' in theme JSON")
            return None

        #strip filename if accidentally given as output_dir
        if output_dir is not None and output_dir.endswith(self.BINARY_FILE_SUFFIX):
            output_dir = self._path_dirname(output_dir)
        if output_dir is None:
            output_dir = "."
        # strip trailing slash to avoid double-slash in output paths
        output_dir = output_dir.rstrip("/")

        colors_out = output_dir + "/" + self._color_compiler.get_binary_filename(theme_name)
        fonts_out  = output_dir + "/" + self._font_compiler.get_binary_filename(theme_name)
        styles_out = output_dir + "/" + self._style_compiler.get_binary_filename(theme_name)

        print("Compiling theme '{}' …".format(theme_name))

        r = self._color_compiler.json_to_binary(json_path, SpecterColorPalette, output_path=colors_out)
        if r is None:
            print("Error: color palette compilation failed")
            return None
        print("  Colors → " + colors_out)

        r = self._font_compiler.json_to_binary(json_path, SpecterFontPalette, output_path=fonts_out)
        if r is None:
            print("Error: font palette compilation failed")
            return None
        print("  Fonts  → " + fonts_out)

        r = self._style_compiler.json_to_binary(json_path, SpecterStylePalette, output_path=styles_out)
        if r is None:
            print("Error: style palette compilation failed")
            return None
        print("  Styles → " + styles_out)

        return (colors_out, fonts_out, styles_out)

    # ── runtime reconstruction (binaries → lv objects) ───────────────────────

    def read_setting_from_binary(self, color_path, font_path, style_path, key_index, mode=ColorMode.DARK):
        reconstruction_context = self.ThemeCompilerContext(
            theme_compiler=self,
            colors_path=color_path,
            fonts_path=font_path,
            styles_path=style_path,
            mode=mode
        )

        (result, err) = self._style_compiler.read_setting_from_binary(style_path, key_index, context=reconstruction_context)
        return (result, err)

    #Alias for easier mapping/use
    def str_to_color_ind(self, key_str):
        """Helper to resolve a key string like "PRIMARY" to the corresponding color_t."""
        return color_ref_to_palette_idx(key_str)

    def str_to_font_ind(self, key_str):
        """Helper to resolve a key string like "TEXT" to the corresponding font index."""
        return font_ref_to_palette_idx(key_str)
    
    def str_to_style_ind(self, key_str):
        """Helper to resolve a key string like "BG.INVISIBLE" to the corresponding style index."""
        return style_ref_to_palette_idx(key_str)

    def read_style_from_binary(self, color_path, font_path, style_path, key_str, mode=ColorMode.DARK):
        return self.read_setting_from_binary(color_path, font_path, style_path, key_str, mode=mode)
    
    def read_color_from_binary(self, color_path, palette_idx, mode=ColorMode.DARK):
        return self._color_compiler.read_setting_from_binary(color_path, palette_idx, mode=mode)
    
    def read_font_from_binary(self, font_path, palette_idx):
        return self._font_compiler.read_setting_from_binary(font_path, palette_idx)

    # ── path helpers ──────────────────────────────────────────────────────────
    
    def get_binary_filenames(self, theme_name, theme_dir = '.'):
        return (
            theme_dir + "/" + self._color_compiler.get_binary_filename(theme_name),
            theme_dir + "/" + self._font_compiler.get_binary_filename(theme_name),
            theme_dir + "/" + self._style_compiler.get_binary_filename(theme_name)
        )

    # ── validation ────────────────────────────────────────────────────────────

    def validate_structure(self, colors_path, fonts_path, styles_path):
        """Structural binary integrity check — runs on PC and device (no lv required)."""
        ok, err = self._color_compiler.validate_binary_file(colors_path)
        if not ok:
            return (False, "ERROR: colors binary invalid: " + str(err))

        ok, err = self._font_compiler.validate_binary_file(fonts_path)
        if not ok:
            return (False, "ERROR: fonts binary invalid: " + str(err))

        ok, err = self._style_compiler.validate_binary_file(styles_path)
        if not ok:
            return (False, "ERROR: styles binary invalid: " + str(err))

        return (True, "OK: all binary files structurally valid")

    def validate(self, colors_path, fonts_path, styles_path):
        """Full validation: structure + materialise every SPECTER_STYLES constant
           in both DARK and LIGHT modes.
        Requires lv (device or simulator). On PC use validate_structure()."""
        ok, err = self.validate_structure(colors_path, fonts_path, styles_path)
        if not ok:
            return (False, err)

        all_indices = collect_int_constants(SpecterStylePalette, recursive=True)
        missing = []
        for mode in (ColorMode.DARK, ColorMode.LIGHT):          
            for idx in all_indices.values():
                s = self.read_setting_from_binary(colors_path, fonts_path, styles_path, idx, mode=mode)[0]
                if s is None:
                    missing.append((idx, mode))

        if missing:
            return (False, "WARNING: {} SPECTER_STYLES constants could not be built: {}".format(len(missing), missing))
        else:
            return (True, "OK: all {} SPECTER_STYLES constants materialised".format(len(all_indices)))


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    import sys
    if len(sys.argv) < 3:
        print("Usage: theme_compiler.py compile <theme.json> <output_dir>")
        print("       theme_compiler.py validate <theme_dir> <theme_name>")
        return

    command = sys.argv[1]

    if command == "compile":
        json_path  = sys.argv[2]
        output_dir = sys.argv[3]
        result = ThemeCompiler().json_to_binary(json_path, SpecterStylePalette, output_dir)
        if result is None:
            print("Error: failed to compile theme")
            sys.exit(1)

    elif command == "validate":
        theme_dir  = sys.argv[2]
        theme_name = sys.argv[3]
        (color_path, font_path, style_path) = ThemeCompiler().get_binary_filenames(theme_name, theme_dir)
        if lv is None:
            ok, err = ThemeCompiler().validate_structure(color_path, font_path, style_path)
        else:
            ok, err = ThemeCompiler().validate(color_path, font_path, style_path)
        if not ok:
            print(err)
            sys.exit(1)
        print(err)

    else:
        print("Error: unknown command '{}'".format(command))
        sys.exit(1)


if __name__ == "__main__":
    main()
