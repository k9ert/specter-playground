# Internationalization (i18n) System for Specter UI

This directory contains the internationalization framework for the Specter UI, enabling multi-language support with efficient binary storage.

## Overview

The i18n system provides:
- Multi-language support with JSON source files (e.g. provided via SD-Card) converted to efficient binary format (during import on device)
- Flash storage for runtime language loading without firmware reflashing
- Automatic fallback to default language (English) for missing translations
- Persistent language selection across sessions
- Easy integration with UI components
- Language file validation (2-letter ISO 639-1 codes only)
- Zero RAM usage for string storage - all text read directly from flash
- Shared string reading utilities for consistent binary format handling

## File Structure

```
i18n/
├── __init__.py              # Module exports
├── i18n_manager.py          # Core i18n management class
├── lang_compiler.py         # JSON to binary converter
├── translation_keys.py      # Auto-generated KEY_TO_INDEX mapping  
├── lang_en.bin              # Auto compiled english (embedded in firmware)
├── language_config.json     # User's selected language (auto-generated)
└── languages/               # Source JSON translation files
    ├── specter_ui_en.json   # English translations (source / default)
    └── specter_ui_de.json   # German translations (source)

# Flash filesystem at runtime:
/flash/i18n/
├── lang_de.bin             # User-added German
├── lang_fr.bin             # User-added French
├── lang_es.bin             # User-added Spanish
└── ...
```

## Binary Format

Each language is stored as an efficient binary file using a custom format optimized for embedded systems:

```
Binary File Format (.bin):
[Header: 12 bytes]
- Magic: "LANG" (4 bytes)
- Version: uint32 (4 bytes)  
- Key count: uint32 (4 bytes)

[Index: key_count * 4 bytes]
- offset[0]: uint32 → absolute string offset or 0xFFFFFFFF if missing
- offset[1]: uint32 → absolute string offset or 0xFFFFFFFF if missing
- ...

[Strings: variable size]
- null-terminated UTF-8 strings stored consecutively
- Order matches index array for easier debugging
```

**Key Features:**
- **Zero RAM usage**: Strings read directly from flash on demand
- **Fast lookup**: O(1) key access via pre-built index
- **Compact storage**: ~1.5-2KB per language file
- **Fallback support**: 0xFFFFFFFF markers for missing translations
- **Aligned data**: Index and strings stored in same order for debugging

## Language File Format (JSON Source)

### English (Default Language)
```json
{
  "_metadata": {
    "language_code": "en",
    "language_name": "English",
    "version": "1.0"
  },
  "translations": {
    "KEY_NAME": "English text"
  }
}
```

### Other Languages
```json
{
  "_metadata": {
    "language_code": "de",
    "language_name": "Deutsch",
    "version": "1.0"
  },
  "translations": {
    "KEY_NAME": {
      "text": "Translated text",
      "ref_en": "English text"
    }
  }
}
```

The `ref_en` field provides English reference text for translators. During compilation, only the `text` field is stored in the binary - `ref_en` has **zero memory footprint**.

## Usage in UI Code

### Initialize in NavigationController
The i18n manager is automatically initialized in the NavigationController:

```python
from ..i18n import I18nManager

class NavigationController(lv.obj):
    def __init__(self, specter_state=None, ui_state=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.i18n = I18nManager()
```

### Use in Menu Classes

```python
def MyMenu(parent, *args, **kwargs):
    # Get i18n manager from NavigationController
    i18n = parent.i18n
    
    # Two ways to access translations:
    # Method 1: t() method (traditional)
    menu_items = [
        (icon, i18n.t("MENU_ITEM_KEY"), "action", None),
        (None, i18n.t("SECTION_HEADER"), None, None),
    ]
    
    # Method 2: Dictionary-style access (alternative)
    # menu_items = [
    #     (icon, i18n["MENU_ITEM_KEY"], "action", None),
    #     (None, i18n["SECTION_HEADER"], None, None),
    # ]
    
    return GenericMenu("menu_id", i18n.t("MENU_TITLE"), menu_items, parent, *args, **kwargs)
```

**Note**: Both `i18n.t("KEY")` and `i18n["KEY"]` work identically. Use whichever style you prefer. Both provide O(1) lookup with automatic fallback to default language for missing keys.

## Build System Integration

The `lang_compiler.py` provides comprehensive tools for managing the binary translation system:

### Translation Key Generation
```bash
# Generate translation_keys.py from default language
python3 lang_compiler.py generate_keys languages/specter_ui_en.json
```

### Binary Compilation  
```bash
# Compile JSON to binary format (auto-detects translation_keys.py)
python3 lang_compiler.py compile languages/specter_ui_en.json
python3 lang_compiler.py compile languages/specter_ui_de.json

# Or specify key mapping explicitly
python3 lang_compiler.py compile languages/specter_ui_XX.json translation_keys.py
```

### Binary Validation
```bash
# Validate binary files with detailed inspection
python3 lang_compiler.py validate lang_en.bin translation_keys.py
python3 lang_compiler.py validate lang_de.bin  # Without key names
```

**Compiler Features:**
- **Automatic validation**: Filename and metadata consistency checks
- **Extra key detection**: Warns about translations not in key mapping
- **Missing key tracking**: Shows count of untranslated strings
- **Language code validation**: Enforces 2-letter ISO 639-1 codes
- **Memory optimization**: Uses minimal RAM during compilation
- **Shared utilities**: `read_string_at_offset()` used by both compiler and runtime

## Adding a New Language

### Method 1: Development (Build-time)
1. Create a new language file: `languages/specter_ui_XX.json` (where XX is the ISO 639-1 language code)
2. Copy the structure from `languages/specter_ui_de.json` as a template
3. Translate all `text` fields, keeping `ref_en` as English reference
4. Set correct `language_code` and `language_name` in metadata
5. Compile to binary: `python3 lang_compiler.py compile languages/specter_ui_XX.json`
6. The binary file `lang_XX.bin` will be automatically created
7. Restart device to detect the new language

### Method 2: Runtime (User Upload)
1. User creates `specter_ui_XX.json` file following the format
2. Copy file to SD card and insert into device
3. Call `i18n.load_language_from_json("path/to/specter_ui_XX.json")`
4. Language is automatically converted to binary and stored in `/flash/i18n/`
5. Restart device to use the new language

**Important**: All languages must be compiled to binary format before use. The system only loads `.bin` files at runtime, never `.json` files.

## Language Selection

The last selected language is automatically saved to `language_config.json` and restored on next startup. Language switching requires only changing a file pointer - no RAM loading.

## Missing Translations

The binary format handles missing translations efficiently:

1. **Binary encoding**: Missing keys are stored as `0xFFFFFFFF` in the index
2. **Runtime fallback**: System automatically reads from default language file
3. **Zero performance impact**: Fallback requires just one additional file read
4. **Seamless operation**: UI continues normally with mixed language display
5. **Build warnings**: Compiler shows count of missing translations per file

Example workflow:
- User selects German language
- Key "NEW_FEATURE" missing in German binary
- System detects `0xFFFFFFFF` marker
- Automatically reads English text from `lang_en.bin`
- UI displays mixed German/English without errors

## Translation Key Naming Convention

Keys follow the pattern: `CATEGORY_SUBCATEGORY_ITEM`

Examples:
- `MAIN_MENU_TITLE` - Main menu title
- `WALLET_MENU_VIEW_ADDRESSES` - Wallet menu item
- `ACTION_SCREEN_BACK` - Generic back button
- `COMMON_WALLET` - Common term used in multiple places

## Adding New Translatable Text

1. Add the English text to `languages/specter_ui_en.json`:
   ```json
   "NEW_KEY_NAME": "English text"
   ```
2. Regenerate translation keys: `python3 lang_compiler.py generate_keys languages/specter_ui_en.json`
3. Add translations to other language files in `languages/`:
   ```json
   "NEW_KEY_NAME": {
     "text": "Translated text",
     "ref_en": "English text"
   }
   ```
4. Recompile all languages: `python3 lang_compiler.py compile languages/specter_ui_XX.json`
5. Use `i18n.t("NEW_KEY_NAME")` or `i18n["NEW_KEY_NAME"]` in your code

## API Reference

### I18nManager Class

#### Methods

- `__init__(i18n_dir=None)` - Initialize manager, scan for language files
- `set_language(lang_code)` - Switch to a different language (returns bool success)
- `get_language()` - Get current language code
- `get_available_languages()` - List available language codes
- `get_language_name(lang_code)` - Get human-readable language name
- `t(key)` - Get translation for a key (primary method)
- `__getitem__(key)` - Dictionary-style access: `i18n["KEY"]` (alternative)
- `load_language_from_json(json_path)` - Convert and load new language from JSON

#### Usage Examples

```python
# Initialize (done by NavigationController)
i18n = I18nManager()

# Get translations
title = i18n.t("MENU_TITLE")           # Method 1: t() method
button_text = i18n["BUTTON_OK"]        # Method 2: Dictionary style

# Change language
success = i18n.set_language("de")
if not success:
    print("German language not available")

# Check available languages
languages = i18n.get_available_languages()  # ["en", "de"]
```

## Technical Details

- **Runtime Format**: Binary only - JSON used only for development/compilation
- **String Reading**: Shared `read_string_at_offset()` utility for consistent handling
- **Encoding**: UTF-8 to support all languages  
- **Language Codes**: ISO 639-1 (2-letter alphabetic codes: en, de, fr, es, etc.)
- **Fallback**: Default language (English) used for missing translations
- **Performance**: All strings read directly from flash, no RAM caching
- **Flash Storage**: Uses dedicated `/flash/i18n/` directory for user-added languages
- **Security**: No code execution - pure binary data files only
- **Memory Usage**: ~336 bytes for index (84 keys × 4 bytes), zero for strings
- **Build Tools**: Comprehensive validation and error checking during compilation

## Command Line Tools

The `lang_compiler.py` provides several utilities:

```bash
# Generate key mapping from default language
python3 lang_compiler.py generate_keys languages/specter_ui_en.json

# Compile JSON to binary  
python3 lang_compiler.py compile languages/specter_ui_de.json

# Validate binary file
python3 lang_compiler.py validate lang_de.bin translation_keys.py
```

## Contributing Translations

To contribute a new language translation:
1. Fork the repository
2. Create a new language file following the format above
3. Translate all strings, keeping `ref_en` fields for context
4. Test the translations using: `python3 lang_compiler.py compile languages/specter_ui_XX.json`
5. Validate the binary: `python3 lang_compiler.py validate lang_XX.bin`
6. Submit a pull request

Please ensure:
- All keys from English file are present
- Translations are accurate and natural
- Special characters are properly escaped in JSON
- Metadata is correctly filled
- Binary compilation succeeds without errors

---

For questions or issues, please open an issue on the repository.
