"""Unit tests for theme_manager.py — ThemeManager singleton."""
import json
import shutil
from pathlib import Path

import pytest

from MockUI.basic.theming.theme_manager import ThemeManager, get_theme_manager
from MockUI.basic.theming.theme_compiler import ThemeCompiler, ColorMode, SPECTER_STYLES

_tc = ThemeCompiler()

_THEMES_DIR = (
    Path(__file__).parent.parent
    / "src" / "MockUI" / "basic" / "theming" / "themes"
)
_SPECTER_JSON = _THEMES_DIR / "specter_ui_theme_specter.json"


# =====================================================================
# Fixtures
# =====================================================================

@pytest.fixture(autouse=True)
def reset_singleton():
    """Ensure ThemeManager singleton is cleared before each test."""
    ThemeManager._instance = None
    yield
    ThemeManager._instance = None


@pytest.fixture
def theme_flash_dir(tmp_path):
    """Temp directory mimicking /flash/themes/ with the default theme pre-installed."""
    flash_dir = tmp_path / "flash" / "themes"
    flash_dir.mkdir(parents=True)

    specter_json = tmp_path / "specter_ui_theme_specter.json"
    shutil.copy(_SPECTER_JSON, specter_json)
    result = _tc.json_to_binary(str(specter_json), SPECTER_STYLES, str(flash_dir))
    assert result is not None, "Failed to compile default theme"
    return flash_dir


@pytest.fixture
def theme_manager(theme_flash_dir):
    """Fully initialised ThemeManager pointing at the temp flash dir."""
    config_path = theme_flash_dir / "config.json"
    with open(config_path, "w") as f:
        json.dump({"selected_file": "specter", "mode": ColorMode.DARK}, f)

    mgr = ThemeManager()
    mgr.FLASH_DIR = str(theme_flash_dir)
    mgr.FLASH_CONFIG_PATH = str(config_path)
    mgr._scan_available_files()
    mgr.set_theme("specter")
    return mgr


def _install_alt_theme(flash_dir, theme_name="custom"):
    """Write a minimal alternate theme JSON and compile it into flash_dir."""
    with open(_SPECTER_JSON, "r") as f:
        data = json.load(f)
    data["_metadata"]["name"] = theme_name.capitalize()
    alt_json = Path(flash_dir).parent / f"specter_ui_theme_{theme_name}.json"
    with open(alt_json, "w") as f:
        json.dump(data, f)
    result = _tc.json_to_binary(str(alt_json), SPECTER_STYLES, str(flash_dir))
    assert result is not None, f"Failed to compile alt theme '{theme_name}'"


# =====================================================================
# TestScanAvailableFiles
# =====================================================================
class TestScanAvailableFiles:
    """_scan_available_files() discovers themes correctly."""

    def test_default_theme_detected(self, theme_manager):
        assert "specter" in theme_manager.available_files

    def test_empty_dir_returns_no_themes(self, tmp_path):
        empty = tmp_path / "flash" / "themes"
        empty.mkdir(parents=True)
        mgr = ThemeManager()
        mgr.FLASH_DIR = str(empty)
        mgr.FLASH_CONFIG_PATH = str(empty / "config.json")
        mgr._scan_available_files()
        assert mgr.available_files == []

    def test_missing_colors_binary_excluded(self, theme_flash_dir, tmp_path):
        """A theme with only styles + fonts (no colors) must be excluded."""
        (theme_flash_dir / "colors_specter.bin").unlink()
        mgr = ThemeManager()
        mgr.FLASH_DIR = str(theme_flash_dir)
        mgr.FLASH_CONFIG_PATH = str(theme_flash_dir / "config.json")
        mgr._scan_available_files()
        assert "specter" not in mgr.available_files

    def test_missing_fonts_binary_excluded(self, theme_flash_dir):
        """A theme with only styles + colors (no fonts) must be excluded."""
        (theme_flash_dir / "fonts_specter.bin").unlink()
        mgr = ThemeManager()
        mgr.FLASH_DIR = str(theme_flash_dir)
        mgr.FLASH_CONFIG_PATH = str(theme_flash_dir / "config.json")
        mgr._scan_available_files()
        assert "specter" not in mgr.available_files

    def test_two_themes_detected(self, theme_flash_dir):
        _install_alt_theme(str(theme_flash_dir), "custom")
        mgr = ThemeManager()
        mgr.FLASH_DIR = str(theme_flash_dir)
        mgr.FLASH_CONFIG_PATH = str(theme_flash_dir / "config.json")
        mgr._scan_available_files()
        assert "specter" in mgr.available_files
        assert "custom" in mgr.available_files


# =====================================================================
# TestSetTheme
# =====================================================================
class TestSetTheme:
    """set_theme() / set_setting()"""

    def test_set_theme_returns_true(self, theme_manager):
        assert theme_manager.set_theme("specter") is True

    def test_set_unavailable_returns_false(self, theme_manager):
        assert theme_manager.set_theme("nonexistent") is False

    def test_set_theme_updates_current(self, theme_manager):
        theme_manager.set_theme("specter")
        assert theme_manager.current == "specter"

    def test_set_theme_with_mode_changes_mode(self, theme_manager):
        theme_manager.set_theme("specter", mode=ColorMode.LIGHT)
        assert theme_manager.mode == ColorMode.LIGHT

    def test_set_theme_with_none_mode_keeps_current_mode(self, theme_manager):
        theme_manager.mode = ColorMode.LIGHT
        theme_manager.set_theme("specter", mode=None)
        assert theme_manager.mode == ColorMode.LIGHT

    def test_set_theme_populates_colors_file(self, theme_manager):
        theme_manager.set_theme("specter")
        assert theme_manager.current_colors_file is not None

    def test_set_theme_populates_fonts_file(self, theme_manager):
        theme_manager.set_theme("specter")
        assert theme_manager.current_fonts_file is not None

    def test_set_theme_populates_default_colors_file(self, theme_manager):
        theme_manager.set_theme("specter")
        assert theme_manager.default_colors_file is not None

    def test_set_theme_populates_default_fonts_file(self, theme_manager):
        theme_manager.set_theme("specter")
        assert theme_manager.default_fonts_file is not None


# =====================================================================
# TestSetMode
# =====================================================================
class TestSetMode:
    """set_mode()"""

    def test_dark_mode_accepted(self, theme_manager):
        assert theme_manager.set_mode(ColorMode.DARK) is True
        assert theme_manager.mode == ColorMode.DARK

    def test_light_mode_accepted(self, theme_manager):
        assert theme_manager.set_mode(ColorMode.LIGHT) is True
        assert theme_manager.mode == ColorMode.LIGHT

    def test_invalid_mode_rejected(self, theme_manager):
        assert theme_manager.set_mode("invalid") is False

    def test_invalid_mode_does_not_change_current(self, theme_manager):
        original = theme_manager.mode
        theme_manager.set_mode("invalid")
        assert theme_manager.mode == original

    def test_set_mode_persists_to_config(self, theme_manager, theme_flash_dir):
        theme_manager.set_mode(ColorMode.LIGHT)
        config_path = theme_flash_dir / "config.json"
        with open(config_path) as f:
            data = json.load(f)
        assert data["mode"] == ColorMode.LIGHT


# =====================================================================
# TestPreferencePersistence
# =====================================================================
class TestPreferencePersistence:
    """_build_preference_data / _apply_loaded_preference / _save_settings_preference"""

    def test_saved_preference_includes_mode(self, theme_manager, theme_flash_dir):
        theme_manager.set_mode(ColorMode.LIGHT)
        config_path = theme_flash_dir / "config.json"
        with open(config_path) as f:
            data = json.load(f)
        assert "mode" in data

    def test_saved_preference_includes_selected_file(self, theme_manager, theme_flash_dir):
        theme_manager.set_theme("specter")
        config_path = theme_flash_dir / "config.json"
        with open(config_path) as f:
            data = json.load(f)
        assert data["selected_file"] == "specter"

    def test_loads_dark_mode_from_config(self, theme_flash_dir):
        config_path = theme_flash_dir / "config.json"
        with open(config_path, "w") as f:
            json.dump({"selected_file": "specter", "mode": ColorMode.DARK}, f)
        mgr = ThemeManager()
        mgr.FLASH_DIR = str(theme_flash_dir)
        mgr.FLASH_CONFIG_PATH = str(config_path)
        mgr._scan_available_files()
        mgr._load_stored_preference()  # re-read now that FLASH_CONFIG_PATH is set
        assert mgr.mode == ColorMode.DARK

    def test_loads_light_mode_from_config(self, theme_flash_dir):
        config_path = theme_flash_dir / "config.json"
        with open(config_path, "w") as f:
            json.dump({"selected_file": "specter", "mode": ColorMode.LIGHT}, f)
        mgr = ThemeManager()
        mgr.FLASH_DIR = str(theme_flash_dir)
        mgr.FLASH_CONFIG_PATH = str(config_path)
        mgr._scan_available_files()
        mgr._load_stored_preference()  # re-read now that FLASH_CONFIG_PATH is set
        assert mgr.mode == ColorMode.LIGHT

    def test_invalid_mode_in_config_falls_back_to_dark(self, theme_flash_dir):
        config_path = theme_flash_dir / "config.json"
        with open(config_path, "w") as f:
            json.dump({"selected_file": "specter", "mode": "INVALID_MODE"}, f)
        mgr = ThemeManager()
        mgr.FLASH_DIR = str(theme_flash_dir)
        mgr.FLASH_CONFIG_PATH = str(config_path)
        mgr._scan_available_files()
        mgr._load_stored_preference()  # re-read now that FLASH_CONFIG_PATH is set
        assert mgr.mode == ColorMode.DARK


# =====================================================================
# TestGetSetting
# =====================================================================
class TestGetSetting:
    """get_setting() — reads styles from binary files"""

    def test_returns_style_for_known_key(self, theme_manager):
        style = theme_manager.get_setting(SPECTER_STYLES.WIDGET.BUTTON)
        assert style is not None

    def test_returns_none_for_out_of_range_key(self, theme_manager):
        style = theme_manager.get_setting(9999)
        assert style is None

    def test_dark_mode_returns_style(self, theme_manager):
        theme_manager.set_mode(ColorMode.DARK)
        style = theme_manager.get_setting(SPECTER_STYLES.BG.DEFAULT)
        assert style is not None

    def test_light_mode_returns_style(self, theme_manager):
        theme_manager.set_mode(ColorMode.LIGHT)
        style = theme_manager.get_setting(SPECTER_STYLES.BG.DEFAULT)
        assert style is not None


# =====================================================================
# TestCurrentStylesFileProperty
# =====================================================================
class TestCurrentStylesFileProperty:
    """current_styles_file property aliases current_file."""

    def test_current_styles_file_equals_current_file(self, theme_manager):
        assert theme_manager.current_styles_file == theme_manager.current_file
