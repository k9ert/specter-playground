"""Unit tests for theme_compiler.py — orchestrates 3-binary theme compilation."""
import json
import shutil
from pathlib import Path

import pytest

from MockUI.basic.theming.theme_compiler import ThemeCompiler, ColorMode, SpecterStylePalette
from MockUI.basic.theming.color_palette_compiler import ColorPaletteCompiler, SpecterColorPalette
from MockUI.basic.theming.font_palette_compiler import FontPaletteCompiler, SpecterFontPalette
from MockUI.basic.theming.style_palette_compiler import StylePaletteCompiler
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
