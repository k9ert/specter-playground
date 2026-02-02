#!/usr/bin/env python3
"""
Language Compiler for Specter UI i18n System

Converts JSON language files to efficient binary format for flash storage.
Generates translation key mappings for runtime lookups.
"""

import json
import struct
import os
from pathlib import Path


# File Format Constants
BINARY_FILE_PREFIX = "lang_"
BINARY_FILE_SUFFIX = ".bin"
JSON_FILE_PREFIX = "specter_ui_"
JSON_FILE_SUFFIX = ".json"



def read_string_at_offset(file_handle, offset):
    """
    Read a null-terminated UTF-8 string from binary file at given offset.
    
    Args:
        file_handle: Open file handle in binary read mode
        offset: Byte offset to start reading from
        
    Returns:
        str: Decoded string or empty string if error
    """
    try:
        file_handle.seek(offset)
        string_data = bytearray()
        while True:
            byte = file_handle.read(1)
            if not byte or byte == b'\x00':
                break
            string_data.extend(byte)
        return string_data.decode('utf-8')
    except Exception as e:
        print(f"Warning: Could not read string at offset {offset}: {e}")
        return ""


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
    filename_only = Path(filename).name
    
    # Check JSON format: specter_ui_XX.json
    if filename_only.startswith(JSON_FILE_PREFIX) and filename_only.endswith(JSON_FILE_SUFFIX):
        # Extract XX from specter_ui_XX.json
        lang_code = filename_only[len(JSON_FILE_PREFIX):-len(JSON_FILE_SUFFIX)]
        expected_format = f"{JSON_FILE_PREFIX}XX{JSON_FILE_SUFFIX} (where XX is 2-letter language code)"
    
    # Check binary format: lang_XX.bin
    elif filename_only.startswith(BINARY_FILE_PREFIX) and filename_only.endswith(BINARY_FILE_SUFFIX):
        # Extract XX from lang_XX.bin
        lang_code = filename_only[len(BINARY_FILE_PREFIX):-len(BINARY_FILE_SUFFIX)]
        expected_format = f"{BINARY_FILE_PREFIX}XX{BINARY_FILE_SUFFIX} (where XX is 2-letter language code)"
    
    else:
        # Unknown format - print error message here
        print(f"Error: Input file '{filename}' does not follow naming conventions.")
        print("Expected formats:")
        print(f"  - {JSON_FILE_PREFIX}XX{JSON_FILE_SUFFIX} (where XX is 2-letter language code)")
        print(f"  - {BINARY_FILE_PREFIX}XX{BINARY_FILE_SUFFIX} (where XX is 2-letter language code)")
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


def generate_translation_keys(default_lang_json_path, output_path=None):
    """
    Generate translation_keys.py from default language JSON file.
    
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
    
    # Determine output path
    if output_path is None:
        output_path = Path(default_lang_json_path).parent / "translation_keys.py"
    
    # Write translation_keys.py
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('"""Auto-generated translation key mappings."""\n\n')
        f.write(f'# Generated from {Path(default_lang_json_path).name}\n')
        f.write(f'# Total keys: {len(keys)}\n\n')
        f.write('KEY_TO_INDEX = {\n')
        for key, index in key_to_index.items():
            f.write(f'    "{key}": {index},\n')
        f.write('}\n')
    
    print(f"Generated {output_path} with {len(keys)} keys")
    return key_to_index


def json_to_binary(json_path, key_to_index, output_path=None):
    """
    Convert JSON language file to binary format.
    
    Binary Format:
    [Header: 12 bytes]
    - magic: 4 bytes "LANG"
    - version: 4 bytes (uint32)  
    - key_count: 4 bytes (uint32)
    
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
    
    # Determine output path
    if output_path is None:
        json_file = Path(json_path)
        output_path = json_file.parent / f"{BINARY_FILE_PREFIX}{lang_code}{BINARY_FILE_SUFFIX}"
    
    # Extract translations - handle both formats
    translations = data.get('translations', {})
    
    if not translations:
        print(f"Error: No translations found in '{json_path}'")
        print("Please ensure the file has a 'translations' section with content")
        return None
    
    # Prepare index and string data - process in key_to_index order for easier debugging
    key_count = len(key_to_index)
    
    # Calculate binary format layout
    magic_size = 4      # "LANG" signature
    version_size = 4    # uint32 version
    key_count_size = 4  # uint32 key count
    header_size = magic_size + version_size + key_count_size  # = 12 bytes
    index_size = key_count * 4  # Each offset is uint32
    strings_start_offset = header_size + index_size  # Where string data begins
    
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
            
            # Index
            for offset in index_data:
                f.write(struct.pack('<I', offset))
            
            # Strings
            f.write(string_data)
    except Exception as e:
        print(f"Error: Could not write binary file '{output_path}': {e}")
        return None
    
    return str(output_path)


def validate_binary_file(binary_path, key_to_index=None):
    """
    Validate and inspect a binary language file.
    
    Args:
        binary_path: Path to .bin file
        key_to_index: Optional KEY_TO_INDEX for detailed inspection
    """
    with open(binary_path, 'rb') as f:
        # Read header
        magic = f.read(4)
        version, key_count = struct.unpack('<II', f.read(8))
        
        print(f"Binary file: {binary_path}")
        print(f"  Magic: {magic}")
        print(f"  Version: {version}")
        print(f"  Key count: {key_count}")
        
        if magic != b"LANG":
            print("  ERROR: Invalid magic signature")
            return False
        
        # Read index
        index = []
        for i in range(key_count):
            offset = struct.unpack('<I', f.read(4))[0]
            index.append(offset)
        
        # Count translations
        translated = sum(1 for offset in index if offset != 0xFFFFFFFF)
        missing = key_count - translated
        
        print(f"  Translated strings: {translated}")
        print(f"  Missing strings: {missing}")
        
        # If we have key mapping, show some examples
        if key_to_index:
            reverse_index = {v: k for k, v in key_to_index.items()}
            
            print("  Sample translations:")
            sample_count = min(5, len(index))
            for i in range(sample_count):
                key = reverse_index[i]
                offset = index[i]
                if offset != 0xFFFFFFFF:
                    text = read_string_at_offset(f, offset)
                    print(f"    {key}: '{text}'")
                else:
                    print(f"    {key}: <missing>")
    
    return True


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
            # Try to find translation_keys.py in same directory
            keys_path = Path(json_path).parent / "translation_keys.py"
            if keys_path.exists():
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
        
        # Load key mapping if provided
        key_to_index = None
        if len(sys.argv) >= 4:
            keys_file = sys.argv[3]
            import importlib.util
            spec = importlib.util.spec_from_file_location("keys", keys_file)
            keys_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(keys_module)
            key_to_index = keys_module.KEY_TO_INDEX
        
        validate_binary_file(binary_path, key_to_index)
    
    else:
        print(f"Error: Unknown command '{command}'")


if __name__ == "__main__":
    main()