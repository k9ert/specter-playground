#!/usr/bin/env python3
"""
Template for compilers for Specter UI settings files.

Converts JSON settings files to efficient binary format for flash storage.
Generates key mappings for runtime lookups and provides run-time access functions.

Usage: Subclass SettingsFileCompiler and override all abstract methods and class
attributes marked with NotImplementedError / None.
"""

import json
import struct
import os


# Binary Format Size Constants (in bytes) — shared by all compiler subclasses
MAGIC_SIZE = 4        # TYPE signature
VERSION_SIZE = 4      # uint32 version number
KEY_COUNT_SIZE = 4    # uint32 key count
NAME_FIELD_SIZE = 32  # fixed-width name field (null-padded UTF-8, max 31 usable bytes)
HEADER_SIZE = MAGIC_SIZE + VERSION_SIZE + KEY_COUNT_SIZE + NAME_FIELD_SIZE  # = 44 bytes
OFFSET_SIZE = 4       # uint32 offset in index


def read_cstring(f):
    """Read a null-terminated UTF-8 string from *f* at the current position.
    Returns the decoded string (may be empty if the first byte is the null terminator)."""
    result = bytearray()
    while True:
        byte = f.read(1)
        if not byte or byte == b'\x00':
            break
        result.extend(byte)
    return result.decode('utf-8')


def collect_int_constants(cls, recursive=False):
    """Return a {name: value} dict of all public integer attributes of *cls*.
    With *recursive=True*, descends into nested class attributes; keys are
    qualified with the nested class name (e.g. 'TEXT.DEFAULT')."""
    result = {}
    for name in dir(cls):
        if name.startswith('_'):
            continue
        val = getattr(cls, name)
        if isinstance(val, int):
            result[name] = val
        elif recursive and isinstance(val, type):
            for sub_name, sub_val in collect_int_constants(val, recursive=True).items():
                result[name + '.' + sub_name] = sub_val
    return result


class SettingsFileCompiler:
    """
    Base class for settings file compilers.

    Subclasses must:
      - Set class attributes: BINARY_FILE_PREFIX, JSON_FILE_PREFIX, MAGIC_BYTES,
        SETTINGS_NAME_DESC
      - Override abstract methods: validate_settings_name,
        reconstruct_setting_from_binary, convert_setting_to_binary,
        validate_metadata_and_extract_settings_name
      - Optionally override: handle_extra_keys_from_json,
        write_lookup_keys_specific_header
    """

    # --- Class attributes that MUST be overridden in subclasses ---
    BINARY_FILE_PREFIX = None   # e.g. "lang_"
    BINARY_FILE_SUFFIX = ".bin"
    JSON_FILE_PREFIX = None     # e.g. "specter_ui_"
    JSON_FILE_SUFFIX = ".json"
    MAGIC_BYTES = None          # 4-byte file type signature, e.g. b"LANG"
    SETTINGS_NAME_DESC = "a settings name"  # used in error messages
    RECURSIVE_KEYS = False      # set True in subclasses with nested key classes (e.g. SPECTER_STYLES)
    SETTINGS_KEY = None         # top-level key in the JSON data section, e.g. "translations"

    # --- Path/Filename helpers (os.path not available in MicroPython) ---

    @staticmethod
    def _path_basename(path):
        """Return the final component of a path (replacement for os.path.basename)."""
        return path.rsplit('/', 1)[-1]

    @staticmethod
    def _path_dirname(path):
        """Return the directory component of a path (replacement for os.path.dirname)."""
        return path.rsplit('/', 1)[0] if '/' in path else '.'

    def get_json_filename(self, settings_name):
        """Construct JSON settings filename from settings name."""
        if self.JSON_FILE_PREFIX is None:
            raise NotImplementedError("JSON_FILE_PREFIX not defined in subclass")
        return f"{self.JSON_FILE_PREFIX}{settings_name}{self.JSON_FILE_SUFFIX}"

    def get_binary_filename(self, settings_name):
        """Construct binary settings filename from settings name."""
        if self.BINARY_FILE_PREFIX is None:
            raise NotImplementedError("BINARY_FILE_PREFIX not defined in subclass")
        return f"{self.BINARY_FILE_PREFIX}{settings_name}{self.BINARY_FILE_SUFFIX}"

    def extract_settings_name_from_filename(self, filename):
        """
        Extract settings name from filename following project naming conventions.

        Supported formats:
        - JSON_FILE_PREFIX<settings_name>JSON_FILE_SUFFIX
        - BINARY_FILE_PREFIX<settings_name>BINARY_FILE_SUFFIX

        Returns:
            str: settings_name (lowercase) or None if invalid format
        """
        if self.BINARY_FILE_PREFIX is None or self.JSON_FILE_PREFIX is None:
            raise NotImplementedError("BINARY_FILE_PREFIX and JSON_FILE_PREFIX must be defined in subclass")

        filename_only = self._path_basename(filename)

        if filename_only.startswith(self.JSON_FILE_PREFIX) and filename_only.endswith(self.JSON_FILE_SUFFIX):
            settings_name = filename_only[len(self.JSON_FILE_PREFIX):-len(self.JSON_FILE_SUFFIX)]
        elif filename_only.startswith(self.BINARY_FILE_PREFIX) and filename_only.endswith(self.BINARY_FILE_SUFFIX):
            settings_name = filename_only[len(self.BINARY_FILE_PREFIX):-len(self.BINARY_FILE_SUFFIX)]
        else:
            print(f"Error: Input file '{filename}' does not follow naming conventions.")
            print(f"  Expected: {self.get_json_filename('XX')} or {self.get_binary_filename('XX')}"
                  f" (where XX is {self.SETTINGS_NAME_DESC})")
            return None

        if self.validate_settings_name(settings_name):
            return settings_name.lower()
        else:
            print(f"Error: Invalid {self.SETTINGS_NAME_DESC} '{settings_name}' in filename '{filename}'.")
            return None

    def extract_settings_name_from_binary_file(self, filename):
        """
        Extract the settings name from a binary settings file header.

        Returns:
            str: Settings name or None on error
        """
        if self.BINARY_FILE_PREFIX is None:
            raise NotImplementedError("BINARY_FILE_PREFIX must be defined in subclass")

        filename_only = self._path_basename(filename)
        if not (filename_only.startswith(self.BINARY_FILE_PREFIX) and filename_only.endswith(self.BINARY_FILE_SUFFIX)):
            print(f"Error: Input file '{filename}' does not follow binary settings naming convention.")
            print(f"Expected format: {self.get_binary_filename('XX')} (where XX is {self.SETTINGS_NAME_DESC})")
            return None

        try:
            with open(filename, 'rb') as f:
                name_offset = MAGIC_SIZE + VERSION_SIZE + KEY_COUNT_SIZE
                f.seek(name_offset)
                name_raw = f.read(NAME_FIELD_SIZE)

                if len(name_raw) < NAME_FIELD_SIZE:
                    print(f"Error: File '{filename}' too small to contain settings name field")
                    return None

                null_pos = name_raw.find(b'\x00')
                if null_pos < 0:
                    print(f"Error: Settings name field in '{filename}' has no null terminator (corrupt file)")
                    return None

                try:
                    return name_raw[:null_pos].decode('utf-8')
                except UnicodeDecodeError:
                    print(f"Error: Invalid UTF-8 in settings name field of '{filename}'")
                    return None
        except OSError as e:
            print(f"Error: Could not open file '{filename}': {e}")
            return None
        except Exception as e:
            print(f"Error: Could not read settings name from '{filename}': {e}")
            return None

    # --- Abstract methods — subclasses MUST override ---

    def validate_settings_name(self, settings_name):
        """Validate a settings name string. Return True if valid, False otherwise."""
        raise NotImplementedError("Subclass must implement validate_settings_name()")

    def reconstruct_setting_from_binary(self, file_handle):
        """
        Read and return one settings entry from file_handle (already seeked to the entry).
        Must return the decoded value, or raise on error.
        """
        raise NotImplementedError("Subclass must implement reconstruct_setting_from_binary()")

    def convert_setting_to_binary(self, entry):
        """
        Encode value and return it as bytearray.
        """
        raise NotImplementedError("Subclass must implement convert_setting_to_binary()")

    def validate_metadata_and_extract_settings_name(self, metadata):
        """
        Validate the _metadata dict from a JSON file and return the settings name string.
        Raise or return None on error.
        """
        raise NotImplementedError("Subclass must implement validate_metadata_and_extract_settings_name()")

    # --- Optional overrides ---

    def handle_extra_keys_from_json(self, binary_file_path, extra_keys):
        """Called after compilation with keys found in JSON that are not in the key mapping."""
        pass

    def after_binary_written(self, output_path):
        """Called unconditionally after the main binary body is written.
        Override to append extra data to the binary file."""
        pass

    def write_lookup_keys_specific_header(self, file_handle):
        """Called inside generate_lookup_keys_from_default_file to write extra header content."""
        pass

    # --- Binary I/O helpers ---

    # --- Core read function ---
    def read_setting_from_binary(self, file_path, key_index):
        """
        Read one setting entry from a pre-validated binary file.

        Args:
            file_path: Path to binary settings file
            key_index: Integer index of the key (0-based)

        Returns:
            Tuple (value, error):
            - (value, None)               — success
            - (None, "missing")           — key marked absent (0xFFFFFFFF)
            - (None, "invalid_key_index") — key_index out of bounds
            - (None, "read_error")        — I/O error
            - (None, "decode_error")      — reconstruct_setting_from_binary raised
        """
        try:
            with open(file_path, 'rb') as f:
                f.seek(MAGIC_SIZE + VERSION_SIZE)
                key_count = struct.unpack('<I', f.read(KEY_COUNT_SIZE))[0]

                if key_index < 0 or key_index >= key_count:
                    return (None, "invalid_key_index")

                index_offset = HEADER_SIZE + (key_index * OFFSET_SIZE)
                f.seek(index_offset)
                entry_offset = struct.unpack('<I', f.read(OFFSET_SIZE))[0]

                if entry_offset == 0xFFFFFFFF:
                    return (None, "missing")

                f.seek(entry_offset)
                try:
                    result = self.reconstruct_setting_from_binary(f)
                    return (result, None)
                except Exception:
                    return (None, "decode_error")

        except Exception:
            return (None, "read_error")

    # --- Key-file generation ---

    def generate_lookup_keys_from_default_file(self, default_settings_json_path, output_path=None):
        """
        Generate a Keys class file from the default settings JSON.

        Args:
            default_settings_json_path: Path to default JSON file
            output_path: Output .py file path (default: ./keys.py)

        Returns:
            dict: key_to_index mapping, or None on error
        """
        if not self.SETTINGS_KEY or not isinstance(self.SETTINGS_KEY, str):
            print("Error: SETTINGS_KEY not defined in subclass")
            return None

        with open(default_settings_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        keys = sorted(data[self.SETTINGS_KEY].keys())
        key_to_index = {key: i for i, key in enumerate(keys)}

        if output_path is None:
            output_path = os.path.join('.', "keys.py")

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('"""Auto-generated key mappings - DO NOT EDIT MANUALLY"""\n')
            f.write(f'# Generated from: {os.path.basename(default_settings_json_path)}\n')
            f.write(f'# Key count: {len(keys)}\n')
            f.write('# Auto-generated by settings_file_compiler.py\n\n')

            self.write_lookup_keys_specific_header(f)

            f.write('class Keys:\n')
            f.write('    """Integer constants for settings keys (RAM efficient)."""\n')
            for key, index in sorted(key_to_index.items(), key=lambda x: x[1]):
                f.write(f'    {key} = {index}\n')
            f.write('\n\n')
            f.write('# Metadata\n')
            f.write(f'KEY_COUNT = {len(keys)}\n')

        print(f"Generated {output_path}")
        print(f"  Keys class: {len(keys)} constants")

        return key_to_index

    # --- JSON → binary compilation ---

    def json_to_binary(self, json_path, default_keys_class, output_path=None):
        """
        Convert a JSON settings file to binary format.

        Binary layout:
          [Header: 44 bytes]  magic(4) | version(4) | key_count(4) | name(32)
          [Index:  key_count * 4 bytes]  per-key data offsets (0xFFFFFFFF = missing)
          [Data:   variable]  entries encoded with convert_setting_to_binary()

        Args:
            json_path: Input JSON file path
            default_keys_class: Keys class (from generate_lookup_keys_from_default_file)
            output_path: Output .bin path (default: auto-generate in CWD)

        Returns:
            str: Path to generated binary file, or None on error
        """
        if not self.SETTINGS_KEY or not isinstance(self.SETTINGS_KEY, str):
            print("Error: SETTINGS_KEY not defined in subclass")
            return None

        settingsfile_name = self.extract_settings_name_from_filename(json_path)
        if settingsfile_name is None:
            return None

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error: Could not read JSON file '{json_path}': {e}")
            return None

        metadata = data.get('_metadata', {})
        settings_name = self.validate_metadata_and_extract_settings_name(metadata)
        if settings_name is None:
            return None

        if settings_name != settingsfile_name:
            print(f"Error: Settings name '{settings_name}' in _metadata does not match "
                  f"filename '{settingsfile_name}' (expected '{settingsfile_name}')")
            return None

        if output_path is None:
            output_path = './' + self.get_binary_filename(settings_name)

        entries = data.get(self.SETTINGS_KEY, {})
        if not entries:
            print(f"Error: No data found under key '{self.SETTINGS_KEY}' in '{json_path}'")
            return None

        key_to_index = collect_int_constants(default_keys_class, recursive=self.RECURSIVE_KEYS)
        # key_count is the size of the index table: must cover the highest index
        # value so sparse key spaces (e.g. SPECTER_STYLES with gaps) work correctly.
        key_count = (max(key_to_index.values()) + 1) if key_to_index else 0

        index_size = key_count * OFFSET_SIZE
        data_start_offset = HEADER_SIZE + index_size

        index_data = [0xFFFFFFFF] * key_count
        binary_data = bytearray()
        index_to_key = {v: k for k, v in key_to_index.items()}
        # Normalise JSON entries to uppercase for case-insensitive lookup
        entries_upper = {k.upper(): v for k, v in entries.items()}

        for i in range(key_count):
            if i not in index_to_key:
                continue  # gap in key space — leave slot as 0xFFFFFFFF
            key = index_to_key[i]
            if key.upper() not in entries_upper:
                print(f"Warning: Missing entry for key '{key}', will fall back to default")
                continue
            entry_offset = len(binary_data)
            binary_data.extend(self.convert_setting_to_binary(entries_upper[key.upper()]))
            index_data[i] = data_start_offset + entry_offset

        if self.MAGIC_BYTES is None:
            print("Error: MAGIC_BYTES not defined in subclass")
            return None

        try:
            with open(output_path, 'wb') as f:
                f.write(self.MAGIC_BYTES)
                f.write(struct.pack('<I', 1))           # version
                f.write(struct.pack('<I', key_count))   # key count
                header_name = self._get_name_for_binary_header(settings_name, metadata)
                name_bytes = header_name.encode('utf-8')[:NAME_FIELD_SIZE - 1]
                f.write(name_bytes + b'\x00' * (NAME_FIELD_SIZE - len(name_bytes)))
                for offset in index_data:
                    f.write(struct.pack('<I', offset))
                f.write(binary_data)
        except Exception as e:
            print(f"Error: Could not write binary file '{output_path}': {e}")
            return None

        extra_keys = [k for k in entries if k.upper() not in {ek.upper() for ek in key_to_index}]
        if extra_keys:
            self.handle_extra_keys_from_json(output_path, extra_keys)

        self.after_binary_written(output_path)

        return str(output_path)

    def _get_name_for_binary_header(self, settings_name, metadata):
        """Return the string to embed in the binary file header name field.
        Base implementation uses the settings name (code). Override in subclasses
        to store a human-readable display name instead."""
        return settings_name

    # --- Validation ---

    def validate_binary_file(self, binary_path, keys_class=None):
        """
        Validate a binary settings file with comprehensive checks.

        Should be called once when first loading a binary file.
        After validation passes, read_setting_from_binary() can be used
        without re-validating on every call.

        Args:
            binary_path: Path to .bin file
            keys_class: Optional Keys class — if provided, verifies KEY_COUNT matches

        Returns:
            Tuple (success: bool, error_msg: str|None)
        """
        if self.MAGIC_BYTES is None:
            return (False, "MAGIC_BYTES not defined in subclass")

        try:
            try:
                os.stat(binary_path)
            except OSError:
                return (False, "File not found")

            with open(binary_path, 'rb') as f:
                f.seek(0, 2)
                file_size = f.tell()
                f.seek(0)

                if file_size < HEADER_SIZE:
                    return (False, f"File too small for header (need {HEADER_SIZE} bytes minimum)")

                magic = f.read(MAGIC_SIZE)
                if magic != self.MAGIC_BYTES:
                    return (False, f"Invalid magic bytes: expected {self.MAGIC_BYTES!r}, got {magic!r}")

                version = struct.unpack('<I', f.read(VERSION_SIZE))[0]
                key_count = struct.unpack('<I', f.read(KEY_COUNT_SIZE))[0]

                name_raw = f.read(NAME_FIELD_SIZE)
                null_pos = name_raw.find(b'\x00')
                if null_pos < 0:
                    return (False, "Name field has no null terminator (corrupt file)")
                try:
                    settings_name = name_raw[:null_pos].decode('utf-8')
                except UnicodeDecodeError:
                    settings_name = '<invalid UTF-8>'

                print(f"Binary file: {binary_path}")
                print(f"  Magic: {magic!r}")
                print(f"  Version: {version}")
                print(f"  Key count: {key_count}")
                print(f"  Settings name: {settings_name!r}")

                if keys_class is not None:
                    key_to_index = collect_int_constants(keys_class)
                    reference_key_count = len(key_to_index)
                    if key_count != reference_key_count:
                        return (False, f"Key count mismatch: expected {reference_key_count}, got {key_count}")

                min_size = HEADER_SIZE + key_count * OFFSET_SIZE
                if file_size < min_size:
                    return (False, f"File too small: {file_size} bytes < minimum {min_size} bytes")

                all_offsets = []
                invalid_offsets = []
                for i in range(key_count):
                    offset = struct.unpack('<I', f.read(OFFSET_SIZE))[0]
                    all_offsets.append(offset)
                    if offset != 0xFFFFFFFF and (offset < 0 or offset >= file_size):
                        invalid_offsets.append((i, offset))

                if invalid_offsets:
                    errors = "; ".join(
                        f"index {i}: offset {o} out of bounds"
                        for i, o in invalid_offsets[:5]
                    )
                    return (False, f"Invalid offsets: {errors}")

                for i, offset in enumerate(all_offsets):
                    if offset == 0xFFFFFFFF:
                        continue
                    try:
                        f.seek(offset)
                        obj = self.reconstruct_setting_from_binary(f)
                        if obj is None:
                            return (False, f"Entry at index {i} (offset {offset}) returned None")
                    except Exception as e:
                        return (False, f"Cannot read entry at index {i} (offset {offset}): {e}")

                reconstructed = sum(1 for o in all_offsets if o != 0xFFFFFFFF)
                print(f"  Reconstructed entries: {reconstructed}")
                print(f"  Missing entries: {key_count - reconstructed}")
                print(f"  File size: {file_size} bytes")

                return (True, None)

        except Exception as e:
            return (False, f"Validation error: {e}")

    # --- CLI key-file loading helpers ---

    @staticmethod
    def try_to_load_keys_file(keys_file):
        """Load a keys .py file by path using importlib. Returns module or None."""
        if os.path.exists(keys_file):
            import importlib.util
            spec = importlib.util.spec_from_file_location("Keys", keys_file)
            keys_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(keys_module)
            return keys_module
        return None

    def try_to_find_keys_file(self, keys_file=None, fallback_path=None):
        """Try to load a keys file; fall back to keys.py in the same dir as fallback_path."""
        keys_module = None
        if keys_file is not None:
            keys_module = self.try_to_load_keys_file(keys_file)
        if keys_module is None and fallback_path is not None:
            fallback_dir = os.path.dirname(fallback_path) or '.'
            candidate = os.path.join(fallback_dir, "keys.py")
            keys_module = self.try_to_load_keys_file(candidate)
        return keys_module

    # --- CLI entry point ---

    def main(self):
        """Command line interface for the settings file compiler."""
        import sys

        if len(sys.argv) < 2:
            print("Usage:")
            print(f"  {__file__} generate_keys <default_file.json> [output_keys_file.py]")
            print(f"  {__file__} compile <file.json> [keys_file.py]")
            print(f"  {__file__} validate <file.bin> [keys_file.py]")
            return

        command = sys.argv[1]

        if command == "generate_keys":
            if len(sys.argv) < 3:
                print("Error: Missing default file JSON path")
                return
            json_path = sys.argv[2]
            output_keys_file = sys.argv[3] if len(sys.argv) >= 4 else None
            self.generate_lookup_keys_from_default_file(json_path, output_path=output_keys_file)

        elif command == "compile":
            if len(sys.argv) < 3:
                print("Error: Missing settings JSON file")
                return
            json_path = sys.argv[2]
            keys_file = sys.argv[3] if len(sys.argv) >= 4 else None
            keys_module = self.try_to_find_keys_file(keys_file=keys_file, fallback_path=json_path)
            if keys_module is None:
                print("Error: No key mapping found. Run 'generate_keys' first.")
                return
            result = self.json_to_binary(json_path, keys_module.Keys)
            if result is None:
                print("Compilation failed.")
                sys.exit(1)

        elif command == "validate":
            if len(sys.argv) < 3:
                print("Error: Missing binary file")
                return
            binary_path = sys.argv[2]
            keys_file = sys.argv[3] if len(sys.argv) >= 4 else None
            keys_module = self.try_to_find_keys_file(keys_file=keys_file, fallback_path=binary_path)
            success, error = self.validate_binary_file(binary_path, keys_module)
            if not success:
                print(f"\nValidation FAILED: {error}")
                sys.exit(1)
            else:
                print("\n✓ Validation passed")

        else:
            print(f"Error: Unknown command '{command}'")


if __name__ == "__main__":
    main()