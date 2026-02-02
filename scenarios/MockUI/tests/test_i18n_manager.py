#!/usr/bin/env python3
"""
Test i18n_manager.py with new interfaces.

Tests the integration of i18n_manager with the updated lang_compiler functions.
"""

import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "i18n"))

import lang_compiler
from i18n.i18n_manager import I18nManager
from i18n.translation_keys import Keys, KEY_TO_INDEX


def create_test_setup(temp_dir):
    """Create test language files and translation_keys.py"""
    # Create English JSON
    en_data = {
        "_metadata": {
            "language_code": "en",
            "language_name": "English"
        },
        "translations": {
            "MAIN_MENU_TITLE": "Main Menu",
            "SETTINGS_BUTTON": "Settings",
            "WALLET_LABEL": "Wallet"
        }
    }
    
    en_json = temp_dir / "specter_ui_en.json"
    with open(en_json, 'w', encoding='utf-8') as f:
        json.dump(en_data, f, indent=2)
    
    # Generate keys
    key_to_index = lang_compiler.generate_translation_keys(str(en_json))
    
    # Compile to binary
    lang_compiler.json_to_binary(str(en_json), key_to_index)
    
    # Create German JSON with missing translation
    de_data = {
        "_metadata": {
            "language_code": "de",
            "language_name": "Deutsch"
        },
        "translations": {
            "MAIN_MENU_TITLE": "Hauptmenü",
            # SETTINGS_BUTTON missing
            "WALLET_LABEL": "Geldbörse"
        }
    }
    
    de_json = temp_dir / "specter_ui_de.json"
    with open(de_json, 'w', encoding='utf-8') as f:
        json.dump(de_data, f, indent=2)
    
    # Compile German
    lang_compiler.json_to_binary(str(de_json), key_to_index)
    
    return temp_dir


def test_string_key_lookup():
    """Test translation lookup with string keys"""
    print("\n" + "="*70)
    print("TEST 1: String Key Lookup")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        create_test_setup(temp_dir)
        
        # Mock the language directory paths in i18n_manager
        # Note: This is a simplified test - in production, files would be in proper locations
        
        # For now, just verify the keys were generated correctly
        print("\n✓ Test environment created successfully")
        print(f"  Keys generated: {len(KEY_TO_INDEX)}")
        print(f"  Sample keys: {list(KEY_TO_INDEX.keys())[:3]}")
        
        # Verify Keys class exists
        assert hasattr(Keys, 'MAIN_MENU_TITLE'), "Keys class missing attributes"
        print(f"  Keys.MAIN_MENU_TITLE = {Keys.MAIN_MENU_TITLE}")
        
        return True


def test_integer_key_lookup():
    """Test translation lookup with integer keys (RAM efficient)"""
    print("\n" + "="*70)
    print("TEST 2: Integer Key Lookup (RAM Efficient)")
    print("="*70)
    
    # Verify integer constants work
    assert isinstance(Keys.MAIN_MENU_TITLE, int), "Keys should be integers"
    assert Keys.MAIN_MENU_TITLE == KEY_TO_INDEX["MAIN_MENU_TITLE"], "Key mismatch"
    
    print(f"  ✓ Keys.MAIN_MENU_TITLE is integer: {Keys.MAIN_MENU_TITLE}")
    print(f"  ✓ Matches KEY_TO_INDEX mapping")
    
    return True


def test_error_codes():
    """Test error code handling"""
    print("\n" + "="*70)
    print("TEST 3: Error Code Handling")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        create_test_setup(temp_dir)
        
        # Test reading from binary with new interface
        binary_path = temp_dir / "lang_en.bin"
        
        # Test valid read
        text, error = lang_compiler.read_translation_from_binary(str(binary_path), 0)
        assert text is not None, "Should read valid translation"
        assert error is None, "Should have no error"
        print(f"  ✓ Valid read: text='{text}', error={error}")
        
        # Test out of range
        text, error = lang_compiler.read_translation_from_binary(str(binary_path), 999)
        assert text is None, "Should fail for out of range"
        assert error == "invalid_key_index", f"Expected 'invalid_key_index', got '{error}'"
        print(f"  ✓ Out of range: text={text}, error='{error}'")
        
        return True


def test_missing_translation_fallback():
    """Test graceful degradation when translation is missing"""
    print("\n" + "="*70)
    print("TEST 4: Missing Translation Fallback (STR_MISSING)")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        flash_dir = temp_dir / "flash" / "i18n"
        flash_dir.mkdir(parents=True)
        
        # Use the real English JSON from the project
        real_en_json = Path(__file__).parent.parent / "i18n" / "specter_ui_en.json"
        
        # Copy it to temp dir
        test_en_json = temp_dir / "specter_ui_en.json"
        shutil.copy(real_en_json, test_en_json)
        
        # Generate binary from real English
        lang_compiler.json_to_binary(str(test_en_json), KEY_TO_INDEX, str(flash_dir / "lang_en.bin"))
        
        # Create German JSON with a missing translation
        # Load the real English to get all keys
        with open(real_en_json, 'r', encoding='utf-8') as f:
            en_data = json.load(f)
        
        # Create German with one key missing
        de_data = {
            "_metadata": {
                "language_code": "de",
                "language_name": "Deutsch (Test)"
            },
            "translations": {}
        }
        
        # Copy most translations but deliberately omit one
        test_missing_key = "MENU_ADD_WALLET"
        for key in en_data["translations"]:
            if key != test_missing_key:
                # Use placeholder German translation
                de_data["translations"][key] = f"DE:{key}"
        
        # Write German JSON
        test_de_json = temp_dir / "specter_ui_de.json"
        with open(test_de_json, 'w', encoding='utf-8') as f:
            json.dump(de_data, f, indent=2, ensure_ascii=False)
        
        # Compile German
        lang_compiler.json_to_binary(str(test_de_json), KEY_TO_INDEX, str(flash_dir / "lang_de.bin"))
        
        # Create config file with default language first
        config_path = flash_dir / "language_config.json"
        with open(config_path, 'w') as f:
            json.dump({"selected_language": "en"}, f)
        
        # Create I18nManager instance AFTER files are in place
        manager = I18nManager()
        manager.FLASH_I18N_DIR = str(flash_dir)
        manager.FLASH_CONFIG_PATH = str(config_path)
        # Re-scan after setting paths
        manager._scan_available_languages()
        
        # Now switch to German (has missing test_missing_key)
        success = manager.set_language("de")
        assert success, "Should successfully set language to 'de'"
        print(f"  ✓ Language switched to: de")
        
        # Test existing translation
        result = manager.t("MAIN_MENU_TITLE")
        assert result == "DE:MAIN_MENU_TITLE", f"Expected 'DE:MAIN_MENU_TITLE', got '{result}'"
        print(f"  ✓ Existing translation: '{result}'")
        
        # Test missing translation - should fall back to English default
        result = manager.t(test_missing_key)
        expected = en_data["translations"][test_missing_key]
        assert result == expected, f"Expected '{expected}' (fallback to en), got '{result}'"
        print(f"  ✓ Missing translation falls back to default: '{result}'")
        
        return True


def test_unknown_key_fallback():
    """Test graceful degradation when key doesn't exist"""
    print("\n" + "="*70)
    print("TEST 5: Unknown Key Fallback (STR_UNKNOWN_KEY)")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        flash_dir = temp_dir / "flash" / "i18n"
        flash_dir.mkdir(parents=True)
        
        # Use the real English JSON from the project
        real_en_json = Path(__file__).parent.parent / "i18n" / "specter_ui_en.json"
        
        # Copy and compile English
        test_en_json = temp_dir / "specter_ui_en.json"
        shutil.copy(real_en_json, test_en_json)
        lang_compiler.json_to_binary(str(test_en_json), KEY_TO_INDEX, str(flash_dir / "lang_en.bin"))
        
        # Create config file
        config_path = flash_dir / "language_config.json"
        with open(config_path, 'w') as f:
            json.dump({"selected_language": "en"}, f)
        
        # Create I18nManager instance AFTER files are in place
        manager = I18nManager()
        manager.FLASH_I18N_DIR = str(flash_dir)
        manager.FLASH_CONFIG_PATH = str(config_path)
        # Re-scan after setting paths
        manager._scan_available_languages()
        manager.set_language("en")
        
        # Test valid key
        result = manager.t("MAIN_MENU_TITLE")
        with open(real_en_json, 'r', encoding='utf-8') as f:
            expected = json.load(f)["translations"]["MAIN_MENU_TITLE"]
        assert result == expected, f"Expected '{expected}', got '{result}'"
        print(f"  ✓ Valid key: '{result}'")
        
        # Test unknown key (not in KEY_TO_INDEX)
        result = manager.t("NONEXISTENT_KEY")
        assert result == manager.STR_UNKNOWN_KEY, f"Expected '{manager.STR_UNKNOWN_KEY}', got '{result}'"
        print(f"  ✓ Unknown key returns: '{result}'")
        
        # Test with integer key out of range
        result = manager.t(9999)
        assert result == manager.STR_MISSING, f"Expected '{manager.STR_MISSING}', got '{result}'"
        print(f"  ✓ Out of range integer key returns: '{result}'")
        
        return True


def test_load_json_to_binary():
    """Test loading JSON and storing as binary"""
    print("\n" + "="*70)
    print("TEST 6: Load JSON and Store to Binary")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        flash_dir = temp_dir / "flash" / "i18n"
        flash_dir.mkdir(parents=True)
        
        # Use the real English JSON from the project
        real_en_json = Path(__file__).parent.parent / "i18n" / "specter_ui_en.json"
        
        # Copy and compile English first (needed as default)
        test_en_json = temp_dir / "specter_ui_en.json"
        shutil.copy(real_en_json, test_en_json)
        lang_compiler.json_to_binary(str(test_en_json), KEY_TO_INDEX, str(flash_dir / "lang_en.bin"))
        print(f"  ✓ Created default language: lang_en.bin")
        
        # Create a test Spanish JSON file
        with open(real_en_json, 'r', encoding='utf-8') as f:
            en_data = json.load(f)
        
        es_data = {
            "_metadata": {
                "language_code": "es",
                "language_name": "Español"
            },
            "translations": {}
        }
        
        # Add Spanish translations for a few keys
        test_keys = ["MAIN_MENU_TITLE", "MENU_ADD_WALLET", "COMMON_WALLET"]
        for key in test_keys:
            es_data["translations"][key] = f"ES:{key}"
        
        # Add remaining keys with placeholders
        for key in en_data["translations"]:
            if key not in es_data["translations"]:
                es_data["translations"][key] = f"ES:{key}"
        
        # Write Spanish JSON to flash directory (simulating user upload)
        test_es_json = flash_dir / "specter_ui_es.json"
        with open(test_es_json, 'w', encoding='utf-8') as f:
            json.dump(es_data, f, indent=2, ensure_ascii=False)
        print(f"  ✓ Created Spanish JSON: {test_es_json.name}")
        
        # Create config file
        config_path = flash_dir / "language_config.json"
        with open(config_path, 'w') as f:
            json.dump({"selected_language": "en"}, f)
        
        # Create I18nManager instance
        manager = I18nManager()
        manager.FLASH_I18N_DIR = str(flash_dir)
        manager.FLASH_CONFIG_PATH = str(config_path)
        manager._scan_available_languages()
        manager.set_language("en")
        
        # Load the Spanish JSON and convert to binary
        success = manager.load_language_from_json(str(test_es_json))
        assert success, "Should successfully load Spanish JSON"
        print(f"  ✓ Loaded Spanish JSON and converted to binary")
        
        # Verify the binary file was created
        es_binary = flash_dir / "lang_es.bin"
        assert es_binary.exists(), f"Binary file should exist: {es_binary}"
        print(f"  ✓ Binary file created: {es_binary.name}")
        
        # Re-scan to pick up the new language
        manager._scan_available_languages()
        assert "es" in manager.available_languages, "Spanish should be in available languages"
        print(f"  ✓ Spanish language available after load")
        
        # Switch to Spanish and verify translations
        manager.set_language("es")
        result = manager.t("MAIN_MENU_TITLE")
        assert result == "ES:MAIN_MENU_TITLE", f"Expected 'ES:MAIN_MENU_TITLE', got '{result}'"
        print(f"  ✓ Can read from newly loaded Spanish binary: '{result}'")
        
        return True


def test_language_switching():
    """Test switching between languages and verifying correct strings"""
    print("\n" + "="*70)
    print("TEST 7: Language Switching")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        flash_dir = temp_dir / "flash" / "i18n"
        flash_dir.mkdir(parents=True)
        
        # Use the real English JSON
        real_en_json = Path(__file__).parent.parent / "i18n" / "specter_ui_en.json"
        
        # Load English translations
        with open(real_en_json, 'r', encoding='utf-8') as f:
            en_data = json.load(f)
        
        # Create English binary
        test_en_json = temp_dir / "specter_ui_en.json"
        shutil.copy(real_en_json, test_en_json)
        lang_compiler.json_to_binary(str(test_en_json), KEY_TO_INDEX, str(flash_dir / "lang_en.bin"))
        
        # Create German JSON with actual different translations
        de_data = {
            "_metadata": {
                "language_code": "de",
                "language_name": "Deutsch"
            },
            "translations": {}
        }
        
        # Add German translations (using placeholder pattern to ensure they differ)
        for key in en_data["translations"]:
            de_data["translations"][key] = f"[DE] {en_data['translations'][key]}"
        
        # Write and compile German
        test_de_json = temp_dir / "specter_ui_de.json"
        with open(test_de_json, 'w', encoding='utf-8') as f:
            json.dump(de_data, f, indent=2, ensure_ascii=False)
        lang_compiler.json_to_binary(str(test_de_json), KEY_TO_INDEX, str(flash_dir / "lang_de.bin"))
        
        # Select test keys that exist in the JSON
        test_keys = ["MAIN_MENU_TITLE", "MENU_ADD_WALLET", "COMMON_WALLET", "MENU_MANAGE_DEVICE"]
        
        # Extract expected values from JSON files
        expected_en = {key: en_data["translations"][key] for key in test_keys}
        expected_de = {key: de_data["translations"][key] for key in test_keys}
        
        print(f"  ✓ Loaded test data from JSON files")
        print(f"    Test keys: {test_keys}")
        
        # Create config file
        config_path = flash_dir / "language_config.json"
        with open(config_path, 'w') as f:
            json.dump({"selected_language": "en"}, f)
        
        # Create I18nManager and initialize with English
        manager = I18nManager()
        manager.FLASH_I18N_DIR = str(flash_dir)
        manager.FLASH_CONFIG_PATH = str(config_path)
        manager._scan_available_languages()
        manager.set_language("en")
        
        # Verify we start with English
        assert manager.get_language() == "en", "Should start with English"
        print(f"  ✓ Initial language: {manager.get_language()}")
        
        # Test English translations match JSON
        for key in test_keys:
            result = manager.t(key)
            expected = expected_en[key]
            assert result == expected, f"English: Expected '{expected}' for '{key}', got '{result}'"
        print(f"  ✓ English translations match JSON source")
        
        # Switch to German
        success = manager.set_language("de")
        assert success, "Should successfully switch to German"
        assert manager.get_language() == "de", "Should now be using German"
        print(f"  ✓ Switched to language: {manager.get_language()}")
        
        # Test German translations match JSON
        for key in test_keys:
            result = manager.t(key)
            expected = expected_de[key]
            assert result == expected, f"German: Expected '{expected}' for '{key}', got '{result}'"
        print(f"  ✓ German translations match JSON source")
        
        # Verify translations actually differ between languages
        for key in test_keys:
            assert expected_en[key] != expected_de[key], f"JSON translations for '{key}' should differ"
        print(f"  ✓ Confirmed JSON translations differ between languages")
        
        # Switch back to English
        success = manager.set_language("en")
        assert success, "Should successfully switch back to English"
        assert manager.get_language() == "en", "Should be back to English"
        print(f"  ✓ Switched back to language: {manager.get_language()}")
        
        # Verify we're back to English translations
        for key in test_keys:
            result = manager.t(key)
            expected = expected_en[key]
            assert result == expected, f"Back to English: Expected '{expected}' for '{key}', got '{result}'"
        print(f"  ✓ English translations verified after switch back")
        
        return True


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("I18N_MANAGER INTEGRATION TEST SUITE")
    print("="*70)
    
    results = {
        "String Key Lookup": test_string_key_lookup(),
        "Integer Key Lookup": test_integer_key_lookup(),
        "Error Code Handling": test_error_codes(),
        "Missing Translation Fallback": test_missing_translation_fallback(),
        "Unknown Key Fallback": test_unknown_key_fallback(),
        "Load JSON to Binary": test_load_json_to_binary(),
        "Language Switching": test_language_switching(),
    }
    
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nNote: Full i18n_manager integration tests require proper file structure.")
        print("These tests verify the key interfaces are working correctly.")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())
