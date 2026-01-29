"""
Internationalization (i18n) Manager for Specter UI.

Handles loading, validating, and providing translations for the user interface.
Supports fallback to default language for missing translations.
"""

import json
import os

# Try to import embedded translations (available in frozen firmware)
try:
    from .translations_embedded import LANGUAGES as _EMBEDDED
except ImportError:
    _EMBEDDED = {}


class I18nManager:
    """Manages UI translations and language switching."""

    # Default paths
    I18N_DIR = None  # Will be set on first instantiation
    LANGUAGE_FILE_PREFIX = "specter_ui_"
    LANGUAGE_FILE_SUFFIX = ".json"
    CONFIG_FILE = "language_config.json"
    DEFAULT_LANGUAGE = "en"  # Default language is English
    
    def __init__(self, i18n_dir=None):
        """
        Initialize the i18n manager.
        
        Args:
            i18n_dir: Path to the directory containing language files.
                     If None, uses the directory where this file is located.
        """
        if i18n_dir is None:
            # Use the directory where this file is located
            # MicroPython doesn't have os.path, use string operations
            file_path = __file__
            # Remove the filename to get directory
            last_slash = file_path.rfind('/')
            if last_slash != -1:
                i18n_dir = file_path[:last_slash]
            else:
                i18n_dir = '.'
        
        self.i18n_dir = i18n_dir
        I18nManager.I18N_DIR = i18n_dir
        
        self.current_language = None
        self.translations = {}
        self.available_languages = []
        
        # Load available languages
        self._scan_available_languages()
        
        # Load last selected language or default
        selected_lang = self._load_language_preference()
        self.set_language(selected_lang)
    
    def _scan_available_languages(self):
        """Scan the i18n directory for available language files."""
        self.available_languages = []
        
        try:
            files = os.listdir(self.i18n_dir)
            for filename in files:
                if filename.startswith(self.LANGUAGE_FILE_PREFIX) and filename.endswith(self.LANGUAGE_FILE_SUFFIX):
                    # Extract language code from filename
                    lang_code = filename[len(self.LANGUAGE_FILE_PREFIX):-len(self.LANGUAGE_FILE_SUFFIX)]
                    
                    # Validate: language code must be exactly 2 letters (a-z, A-Z)
                    if len(lang_code) == 2 and lang_code.isalpha():
                        self.available_languages.append(lang_code.lower())
                    else:
                        print(f"Warning: Invalid language code '{lang_code}' in filename '{filename}'. "
                              f"Language codes must be exactly 2 letters (ISO 639-1).")
        except Exception as e:
            print(f"Warning: Could not scan i18n directory: {e}")
        
        # Include languages from embedded translations (frozen firmware)
        for lang_code in _EMBEDDED:
            if lang_code not in self.available_languages:
                self.available_languages.append(lang_code)

        # Ensure default language is always available (even if file is missing, we'll use empty dict)
        if self.DEFAULT_LANGUAGE not in self.available_languages:
            self.available_languages.append(self.DEFAULT_LANGUAGE)
    
    def _load_language_preference(self):
        """Load the last selected language from config file."""
        config_path = self.i18n_dir + '/' + self.CONFIG_FILE
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                lang = config.get('selected_language', self.DEFAULT_LANGUAGE)
                
                # Validate that the language is available
                if lang in self.available_languages:
                    return lang
                else:
                    print(f"Warning: Saved language '{lang}' not available, using default language '{self.DEFAULT_LANGUAGE}'")
                    return self.DEFAULT_LANGUAGE
        except OSError:
            # Config file doesn't exist yet, use default language
            return self.DEFAULT_LANGUAGE
        except Exception as e:
            print(f"Warning: Could not load language preference: {e}")
            return self.DEFAULT_LANGUAGE
    
    def _save_language_preference(self, lang_code):
        """Save the selected language to config file."""
        config_path = self.i18n_dir + '/' + self.CONFIG_FILE
        
        try:
            config = {'selected_language': lang_code}
            with open(config_path, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Warning: Could not save language preference: {e}")
    
    def _load_language_file(self, lang_code):
        """
        Load a language file and validate it.
        Temporarily loads default language to fill missing keys, then frees it.
        
        Args:
            lang_code: ISO 639-1 language code (e.g., 'en', 'de')
            
        Returns:
            dict: Translations dictionary with missing keys filled from default language
        """
        # Step 1: Load default language (English) for reference
        default_file = self.i18n_dir + '/' + f"{self.LANGUAGE_FILE_PREFIX}{self.DEFAULT_LANGUAGE}{self.LANGUAGE_FILE_SUFFIX}"
        default_translations = {}
        
        try:
            with open(default_file, 'r') as f:
                default_data = json.load(f)

            # Extract default translations
            default_raw = default_data.get('translations', {})
            for key, value in default_raw.items():
                if isinstance(value, str):
                    default_translations[key] = value
                elif isinstance(value, dict):
                    default_translations[key] = value.get('text', value.get('ref_en', key))
                else:
                    default_translations[key] = str(value)
        except OSError:
            # Fall back to embedded translations
            if self.DEFAULT_LANGUAGE in _EMBEDDED:
                default_translations = dict(_EMBEDDED[self.DEFAULT_LANGUAGE].get('translations', {}))
            else:
                print(f"Warning: Default language file not found at {default_file}")
        except Exception as e:
            print(f"Warning: Could not load default language: {e}")
        
        # Step 2: Load selected language file
        lang_file = self.i18n_dir + '/' + f"{self.LANGUAGE_FILE_PREFIX}{lang_code}{self.LANGUAGE_FILE_SUFFIX}"
        
        try:
            with open(lang_file, 'r') as f:
                data = json.load(f)
        except OSError:
            # Fall back to embedded translations
            if lang_code in _EMBEDDED:
                data = _EMBEDDED[lang_code]
            else:
                print(f"Warning: Language file not found: {lang_file}, using default language")
                return default_translations
        except (ValueError, KeyError) as e:
            print(f"Error: Invalid JSON in language file {lang_file}: {e}")
            return default_translations
        except Exception as e:
            print(f"Error: Could not load language file {lang_file}: {e}")
            return default_translations
        
        # Validate metadata
        metadata = data.get('_metadata', {})
        if metadata.get('language_code') != lang_code:
            print(f"Warning: Language code mismatch in {lang_file}")
        
        # Step 3: Extract translations from selected language
        raw_translations = data.get('translations', {})
        translations = {}
        
        # Process translations based on format
        for key, value in raw_translations.items():
            if isinstance(value, str):
                # Simple string format (used for default language)
                translations[key] = value
            elif isinstance(value, dict):
                # Object format with 'text' and 'ref_en' fields
                translations[key] = value.get('text', value.get('ref_en', key))
            else:
                print(f"Warning: Invalid translation format for key '{key}' in {lang_file}")
                translations[key] = str(value)
        
        # Step 4: Fill missing keys from default language
        missing_keys = []
        for key in default_translations.keys():
            if key not in translations:
                missing_keys.append(key)
                translations[key] = default_translations[key]
        
        # Warn about missing translations
        if missing_keys and lang_code != self.DEFAULT_LANGUAGE:
            print(f"Warning: Language '{lang_code}' is missing {len(missing_keys)} translation(s). "
                  f"Default language fallback will be used for missing keys.")
        
        # Step 5: Free default language memory (Python will garbage collect)
        default_translations = None
        
        return translations
    
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
        
        # Load the language file
        self.translations = self._load_language_file(lang_code)
        self.current_language = lang_code
        
        # Save preference
        self._save_language_preference(lang_code)
        
        return True
    
    def get_language(self):
        """Get the current language code."""
        return self.current_language
    
    def get_available_languages(self):
        """Get list of available language codes."""
        return self.available_languages.copy()
    
    def get_language_name(self, lang_code):
        """
        Get the human-readable name of a language.
        
        Args:
            lang_code: ISO 639-1 language code
            
        Returns:
            str: Language name or the code if name not found
        """
        lang_file = self.i18n_dir + '/' + f"{self.LANGUAGE_FILE_PREFIX}{lang_code}{self.LANGUAGE_FILE_SUFFIX}"
        
        try:
            with open(lang_file, 'r') as f:
                data = json.load(f)
                metadata = data.get('_metadata', {})
                return metadata.get('language_name', lang_code)
        except:
            # Fall back to embedded translations metadata
            if lang_code in _EMBEDDED:
                return _EMBEDDED[lang_code].get('_metadata', {}).get('language_name', lang_code)
            return lang_code
    
    def t(self, key):
        """
        Get translation for a key.
        
        Args:
            key: Translation key (e.g., 'MAIN_MENU_TITLE')
            
        Returns:
            str: Translated text or the key itself if not found
        """
        return self.translations.get(key, key)
    
    def __call__(self, key):
        """Allow using the manager as a function: i18n('KEY')"""
        return self.t(key)


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
