"""Unit tests for theme_compiler.py — orchestrates 3-binary theme compilation."""
import json
import shutil
from pathlib import Path

import pytest

from MockUI.basic.theming.theme_compiler import ThemeCompiler, ColorMode, SpecterStylePalette
from MockUI.basic.theming.theme_schema import StyleRole
from MockUI.basic.theming.color_palette_compiler import ColorPaletteCompiler, SpecterColorPalette
from MockUI.basic.theming.font_palette_compiler import FontPaletteCompiler, SpecterFontPalette
from MockUI.basic.theming.style_palette_compiler import (
    StylePaletteCompiler,
    _read_entry_header,
    _read_style_body,
)
from MockUI.basic.templates.settings_file_compiler import collect_int_constants

# Module-level compiler instance
_tc = ThemeCompiler()

# Path to the bundled default theme JSON
_THEMES_DIR = (
    Path(__file__).parent.parent
    / "src" / "MockUI" / "basic" / "theming" / "themes"
)
_SPECTER_JSON = _THEMES_DIR / "specter_ui_theme_specter.json"


# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture
def specter_json_path(tmp_path):
    """Copy of default theme JSON in a temp directory."""
    dest = tmp_path / "specter_ui_theme_specter.json"
    shutil.copy(_SPECTER_JSON, dest)
    return dest


@pytest.fixture
def theme_flash_dir(tmp_path):
    """Temp directory mimicking /flash/themes/."""
    d = tmp_path / "flash" / "themes"
    d.mkdir(parents=True)
    return d


@pytest.fixture
def specter_binaries(specter_json_path, theme_flash_dir):
    """Compiled (colors, fonts, styles) binaries for the 'specter' theme."""
    result = _tc.json_to_binary(str(specter_json_path), SpecterStylePalette, str(theme_flash_dir))
    assert result is not None, "json_to_binary returned None for default theme"
    colors_path, fonts_path, styles_path = result
    return Path(colors_path), Path(fonts_path), Path(styles_path)


# =====================================================================
# TestGetBinaryFilenames
# =====================================================================
class TestGetBinaryFilenames:
    """get_binary_filenames()"""

    def test_returns_three_paths(self):
        result = _tc.get_binary_filenames("specter", "/flash/themes")
        assert len(result) == 3

    def test_colors_prefix(self):
        colors, _, _ = _tc.get_binary_filenames("specter", "/flash/themes")
        assert Path(colors).name == "colors_specter.bin"

    def test_fonts_prefix(self):
        _, fonts, _ = _tc.get_binary_filenames("specter", "/flash/themes")
        assert Path(fonts).name == "fonts_specter.bin"

    def test_styles_prefix(self):
        _, _, styles = _tc.get_binary_filenames("specter", "/flash/themes")
        assert Path(styles).name == "styles_specter.bin"

    def test_custom_dir(self):
        colors, fonts, styles = _tc.get_binary_filenames("mytheme", "/custom/dir")
        assert colors.startswith("/custom/dir/")
        assert fonts.startswith("/custom/dir/")
        assert styles.startswith("/custom/dir/")


# =====================================================================
# TestJsonToBinary
# =====================================================================
class TestJsonToBinary:
    """json_to_binary() — compile-time"""

    def test_returns_three_paths_on_success(self, specter_json_path, theme_flash_dir):
        result = _tc.json_to_binary(str(specter_json_path), SpecterStylePalette, str(theme_flash_dir))
        assert result is not None
        assert len(result) == 3

    def test_output_files_created(self, specter_binaries):
        colors_path, fonts_path, styles_path = specter_binaries
        assert colors_path.exists()
        assert fonts_path.exists()
        assert styles_path.exists()

    def test_output_file_names(self, specter_binaries):
        colors_path, fonts_path, styles_path = specter_binaries
        assert colors_path.name == "colors_specter.bin"
        assert fonts_path.name == "fonts_specter.bin"
        assert styles_path.name == "styles_specter.bin"

    def test_returns_none_on_missing_file(self, tmp_path):
        result = _tc.json_to_binary(str(tmp_path / "nonexistent.json"), SpecterStylePalette, str(tmp_path))
        assert result is None

    def test_returns_none_on_missing_metadata(self, tmp_path):
        bad = tmp_path / "specter_ui_theme_noname.json"
        bad.write_text(json.dumps({"colors": {}, "fonts": {}, "styles": {}}))
        result = _tc.json_to_binary(str(bad), SpecterStylePalette, str(tmp_path))
        assert result is None

    def test_strips_bin_suffix_from_output_dir(self, specter_json_path, theme_flash_dir):
        """output_dir is accidentally a full .bin path — should still work."""
        fake_out = str(theme_flash_dir / "styles_specter.bin")
        result = _tc.json_to_binary(str(specter_json_path), SpecterStylePalette, fake_out)
        assert result is not None

    def test_colors_binary_has_correct_theme_name(self, specter_binaries):
        colors_path, _, _ = specter_binaries
        name = _tc._color_compiler.extract_settings_name_from_binary_file(str(colors_path))
        assert name == "Specter"

    def test_fonts_binary_has_correct_theme_name(self, specter_binaries):
        _, fonts_path, _ = specter_binaries
        name = _tc._font_compiler.extract_settings_name_from_binary_file(str(fonts_path))
        assert name == "Specter"

    def test_styles_binary_has_correct_theme_name(self, specter_binaries):
        _, _, styles_path = specter_binaries
        name = _tc._style_compiler.extract_settings_name_from_binary_file(str(styles_path))
        assert name == "Specter"


# =====================================================================
# TestValidateStructure
# =====================================================================
class TestValidateStructure:
    """validate_structure() — PC-safe binary integrity check"""

    def test_valid_binaries_return_ok(self, specter_binaries):
        colors_path, fonts_path, styles_path = specter_binaries
        ok, msg = _tc.validate_structure(str(colors_path), str(fonts_path), str(styles_path))
        assert ok is True

    def test_corrupt_colors_returns_false(self, specter_binaries, tmp_path):
        _, fonts_path, styles_path = specter_binaries
        bad_colors = tmp_path / "colors_specter.bin"
        bad_colors.write_bytes(b"JUNK")
        ok, msg = _tc.validate_structure(str(bad_colors), str(fonts_path), str(styles_path))
        assert ok is False

    def test_corrupt_fonts_returns_false(self, specter_binaries, tmp_path):
        colors_path, _, styles_path = specter_binaries
        bad_fonts = tmp_path / "fonts_specter.bin"
        bad_fonts.write_bytes(b"JUNK")
        ok, msg = _tc.validate_structure(str(colors_path), str(bad_fonts), str(styles_path))
        assert ok is False

    def test_corrupt_styles_returns_false(self, specter_binaries, tmp_path):
        colors_path, fonts_path, _ = specter_binaries
        bad_styles = tmp_path / "styles_specter.bin"
        bad_styles.write_bytes(b"JUNK")
        ok, msg = _tc.validate_structure(str(colors_path), str(fonts_path), str(bad_styles))
        assert ok is False


# =====================================================================
# TestReadSettingFromBinary
# =====================================================================
class TestReadSettingFromBinary:
    """read_setting_from_binary() — runtime reconstruction"""

    def test_returns_tuple(self, specter_binaries):
        colors_path, fonts_path, styles_path = specter_binaries
        result = _tc.read_setting_from_binary(
            str(colors_path), str(fonts_path), str(styles_path),
            SpecterStylePalette.WIDGET.BUTTON, ColorMode.DARK)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_dark_mode_returns_style(self, specter_binaries):
        colors_path, fonts_path, styles_path = specter_binaries
        style, err = _tc.read_setting_from_binary(
            str(colors_path), str(fonts_path), str(styles_path),
            SpecterStylePalette.WIDGET.BUTTON, ColorMode.DARK)
        assert style is not None

    def test_light_mode_returns_style(self, specter_binaries):
        colors_path, fonts_path, styles_path = specter_binaries
        style, err = _tc.read_setting_from_binary(
            str(colors_path), str(fonts_path), str(styles_path),
            SpecterStylePalette.WIDGET.BUTTON, ColorMode.LIGHT)
        assert style is not None

    def test_all_widget_styles_readable_dark(self, specter_binaries):
        """Every SpecterStylePalette constant must materialise without error in DARK mode."""
        colors_path, fonts_path, styles_path = specter_binaries
        all_indices = collect_int_constants(SpecterStylePalette, recursive=True)
        failed = []
        for name, idx in all_indices.items():
            style, err = _tc.read_setting_from_binary(
                str(colors_path), str(fonts_path), str(styles_path),
                idx, ColorMode.DARK)
            if style is None:
                failed.append((name, idx, err))
        assert failed == [], f"Styles failed to materialise in DARK: {failed}"

    def test_all_widget_styles_readable_light(self, specter_binaries):
        """Every SpecterStylePalette constant must materialise without error in LIGHT mode."""
        colors_path, fonts_path, styles_path = specter_binaries
        all_indices = collect_int_constants(SpecterStylePalette, recursive=True)
        failed = []
        for name, idx in all_indices.items():
            style, err = _tc.read_setting_from_binary(
                str(colors_path), str(fonts_path), str(styles_path),
                idx, ColorMode.LIGHT)
            if style is None:
                failed.append((name, idx, err))
        assert failed == [], f"Styles failed to materialise in LIGHT: {failed}"

    def test_out_of_range_key_returns_none(self, specter_binaries):
        colors_path, fonts_path, styles_path = specter_binaries
        style, err = _tc.read_setting_from_binary(
            str(colors_path), str(fonts_path), str(styles_path),
            9999, ColorMode.DARK)
        assert style is None


# =====================================================================
# TestStyleRoles — role containers: resolution, fallback, framing
# =====================================================================
class TestStyleRoles:
    """Role-based sub-styles inside a composite widget's entry.

    lv.style_t objects are opaque no-op sentinels under the test mock, so
    content is compared at the decoded-op level (what actually gets applied).
    """

    MB = SpecterStylePalette.WIDGET.MENU_BUTTON

    def _read(self, specter_binaries, role_code):
        colors_path, fonts_path, styles_path = specter_binaries
        return _tc.read_setting_from_binary(
            str(colors_path), str(fonts_path), str(styles_path),
            self.MB, ColorMode.DARK, role_code=role_code)

    def _ops(self, specter_binaries, role_code):
        """Decoded op list for a role of MENU_BUTTON, via the runtime read path."""
        _, _, styles_path = specter_binaries
        with open(str(styles_path), "rb") as f:
            ops, err = StylePaletteCompiler()._read_ops_from_handle(f, self.MB, role_code)
        assert err is None, err
        return ops

    def _raw_main_body_ops(self, specter_binaries):
        """The MAIN body read straight from the binary, bypassing the role API."""
        _, _, styles_path = specter_binaries
        with open(str(styles_path), "rb") as f:
            # Locate the MENU_BUTTON entry start via the style index, then read
            # the container's MAIN role body without going through _read_ops_from_handle.
            import struct
            from MockUI.basic.templates.settings_file_compiler import (
                MAGIC_SIZE, VERSION_SIZE, KEY_COUNT_SIZE, HEADER_SIZE, OFFSET_SIZE)
            f.seek(MAGIC_SIZE + VERSION_SIZE)
            key_count = struct.unpack("<I", f.read(KEY_COUNT_SIZE))[0]
            assert self.MB < key_count
            f.seek(HEADER_SIZE + self.MB * OFFSET_SIZE)
            entry_off = struct.unpack("<I", f.read(OFFSET_SIZE))[0]
            header = _read_entry_header(f, entry_off)
            assert header is not None
            is_container, _, role_table = header
            assert is_container, "MENU_BUTTON must be a role container in specter"
            return _read_style_body(f, role_table[StyleRole.MAIN])

    def test_main_role_is_base_style(self, specter_binaries):
        """role_code=None resolves the exact ops of the container's MAIN body."""
        assert self._ops(specter_binaries, None) == self._raw_main_body_ops(specter_binaries)

    def test_explicit_main_role_matches_none(self, specter_binaries):
        """role_code=StyleRole.MAIN resolves the exact same ops as role_code=None."""
        assert self._ops(specter_binaries, None) == self._ops(specter_binaries, StyleRole.MAIN)

    def test_defined_roles_resolve(self, specter_binaries):
        """Every MENU_BUTTON role the specter theme defines must materialise."""
        for role in (StyleRole.FG, StyleRole.ICON, StyleRole.LABEL,
                     StyleRole.INDICATOR, StyleRole.RHS):
            style, err = self._read(specter_binaries, role)
            assert style is not None, f"role {role} failed: {err}"

    def test_role_style_differs_from_main(self, specter_binaries):
        """A role sub-style carries different content (ops) from the MAIN body."""
        assert self._ops(specter_binaries, StyleRole.LABEL) != self._ops(specter_binaries, None)

    def test_missing_role_returns_none(self, specter_binaries):
        """A role code the theme does not define resolves to (None, err)."""
        # CURSOR is not a MENU_BUTTON role in the specter theme.
        style, err = self._read(specter_binaries, StyleRole.CURSOR)
        assert style is None
        assert err is not None

    def test_leaf_style_rejects_non_main_role(self, specter_binaries):
        """A leaf style (no roles block) yields no style for a non-MAIN role."""
        colors_path, fonts_path, styles_path = specter_binaries
        leaf_idx = SpecterStylePalette.BG.DEFAULT  # plain leaf, no roles
        style, err = _tc.read_setting_from_binary(
            str(colors_path), str(fonts_path), str(styles_path),
            leaf_idx, ColorMode.DARK, role_code=StyleRole.FG)
        assert style is None


# =====================================================================
# TestRoleContainerEncoding — write side: convert_setting_to_binary framing
# =====================================================================
class TestRoleContainerEncoding:
    """convert_setting_to_binary() must emit the container framing for roles."""

    def _compile_entry(self, entry):
        return StylePaletteCompiler().convert_setting_to_binary(entry)

    def test_leaf_entry_has_clear_high_bit(self):
        """A style without roles -> first byte high bit clear, value = op_count."""
        buf = self._compile_entry({"bg_color": "@CANVAS"})
        assert buf[0] & 0x80 == 0, "leaf entry must not set the container flag"

    def test_roles_entry_has_container_flag(self):
        """A style with roles -> first byte = 0x80 | role_count."""
        entry = {"bg_color": "@CANVAS",
                 "roles": {"FG": {"text_color": "@INK"}}}
        buf = self._compile_entry(entry)
        assert buf[0] & 0x80, "roles entry must set the container flag"
        # role_count = MAIN + FG = 2
        assert (buf[0] & 0x7F) == 2

    def test_roles_entry_table_layout(self):
        """Container table holds role codes (MAIN first) with inline bodies."""
        entry = {"bg_color": "@CANVAS",
                 "roles": {"LABEL": {"text_color": "@INK"},
                           "FG": {"text_color": "@INK"}}}
        buf = self._compile_entry(entry)
        role_count = buf[0] & 0x7F
        assert role_count == 3  # MAIN + FG + LABEL
        # Table entries are (role_code u8, offset u16le), MAIN (0) first,
        # then ascending role code (FG=1, LABEL=3).
        codes = [buf[1 + i*3] for i in range(role_count)]
        assert codes == [StyleRole.MAIN, StyleRole.FG, StyleRole.LABEL]

    def test_unknown_role_is_skipped_with_warning(self, capsys):
        """An unrecognised role name is dropped; the rest still encodes."""
        entry = {"bg_color": "@CANVAS",
                 "roles": {"FG": {"text_color": "@INK"},
                           "NOPE": {"text_color": "@INK"}}}
        buf = self._compile_entry(entry)
        # Only MAIN + FG made it in; NOPE was skipped.
        assert (buf[0] & 0x7F) == 2
        assert "unknown role" in capsys.readouterr().out.lower()


