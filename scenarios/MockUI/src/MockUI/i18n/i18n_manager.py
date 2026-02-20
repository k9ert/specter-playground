"""
Internationalization (i18n) Manager for Specter UI.

Handles loading, validating, and providing translations from efficient binary format.
Supports fallback to default language for missing translations.
Enables runtime loading of new languages via JSON to binary conversion.
"""

import os
import json
from .translation_keys import KEY_TO_INDEX, Keys
from .lang_compiler import (
    read_translation_from_binary,
    get_binary_filename,
    get_json_filename,
    BINARY_FILE_PREFIX,
    BINARY_FILE_SUFFIX,
    JSON_FILE_PREFIX,
    JSON_FILE_SUFFIX,
    extract_language_code_from_filename,
    extract_language_name_from_file,
    json_to_binary
)


class I18nManager:
    """Manages UI translations and language switching."""

    # Fallback strings
    STR_MISSING = "[MISSING]"
    STR_UNKNOWN_KEY = "[UNKNOWN_KEY]"
    
    # Default paths
    DEFAULT_LANGUAGE = "en"  # Default language is English
    FLASH_I18N_DIR = "/flash/i18n"  # Flash filesystem directory for all language files
    FLASH_CONFIG_PATH = FLASH_I18N_DIR + "/language_config.json"  # Persistent language preference storage
    
    def __init__(self):
        """
        Initialize the i18n manager.
        
        All language files are stored in /flash/i18n/ including the
        default language (embedded via build system).
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
        """Verify the flash i18n directory exists (should be created by build system)."""
        try:
            # Check if directory exists by trying to list it
            os.listdir(self.FLASH_I18N_DIR)
        except OSError:
            # Directory doesn't exist - this indicates a build system problem
            print(f"Warning: {self.FLASH_I18N_DIR} does not exist!")
            print("This directory should be created by the build system.")
            print("Language system may not work correctly.")
        except Exception as e:
            print(f"Warning: Could not access flash i18n directory: {e}")

    def _scan_available_languages(self):
        """Scan for available language files (binary format) in flash directory."""
        self.available_languages = []
        lang_codes = set()
        
        try:
            files = os.listdir(self.FLASH_I18N_DIR)
            for filename in files:
                # FAT filesystem returns uppercase names (e.g. LANG_EN.BIN), so normalise
                filename_lower = filename.lower()
                if filename_lower.startswith(BINARY_FILE_PREFIX) and filename_lower.endswith(BINARY_FILE_SUFFIX):
                    # Use lang_compiler function to extract language code (pass lowercase)
                    lang_code = extract_language_code_from_filename(filename_lower)
                    if lang_code:  # None if invalid
                        lang_codes.add(lang_code)
        except OSError:
            pass  # Directory doesn't exist yet
        except Exception as e:
            print(f"Warning: Error scanning {self.FLASH_I18N_DIR}: {e}")

        self.available_languages = sorted(list(lang_codes))

        # Verify default language is available (critical requirement)
        if self.DEFAULT_LANGUAGE not in self.available_languages:
            print(f"CRITICAL ERROR: Default language '{self.DEFAULT_LANGUAGE}' not found in {self.FLASH_I18N_DIR}!")
            print(f"Expected file: {get_binary_filename(self.DEFAULT_LANGUAGE)}")
            print("This indicates a build system problem - the default language should be embedded in firmware.")
            print("All translations will show as '[MISSING]' until this is fixed.")
    
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
        except Exception as e:
            # Config file doesn't exist or can't be read - use default and try to create it
            print(f"Config file not found or unreadable, using default language: {self.DEFAULT_LANGUAGE}")
            self._save_language_preference(self.DEFAULT_LANGUAGE)
            return self.DEFAULT_LANGUAGE
    
    def _save_language_preference(self, lang_code):
        """Save the selected language to flash filesystem."""
        try:
            config = {'selected_language': lang_code}
            with open(self.FLASH_CONFIG_PATH, 'w') as f:
                json.dump(config, f)
            print(f"Language preference saved: {lang_code}")
        except Exception as e:
            # Preference won't persist across reboots, but language still works in current session
            print(f"Warning: Could not save language preference (will use default on next boot): {e}")
    
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
        
        # Construct file paths directly (all files in FLASH_I18N_DIR)
        current_path = f"{self.FLASH_I18N_DIR}/{get_binary_filename(lang_code)}"
        default_path = f"{self.FLASH_I18N_DIR}/{get_binary_filename(self.DEFAULT_LANGUAGE)}"
        
        # Verify files exist
        try:
            # Just check if we can stat the files
            os.stat(current_path)
            os.stat(default_path)
        except OSError as e:
            print(f"Error: Language file not found: {e}")
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

    def get_language_name(self, lang_code):
        """
        Return the human-readable language name read from the binary language file.
        
        Returns None and prints an error if lang_code is not in the set of available
        languages. Otherwise reads the name from the language name field in the binary
        header. Falls back to lang_code itself if the file read fails.
        """
        if lang_code not in self.available_languages:
            print(f"Error: Language '{lang_code}' is not available. Available: {self.available_languages}")
            return None
        
        binary_path = f"{self.FLASH_I18N_DIR}/{get_binary_filename(lang_code)}"
        name = extract_language_name_from_file(binary_path)
        if name is None:
            # File read failed — degrade gracefully to the raw code
            return lang_code
        return name

    def t(self, key):
        """
        Get translation for a key using binary file lookup.
        
        Supports both string keys (e.g., "MAIN_MENU_TITLE") and
        integer keys (e.g., Keys.MAIN_MENU_TITLE) for RAM efficiency.
        
        Args:
            key: Translation key (string or integer from Keys class)
            
        Returns:
            str: Translated text or fallback string
        """
        # Validate setup
        if not self.current_lang_file or not self.default_lang_file:
            print(f"Warning: Language files not set up properly")
            return self.STR_MISSING
        
        # Convert string key to index if needed
        if isinstance(key, str):
            key_index = KEY_TO_INDEX.get(key)
            if key_index is None:
                print(f"Warning: Unknown translation key '{key}'")
                return self.STR_UNKNOWN_KEY
        else:
            # Direct integer index (RAM efficient)
            key_index = key
        
        # Try to read from current language file
        text, error = read_translation_from_binary(self.current_lang_file, key_index)
        
        # If not found in current language, try default language
        if text is None and error == "missing":
            text, error = read_translation_from_binary(self.default_lang_file, key_index)
        
        # If still not found, return fallback
        if text is None:
            if error == "missing":
                return self.STR_MISSING
            else:
                # Other errors (invalid_key_index, read_error, etc.)
                print(f"Warning: Error reading translation: {error}")
                return self.STR_MISSING
        
        return text
    
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
            lang_code: Language code override (extracted from JSON filename if None)
            
        Returns:
            bool: True if language was loaded successfully
        """
        try:
            # Extract language code from filename if not provided
            if lang_code is None:
                lang_code = extract_language_code_from_filename(json_path)
                if lang_code is None:
                    print(f"Error: Could not extract language code from filename: {json_path}")
                    print(f"Expected format: {get_json_filename('XX')} where XX is 2-letter language code")
                    return False

            # Validate language code to prevent path traversal and invalid filenames
            if not (len(lang_code) == 2 and lang_code.isalpha()):
                print(f"Error: Invalid language code '{lang_code}': must be exactly 2 letters")
                return False

            # Construct target path in flash directory
            output_path = f"{self.FLASH_I18N_DIR}/{get_binary_filename(lang_code)}"
            
            # Convert JSON to binary - write directly to target location
            result_path = json_to_binary(json_path, KEY_TO_INDEX, output_path)
            
            if result_path is None:
                print("Error: Language compilation failed due to validation errors")
                return False
            
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
