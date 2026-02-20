#!/usr/bin/env python3
"""
Language Compiler for Specter UI i18n System

Converts JSON language files to efficient binary format for flash storage.
Generates translation key mappings for runtime lookups.
"""

import json
import struct
import os


# File Format Constants
BINARY_FILE_PREFIX = "lang_"
BINARY_FILE_SUFFIX = ".bin"
JSON_FILE_PREFIX = "specter_ui_"
JSON_FILE_SUFFIX = ".json"

# Binary Format Size Constants (in bytes)
MAGIC_SIZE = 4        # "LANG" signature
VERSION_SIZE = 4      # uint32 version number
KEY_COUNT_SIZE = 4    # uint32 key count
LANG_NAME_FIELD_SIZE = 32  # fixed-width language name field (null-padded UTF-8, max 31 usable bytes)
HEADER_SIZE = MAGIC_SIZE + VERSION_SIZE + KEY_COUNT_SIZE + LANG_NAME_FIELD_SIZE  # = 44 bytes
OFFSET_SIZE = 4       # uint32 offset in index


# --- Path helpers (os.path not available in MicroPython) ---

def _path_basename(path):
    """Return the final component of a path (replacement for os.path.basename)."""
    return path.rsplit('/', 1)[-1]


def _path_dirname(path):
    """Return the directory component of a path (replacement for os.path.dirname)."""
    return path.rsplit('/', 1)[0] if '/' in path else '.'


def get_json_filename(lang_code):
    """
    Construct JSON language filename from language code.
    
    Args:
        lang_code: ISO 639-1 language code (e.g., 'en', 'de')
    
    Returns:
        str: Filename like 'specter_ui_en.json'
    """
    return f"{JSON_FILE_PREFIX}{lang_code}{JSON_FILE_SUFFIX}"


def get_binary_filename(lang_code):
    """
    Construct binary language filename from language code.
    
    Args:
        lang_code: ISO 639-1 language code (e.g., 'en', 'de')
    
    Returns:
        str: Filename like 'lang_en.bin'
    """
    return f"{BINARY_FILE_PREFIX}{lang_code}{BINARY_FILE_SUFFIX}"



def read_translation_from_binary(file_path, key_index):
    """
    Read translation string from binary file.
    
    This function assumes the binary file has already been validated
    (via validate_binary_file) during import/load. It performs minimal
    checks for performance - use validate_binary_file() before first use.
    
    Args:
        file_path: Path to binary language file (must be pre-validated)
        key_index: Integer index of the translation key (0-based)
    
    Returns:
        Tuple of (text: str|None, error: str|None):
        - ("translated text", None) - Success, use the text
        - (None, "missing") - Translation not present (0xFFFFFFFF marker)
        - (None, "invalid_key_index") - key_index out of bounds (>= key_count)
        - (None, "read_error") - I/O error during read
        - (None, "utf8_decode_error") - Invalid UTF-8 sequence
        
    Usage:
        text, error = read_translation_from_binary(path, index)
        if text is not None:
            # Use the text
        else:
            # Handle error (check error code)
    
    Note: File must be validated with validate_binary_file() before use.
    """
    try:
        with open(file_path, 'rb') as f:
            # Read header to get key_count
            f.seek(MAGIC_SIZE + VERSION_SIZE)
            key_count = struct.unpack('<I', f.read(KEY_COUNT_SIZE))[0]
            
            # Validate key_index is in bounds (reject negative indices too)
            if key_index < 0 or key_index >= key_count:
                return (None, "invalid_key_index")
            
            # Seek to index entry for this key
            index_offset = HEADER_SIZE + (key_index * OFFSET_SIZE)
            f.seek(index_offset)
            string_offset = struct.unpack('<I', f.read(OFFSET_SIZE))[0]
            
            # Check for missing translation sentinel
            if string_offset == 0xFFFFFFFF:
                return (None, "missing")
            
            # Seek to string and read until null terminator
            f.seek(string_offset)
            result = bytearray()
            
            while True:
                byte = f.read(1)
                if not byte or byte == b'\x00':
                    break
                result.extend(byte)
            
            # Decode UTF-8
            try:
                text = result.decode('utf-8')
                return (text, None)
            except UnicodeDecodeError:
                return (None, "utf8_decode_error")
                
    except Exception:
        return (None, "read_error")


def extract_language_code_from_filename(filename):
    """
    Extract language code from filename following project naming conventions.
    
    Supported formats:
    - specter_ui_XX.json (where XX is 2-letter language code)
    - lang_XX.bin (where XX is 2-letter language code)
    
    Args:
        filename: String filename (can be full path or just filename)
        
    Returns:
        str: 2-letter language code (lowercase) or None if invalid format
    """
    # Extract just the filename from path
    filename_only = _path_basename(filename)
    
    # Check JSON format: specter_ui_XX.json
    if filename_only.startswith(JSON_FILE_PREFIX) and filename_only.endswith(JSON_FILE_SUFFIX):
        # Extract XX from specter_ui_XX.json
        lang_code = filename_only[len(JSON_FILE_PREFIX):-len(JSON_FILE_SUFFIX)]
        expected_format = get_json_filename("XX") + " (where XX is 2-letter language code)"
    
    # Check binary format: lang_XX.bin
    elif filename_only.startswith(BINARY_FILE_PREFIX) and filename_only.endswith(BINARY_FILE_SUFFIX):
        # Extract XX from lang_XX.bin
        lang_code = filename_only[len(BINARY_FILE_PREFIX):-len(BINARY_FILE_SUFFIX)]
        expected_format = get_binary_filename("XX") + " (where XX is 2-letter language code)"
    
    else:
        # Unknown format - print error message here
        print(f"Error: Input file '{filename}' does not follow naming conventions.")
        print("Expected formats:")
        print(f"  - {get_json_filename('XX')} (where XX is 2-letter language code)")
        print(f"  - {get_binary_filename('XX')} (where XX is 2-letter language code)")
        return None
    
    # Validate language code: must be exactly 2 alphabetic characters
    if len(lang_code) == 2 and lang_code.isalpha():
        return lang_code.lower()
    else:
        # Invalid language code - print error message here
        print(f"Error: Invalid language code '{lang_code}' in filename '{filename}'.")
        print(f"Expected format: {expected_format}")
        print("Language code must be exactly 2 alphabetic characters (e.g., 'en', 'de', 'fr')")
        return None


def extract_language_name_from_file(filename):
    """
    Extract the language name from a binary language file.
    
    Opens the file and reads the language name from the fixed-width header field.
    
    Args:
        filename: Path to binary language file (e.g. 'lang_en.bin' or full path)
    
    Returns:
        str: Language name (e.g. 'English', 'Deutsch') or None on error
    """
    # Validate filename follows binary naming convention: lang_XX.bin
    filename_only = _path_basename(filename)
    if not (filename_only.startswith(BINARY_FILE_PREFIX) and filename_only.endswith(BINARY_FILE_SUFFIX)):
        print(f"Error: Input file '{filename}' does not follow binary naming convention.")
        print(f"Expected format: {get_binary_filename('XX')} (where XX is 2-letter language code)")
        return None

    try:
        with open(filename, 'rb') as f:
            # Seek past magic + version + key_count to the language name field
            name_offset = MAGIC_SIZE + VERSION_SIZE + KEY_COUNT_SIZE
            f.seek(name_offset)
            name_raw = f.read(LANG_NAME_FIELD_SIZE)
            
            if len(name_raw) < LANG_NAME_FIELD_SIZE:
                print(f"Error: File '{filename}' too small to contain language name field")
                return None
            
            # Strip null padding — no null terminator means the field is corrupt
            null_pos = name_raw.find(b'\x00')
            if null_pos < 0:
                print(f"Error: Language name field in '{filename}' has no null terminator (corrupt file)")
                return None
            name_bytes = name_raw[:null_pos]
            
            try:
                return name_bytes.decode('utf-8')
            except UnicodeDecodeError:
                print(f"Error: Invalid UTF-8 in language name field of '{filename}'")
                return None
    except OSError as e:
        print(f"Error: Could not open file '{filename}': {e}")
        return None
    except Exception as e:
        print(f"Error: Could not read language name from '{filename}': {e}")
        return None


def generate_translation_keys(default_lang_json_path, output_path=None):
    """
    Generate translation_keys.py from default language JSON file.
    
    Creates both Keys class (with integer constants for RAM efficiency)
    and KEY_TO_INDEX dictionary (for backward compatibility).
    
    Args:
        default_lang_json_path: Path to specter_ui_en.json
        output_path: Where to write translation_keys.py (default: same dir)
    
    Returns:
        dict: KEY_TO_INDEX mapping
    """
    with open(default_lang_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract and sort keys for consistent ordering
    keys = sorted(data["translations"].keys())
    
    # Generate mapping
    key_to_index = {key: i for i, key in enumerate(keys)}
    
    # Determine output path — always write to CWD (not the JSON subdirectory)
    if output_path is None:
        output_path = os.path.join('.', "translation_keys.py")
    
    # Write translation_keys.py with both Keys class and dictionary
    with open(output_path, 'w', encoding='utf-8') as f:
        # Header
        f.write('"""Auto-generated translation key mappings - DO NOT EDIT MANUALLY"""\n')
        f.write(f'# Generated from: {os.path.basename(default_lang_json_path)}\n')
        f.write(f'# Key count: {len(keys)}\n')
        f.write('# Auto-generated by lang_compiler.py\n\n')
        
        # Keys class with integer constants (RAM efficient)
        f.write('class Keys:\n')
        f.write('    """Integer constants for translation keys (RAM efficient).\n')
        f.write('    \n')
        f.write('    Usage:\n')
        f.write('        from translation_keys import Keys\n')
        f.write('        text = i18n.t(Keys.MAIN_MENU_TITLE)  # No string allocation\n')
        f.write('    """\n')
        
        for key, index in sorted(key_to_index.items(), key=lambda x: x[1]):
            f.write(f'    {key} = {index}\n')
        
        f.write('\n\n')
        
        # KEY_TO_INDEX dictionary (backward compatibility)
        f.write('# String to index mapping (for convenience/backward compatibility)\n')
        f.write('# When using strings, prefer Keys.CONSTANT for RAM efficiency\n')
        f.write('KEY_TO_INDEX = {\n')
        for key, index in sorted(key_to_index.items(), key=lambda x: x[1]):
            f.write(f'    "{key}": Keys.{key},\n')
        f.write('}\n\n')
        
        # Metadata for validation
        f.write(f'# Metadata\n')
        f.write(f'KEY_COUNT = {len(keys)}\n')
        f.write(f'VERSION = 1\n')
    
    print(f"Generated {output_path}")
    print(f"  Keys class: {len(keys)} constants")
    print(f"  KEY_TO_INDEX: {len(keys)} entries")
    print(f"  Usage: i18n.t(Keys.MAIN_MENU_TITLE) or i18n.t('MAIN_MENU_TITLE')")
    
    return key_to_index


def json_to_binary(json_path, key_to_index, output_path=None):
    """
    Convert JSON language file to binary format.
    
    Binary Format:
    [Header: 44 bytes]
    - magic: 4 bytes "LANG"
    - version: 4 bytes (uint32)  
    - key_count: 4 bytes (uint32)
    - lang_name: 32 bytes (null-padded UTF-8, max 31 usable bytes)
    
    [Index: key_count * 4 bytes]
    - offset[0]: 4 bytes → string offset or 0xFFFFFFFF if missing
    - offset[1]: 4 bytes → string offset or 0xFFFFFFFF if missing
    - ...
    
    [Strings: variable size]
    - null-terminated UTF-8 strings
    
    Args:
        json_path: Input JSON file path
        key_to_index: KEY_TO_INDEX mapping from generate_translation_keys()
        output_path: Output .bin file path (default: auto-generate)
        calc_stats: If True, calculate and print statistics about translations
    Returns:
        str: Path to generated binary file, or None if validation failed
    """
    # Validate input filename format
    filename_lang_code = extract_language_code_from_filename(json_path)
    if filename_lang_code is None:
        return None
    
    # Load JSON
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: Could not read JSON file '{json_path}': {e}")
        return None
    
    # Extract and validate metadata
    metadata = data.get('_metadata', {})
    header_lang_code = metadata.get('language_code')
    
    if not header_lang_code:
        print(f"Error: Missing 'language_code' in _metadata section of '{json_path}'")
        print("Please add: \"language_code\": \"XX\" to the _metadata section")
        return None
    
    # Normalize header language code
    header_lang_code = header_lang_code.lower()
    
    # Check language code consistency
    if filename_lang_code != header_lang_code:
        print(f"Error: Language code mismatch in '{json_path}'")
        print(f"  Filename indicates: '{filename_lang_code}'")
        print(f"  _metadata.language_code: '{header_lang_code}'")
        print("Please ensure filename and metadata language codes match")
        return None
    
    lang_code = filename_lang_code  # Use validated language code
    
    # Determine output path — always write to CWD (not the JSON subdirectory)
    if output_path is None:
        output_path = './' + get_binary_filename(lang_code)
    
    # Extract translations - handle both formats
    translations = data.get('translations', {})
    
    if not translations:
        print(f"Error: No translations found in '{json_path}'")
        print("Please ensure the file has a 'translations' section with content")
        return None
    
    # Prepare index and string data - process in key_to_index order for easier debugging
    key_count = len(key_to_index)
    
    # Calculate binary format layout
    index_size = key_count * OFFSET_SIZE  # Each offset is uint32
    strings_start_offset = HEADER_SIZE + index_size  # Where string data begins
    
    index_data = [0xFFFFFFFF] * key_count  # Initialize with "missing" markers
    string_data = bytearray()
    
    # Create reverse mapping for ordered processing
    index_to_key = {v: k for k, v in key_to_index.items()}
    
    # Process translations in index order (same order as index_data)
    for i in range(key_count):
        key = index_to_key[i]
        
        if key not in translations:
            # Missing translation - index_data[i] stays 0xFFFFFFFF
            print(f"Warning: Missing translation for key '{key}', will fall back to default language")
            continue
            
        translation = translations[key]
        
        # Extract text based on format
        if isinstance(translation, str):
            # Simple string format (default language) [used for default language]
            text = translation
        elif isinstance(translation, dict):
            # Object format with 'text' and 'ref_en' fields [used for other languages]
            text = translation.get('text', '')
        else:
            print(f"Warning: Invalid translation format for key '{key}', will fall back to default language")
            continue
        
        # Store string and update index - both use same index i for alignment
        string_offset = len(string_data)
        string_data.extend(text.encode('utf-8'))
        string_data.append(0)  # null terminator
        
        # Store absolute file offset (already includes header + index offset)
        index_data[i] = strings_start_offset + string_offset
    
    # Second pass: detect extra translations (keys in JSON but not in key mapping)
    # This saves RAM compared to building a processed_keys set
    extra_keys = []
    for key in translations.keys():
        if key not in key_to_index:
            extra_keys.append(key)
    
    if extra_keys:
        print(f"Warning: Found {len(extra_keys)} extra translation(s) not in key mapping:")
        for extra_key in sorted(extra_keys):
            print(f"  - '{extra_key}' (will be ignored)")
        print("These keys may need to be added to the default language file.")
    
    # Write binary file
    try:
        with open(output_path, 'wb') as f:
            # Header
            f.write(b"LANG")  # Magic signature
            f.write(struct.pack('<I', 1))  # Version
            f.write(struct.pack('<I', key_count))  # Key count
            
            # Language name (fixed LANG_NAME_FIELD_SIZE bytes, null-padded)
            lang_name = metadata.get('language_name', '')
            name_bytes = lang_name.encode('utf-8')[:LANG_NAME_FIELD_SIZE - 1]  # Reserve 1 byte for null
            name_field = name_bytes + b'\x00' * (LANG_NAME_FIELD_SIZE - len(name_bytes))
            f.write(name_field)
            
            # Index
            for offset in index_data:
                f.write(struct.pack('<I', offset))
            
            # Strings
            f.write(string_data)
    except Exception as e:
        print(f"Error: Could not write binary file '{output_path}': {e}")
        return None
    
    return str(output_path)


def validate_binary_file(binary_path, translation_keys_module=None):
    """
    Validate and inspect a binary language file with comprehensive checks.
    
    This function performs complete structural validation including:
    - File format (magic bytes, header structure)
    - All index offsets are valid (within file bounds or 0xFFFFFFFF)
    - File size consistency
    - Key count matches (if translation_keys provided)
    - All strings are readable and null-terminated
    
    IMPORTANT: Call this function once when loading/importing a binary language file.
    After validation passes, read_translation_from_binary() can safely be used
    without re-validating on every call.
    
    Args:
        binary_path: Path to .bin file
        translation_keys_module: Optional translation_keys module for validation
                                If provided, verifies key_count matches
    
    Returns:
        Tuple of (success: bool, error_msg: str|None):
        - (True, None) - File is valid and safe to use
        - (False, "error description") - Validation failed, do not use file
    """
    try:
        try:
            os.stat(binary_path)
        except OSError:
            return (False, "File not found")
        
        with open(binary_path, 'rb') as f:
            # Get file size for validation
            f.seek(0, 2)
            file_size = f.tell()
            f.seek(0)
            
            # Check minimum file size (header)
            if file_size < HEADER_SIZE:
                return (False, f"File too small for header (need {HEADER_SIZE} bytes minimum)")
            
            # Read and validate header
            magic = f.read(4)
            if magic != b'LANG':
                return (False, f"Invalid magic bytes: expected b'LANG', got {magic!r}")
            
            version = struct.unpack('<I', f.read(4))[0]
            key_count = struct.unpack('<I', f.read(4))[0]
            
            # Language name field — no null terminator means the field is corrupt
            name_raw = f.read(LANG_NAME_FIELD_SIZE)
            null_pos = name_raw.find(b'\x00')
            if null_pos < 0:
                return (False, "Language name field has no null terminator (corrupt file)")
            name_bytes = name_raw[:null_pos]
            try:
                lang_name = name_bytes.decode('utf-8')
            except UnicodeDecodeError:
                lang_name = '<invalid UTF-8>'
            
            print(f"Binary file: {binary_path}")
            print(f"  Magic: {magic!r}")
            print(f"  Version: {version}")
            print(f"  Key count: {key_count}")
            print(f"  Language name: {lang_name!r}")
            
            # Verify key count matches expected (if translation_keys provided)
            if translation_keys_module is not None:
                if hasattr(translation_keys_module, 'KEY_COUNT'):
                    expected_count = translation_keys_module.KEY_COUNT
                elif hasattr(translation_keys_module, 'KEY_TO_INDEX'):
                    expected_count = len(translation_keys_module.KEY_TO_INDEX)
                else:
                    return (False, "translation_keys module missing KEY_COUNT or KEY_TO_INDEX")
                
                if key_count != expected_count:
                    return (False, f"Key count mismatch: expected {expected_count}, got {key_count}")
            
            # Calculate expected minimum file size
            index_size = key_count * OFFSET_SIZE
            min_size = HEADER_SIZE + index_size
            
            if file_size < min_size:
                return (False, f"File too small: {file_size} bytes < minimum {min_size} bytes")
            
            # Validate all index offsets point to valid locations
            invalid_offsets = []
            all_offsets = []
            for i in range(key_count):
                offset = struct.unpack('<I', f.read(4))[0]
                all_offsets.append(offset)
                if offset != 0xFFFFFFFF and offset >= file_size:
                    invalid_offsets.append((i, offset))
            
            if invalid_offsets:
                errors = "; ".join([f"index {i}: offset {o} >= file_size {file_size}" 
                                   for i, o in invalid_offsets[:5]])
                return (False, f"Invalid offsets found: {errors}")
            
            # Verify all strings are properly null-terminated
            for i, offset in enumerate(all_offsets):
                if offset == 0xFFFFFFFF:
                    continue  # Missing translation, OK
                
                # Try to read the string to ensure it's valid
                try:
                    f.seek(offset)
                    found_terminator = False
                    bytes_read = 0
                    max_read = file_size - offset
                    
                    while bytes_read < max_read:
                        byte = f.read(1)
                        if not byte:
                            return (False, f"String at index {i} (offset {offset}) has unexpected EOF")
                        if byte == b'\x00':
                            found_terminator = True
                            break
                        bytes_read += 1
                    
                    if not found_terminator:
                        return (False, f"String at index {i} (offset {offset}) missing null terminator")
                        
                except Exception as e:
                    return (False, f"Cannot read string at index {i} (offset {offset}): {e}")
            
            # Count translations
            translated = sum(1 for o in all_offsets if o != 0xFFFFFFFF)
            missing = key_count - translated
            
            print(f"  Translated strings: {translated}")
            print(f"  Missing strings: {missing}")
            print(f"  File size: {file_size} bytes")
            
            return (True, None)
            
    except Exception as e:
        return (False, f"Validation error: {e}")


def main():
    """Command line interface for the language compiler."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  lang_compiler.py generate_keys <default_lang.json>")
        print("  lang_compiler.py compile <lang.json> [keys_file.py]")
        print("  lang_compiler.py validate <lang.bin> [keys_file.py]")
        return
    
    command = sys.argv[1]
    
    if command == "generate_keys":
        if len(sys.argv) < 3:
            print("Error: Missing default language JSON file")
            return
        
        json_path = sys.argv[2]
        generate_translation_keys(json_path)
    
    elif command == "compile":
        if len(sys.argv) < 3:
            print("Error: Missing language JSON file")
            return
        
        json_path = sys.argv[2]
        
        # Load or generate key mapping
        if len(sys.argv) >= 4:
            keys_file = sys.argv[3]
            # Import the keys file
            import importlib.util
            spec = importlib.util.spec_from_file_location("keys", keys_file)
            keys_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(keys_module)
            key_to_index = keys_module.KEY_TO_INDEX
        else:
            # Try to find translation_keys.py in CWD first, then fall back to JSON dir
            keys_path = os.path.join('.', "translation_keys.py")
            if not os.path.exists(keys_path):
                json_dir = os.path.dirname(json_path) or '.'
                keys_path = os.path.join(json_dir, "translation_keys.py")
            if os.path.exists(keys_path):
                import importlib.util
                spec = importlib.util.spec_from_file_location("keys", keys_path)
                keys_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(keys_module)
                key_to_index = keys_module.KEY_TO_INDEX
            else:
                print("Error: No key mapping found. Run 'generate_keys' first.")
                return
        
        result = json_to_binary(json_path, key_to_index)
        if result is None:
            print("Compilation failed due to validation errors.")
            sys.exit(1)
    
    elif command == "validate":
        if len(sys.argv) < 3:
            print("Error: Missing binary file")
            return
        
        binary_path = sys.argv[2]
        
        # Load translation_keys module if provided
        translation_keys_module = None
        if len(sys.argv) >= 4:
            keys_file = sys.argv[3]
            import importlib.util
            spec = importlib.util.spec_from_file_location("translation_keys", keys_file)
            translation_keys_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(translation_keys_module)
        else:
            # Try to find translation_keys.py in same directory
            binary_dir = os.path.dirname(binary_path) or '.'
            keys_path = os.path.join(binary_dir, "translation_keys.py")
            if os.path.exists(keys_path):
                import importlib.util
                spec = importlib.util.spec_from_file_location("translation_keys", str(keys_path))
                translation_keys_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(translation_keys_module)
        
        success, error = validate_binary_file(binary_path, translation_keys_module)
        if not success:
            print(f"\nValidation FAILED: {error}")
            sys.exit(1)
        else:
            print("\n✓ Validation passed")
    
    else:
        print(f"Error: Unknown command '{command}'")


if __name__ == "__main__":
    main()