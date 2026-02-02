"""
Internationalization (i18n) Manager for Specter UI.

Handles loading, validating, and providing translations from efficient binary format.
Supports fallback to default language for missing translations.
Enables runtime loading of new languages via JSON to binary conversion.
"""

import os
import struct
import json
import platform
from .translation_keys import KEY_TO_INDEX
from .lang_compiler import read_string_at_offset, BINARY_FILE_PREFIX, BINARY_FILE_SUFFIX, extract_language_code_from_filename, json_to_binary


class I18nManager:
    """Manages UI translations and language switching."""

    # Default paths
    DEFAULT_LANGUAGE = "en"  # Default language is English
    EMBEDDED_I18N_DIR = "data/lang"  # Language files embedded in firmware
    FLASH_I18N_DIR = "/flash/i18n"  # Flash filesystem directory for user-added languages
    FLASH_CONFIG_PATH = "/flash/language_config.json"  # Persistent language preference storage
    
    # Search paths for language files (in priority order)
    LANG_SEARCH_PATHS = [
        EMBEDDED_I18N_DIR,  # Embedded in firmware (relative to root)
        FLASH_I18N_DIR,  # User-added languages on flash filesystem
    ]
    
    def __init__(self):
        """
        Initialize the i18n manager.
        
        Language files are searched in:
        1. data/lang (embedded in firmware)
        2. /flash/i18n (user-added languages)
        """
        self.current_language = None
        self.current_lang_file = None
        self.default_lang_file = None
        self.available_languages = []
        
        # Ensure flash directory exists
        self._ensure_flash_i18n_dir()
        
        # Load available languages
        self._scan_available_languages()
        
        # Load last selected language or default
        selected_lang = self._load_language_preference()
        self.set_language(selected_lang)
    
    def _ensure_flash_i18n_dir(self):
        """Ensure the flash i18n directory exists."""
        try:
            # Try to create flash i18n directory
            platform.maybe_mkdir(self.FLASH_I18N_DIR)
        except OSError:
            # Flash filesystem might not be mounted yet or not available
            # This is normal on development systems
            pass
        except Exception as e:
            print(f"Warning: Could not create flash i18n directory: {e}")

    def _find_language_file(self, lang_code):
        """Find a language file across all search paths."""
        filename = f"{BINARY_FILE_PREFIX}{lang_code}{BINARY_FILE_SUFFIX}"
        
        for search_path in self.LANG_SEARCH_PATHS:
            try:
                # Check if directory exists
                try:
                    # MicroPython uses os.ilistdir() which returns iterator of (name, type, inode, size) tuples
                    files = [f[0] for f in os.ilistdir(search_path)]
                except OSError:
                    continue  # Directory doesn't exist, try next path
                
                if filename in files:
                    return f"{search_path}/{filename}"
            except Exception as e:
                continue  # Error accessing this path, try next
        
        return None

    def _scan_available_languages(self):
        """Scan for available language files (binary format) across all search paths."""
        self.available_languages = []
        lang_codes = set()
        
        # Scan all search paths for binary files
        for search_path in self.LANG_SEARCH_PATHS:
            try:
                # MicroPython uses os.ilistdir() which returns iterator of (name, type, inode, size) tuples
                files = [f[0] for f in os.ilistdir(search_path)]
                for filename in files:
                    if filename.startswith(BINARY_FILE_PREFIX) and filename.endswith(BINARY_FILE_SUFFIX):
                        # Use lang_compiler function to extract language code
                        lang_code = extract_language_code_from_filename(filename)
                        if lang_code:  # None if invalid
                            lang_codes.add(lang_code)
            except OSError:
                continue  # Directory doesn't exist, skip
            except Exception as e:
                print(f"Warning: Error scanning {search_path}: {e}")
        
        self.available_languages = sorted(list(lang_codes))
        try:
            if platform.file_exists(self.FLASH_I18N_DIR):
                # MicroPython uses os.ilistdir() which returns iterator of (name, type, inode, size) tuples
                files = [f[0] for f in os.ilistdir(self.FLASH_I18N_DIR)]
                for filename in files:
                    if filename.startswith(BINARY_FILE_PREFIX) and filename.endswith(BINARY_FILE_SUFFIX):
                        # Use lang_compiler function to extract language code
                        lang_code = extract_language_code_from_filename(filename)
                        if lang_code and lang_code not in lang_codes:
                            lang_codes.add(lang_code)
        except Exception as e:
            print(f"Warning: Could not scan flash i18n directory: {e}")

        self.available_languages = sorted(list(lang_codes))

        # Ensure default language is always available
        if self.DEFAULT_LANGUAGE not in self.available_languages:
            self.available_languages.append(self.DEFAULT_LANGUAGE)
    
    def _load_language_preference(self):
        """Load the last selected language from flash config file."""
        try:
            with open(self.FLASH_CONFIG_PATH, 'r') as f:
                config = json.load(f)
                lang = config.get('selected_language', self.DEFAULT_LANGUAGE)
                
                # Validate that the language is available
                if lang in self.available_languages:
                    return lang
                else:
                    print(f"Warning: Saved language '{lang}' not available, using default language '{self.DEFAULT_LANGUAGE}'")
                    return self.DEFAULT_LANGUAGE
        except OSError:
            # Config file doesn't exist, create it with default language
            print(f"Config file not found, creating with default language: {self.DEFAULT_LANGUAGE}")
            self._save_language_preference(self.DEFAULT_LANGUAGE)
            return self.DEFAULT_LANGUAGE
        except Exception as e:
            print(f"Error loading language preference: {e}")
            # Try to recreate config file
            self._save_language_preference(self.DEFAULT_LANGUAGE)
            return self.DEFAULT_LANGUAGE
    
    def _save_language_preference(self, lang_code):
        """Save the selected language to flash filesystem."""
        try:
            # Ensure flash directory exists
            flash_dir = "/flash"
            try:
                platform.maybe_mkdir(flash_dir)
            except OSError:
                pass  # Directory might already exist
            
            config = {'selected_language': lang_code}
            with open(self.FLASH_CONFIG_PATH, 'w') as f:
                json.dump(config, f)
            print(f"Language preference saved: {lang_code}")
        except OSError as e:
            # Filesystem is not writable - this is a fatal error for persistent settings
            raise RuntimeError(f"Flash filesystem not writable, cannot save language preference: {e}")
        except Exception as e:
            # Other errors are also fatal since we need persistent storage
            raise RuntimeError(f"Failed to save language preference: {e}")
    
    def _get_language_file_path(self, lang_code):
        """
        Get the full path to a language binary file.
        Uses search paths to find language files in priority order.
        
        Args:
            lang_code: ISO 639-1 language code (e.g., 'en', 'de')
            
        Returns:
            str: Path to language binary file or None if not found
        """
        return self._find_language_file(lang_code)
    
    def _read_binary_offset(self, file_path, position):
        """
        Read a 4-byte offset from binary file at given position.
        
        Args:
            file_path: Path to binary language file
            position: Byte position to read from
            
        Returns:
            int: Offset value or 0xFFFFFFFF if file error
        """
        try:
            with open(file_path, 'rb') as f:
                f.seek(position)
                data = f.read(4)
                if len(data) == 4:
                    return struct.unpack('<I', data)[0]
        except Exception as e:
            print(f"Warning: Could not read offset from {file_path} at position {position}: {e}")
        
        return 0xFFFFFFFF  # Signal missing/error
    
    def _read_binary_string(self, file_path, offset):
        """
        Read a null-terminated string from binary file at given offset.
        
        Args:
            file_path: Path to binary language file
            offset: Byte offset to start reading from
            
        Returns:
            str: Decoded string or empty string if error
        """
        try:
            with open(file_path, 'rb') as f:
                return read_string_at_offset(f, offset)
        except Exception as e:
            print(f"Warning: Could not read string from {file_path} at offset {offset}: {e}")
            return ""
    
    def set_language(self, lang_code):
        """
        Set the active language.
        
        Args:
            lang_code: ISO 639-1 language code (e.g., 'en', 'de')
            
        Returns:
            bool: True if language was set successfully, False otherwise
        """
        if lang_code not in self.available_languages:
            print(f"Warning: Language '{lang_code}' not available. Available: {self.available_languages}")
            return False
        
        # Find language file paths
        current_path = self._get_language_file_path(lang_code)
        default_path = self._get_language_file_path(self.DEFAULT_LANGUAGE)
        
        if current_path is None:
            print(f"Error: Could not find binary file for language '{lang_code}'")
            return False
        
        if default_path is None:
            print(f"Error: Could not find binary file for default language '{self.DEFAULT_LANGUAGE}'")
            return False
        
        # Set file paths
        self.current_lang_file = current_path
        self.default_lang_file = default_path
        self.current_language = lang_code
        
        # Save preference
        self._save_language_preference(lang_code)
        
        print(f"Language set to '{lang_code}' (file: {current_path})")
        return True
    
    def get_language(self):
        """Get the current language code."""
        return self.current_language
    
    def get_available_languages(self):
        """Get list of available language codes."""
        return self.available_languages.copy()
    
    def t(self, key):
        """
        Get translation for a key using binary file lookup.
        
        Args:
            key: Translation key (e.g., 'MAIN_MENU_TITLE')
            
        Returns:
            str: Translated text or the key itself if not found
        """
        # Validate setup
        if not self.current_lang_file or not self.default_lang_file:
            print(f"Warning: Language files not set up properly")
            return key
        
        # Get index position for key
        if key not in KEY_TO_INDEX:
            print(f"Warning: Translation key '{key}' not found in KEY_TO_INDEX")
            return key
        
        index_position = KEY_TO_INDEX[key]
        
        # Calculate byte position in index (after 12-byte header)
        byte_position = 12 + index_position * 4
        
        # Try to read from current language file
        offset = self._read_binary_offset(self.current_lang_file, byte_position)
        
        # Fallback to default language if missing
        if offset == 0xFFFFFFFF:
            offset = self._read_binary_offset(self.default_lang_file, byte_position)
            if offset == 0xFFFFFFFF:
                print(f"Warning: Translation for '{key}' not found in any language file")
                return key
            # Read from default language file
            text = self._read_binary_string(self.default_lang_file, offset)
        else:
            # Read from current language file  
            text = self._read_binary_string(self.current_lang_file, offset)
        
        return text if text else key
    
    def __getitem__(self, key):
        """Allow using the manager as a dictionary: i18n['KEY']"""
        return self.t(key)
    
    def __call__(self, key):
        """Allow using the manager as a function: i18n('KEY')"""
        return self.t(key)
    
    def load_language_from_json(self, json_path, lang_code=None):
        """
        Load a new language from JSON file and convert to binary format.
        Saves the binary file to flash filesystem for persistent access.
        
        Args:
            json_path: Path to JSON language file
            lang_code: Language code override (extracted from JSON if None)
            
        Returns:
            bool: True if language was loaded successfully
        """
        try:            
            # Convert JSON to binary - this includes all validation
            result_path = json_to_binary(json_path, KEY_TO_INDEX, None)
            
            if result_path is None:
                print("Error: Language compilation failed due to validation errors")
                return False
            
            # Extract language code from result path
            lang_code = extract_language_code_from_filename(result_path)
            
            if lang_code is None:
                print("Error: Could not determine language code from compiled file")
                return False
            
            # Move to flash directory if not already there
            import shutil
            flash_path = f"{self.FLASH_I18N_DIR}/{BINARY_FILE_PREFIX}{lang_code}{BINARY_FILE_SUFFIX}"
            
            if result_path != flash_path:
                try:
                    shutil.move(result_path, flash_path)
                    result_path = flash_path
                except Exception as e:
                    print(f"Warning: Could not move to flash directory: {e}")
                    # Continue with current location
            
            # Rescan available languages
            self._scan_available_languages()
            
            print(f"Successfully loaded language '{lang_code}' from {json_path}")
            print(f"Binary file saved to: {result_path}")
            print("Language is now available for selection.")
            
            return True
            
        except Exception as e:
            print(f"Error loading language from JSON: {e}")
            return False


# Global instance (will be initialized by NavigationController or main app)
_global_i18n_manager = None


def get_i18n_manager():
    """Get the global i18n manager instance."""
    global _global_i18n_manager
    if _global_i18n_manager is None:
        _global_i18n_manager = I18nManager()
    return _global_i18n_manager


def t(key):
    """
    Convenience function to get translation for a key.
    Uses the global i18n manager instance.
    
    Args:
        key: Translation key (e.g., 'MAIN_MENU_TITLE')
        
    Returns:
        str: Translated text or the key itself if not found
    """
    return get_i18n_manager().t(key)
