"""End-to-end integration tests for the i18n system.

These tests exercise the full Python code path (generate keys -> compile ->
init manager -> translate -> switch -> fallback) without any hardware.
All file I/O goes through tmp_path.
"""
import json
import shutil
from pathlib import Path

import pytest

from MockUI.i18n import I18nManager
from MockUI.i18n.translation_keys import KEY_TO_INDEX, Keys
import MockUI.i18n.lang_compiler as lang_compiler


# Path to real language source files
_I18N_LANGUAGES_DIR = Path(__file__).parent.parent / "src" / "MockUI" / "i18n" / "languages"
_EN_JSON = _I18N_LANGUAGES_DIR / "specter_ui_en.json"
_DE_JSON = _I18N_LANGUAGES_DIR / "specter_ui_de.json"


# =====================================================================
# TestFullWorkflow
# =====================================================================
class TestFullWorkflow:
    """End-to-end workflows exercising the complete code path."""

    def test_build_time_workflow(self, tmp_path):
        """generate_keys -> compile EN -> compile DE -> validate both."""
        en_src = tmp_path / "specter_ui_en.json"
        de_src = tmp_path / "specter_ui_de.json"
        shutil.copy(_EN_JSON, en_src)
        shutil.copy(_DE_JSON, de_src)

        # Step 1: Generate keys
        keys_out = str(tmp_path / "translation_keys.py")
        kti = lang_compiler.generate_translation_keys(str(en_src), output_path=keys_out)
        assert len(kti) > 0

        # Step 2: Compile EN
        en_bin = str(tmp_path / "lang_en.bin")
        assert lang_compiler.json_to_binary(str(en_src), kti, en_bin) is not None

        # Step 3: Compile DE
        de_bin = str(tmp_path / "lang_de.bin")
        assert lang_compiler.json_to_binary(str(de_src), kti, de_bin) is not None

        # Step 4: Validate both
        success, error = lang_compiler.validate_binary_file(en_bin)
        assert success, f"EN validation failed: {error}"
        success, error = lang_compiler.validate_binary_file(de_bin)
        assert success, f"DE validation failed: {error}"

    def test_runtime_workflow(self, tmp_path):
        """Init manager with EN -> translate -> switch to DE -> fallback -> switch back."""
        flash_dir = tmp_path / "flash" / "i18n"
        flash_dir.mkdir(parents=True)

        # Prepare binaries
        en_src = tmp_path / "specter_ui_en.json"
        de_src = tmp_path / "specter_ui_de.json"
        shutil.copy(_EN_JSON, en_src)
        shutil.copy(_DE_JSON, de_src)

        en_bin = str(flash_dir / "lang_en.bin")
        de_bin = str(flash_dir / "lang_de.bin")
        lang_compiler.json_to_binary(str(en_src), KEY_TO_INDEX, en_bin)
        lang_compiler.json_to_binary(str(de_src), KEY_TO_INDEX, de_bin)

        config_path = flash_dir / "language_config.json"
        with open(config_path, "w") as f:
            json.dump({"selected_language": "en"}, f)

        # Init manager
        mgr = I18nManager()
        mgr.FLASH_I18N_DIR = str(flash_dir)
        mgr.FLASH_CONFIG_PATH = str(config_path)
        mgr._scan_available_languages()
        mgr.set_language("en")

        # Load expected values
        with open(_EN_JSON, "r", encoding="utf-8") as f:
            en_data = json.load(f)
        with open(_DE_JSON, "r", encoding="utf-8") as f:
            de_data = json.load(f)

        # Verify English
        en_text = mgr.t("MAIN_MENU_TITLE")
        assert en_text == en_data["translations"]["MAIN_MENU_TITLE"]

        # Switch to German
        assert mgr.set_language("de") is True
        de_text = mgr.t("MAIN_MENU_TITLE")
        de_expected = de_data["translations"]["MAIN_MENU_TITLE"]
        if isinstance(de_expected, dict):
            de_expected = de_expected["text"]
        assert de_text == de_expected
        assert de_text != en_text  # Sanity: languages differ

        # Switch back to English
        assert mgr.set_language("en") is True
        assert mgr.t("MAIN_MENU_TITLE") == en_text

    def test_language_load_workflow(self, tmp_path):
        """Init with EN only -> load ES from JSON -> switch -> verify."""
        flash_dir = tmp_path / "flash" / "i18n"
        flash_dir.mkdir(parents=True)

        en_src = tmp_path / "specter_ui_en.json"
        shutil.copy(_EN_JSON, en_src)
        en_bin = str(flash_dir / "lang_en.bin")
        lang_compiler.json_to_binary(str(en_src), KEY_TO_INDEX, en_bin)

        config_path = flash_dir / "language_config.json"
        with open(config_path, "w") as f:
            json.dump({"selected_language": "en"}, f)

        mgr = I18nManager()
        mgr.FLASH_I18N_DIR = str(flash_dir)
        mgr.FLASH_CONFIG_PATH = str(config_path)
        mgr._scan_available_languages()
        mgr.set_language("en")

        # Only English available initially
        assert mgr.get_available_languages() == ["en"]

        # Create Spanish JSON
        with open(_EN_JSON, "r", encoding="utf-8") as f:
            en_data = json.load(f)
        es_data = {
            "_metadata": {"language_code": "es", "language_name": "Español"},
            "translations": {k: f"ES:{k}" for k in en_data["translations"]},
        }
        es_json = tmp_path / "specter_ui_es.json"
        with open(es_json, "w", encoding="utf-8") as f:
            json.dump(es_data, f, ensure_ascii=False)

        # Load Spanish
        assert mgr.load_language_from_json(str(es_json)) is True
        assert "es" in mgr.get_available_languages()

        # Switch and verify
        assert mgr.set_language("es") is True
        assert mgr.t("MAIN_MENU_TITLE") == "ES:MAIN_MENU_TITLE"

    def test_persistence_simulation(self, tmp_path):
        """Set language -> re-create manager with same flash dir -> verify restored."""
        flash_dir = tmp_path / "flash" / "i18n"
        flash_dir.mkdir(parents=True)

        en_src = tmp_path / "specter_ui_en.json"
        de_src = tmp_path / "specter_ui_de.json"
        shutil.copy(_EN_JSON, en_src)
        shutil.copy(_DE_JSON, de_src)

        lang_compiler.json_to_binary(str(en_src), KEY_TO_INDEX, str(flash_dir / "lang_en.bin"))
        lang_compiler.json_to_binary(str(de_src), KEY_TO_INDEX, str(flash_dir / "lang_de.bin"))

        config_path = flash_dir / "language_config.json"
        with open(config_path, "w") as f:
            json.dump({"selected_language": "en"}, f)

        # First "boot" — switch to German
        mgr1 = I18nManager()
        mgr1.FLASH_I18N_DIR = str(flash_dir)
        mgr1.FLASH_CONFIG_PATH = str(config_path)
        mgr1._scan_available_languages()
        mgr1.set_language("de")
        assert mgr1.get_language() == "de"

        # Second "boot" — new manager instance, same flash dir
        mgr2 = I18nManager()
        mgr2.FLASH_I18N_DIR = str(flash_dir)
        mgr2.FLASH_CONFIG_PATH = str(config_path)
        mgr2._scan_available_languages()
        selected = mgr2._load_language_preference()
        mgr2.set_language(selected)
        assert mgr2.get_language() == "de"


# =====================================================================
# TestRealLanguageFiles
# =====================================================================
class TestRealLanguageFiles:
    """Tests using the actual specter_ui_en.json and specter_ui_de.json files."""

    def test_all_english_keys_present_in_binary(self, en_binary_path, key_to_index, en_json_data):
        """Every key from translation_keys maps to a real string in the EN binary."""
        for key, idx in key_to_index.items():
            text, error = lang_compiler.read_translation_from_binary(str(en_binary_path), idx)
            assert text is not None, f"Key '{key}' (index {idx}) missing in EN binary: {error}"
            assert text == en_json_data["translations"][key]

    def test_german_translations_differ(self, de_binary_path, en_binary_path, key_to_index, de_json_data):
        """Where German has a translation, it differs from English."""
        for key, idx in key_to_index.items():
            if key not in de_json_data["translations"]:
                continue
            de_text, _ = lang_compiler.read_translation_from_binary(str(de_binary_path), idx)
            en_text, _ = lang_compiler.read_translation_from_binary(str(en_binary_path), idx)
            if de_text is not None and en_text is not None:
                de_expected = de_json_data["translations"][key]
                if isinstance(de_expected, dict):
                    de_expected = de_expected["text"]
                assert de_text == de_expected

    def test_validate_real_english_binary(self, en_binary_path):
        success, error = lang_compiler.validate_binary_file(str(en_binary_path))
        assert success, f"Validation failed: {error}"

    def test_validate_real_german_binary(self, de_binary_path):
        success, error = lang_compiler.validate_binary_file(str(de_binary_path))
        assert success, f"Validation failed: {error}"

    def test_roundtrip_every_english_key(self, en_json_path, key_to_index, tmp_path, en_json_data):
        """Compile from JSON and read back every single key."""
        out = str(tmp_path / "lang_en.bin")
        lang_compiler.json_to_binary(str(en_json_path), key_to_index, out)
        translations = en_json_data["translations"]
        for key, idx in key_to_index.items():
            text, error = lang_compiler.read_translation_from_binary(out, idx)
            assert error is None, f"Error reading '{key}': {error}"
            assert text == translations[key], f"Mismatch for '{key}': got '{text}'"

    def test_roundtrip_every_german_key(self, de_json_path, key_to_index, tmp_path, de_json_data):
        """Compile German and read back all translated keys."""
        out = str(tmp_path / "lang_de.bin")
        lang_compiler.json_to_binary(str(de_json_path), key_to_index, out)
        translations = de_json_data["translations"]
        for key, idx in key_to_index.items():
            text, error = lang_compiler.read_translation_from_binary(out, idx)
            if key in translations:
                expected = translations[key]
                if isinstance(expected, dict):
                    expected = expected["text"]
                assert text == expected, f"Mismatch for '{key}'"
            else:
                assert error == "missing", f"Key '{key}' should be missing, got text='{text}'"

    def test_key_count_matches_json(self, en_json_data):
        """translation_keys.py key count matches the English JSON."""
        assert len(KEY_TO_INDEX) == len(en_json_data["translations"])

    def test_all_json_keys_in_key_to_index(self, en_json_data):
        """Every key in the English JSON is mapped in KEY_TO_INDEX."""
        for key in en_json_data["translations"]:
            assert key in KEY_TO_INDEX, f"Key '{key}' from JSON not in KEY_TO_INDEX"

    def test_keys_class_matches_dict(self):
        """Keys.CONSTANT == KEY_TO_INDEX['CONSTANT'] for all entries."""
        for key, idx in KEY_TO_INDEX.items():
            assert getattr(Keys, key) == idx, f"Keys.{key} != KEY_TO_INDEX['{key}']"
