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

### Storage Formats

- Master format, development/build time: **JSON** (`specter_ui_XX.json` - human-editable)
- Runtime format: **Binary** (`lang_XX.bin` - efficient, indexed)

### End User Experience

#### Use default language included in firmware

1. User runs `nix develop -c make mockui` (which compiles default English JSON (`languages/specter_ui_en.json`) to binary (`lang_en.bin`) in `build/flash_image/i18n/ and pack it into the resulting firmware binary) OR downloads pre-built firmware with English included from released versions
2. Flash single `.bin` firmware → English works immediately

#### Add new language Option 1: Include language in firmware build

1. User runs `nix develop -c make mockui LANG=XX, YY, ...` (which also compiles XX, YY, ... JSON (`languages/specter_ui_XX.json`, ...) to binaries (`lang_XX.bin`, ...) in `build/flash_image/i18n/ and packs them into the resulting firmware binary)
2. Flash single `.bin` firmware → English and additional languages XX, YY, ... work immediately (English is always included as default at first startup)

#### Add new language Option 2: Load language at runtime from SD card

1. Copy `languages/specter_ui_XX.json` to SD card and insert into device
2. Power up device (with already flashed firmware)
3. Load new language from SD card (JSON) via UI → Auto-converts to binary
4. Binary (automatically) saved on device to `/flash/i18n/` → Persists across reboots
5. SD card not needed after initial load

#### Initialize in NavigationController

The i18n manager is automatically initialized in the NavigationController:

```python
from ..i18n import I18nManager

class NavigationController(lv.obj):
    def __init__(self, specter_state=None, ui_state=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.i18n = I18nManager()
```

#### Use existing End-User facing strings

Option 1:

1. Make i18n_manager instance available (it's a singleton) (e.g. via i18n = parent.i18n)
2. Wrap all user-facing strings with `i18n.t("KEY_NAME")` or `i18n["KEY_NAME"]` for dictionary-style access

Option 2:

1. Make i18n.t() method available in your class (e.g. t = parent.i18n.t)
2. Wrap all user-facing strings with `t("KEY_NAME")`

Example:

```python
def MyMenu(parent, *args, **kwargs):
    # Get i18n manager from NavigationController
    i18n = parent.i18n
    t = i18n.t  # Optional: make t() method available for convenience
    
    # Two ways to access translations:
    # Method 1: t() method (traditional)
    menu_items = [
        (icon, i18n.t("MENU_ITEM_KEY"), "action", None),
        (None, t("SECTION_HEADER"), None, None),
    ]
    
    # Method 2: Dictionary-style access (alternative)
    # menu_items = [
    #     (icon, i18n["MENU_ITEM_KEY"], "action", None),
    #     (None, i18n["SECTION_HEADER"], None, None),
    # ]
    
    return GenericMenu("menu_id", i18n["MENU_TITLE"], menu_items, parent, *args, **kwargs)
```

**Note**: Both `i18n.t("KEY")` and `i18n["KEY"]` work identically. Use whichever style you prefer. Both provide O(1) lookup with automatic fallback to default language for missing keys.

#### Define new End-User facing strings

1. Add new key to "translations" in `languages/specter_ui_en.json` with English text to be displayed (follow obvious naming convention for keys or check "Translation Key Naming Convention" below)

   ```json
   "NEW_KEY_NAME": "<English text>"
   ```

2. Use the key in your code with `i18n.t("KEY_NAME")` or `i18n["KEY_NAME"]` or `t("KEY_NAME")` [see above]
3. Trigger build process to auto-generate translation keys and compile binary files
Optional/Later:
4. Add translations to other language JSON files in `languages/`

   ```json
   "NEW_KEY_NAME": {
     "text": "<Translated text>",
     "ref_en": "<English text>"
   }
   ```

  and recompile.

### Translation Workflow

#### Create a new language

To contribute a new language translation:

1. Fork the repository
2. Create `languages/specter_ui_XX.json` with correct metadata and translations #TO DO: Add helper script to auto-generate new language JSON file from English template with empty translations
3. Insert translated strings for all keys (keep `ref_en` for context)
4. Test the translations using: `python3 lang_compiler.py compile languages/specter_ui_XX.json`
5. Validate the binary: `python3 lang_compiler.py validate lang_XX.bin` (and fix findings)
6. Submit a pull request

Please ensure:

- All keys from English file are present
- Translations are accurate and natural
- Special characters are properly escaped in JSON
- Metadata is correctly filled
- Binary compilation succeeds without errors

### Degradation

- Translation lookup fails: Selected language → Default (English) → `"STR_MISSING"`
- No embedded strings in Python (except `"STR_MISSING"`)
- All translations read from binary files on `/flash/i18n`

## Architecture & Design

Hint regarding security: This design does not use frozen .py files to generate flash content on the device (but instead uses a self maintained binary format with clear string termination etc.) so that no injected code execution is possible on the device - pure binary data files only.

### File Structure

**Naming Convention:**

- JSON files: `specter_ui_XX.json` (XX = ISO 639-1 code)
- Binary files: `lang_XX.bin` (XX = ISO 639-1 code)
- Language Codes: ISO 639-1 (2-letter alphabetic codes: en, de, fr, es, etc.)

Filesystem in git repository:

```bash
# Runtime infrastructure/code
/scenarios/MockUI/src/MockUI/i18n/
├── __init__.py              # Module exports
├── i18n_manager.py          # Core i18n management class
├── lang_compiler.py         # JSON to binary converter, binary format master
└── languages/               # Source JSON translation files and auto-generated key mapping
    ├── specter_ui_en.json   # English translations (source / default)
    ├── specter_ui_XX.json   # XX translations (source)
    └── translation_keys.py  # Auto-generated KEY_TO_INDEX mapping

# Build-time tools
/tools/
├── make_fat_image.py        # Creates FAT12 image from staged files in build/flash_image/
├── merge_firmware_flash.py  # Combines firmware binary with filesystem image for flashing
└── sync_i18n.py             # Sync JSON language files with source code and default language file (adds/removes keys)

# Temporary build artefacts:
/build/
├── i18n_sync_master.log              # Master log from last sync-i18n run (always written, incl. dry-run)
├── i18n_sync_specter_ui_XX.log       # Per-language log from last sync-i18n run
└── flash_image/             # Staging area for files to be included in flash filesystem image
    ├── flash_fs.img         # Generated FAT12 image containing staged files (created by build-flash-image target)
    ├── i18n/
        ├── lang_en.bin      # Compiled default language binary (created by build-i18n target)
        ├── lang_xx.bin      # Compiled xx language binary (optional, if added at build time)
        └── ...              # Additional language binaries
```

Flash filesystem on device at runtime:

```bash
/flash/i18n/
├── LANG_EN.BIN             # Default: English
├── LANG_XX.BIN             # User-added language with language code XX
└── ...
```

### Language File Format (JSON Source)

#### English (Default Language)

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

#### Other Languages

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

The `ref_en` field provides English reference text for translators. During compilation, only the `text` field is stored in the binary - `ref_en` has **zero memory footprint on device**.

### Binary Format

Each language is stored as an efficient binary file using a custom format optimized for embedded systems:

- Compact storage (no JSON parsing overhead)
- Encoding: UTF-8 to support all languages  
- Language Codes: ISO 639-1 (2-letter alphabetic codes: en, de, fr, es, etc.)
- little RAM usage during runtime as only the strings of the current screen need to be copied into RAM
- Fast lookups via index
- Fallback support: 0xFFFFFFFF markers for missing translations
- Aligned data: Index and strings stored in same order for debugging
- Low memory footprint (~1.5-2KB per language file)
- Power-loss safe (read-only operations)

Binary File Format (.bin):

```bash
[Header: 44 bytes]
  magic:     4 bytes  → "LANG" (signature)
  version:   4 bytes  → uint32 (match firmware version [fw defines which strings are needed; TODO: not checked yet])
  key_count: 4 bytes  → uint32 (number of translation keys)
  lang_name: 32 bytes → null-padded UTF-8 language name (e.g. "English", "Deutsch")
                        max 31 usable bytes + 1 null terminator

[Index: key_count × 4 bytes]
  offset[0]: 4 bytes  → absolute file offset to string, or 0xFFFFFFFF if missing
  offset[1]: 4 bytes  → absolute file offset to string, or 0xFFFFFFFF if missing
  ...

[Strings: variable size]
  null-terminated UTF-8 strings
- Order matches index array for easier debugging
```

### Component Responsibilities

#### 1. `lang_compiler.py`

**Purpose:** JSON ↔ binary conversion and file I/O (location-agnostic)

**Key Constants:**

- `FILL_PLACEHOLDER = "<FILL>"` → Sentinel value written by `sync_i18n.py` for keys that have not yet been translated. `i18n_manager.t()` detects this value at runtime and falls back to English so the placeholder never appears in the UI. Imported by `sync_i18n.py` to keep both in sync.

**Key Functions:**

- `generate_translation_keys(json_path)` → Creates `translation_keys.py` from default language [used during build process to generate key mapping]
- `json_to_binary(json_path, key_to_index)` → Converts JSON to binary format, given key mapping from `translation_keys.py`
- `read_translation_from_binary(file_path, key_index)` → Reads translation string by index; returns `(text, None)` or `(None, error_code)` with 0xFFFFFFFF detection
- `extract_language_code_from_filename(filename)` → Extracts ISO code from filename (supports both JSON and binary naming conventions)
- `extract_language_name_from_file(filename)` → Reads language name from fixed-width header field of a binary file; validates naming convention, null-termination, and UTF-8 encoding
- `validate_binary_file(binary_path)` → Inspects and validates binary files (magic, version, key count, all offsets, all strings, language name field) [not to be called during runtime, only for build-time validation and testing]

**Design Principles:**

- **Location-agnostic**: Does not know or care where files are stored
- **Binary format knowledge lives here**: Including 0xFFFFFFFF = missing translation
- **Returns structured results**: Caller decides policy (fallback, error, etc.)
- **Reusable**: Same code used at build-time and runtime (for shared functionality)
- **Robust validation**: Checks filename format, language code consistency, metadata
- **No duplication**: Single implementation for all conversion needs

**Responsibility Boundary:**

- Knows: Binary format, file I/O, validation
- Doesn't know: Fallback logic, which files to use, language preferences

#### 2. `i18n_manager.py`

**Purpose:** Runtime language file management and translation lookups on device

**Key Responsibilities:**

- **File Location Management:**
  - Searches for language files in `/flash/i18n/`
  - Identifies available/installed languages
  - Manages persistent language selection (`/flash/language_config.json`)

- **Runtime Loading:**
  - Loads new languages from SD card (JSON format) [TODO: add SD Card support]
  - Converts JSON to binary using `lang_compiler.json_to_binary()`
  - Saves binary to `/flash/i18n/` for persistent access

- **Translation Lookups:**
  - Uses `translation_keys.KEY_TO_INDEX` for key → index mapping
  - Calls `lang_compiler` functions to read from specific binary files
  - Implements fallback chain (no binary format knowledge needed)

- **Graceful Degradation:**
  1. Call `lang_compiler.read_translation_from_binary(current_lang_file, key_index)`
  2. If returns `"missing"`, call same function with `default_lang_file`
  3. If still missing, return `"STR_MISSING"`
  4. If the resolved text equals `FILL_PLACEHOLDER` (`"<FILL>"`), fall back to the default language (English). If even English has `<FILL>` (brand-new key not yet given an English value), return `"STR_MISSING"`.
  5. **No placeholder text ever reaches the UI** — `<FILL>` is always caught before rendering

**Responsibility Boundary:**

- Knows: Where files live, fallback policy, user preferences, storage management
- Doesn't know: Binary format details, 0xFFFFFFFF marker meaning

**Key Methods:**

- `set_language(lang_code)` → Activates a language
- `get_available_languages()` → Lists installed languages (scans `/flash/i18n/` for binary language files)
- `get_language_name(lang_code)` → Returns human-readable name read from the binary header; returns `None` (with error print to console) if `lang_code` not in available languages; falls back to lang_code string if file read fails
- `t(key)` → Translates a key with fallback logic
- `load_language_from_json(json_path)` → Imports new language from SD card, converts to binary, rescans available languages

**Design Principles:**

- **Unified storage**: All languages in `/flash/i18n/`
- **Memory efficient**: No string caching, direct file reads
- **User-friendly**: Automatic format conversion, clear error messages

#### 3. `translation_keys.py` (Auto-generated)

**Purpose:** Contract between build-time and runtime

**Contents:**

```python
KEY_TO_INDEX = {
    "MAIN_MENU_TITLE": 0,
    "SETTINGS_BUTTON": 1,
    # ... all keys in sorted order
}
```

**Why separate module:**

- Generated from default language JSON
- Imported by both `lang_compiler.py` (at build-time) and `i18n_manager.py` (at runtime)
- Avoids circular imports
- Clear separation: data vs. logic

### Build System Integration

#### Dedicated Makefile targets

- `sync-i18n`: Runs `tools/sync_i18n.py --dry-run` during the build to **detect** drift between source code and language files. Writes logs to `build/` but **does not modify any files**. If drift is detected, run `python3 tools/sync_i18n.py` manually to apply changes before the next build. **Called automatically as the first step of `build-i18n`.**
- `build-i18n`: Depends on `sync-i18n`. Generates translation keys and compiles default language JSON to binary to `build/flash_image/i18n/` via `lang_compiler.py`
- `build-flash-image`: Creates FAT12 image from staged file in `build/flash_image/` via `tools/make_fat_image.py`
- `mockui`: Builds firmware and merges it with embedded filesystem for language file via `tools/merge_firmware_flash.py`

On device, language file appears at `/flash/i18n/lang_en.bin` (although with uppercase due to FAT12)

**Optional: Include additional languages at build time:**

```bash
make mockui ADD_LANG=de,fr, ..
# → Also compiles lang_de.bin and lang_fr.bin and ... into firmware (if json files are present)
```

#### Used helper scripts

- `lang_compiler.py`: For JSON ↔ binary conversion and validation
- `tools/sync_i18n.py`: Synchronizes JSON language files with source code and the default language file (see below)
- `tools/make_fat_image.py`: For creating FAT12 image from staged files in `build/flash_image/`
- `tools/merge_firmware_flash.py`: For combining firmware binary with filesystem image for flashing (if needed; otherwise can flash separately via ST-Link)

#### Synchronizing language files with source code

The build target `sync-i18n` runs the tool in **dry-run mode** to detect — but not fix — drift. To actually apply changes, run manually:

```bash
# Apply changes (add/remove keys, update ref_en)
python3 tools/sync_i18n.py

# Dry run — show what would change without touching any file
python3 tools/sync_i18n.py --dry-run

# Override directories
python3 tools/sync_i18n.py \
    --languages-dir scenarios/MockUI/i18n/languages \
    --source-dir    scenarios/MockUI \
    --log-dir       build
```

What the tool does:

1. **Scans source code** for all i18n key usages — recognises `t("KEY")`, `i18n["KEY"]`, `i18n("KEY")`, `i18n_manager["KEY"]`, `i18n_manager("KEY")` (single and double quotes).
2. **Syncs English master** (`specter_ui_en.json`): adds missing keys with `<FILL>`, removes obsolete keys.
3. **Syncs all other language files**: adds new keys with `<FILL>` + `ref_en`, updates `ref_en` when English text changed, removes obsolete keys, migrates any plain-string values to the standard `{text, ref_en}` format (with a warning).
4. **Validates filenames** using `extract_language_code_from_filename()` — non-conforming files are skipped with a warning.
5. **Writes logs to `build/`** immediately as changes are detected (open/write/close per entry — crash-safe). Log files are always created, even in dry-run mode. The header line `*** DRY RUN — no changes will be made ***` appears at the top of each log file when applicable.

`<FILL>` values in compiled binaries are automatically caught at runtime by `i18n_manager.t()` and replaced with the English fallback — they never reach the UI.

#### Translation Key Generation

```bash
# Generate translation_keys.py from default language
python3 lang_compiler.py generate_keys languages/specter_ui_en.json
```

#### Binary Compilation  

```bash
# Compile JSON to binary format (auto-detects translation_keys.py)
python3 lang_compiler.py compile languages/specter_ui_en.json
python3 lang_compiler.py compile languages/specter_ui_de.json

# Or specify key mapping explicitly
python3 lang_compiler.py compile languages/specter_ui_XX.json translation_keys.py
```

#### Binary Validation

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

#### STM32F469 Discovery Board Internal Flash Layout

- Combine firmware code + filesystem image into single `.bin`
  - Firmware code at 0x08020000+ (FLASH_TEXT)
  - Filesystem image at 0x08008000 (FLASH_FS)
  - Single file to flash via ST-Link [target option for current development]

```bash
0x08000000 - 0x08004000  (16KB)   FLASH_START: Sector 0 (ISR vectors)
0x08004000 - 0x08008000  (16KB)   FLASH_RSV: Sector 1 (reserved)
0x08008000 - 0x08020000  (96KB)   FLASH_FS: Sectors 2-4 (/flash filesystem)
0x08020000 - 0x08200000  (1.9MB)  FLASH_TEXT: Sectors 5-23 (firmware code)
```

## Run-time language Selection (on device)

The last selected language is automatically saved to `language_config.json` and restored on next startup by `i18n_manager`. Language switching requires only changing a file pointer - no RAM loading.

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