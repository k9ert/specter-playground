"""Unit tests for lang_compiler.py — binary format engine."""
import importlib.util
import json
import struct
from pathlib import Path

import pytest

import MockUI.i18n.lang_compiler as lc
from MockUI.i18n.lang_compiler import (
    BINARY_FILE_PREFIX,
    BINARY_FILE_SUFFIX,
    HEADER_SIZE,
    KEY_COUNT_SIZE,
    LANG_NAME_FIELD_SIZE,
    MAGIC_SIZE,
    OFFSET_SIZE,
    VERSION_SIZE,
    extract_language_code_from_filename,
    extract_language_name_from_file,
    generate_translation_keys,
    get_binary_filename,
    get_json_filename,
    json_to_binary,
    read_translation_from_binary,
    validate_binary_file,
)


# =====================================================================
# TestExtractLanguageCode
# =====================================================================
class TestExtractLanguageCode:
    """extract_language_code_from_filename()"""

    def test_valid_json_filename(self):
        assert extract_language_code_from_filename("specter_ui_en.json") == "en"

    def test_valid_binary_filename(self):
        assert extract_language_code_from_filename("lang_de.bin") == "de"

    def test_valid_json_full_path(self):
        assert extract_language_code_from_filename("/some/dir/specter_ui_fr.json") == "fr"

    def test_valid_binary_full_path(self):
        assert extract_language_code_from_filename("/flash/i18n/lang_es.bin") == "es"

    def test_uppercase_normalised(self):
        """FAT returns uppercase; caller lowercases before passing."""
        assert extract_language_code_from_filename("lang_en.bin") == "en"

    def test_unrecognised_format_returns_none(self):
        assert extract_language_code_from_filename("random_file.txt") is None

    def test_invalid_three_letter_code(self):
        assert extract_language_code_from_filename("specter_ui_eng.json") is None

    def test_invalid_numeric_code(self):
        assert extract_language_code_from_filename("lang_12.bin") is None

    def test_empty_code(self):
        assert extract_language_code_from_filename("lang_.bin") is None

    def test_single_letter_code(self):
        assert extract_language_code_from_filename("specter_ui_e.json") is None


# =====================================================================
# TestExtractLanguageName
# =====================================================================
class TestExtractLanguageName:
    """extract_language_name_from_file()"""

    def test_reads_english_name(self, en_binary_path):
        assert extract_language_name_from_file(str(en_binary_path)) == "English"

    def test_reads_german_name(self, de_binary_path):
        assert extract_language_name_from_file(str(de_binary_path)) == "Deutsch"

    def test_rejects_non_binary_filename(self, tmp_path):
        """Filename must follow lang_XX.bin convention."""
        bad = tmp_path / "specter_ui_en.json"
        bad.write_text("{}")
        assert extract_language_name_from_file(str(bad)) is None

    def test_returns_none_on_missing_null_terminator(self, tmp_path):
        """Corrupt file: name field filled with non-null bytes."""
        corrupt = tmp_path / "lang_xx.bin"
        with open(corrupt, "wb") as f:
            f.write(b"LANG")
            f.write(struct.pack("<I", 1))
            f.write(struct.pack("<I", 0))
            f.write(b"A" * LANG_NAME_FIELD_SIZE)  # No null terminator
        assert extract_language_name_from_file(str(corrupt)) is None

    def test_returns_none_on_invalid_utf8(self, tmp_path):
        corrupt = tmp_path / "lang_xx.bin"
        with open(corrupt, "wb") as f:
            f.write(b"LANG")
            f.write(struct.pack("<I", 1))
            f.write(struct.pack("<I", 0))
            f.write(b"\xff\xfe" + b"\x00" * (LANG_NAME_FIELD_SIZE - 2))
        assert extract_language_name_from_file(str(corrupt)) is None

    def test_returns_none_on_file_too_small(self, tmp_path):
        tiny = tmp_path / "lang_xx.bin"
        tiny.write_bytes(b"LAN")  # Only 3 bytes
        assert extract_language_name_from_file(str(tiny)) is None

    def test_returns_none_on_nonexistent_file(self):
        assert extract_language_name_from_file("/nonexistent/lang_xx.bin") is None


# =====================================================================
# TestGenerateTranslationKeys
# =====================================================================
class TestGenerateTranslationKeys:
    """generate_translation_keys()"""

    def test_generates_key_to_index(self, en_json_path):
        kti = generate_translation_keys(str(en_json_path))
        assert isinstance(kti, dict)
        assert len(kti) > 0

    def test_keys_are_sorted_sequential(self, en_json_path):
        kti = generate_translation_keys(str(en_json_path))
        keys_sorted = sorted(kti.keys())
        for i, key in enumerate(keys_sorted):
            assert kti[key] == i, f"Key '{key}' should have index {i}, got {kti[key]}"

    def test_output_file_importable(self, en_json_path, tmp_path):
        out = str(tmp_path / "translation_keys.py")
        generate_translation_keys(str(en_json_path), output_path=out)
        spec = importlib.util.spec_from_file_location("tk", out)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert hasattr(mod, "Keys")
        assert hasattr(mod, "KEY_TO_INDEX")
        assert hasattr(mod, "KEY_COUNT")
        assert mod.KEY_COUNT == len(mod.KEY_TO_INDEX)

    def test_keys_class_has_integer_attrs(self, en_json_path, tmp_path):
        out = str(tmp_path / "translation_keys.py")
        kti = generate_translation_keys(str(en_json_path), output_path=out)
        spec = importlib.util.spec_from_file_location("tk", out)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        for key, idx in kti.items():
            assert getattr(mod.Keys, key) == idx


# =====================================================================
# TestJsonToBinary
# =====================================================================
class TestJsonToBinary:
    """json_to_binary()"""

    def test_english_roundtrip(self, en_json_path, key_to_index, tmp_path, en_json_data):
        """Compile EN, read back every key, verify matches JSON."""
        out = str(tmp_path / "lang_en.bin")
        result = json_to_binary(str(en_json_path), key_to_index, out)
        assert result is not None
        translations = en_json_data["translations"]
        for key, idx in key_to_index.items():
            text, error = read_translation_from_binary(out, idx)
            assert text == translations[key], f"Mismatch for '{key}'"
            assert error is None

    def test_german_object_format(self, de_json_path, key_to_index, tmp_path, de_json_data):
        """German uses {text, ref_en} — only 'text' should be stored."""
        out = str(tmp_path / "lang_de.bin")
        result = json_to_binary(str(de_json_path), key_to_index, out)
        assert result is not None
        translations = de_json_data["translations"]
        for key, idx in key_to_index.items():
            text, error = read_translation_from_binary(out, idx)
            if key in translations:
                expected = translations[key]
                if isinstance(expected, dict):
                    expected = expected["text"]
                assert text == expected, f"Mismatch for '{key}'"

    def test_missing_translations_become_sentinel(self, tmp_path, key_to_index):
        """Keys not present in JSON -> 0xFFFFFFFF in binary."""
        partial = {
            "_metadata": {"language_code": "xx", "language_name": "Test"},
            "translations": {"MAIN_MENU_TITLE": "Only one key"},
        }
        json_path = tmp_path / "specter_ui_xx.json"
        with open(json_path, "w") as f:
            json.dump(partial, f)
        out = str(tmp_path / "lang_xx.bin")
        result = json_to_binary(str(json_path), key_to_index, out)
        assert result is not None
        idx = key_to_index["MAIN_MENU_TITLE"]
        text, error = read_translation_from_binary(out, idx)
        assert text == "Only one key"
        other_key = [k for k in key_to_index if k != "MAIN_MENU_TITLE"][0]
        text, error = read_translation_from_binary(out, key_to_index[other_key])
        assert text is None
        assert error == "missing"

    def test_missing_language_code_in_metadata(self, tmp_path, key_to_index):
        data = {"_metadata": {"language_name": "Test"}, "translations": {"A": "a"}}
        p = tmp_path / "specter_ui_xx.json"
        with open(p, "w") as f:
            json.dump(data, f)
        assert json_to_binary(str(p), key_to_index) is None

    def test_language_code_mismatch(self, tmp_path, key_to_index):
        """Filename says 'xx' but metadata says 'yy'."""
        data = {
            "_metadata": {"language_code": "yy", "language_name": "Test"},
            "translations": {"A": "a"},
        }
        p = tmp_path / "specter_ui_xx.json"
        with open(p, "w") as f:
            json.dump(data, f)
        assert json_to_binary(str(p), key_to_index) is None

    def test_invalid_filename_format(self, tmp_path, key_to_index):
        p = tmp_path / "bad_name.json"
        with open(p, "w") as f:
            json.dump({"_metadata": {"language_code": "en"}, "translations": {"A": "a"}}, f)
        assert json_to_binary(str(p), key_to_index) is None

    def test_language_name_in_header(self, en_binary_path):
        """The 32-byte name field contains the language name."""
        with open(en_binary_path, "rb") as f:
            f.seek(MAGIC_SIZE + VERSION_SIZE + KEY_COUNT_SIZE)
            raw = f.read(LANG_NAME_FIELD_SIZE)
        null_pos = raw.find(b"\x00")
        assert null_pos > 0
        assert raw[:null_pos].decode("utf-8") == "English"

    def test_extra_keys_warning(self, tmp_path, key_to_index, capsys):
        """Keys in JSON not in mapping trigger a warning."""
        data = {
            "_metadata": {"language_code": "xx", "language_name": "Test"},
            "translations": {
                "MAIN_MENU_TITLE": "exists",
                "THIS_KEY_DOES_NOT_EXIST": "extra",
            },
        }
        p = tmp_path / "specter_ui_xx.json"
        with open(p, "w") as f:
            json.dump(data, f)
        out = str(tmp_path / "lang_xx.bin")
        result = json_to_binary(str(p), key_to_index, out)
        assert result is not None
        captured = capsys.readouterr()
        assert "THIS_KEY_DOES_NOT_EXIST" in captured.out

    def test_empty_translations_rejected(self, tmp_path, key_to_index):
        data = {
            "_metadata": {"language_code": "xx", "language_name": "Test"},
            "translations": {},
        }
        p = tmp_path / "specter_ui_xx.json"
        with open(p, "w") as f:
            json.dump(data, f)
        assert json_to_binary(str(p), key_to_index) is None


# =====================================================================
# TestReadTranslationFromBinary
# =====================================================================
class TestReadTranslationFromBinary:
    """read_translation_from_binary()"""

    def test_read_valid_key(self, en_binary_path, key_to_index, en_json_data):
        idx = key_to_index["MAIN_MENU_TITLE"]
        text, error = read_translation_from_binary(str(en_binary_path), idx)
        assert text == en_json_data["translations"]["MAIN_MENU_TITLE"]
        assert error is None

    def test_missing_returns_missing(self, tmp_path, key_to_index):
        """Binary with only one key — other indices return 'missing'."""
        data = {
            "_metadata": {"language_code": "xx", "language_name": "Test"},
            "translations": {"MAIN_MENU_TITLE": "hello"},
        }
        p = tmp_path / "specter_ui_xx.json"
        with open(p, "w") as f:
            json.dump(data, f)
        out = str(tmp_path / "lang_xx.bin")
        json_to_binary(str(p), key_to_index, out)
        other = [k for k in key_to_index if k != "MAIN_MENU_TITLE"][0]
        text, error = read_translation_from_binary(out, key_to_index[other])
        assert text is None
        assert error == "missing"

    def test_out_of_range_high(self, en_binary_path):
        text, error = read_translation_from_binary(str(en_binary_path), 9999)
        assert text is None
        assert error == "invalid_key_index"

    def test_out_of_range_negative(self, en_binary_path):
        text, error = read_translation_from_binary(str(en_binary_path), -1)
        assert text is None
        assert error == "invalid_key_index"

    def test_nonexistent_file(self):
        text, error = read_translation_from_binary("/nonexistent/file.bin", 0)
        assert text is None
        assert error == "read_error"

    def test_corrupt_truncated_file(self, tmp_path):
        corrupt = tmp_path / "lang_xx.bin"
        corrupt.write_bytes(b"LANG")  # Header incomplete
        text, error = read_translation_from_binary(str(corrupt), 0)
        assert text is None
        assert error == "read_error"

    def test_utf8_decode_error(self, tmp_path, key_to_index):
        """Hand-craft a binary with invalid UTF-8 in the string data."""
        key_count = len(key_to_index)
        index_size = key_count * OFFSET_SIZE
        strings_offset = HEADER_SIZE + index_size

        offsets = [0xFFFFFFFF] * key_count
        offsets[0] = strings_offset
        bad_string = b"\xc0\xaf\x00"  # Invalid UTF-8 + null terminator

        binary = tmp_path / "lang_xx.bin"
        with open(binary, "wb") as f:
            f.write(b"LANG")
            f.write(struct.pack("<I", 1))
            f.write(struct.pack("<I", key_count))
            f.write(b"Bad\x00" + b"\x00" * (LANG_NAME_FIELD_SIZE - 4))
            for o in offsets:
                f.write(struct.pack("<I", o))
            f.write(bad_string)

        text, error = read_translation_from_binary(str(binary), 0)
        assert text is None
        assert error == "utf8_decode_error"

    def test_very_long_string_reads_without_hang(self, tmp_path, key_to_index):
        """A valid binary with a very long (64 KB) string is read completely."""
        key_count = len(key_to_index)
        index_size = key_count * OFFSET_SIZE
        strings_offset = HEADER_SIZE + index_size

        long_text = "A" * 65536  # 64 KB string
        offsets = [0xFFFFFFFF] * key_count
        offsets[0] = strings_offset

        binary = tmp_path / "lang_xx.bin"
        with open(binary, "wb") as f:
            f.write(b"LANG")
            f.write(struct.pack("<I", 1))
            f.write(struct.pack("<I", key_count))
            f.write(b"Big\x00" + b"\x00" * (LANG_NAME_FIELD_SIZE - 4))
            for o in offsets:
                f.write(struct.pack("<I", o))
            f.write(long_text.encode("utf-8") + b"\x00")

        text, error = read_translation_from_binary(str(binary), 0)
        assert error is None
        assert text == long_text
        assert len(text) == 65536

    def test_file_handle_closed_after_successful_read(self, en_binary_path, key_to_index):
        """File handle is released after read (uses context manager)."""
        import gc
        idx = key_to_index["MAIN_MENU_TITLE"]
        # Read many times — if handles leaked, OS would eventually refuse
        for _ in range(200):
            text, error = read_translation_from_binary(str(en_binary_path), idx)
            assert text is not None
        gc.collect()
        # If we get here without OSError, handles are cleaned up

    def test_file_handle_closed_after_error(self, tmp_path):
        """File handle is released even when read fails."""
        import gc
        corrupt = tmp_path / "lang_xx.bin"
        corrupt.write_bytes(b"LANG\x01\x00\x00\x00")  # Truncated header
        for _ in range(200):
            text, error = read_translation_from_binary(str(corrupt), 0)
            assert error == "read_error"
        gc.collect()


# =====================================================================
# TestValidateBinaryFile
# =====================================================================
class TestValidateBinaryFile:
    """validate_binary_file()"""

    def test_valid_english(self, en_binary_path):
        success, error = validate_binary_file(str(en_binary_path))
        assert success is True
        assert error is None

    def test_valid_german(self, de_binary_path):
        success, error = validate_binary_file(str(de_binary_path))
        assert success is True

    def test_with_translation_keys_module(self, en_binary_path):
        """Pass the real translation_keys module for key-count checking."""
        from MockUI.i18n import translation_keys as tk_mod
        success, error = validate_binary_file(str(en_binary_path), tk_mod)
        assert success is True

    def test_wrong_magic(self, tmp_path):
        bad = tmp_path / "lang_xx.bin"
        with open(bad, "wb") as f:
            f.write(b"BAAD")
            f.write(struct.pack("<I", 1))
            f.write(struct.pack("<I", 5))
            f.write(b"\x00" * LANG_NAME_FIELD_SIZE)
        success, error = validate_binary_file(str(bad))
        assert success is False
        assert "Invalid magic" in error

    def test_key_count_mismatch(self, tmp_path):
        bad = tmp_path / "lang_xx.bin"
        with open(bad, "wb") as f:
            f.write(b"LANG")
            f.write(struct.pack("<I", 1))
            f.write(struct.pack("<I", 999))
            f.write(b"Test\x00" + b"\x00" * (LANG_NAME_FIELD_SIZE - 5))
        from MockUI.i18n import translation_keys as tk_mod
        success, error = validate_binary_file(str(bad), tk_mod)
        assert success is False
        assert "mismatch" in error

    def test_file_too_small(self, tmp_path):
        tiny = tmp_path / "lang_xx.bin"
        tiny.write_bytes(b"LANG\x01\x00\x00\x00")  # Only 8 bytes
        success, error = validate_binary_file(str(tiny))
        assert success is False
        assert "too small" in error

    def test_invalid_offset_past_eof(self, tmp_path, key_to_index):
        """Index entry pointing beyond file size."""
        key_count = len(key_to_index)
        bad = tmp_path / "lang_xx.bin"
        with open(bad, "wb") as f:
            f.write(b"LANG")
            f.write(struct.pack("<I", 1))
            f.write(struct.pack("<I", key_count))
            f.write(b"Bad\x00" + b"\x00" * (LANG_NAME_FIELD_SIZE - 4))
            f.write(struct.pack("<I", 0xFFFFFFFE))  # Past EOF
            for _ in range(key_count - 1):
                f.write(struct.pack("<I", 0xFFFFFFFF))
        success, error = validate_binary_file(str(bad))
        assert success is False
        assert "Invalid offsets" in error

    def test_file_not_found(self):
        success, error = validate_binary_file("/nonexistent/lang_xx.bin")
        assert success is False
        assert "not found" in error.lower() or "File not found" in error

    def test_missing_null_terminator_in_name(self, tmp_path):
        bad = tmp_path / "lang_xx.bin"
        with open(bad, "wb") as f:
            f.write(b"LANG")
            f.write(struct.pack("<I", 1))
            f.write(struct.pack("<I", 0))
            f.write(b"A" * LANG_NAME_FIELD_SIZE)  # No null
        success, error = validate_binary_file(str(bad))
        assert success is False
        assert "null terminator" in error.lower()

    def test_unterminated_string(self, tmp_path, key_to_index):
        """String data without a null terminator at the end."""
        key_count = len(key_to_index)
        index_size = key_count * OFFSET_SIZE
        strings_offset = HEADER_SIZE + index_size

        bad = tmp_path / "lang_xx.bin"
        with open(bad, "wb") as f:
            f.write(b"LANG")
            f.write(struct.pack("<I", 1))
            f.write(struct.pack("<I", key_count))
            f.write(b"Bad\x00" + b"\x00" * (LANG_NAME_FIELD_SIZE - 4))
            f.write(struct.pack("<I", strings_offset))
            for _ in range(key_count - 1):
                f.write(struct.pack("<I", 0xFFFFFFFF))
            f.write(b"hello")  # No \x00

        success, error = validate_binary_file(str(bad))
        assert success is False
        assert "null terminator" in error.lower() or "EOF" in error


# =====================================================================
# TestHelperFunctions
# =====================================================================
class TestHelperFunctions:
    """get_json_filename / get_binary_filename and constants."""

    def test_get_json_filename(self):
        assert get_json_filename("en") == "specter_ui_en.json"
        assert get_json_filename("de") == "specter_ui_de.json"

    def test_get_binary_filename(self):
        assert get_binary_filename("en") == "lang_en.bin"
        assert get_binary_filename("fr") == "lang_fr.bin"

    def test_header_size_is_44(self):
        assert HEADER_SIZE == 44
