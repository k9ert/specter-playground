"""
Internationalization (i18n) Manager for Specter UI.

Handles loading, validating, and providing translations from efficient binary format.
Supports fallback to default language for missing translations.
Enables runtime loading of new languages via JSON to binary conversion.
"""

from .translation_keys import Keys
from .lang_compiler import LangCompiler
from ..templates.settings_file_manager import SettingFileManager


class I18nManager(SettingFileManager):
    """Manages UI translations and language switching."""

    # --- Mandatory base-class attributes ---
    COMPILER = LangCompiler()
    KEYS_CLASS = Keys
    SETTINGS_DIR = "/i18n"
    DEFAULT_SETTING_FILE = "en"

    # Fallback strings
    STR_MISSING = "[MISSING]"
    STR_UNKNOWN_KEY = "[UNKNOWN_KEY]"

    # --- Core translation method ---

    def t(self, key):
        """
        Get translation for a key.

        Accepts either a string key (e.g. "MAIN_MENU_TITLE") or an integer
        index (e.g. Keys.MAIN_MENU_TITLE) for RAM efficiency.

        Falls back to default language for missing or placeholder entries.

        Returns:
            str: Translated text, or STR_MISSING / STR_UNKNOWN_KEY on error.
        """
        if not self.current_file or not self.default_file:
            print("Warning: Language files not set up properly")
            return self.STR_MISSING

        # Resolve string key to integer index
        if isinstance(key, str):
            key_index = getattr(self.KEYS_CLASS, key, None)
            if key_index is None:
                print(f"Warning: Unknown translation key '{key}'")
                return self.STR_UNKNOWN_KEY
        else:
            key_index = key

        # get_setting handles current → default fallback
        value = self.get_setting(key_index)

        if value is None:
            return self.STR_MISSING

        # Replace untranslated placeholder with default-language text
        if value == self.COMPILER.FILL_PLACEHOLDER:
            fallback, _ = self.COMPILER.read_setting_from_binary(self.default_file, key_index)
            if fallback and fallback != self.COMPILER.FILL_PLACEHOLDER:
                return fallback
            return self.STR_MISSING

        return value

    def __getitem__(self, key):
        """Allow i18n['KEY']"""
        return self.t(key)

    def __call__(self, key):
        """Allow i18n('KEY')"""
        return self.t(key)

    # --- Public API aliases (keep callers unchanged) ---

    def set_language(self, lang_code):
        return self.set_setting(lang_code)

    def get_language(self):
        return self.current

    def get_available_languages(self):
        return self.get_available_files()

    def get_language_name(self, lang_code):
        return self.get_file_name(lang_code)

    def load_language_from_json(self, json_path, lang_code=None):
        return self.load_setting_from_json(json_path, lang_code)

    # --- Read-only property aliases for direct attribute access ---

    @property
    def current_language(self):
        return self.current

    @property
    def available_languages(self):
        return self.available_files

    @property
    def current_lang_file(self):
        return self.current_file

    @property
    def default_lang_file(self):
        return self.default_file


# --- Module-level convenience API (unchanged from before) ---

def get_i18n_manager():
    """Get the global I18nManager singleton."""
    return I18nManager.get_instance()


def t(key):
    """Module-level translation shortcut."""
    return get_i18n_manager().t(key)
