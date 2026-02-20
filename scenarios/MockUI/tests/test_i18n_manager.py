"""Unit tests for i18n_manager.py — runtime manager."""
import json
from pathlib import Path

import pytest

from MockUI.i18n import I18nManager
from MockUI.i18n.translation_keys import KEY_TO_INDEX, Keys
import MockUI.i18n.lang_compiler as lang_compiler


# =====================================================================
# TestI18nManagerInit
# =====================================================================
class TestI18nManagerInit:
    """Initialisation and startup behaviour."""

    def test_default_language_is_english(self, i18n_manager):
        assert i18n_manager.get_language() == "en"

    def test_scans_available_languages(self, i18n_manager):
        langs = i18n_manager.get_available_languages()
        assert "en" in langs

    def test_detects_multiple_languages(self, i18n_manager, de_binary_path):
        """After adding German binary, rescan picks it up."""
        i18n_manager._scan_available_languages()
        assert "de" in i18n_manager.get_available_languages()

    def test_loads_preference_from_config(self, i18n_flash_dir, en_binary_path, de_binary_path):
        """Manager respects saved preference on init."""
        config_path = i18n_flash_dir / "language_config.json"
        with open(config_path, "w") as f:
            json.dump({"selected_language": "de"}, f)

        mgr = I18nManager()
        mgr.FLASH_I18N_DIR = str(i18n_flash_dir)
        mgr.FLASH_CONFIG_PATH = str(config_path)
        mgr._scan_available_languages()
        # Re-load preference
        selected = mgr._load_language_preference()
        mgr.set_language(selected)
        assert mgr.get_language() == "de"

    def test_falls_back_when_saved_lang_unavailable(self, i18n_flash_dir, en_binary_path):
        """If config says 'xx' but only 'en' exists, fall back to default."""
        config_path = i18n_flash_dir / "language_config.json"
        with open(config_path, "w") as f:
            json.dump({"selected_language": "xx"}, f)

        mgr = I18nManager()
        mgr.FLASH_I18N_DIR = str(i18n_flash_dir)
        mgr.FLASH_CONFIG_PATH = str(config_path)
        mgr._scan_available_languages()
        selected = mgr._load_language_preference()
        assert selected == "en"

    def test_handles_missing_flash_dir_gracefully(self, tmp_path):
        """Manager doesn't crash if /flash/i18n doesn't exist."""
        mgr = I18nManager()
        mgr.FLASH_I18N_DIR = str(tmp_path / "nonexistent")
        mgr.FLASH_CONFIG_PATH = str(tmp_path / "nonexistent" / "config.json")
        mgr._scan_available_languages()
        assert mgr.get_available_languages() == []

    def test_handles_missing_config_file(self, i18n_flash_dir, en_binary_path):
        """No config file -> default language."""
        config_path = i18n_flash_dir / "language_config.json"
        if config_path.exists():
            config_path.unlink()

        mgr = I18nManager()
        mgr.FLASH_I18N_DIR = str(i18n_flash_dir)
        mgr.FLASH_CONFIG_PATH = str(config_path)
        mgr._scan_available_languages()
        selected = mgr._load_language_preference()
        assert selected == "en"


# =====================================================================
# TestLanguageSwitching
# =====================================================================
class TestLanguageSwitching:
    """set_language / get_language / get_available_languages"""

    def test_set_language_returns_true(self, i18n_manager, de_binary_path):
        i18n_manager._scan_available_languages()
        assert i18n_manager.set_language("de") is True

    def test_set_unavailable_returns_false(self, i18n_manager):
        assert i18n_manager.set_language("xx") is False

    def test_get_language_reflects_current(self, i18n_manager, de_binary_path):
        i18n_manager._scan_available_languages()
        i18n_manager.set_language("de")
        assert i18n_manager.get_language() == "de"

    def test_get_available_languages_returns_copy(self, i18n_manager):
        langs = i18n_manager.get_available_languages()
        langs.append("xx")
        assert "xx" not in i18n_manager.get_available_languages()


# =====================================================================
# TestTranslationLookup
# =====================================================================
class TestTranslationLookup:
    """t() method — the core translation interface."""

    def test_string_key_returns_text(self, i18n_manager, en_json_data):
        result = i18n_manager.t("MAIN_MENU_TITLE")
        assert result == en_json_data["translations"]["MAIN_MENU_TITLE"]

    def test_integer_key_returns_same_text(self, i18n_manager, en_json_data):
        result = i18n_manager.t(Keys.MAIN_MENU_TITLE)
        assert result == en_json_data["translations"]["MAIN_MENU_TITLE"]

    def test_unknown_string_key_returns_unknown(self, i18n_manager):
        assert i18n_manager.t("NONEXISTENT_KEY") == I18nManager.STR_UNKNOWN_KEY

    def test_out_of_range_integer_returns_missing(self, i18n_manager):
        assert i18n_manager.t(9999) == I18nManager.STR_MISSING

    def test_german_translation_returned(self, i18n_manager, de_binary_path, de_json_data):
        i18n_manager._scan_available_languages()
        i18n_manager.set_language("de")
        result = i18n_manager.t("MAIN_MENU_TITLE")
        expected = de_json_data["translations"]["MAIN_MENU_TITLE"]
        if isinstance(expected, dict):
            expected = expected["text"]
        assert result == expected

    def test_missing_translation_falls_back_to_english(
        self, i18n_flash_dir, en_binary_path, key_to_index,
        incomplete_de_json_path, en_json_data
    ):
        """German binary with missing keys -> falls back to English."""
        de_out = str(i18n_flash_dir / "lang_de.bin")
        lang_compiler.json_to_binary(str(incomplete_de_json_path), key_to_index, de_out)

        config_path = i18n_flash_dir / "language_config.json"
        with open(config_path, "w") as f:
            json.dump({"selected_language": "en"}, f)

        mgr = I18nManager()
        mgr.FLASH_I18N_DIR = str(i18n_flash_dir)
        mgr.FLASH_CONFIG_PATH = str(config_path)
        mgr._scan_available_languages()
        mgr.set_language("de")

        # Pick a key that's in the second half (not in incomplete DE)
        all_keys = sorted(en_json_data["translations"].keys())
        missing_key = all_keys[-1]  # Last key — not in incomplete DE
        result = mgr.t(missing_key)
        # Should fall back to English
        assert result == en_json_data["translations"][missing_key]

    def test_dict_access(self, i18n_manager, en_json_data):
        assert i18n_manager["MAIN_MENU_TITLE"] == en_json_data["translations"]["MAIN_MENU_TITLE"]

    def test_callable_access(self, i18n_manager, en_json_data):
        assert i18n_manager("MAIN_MENU_TITLE") == en_json_data["translations"]["MAIN_MENU_TITLE"]

    def test_returns_missing_when_not_setup(self):
        """Manager with no language files set returns STR_MISSING."""
        mgr = I18nManager()
        mgr.FLASH_I18N_DIR = "/nonexistent"
        mgr.FLASH_CONFIG_PATH = "/nonexistent/config.json"
        mgr.current_lang_file = None
        mgr.default_lang_file = None
        assert mgr.t("MAIN_MENU_TITLE") == I18nManager.STR_MISSING

    def test_corrupt_binary_returns_missing(self, i18n_flash_dir, en_binary_path):
        """Manager returns STR_MISSING when current language binary is corrupt."""
        config_path = i18n_flash_dir / "language_config.json"
        with open(config_path, "w") as f:
            json.dump({"selected_language": "en"}, f)

        # Corrupt the English binary (overwrite with garbage)
        with open(en_binary_path, "wb") as f:
            f.write(b"GARBAGE_DATA")

        mgr = I18nManager()
        mgr.FLASH_I18N_DIR = str(i18n_flash_dir)
        mgr.FLASH_CONFIG_PATH = str(config_path)
        mgr._scan_available_languages()
        mgr.set_language("en")

        # t() should not crash — returns STR_MISSING gracefully
        result = mgr.t("MAIN_MENU_TITLE")
        assert result == I18nManager.STR_MISSING

    def test_corrupt_binary_integer_key_returns_missing(self, i18n_flash_dir, en_binary_path):
        """Manager handles corrupt binary with integer key access too."""
        config_path = i18n_flash_dir / "language_config.json"
        with open(config_path, "w") as f:
            json.dump({"selected_language": "en"}, f)

        # Truncate the binary (valid header, missing index/data)
        with open(en_binary_path, "rb") as f:
            header = f.read(44)  # Keep only the 44-byte header
        with open(en_binary_path, "wb") as f:
            f.write(header)

        mgr = I18nManager()
        mgr.FLASH_I18N_DIR = str(i18n_flash_dir)
        mgr.FLASH_CONFIG_PATH = str(config_path)
        mgr._scan_available_languages()
        mgr.set_language("en")

        result = mgr.t(Keys.MAIN_MENU_TITLE)
        assert result == I18nManager.STR_MISSING


# =====================================================================
# TestLanguagePreference
# =====================================================================
class TestLanguagePreference:
    """Persistent language selection."""

    def test_saves_on_set_language(self, i18n_manager, i18n_flash_dir):
        config_path = Path(i18n_manager.FLASH_CONFIG_PATH)
        i18n_manager.set_language("en")
        assert config_path.exists()
        with open(config_path) as f:
            data = json.load(f)
        assert data["selected_language"] == "en"

    def test_saves_german_preference(self, i18n_manager, de_binary_path, i18n_flash_dir):
        i18n_manager._scan_available_languages()
        i18n_manager.set_language("de")
        config_path = Path(i18n_manager.FLASH_CONFIG_PATH)
        with open(config_path) as f:
            data = json.load(f)
        assert data["selected_language"] == "de"

    def test_corrupt_config_falls_back(self, i18n_flash_dir, en_binary_path):
        """Corrupt JSON in config file -> default."""
        config_path = i18n_flash_dir / "language_config.json"
        config_path.write_text("NOT JSON{{{")

        mgr = I18nManager()
        mgr.FLASH_I18N_DIR = str(i18n_flash_dir)
        mgr.FLASH_CONFIG_PATH = str(config_path)
        mgr._scan_available_languages()
        selected = mgr._load_language_preference()
        assert selected == "en"


# =====================================================================
# TestLanguageName
# =====================================================================
class TestLanguageName:
    """get_language_name()"""

    def test_english_name(self, i18n_manager):
        assert i18n_manager.get_language_name("en") == "English"

    def test_german_name(self, i18n_manager, de_binary_path):
        i18n_manager._scan_available_languages()
        assert i18n_manager.get_language_name("de") == "Deutsch"

    def test_unavailable_returns_none(self, i18n_manager):
        assert i18n_manager.get_language_name("xx") is None

    def test_falls_back_to_code_on_read_failure(self, i18n_manager, i18n_flash_dir):
        """If binary header unreadable, return lang_code string."""
        # Create a broken binary
        broken = i18n_flash_dir / "lang_zz.bin"
        broken.write_bytes(b"LANG\x01\x00\x00\x00\x00\x00\x00\x00")  # Too small for name
        i18n_manager._scan_available_languages()
        if "zz" in i18n_manager.available_languages:
            result = i18n_manager.get_language_name("zz")
            # Should fall back to "zz" since file read fails
            assert result == "zz"


# =====================================================================
# TestLoadLanguageFromJson
# =====================================================================
class TestLoadLanguageFromJson:
    """load_language_from_json() — runtime JSON import."""

    def test_load_creates_binary(self, i18n_manager, tmp_path, en_json_data, i18n_flash_dir):
        """Loading Spanish JSON creates lang_es.bin in flash dir."""
        es_data = {
            "_metadata": {"language_code": "es", "language_name": "Español"},
            "translations": {k: f"ES:{k}" for k in en_json_data["translations"]},
        }
        es_json = tmp_path / "specter_ui_es.json"
        with open(es_json, "w", encoding="utf-8") as f:
            json.dump(es_data, f, ensure_ascii=False)

        assert i18n_manager.load_language_from_json(str(es_json)) is True
        assert (i18n_flash_dir / "lang_es.bin").exists()

    def test_loaded_language_available(self, i18n_manager, tmp_path, en_json_data):
        """After load, language appears in available list."""
        es_data = {
            "_metadata": {"language_code": "es", "language_name": "Español"},
            "translations": {k: f"ES:{k}" for k in en_json_data["translations"]},
        }
        es_json = tmp_path / "specter_ui_es.json"
        with open(es_json, "w", encoding="utf-8") as f:
            json.dump(es_data, f, ensure_ascii=False)

        i18n_manager.load_language_from_json(str(es_json))
        assert "es" in i18n_manager.get_available_languages()

    def test_switch_to_loaded_language(self, i18n_manager, tmp_path, en_json_data):
        """Can switch to and read from newly loaded language."""
        es_data = {
            "_metadata": {"language_code": "es", "language_name": "Español"},
            "translations": {k: f"ES:{k}" for k in en_json_data["translations"]},
        }
        es_json = tmp_path / "specter_ui_es.json"
        with open(es_json, "w", encoding="utf-8") as f:
            json.dump(es_data, f, ensure_ascii=False)

        i18n_manager.load_language_from_json(str(es_json))
        i18n_manager.set_language("es")
        assert i18n_manager.t("MAIN_MENU_TITLE") == "ES:MAIN_MENU_TITLE"

    def test_rejects_invalid_filename(self, i18n_manager, tmp_path):
        bad = tmp_path / "bad_name.json"
        bad.write_text('{"_metadata":{"language_code":"xx"},"translations":{"A":"a"}}')
        assert i18n_manager.load_language_from_json(str(bad)) is False

    def test_rejects_compilation_failure(self, i18n_manager, tmp_path):
        """Missing language_code in metadata -> compilation fails."""
        bad = tmp_path / "specter_ui_xx.json"
        bad.write_text('{"_metadata":{"language_name":"Bad"},"translations":{"A":"a"}}')
        assert i18n_manager.load_language_from_json(str(bad)) is False
