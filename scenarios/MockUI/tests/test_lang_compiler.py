#!/usr/bin/env python3
"""
Round-trip test for language file compilation and reading.

Tests the complete workflow with safety checks:
1. Generate translation keys from English JSON
2. Compile English JSON to binary
3. Read all translations back and verify
4. Create test files with missing translations
5. Verify bounds checking prevents invalid reads
6. Test validation catches errors
"""

import os
import sys
import json
import tempfile
import struct
from pathlib import Path

# Import the modules we're testing
sys.path.insert(0, str(Path(__file__).parent.parent / "i18n"))
import lang_compiler


def create_test_english_json(temp_dir):
    """Create a test English JSON file with sample translations."""
    data = {
        "_metadata": {
            "language_code": "en",
            "language_name": "English"
        },
        "translations": {
            "MAIN_MENU_TITLE": "Main Menu",
            "SETTINGS_BUTTON": "Settings",
            "WALLET_LABEL": "Wallet",
            "ADDRESS_DISPLAY": "Bitcoin Address",
            "BACK_BUTTON": "Back"
        }
    }
    
    json_path = temp_dir / "specter_ui_en.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    return json_path


def create_test_german_json(temp_dir):
    """Create a test German JSON file with some missing translations."""
    data = {
        "_metadata": {
            "language_code": "de",
            "language_name": "Deutsch"
        },
        "translations": {
            "MAIN_MENU_TITLE": "Hauptmenü",
            "SETTINGS_BUTTON": "Einstellungen",
            # Missing: WALLET_LABEL
            "ADDRESS_DISPLAY": "Bitcoin-Adresse",
            # Missing: BACK_BUTTON
        }
    }
    
    json_path = temp_dir / "specter_ui_de.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    return json_path


def test_english_roundtrip():
    """Test English: JSON → keys → binary → read back."""
    print("\n" + "="*70)
    print("TEST 1: English Round-Trip (JSON → Binary → Read Back)")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        
        # Step 1: Create test English JSON
        print("\n[1/4] Creating test English JSON...")
        json_path = create_test_english_json(temp_dir)
        print(f"  ✓ Created: {json_path.name}")
        
        # Step 2: Generate translation keys
        print("\n[2/4] Generating translation keys...")
        key_to_index = lang_compiler.generate_translation_keys(str(json_path))
        keys_path = temp_dir / "translation_keys.py"
        assert keys_path.exists(), "translation_keys.py not created"
        print(f"  ✓ Generated {len(key_to_index)} keys")
        
        # Verify Keys class was generated
        with open(keys_path, 'r') as f:
            keys_content = f.read()
            assert 'class Keys:' in keys_content, "Keys class not found"
            assert 'KEY_TO_INDEX' in keys_content, "KEY_TO_INDEX not found"
            print("  ✓ Keys class and KEY_TO_INDEX generated")
        
        # Step 3: Compile to binary
        print("\n[3/4] Compiling to binary...")
        binary_path = lang_compiler.json_to_binary(str(json_path), key_to_index)
        assert binary_path is not None, "Binary compilation failed"
        assert Path(binary_path).exists(), "Binary file not created"
        print(f"  ✓ Created: {Path(binary_path).name}")
        
        # Step 4: Read back all translations and verify they match
        print("\n[4/4] Reading back translations and verifying...")
        
        # Load original translations from JSON
        with open(json_path, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        original_translations = original_data["translations"]
        
        all_success = True
        for key, index in key_to_index.items():
            text, error = lang_compiler.read_translation_from_binary(
                binary_path, index
            )
            
            if text is None:
                print(f"  ✗ Failed to read key '{key}' (index {index}): {error}")
                all_success = False
            else:
                # Verify the text matches the original
                original_text = original_translations.get(key)
                if text == original_text:
                    print(f"  ✓ [{index}] {key}: '{text}' (matches)")
                else:
                    print(f"  ✗ [{index}] {key}: Expected '{original_text}', got '{text}'")
                    all_success = False
        
        if all_success:
            print("\n✓ TEST 1 PASSED: All translations read back and match originals")
            return True
        else:
            print("\n✗ TEST 1 FAILED: Some translations could not be read or didn't match")
            return False


def test_missing_translations():
    """Test German with missing keys → verify 0xFFFFFFFF handling."""
    print("\n" + "="*70)
    print("TEST 2: Missing Translation Handling")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        
        # Create English (for keys) and German (with missing translations)
        print("\n[1/4] Creating test files...")
        en_json = create_test_english_json(temp_dir)
        de_json = create_test_german_json(temp_dir)
        print("  ✓ Created English and German test files")
        
        # Generate keys from English
        print("\n[2/4] Generating translation keys from English...")
        key_to_index = lang_compiler.generate_translation_keys(str(en_json))
        print(f"  ✓ Generated {len(key_to_index)} keys")
        
        # Compile German (with missing translations)
        print("\n[3/4] Compiling German (with missing translations)...")
        de_binary = lang_compiler.json_to_binary(str(de_json), key_to_index)
        assert de_binary is not None, "German compilation failed"
        print(f"  ✓ Created: {Path(de_binary).name}")
        
        # Test reading missing translations
        print("\n[4/4] Testing missing translation detection...")
        test_cases = [
            ("MAIN_MENU_TITLE", True),   # Should exist
            ("WALLET_LABEL", False),     # Missing
            ("BACK_BUTTON", False),      # Missing
        ]
        
        all_correct = True
        for key, should_exist in test_cases:
            index = key_to_index[key]
            text, error = lang_compiler.read_translation_from_binary(
                de_binary, index
            )
            
            if should_exist:
                if text is not None:
                    print(f"  ✓ {key}: Found ('{text}')")
                else:
                    print(f"  ✗ {key}: Should exist but got error: {error}")
                    all_correct = False
            else:
                if text is None and error == "missing":
                    print(f"  ✓ {key}: Correctly detected as missing")
                else:
                    print(f"  ✗ {key}: Should be missing, got: text={text}, error={error}")
                    all_correct = False
        
        if all_correct:
            print("\n✓ TEST 2 PASSED: Missing translations correctly detected")
            return True
        else:
            print("\n✗ TEST 2 FAILED: Missing translation detection incorrect")
            return False


def test_bounds_checking():
    """Test bounds checking prevents invalid reads."""
    print("\n" + "="*70)
    print("TEST 3: Bounds Checking & Safety")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        
        # Create and compile English
        print("\n[1/2] Creating test binary...")
        json_path = create_test_english_json(temp_dir)
        key_to_index = lang_compiler.generate_translation_keys(str(json_path))
        binary_path = lang_compiler.json_to_binary(str(json_path), key_to_index)
        print(f"  ✓ Created test binary")
        
        # Test various invalid reads
        print("\n[2/2] Testing bounds checking...")
        test_cases = [
            ("out_of_range_high", 9999, "invalid_key_index"),
            ("out_of_range_negative", -1, "invalid_key_index"),
        ]
        
        all_caught = True
        for test_name, bad_index, expected_error in test_cases:
            text, error = lang_compiler.read_translation_from_binary(
                binary_path, bad_index
            )
            
            if text is None and expected_error in error:
                print(f"  ✓ {test_name}: Correctly rejected (error: {error})")
            else:
                print(f"  ✗ {test_name}: Should reject with '{expected_error}', got text={text}, error={error}")
                all_caught = False
        
        # Test non-existent file
        fake_path = temp_dir / "nonexistent.bin"
        text, error = lang_compiler.read_translation_from_binary(
            str(fake_path), 0
        )
        if text is None and error == "read_error":
            print(f"  ✓ nonexistent_file: Correctly rejected")
        else:
            print(f"  ✗ nonexistent_file: Should reject, got text={text}, error={error}")
            all_caught = False
        
        # Test corrupted file (too small)
        corrupt_path = temp_dir / "corrupt.bin"
        with open(corrupt_path, 'wb') as f:
            f.write(b'LANG')  # Only magic, missing version and key_count
        
        text, error = lang_compiler.read_translation_from_binary(
            str(corrupt_path), 0
        )
        if text is None and error == "read_error":
            print(f"  ✓ corrupted_file: Correctly rejected")
        else:
            print(f"  ✗ corrupted_file: Should reject, got text={text}, error={error}")
            all_caught = False
        
        if all_caught:
            print("\n✓ TEST 3 PASSED: All invalid reads correctly rejected")
            return True
        else:
            print("\n✗ TEST 3 FAILED: Some invalid reads not caught")
            return False


def test_validation():
    """Test validation catches errors."""
    print("\n" + "="*70)
    print("TEST 4: Binary File Validation")
    print("="*70)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        
        # Create valid binary
        print("\n[1/3] Creating valid binary...")
        json_path = create_test_english_json(temp_dir)
        key_to_index = lang_compiler.generate_translation_keys(str(json_path))
        binary_path = lang_compiler.json_to_binary(str(json_path), key_to_index)
        
        # Import translation_keys module
        import importlib.util
        keys_path = temp_dir / "translation_keys.py"
        spec = importlib.util.spec_from_file_location("translation_keys", str(keys_path))
        translation_keys = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(translation_keys)
        
        print("  ✓ Created valid binary")
        
        # Test valid file
        print("\n[2/3] Validating correct binary...")
        success, error = lang_compiler.validate_binary_file(binary_path, translation_keys)
        if success:
            print("  ✓ Valid binary accepted")
        else:
            print(f"  ✗ Valid binary rejected: {error}")
            return False
        
        # Test invalid files
        print("\n[3/3] Testing invalid binary detection...")
        all_caught = True
        
        # Wrong magic
        bad_magic_path = temp_dir / "bad_magic.bin"
        with open(bad_magic_path, 'wb') as f:
            f.write(b'BAAD')  # Wrong magic
            f.write(struct.pack('<I', 1))  # version
            f.write(struct.pack('<I', 5))  # key_count
        
        success, error = lang_compiler.validate_binary_file(str(bad_magic_path))
        if not success and "Invalid magic" in error:
            print(f"  ✓ bad_magic: Correctly rejected")
        else:
            print(f"  ✗ bad_magic: Should reject, got success={success}")
            all_caught = False
        
        # Wrong key count
        bad_count_path = temp_dir / "bad_count.bin"
        with open(bad_count_path, 'wb') as f:
            f.write(b'LANG')
            f.write(struct.pack('<I', 1))     # version
            f.write(struct.pack('<I', 999))   # wrong key_count
        
        success, error = lang_compiler.validate_binary_file(
            str(bad_count_path), translation_keys
        )
        if not success and "mismatch" in error:
            print(f"  ✓ bad_key_count: Correctly rejected")
        else:
            print(f"  ✗ bad_key_count: Should reject, got success={success}")
            all_caught = False
        
        if all_caught:
            print("\n✓ TEST 4 PASSED: Validation correctly identifies issues")
            return True
        else:
            print("\n✗ TEST 4 FAILED: Some validation checks failed")
            return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("LANG_COMPILER ROUND-TRIP TEST SUITE")
    print("="*70)
    
    results = {
        "English Round-Trip": test_english_roundtrip(),
        "Missing Translations": test_missing_translations(),
        "Bounds Checking": test_bounds_checking(),
        "Validation": test_validation(),
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
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(main())
