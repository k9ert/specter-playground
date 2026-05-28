"""Device integration tests for the i18n system.

Run with a connected STM32F469 Discovery board:
    .venv/bin/pytest scenarios/MockUI/tests_device/ -v \
        -c scenarios/MockUI/tests_device/pytest.ini

Prerequisites:
  - MockUI firmware flashed and running
  - Board connected via USB
  - disco tool + deps available (see conftest.py)

Test order (infrastructure first, then functional):
  1. test_i18n_repl_interface — REPL access, I18nManager, translations, errors
  2. test_i18n_files_on_flash — config file + binary language packs
  3. test_language_navigation_switch_persistence — UI labels, navigation,
     switch to non-default language, soft-reset persistence, restore English
"""
import json
import time

import pytest

from conftest import (
    disco_run, find_labels, go_back, ensure_main_menu, soft_reset,
    navigate_to_language_menu, click_by_label, _load_label, _load_metadata,
)

# Sentinel strings returned by I18nManager — must match i18n_manager.py.
STR_MISSING = "[MISSING]"
STR_UNKNOWN_KEY = "[UNKNOWN_KEY]"

# Language codes used throughout these tests.
LANG_EN = "en"
LANG_DE = "de"

# Labels loaded from language files — used in assertions.
_MAIN_MENU_TITLE_EN = _load_label("MAIN_MENU_TITLE", LANG_EN)[0]
_MAIN_MENU_TITLE_DE = _load_label("MAIN_MENU_TITLE", LANG_DE)[0]
_DEUTSCH = _load_metadata("language_name", LANG_DE)[0]
_ENGLISH = _load_metadata("language_name", LANG_EN)[0]


class TestI18nInfrastructure:
    """Infrastructure tests — verify REPL access and files on flash.

    Run *before* UI tests so that failures here immediately point to
    a setup / connectivity problem rather than a UI bug.
    """

    def test_i18n_repl_interface(self):
        """I18nManager is importable and functional via REPL.

        Sub-checks:
          1. Import & instantiate I18nManager, read current language
          2. Translate a string key (MAIN_MENU_TITLE)
          3. Translate an integer key (Keys.MAIN_MENU_TITLE)
          4. get_available_languages() includes 'en'
          5. get_language_name('en') returns 'English'
          6. Unknown string key returns [UNKNOWN_KEY]
          7. Out-of-range integer key returns [MISSING]
          8. t(None) does not crash the device
        """
        # --- 1. Import & get current language ---
        output = disco_run(
            "repl", "exec",
            "from MockUI.basic.i18n import I18nManager; "
            "mgr = I18nManager(); print(mgr.get_language())",
        )
        lang = output.strip().split("\n")[-1].strip()
        assert len(lang) == 2 and lang.isalpha(), (
            f"[1] Unexpected language code: {lang!r}\nFull output: {output}"
        )

        # --- 2. Translate string key ---
        output = disco_run(
            "repl", "exec",
            "from MockUI.basic.i18n import I18nManager; "
            "mgr = I18nManager(); print(repr(mgr.t('MAIN_MENU_TITLE')))",
        )
        assert STR_MISSING not in output, f"[2] Translation missing: {output}"
        assert STR_UNKNOWN_KEY not in output, f"[2] Unknown key: {output}"
        assert len(output.strip()) > 2, f"[2] Empty translation: {output}"

        # --- 3. Translate integer key ---
        output = disco_run(
            "repl", "exec",
            "from MockUI.basic.i18n import I18nManager; "
            "from MockUI.basic.i18n.translation_keys import Keys; "
            "mgr = I18nManager(); print(repr(mgr.t(Keys.MAIN_MENU_TITLE)))",
        )
        assert STR_MISSING not in output, f"[3] Missing with integer key: {output}"
        assert STR_UNKNOWN_KEY not in output, f"[3] Unknown integer key: {output}"

        # --- 4. Available languages include English ---
        output = disco_run(
            "repl", "exec",
            "from MockUI.basic.i18n import I18nManager; "
            "mgr = I18nManager(); print(mgr.get_available_languages())",
        )
        assert "'en'" in output, f"[4] English not in available languages: {output}"

        # --- 5. Language name for 'en' ---
        output = disco_run(
            "repl", "exec",
            "from MockUI.basic.i18n import I18nManager; "
            "mgr = I18nManager(); print(mgr.get_language_name('en'))",
        )
        assert _ENGLISH in output, f"[5] Expected {_ENGLISH}, got: {output}"

        # --- 6. Unknown string key → [UNKNOWN_KEY] ---
        output = disco_run(
            "repl", "exec",
            "from MockUI.basic.i18n import I18nManager; "
            "mgr = I18nManager(); print(mgr.t('NONEXISTENT_KEY_12345'))",
        )
        assert STR_UNKNOWN_KEY in output, f"[6] Expected [UNKNOWN_KEY]: {output}"

        # --- 7. Out-of-range integer key → [MISSING] ---
        output = disco_run(
            "repl", "exec",
            "from MockUI.basic.i18n import I18nManager; "
            "mgr = I18nManager(); print(mgr.t(99999))",
        )
        assert STR_MISSING in output, f"[7] Expected [MISSING]: {output}"

        # --- 8. t(None) doesn't crash ---
        output = disco_run(
            "repl", "exec",
            "from MockUI.basic.i18n import I18nManager; "
            "mgr = I18nManager(); "
            "try:\n"
            "    result = mgr.t(None)\n"
            "    print('OK:' + str(result))\n"
            "except Exception as e:\n"
            "    print('EXCEPTION:' + str(e))",
        )
        assert "OK:" in output or "EXCEPTION:" in output, (
            f"[8] Unexpected output (possible crash): {output}"
        )

    def test_i18n_files_on_flash(self):
        """Config file and binary language packs exist on /flash/i18n/.

        Sub-checks:
          1. language_config.json exists and contains a valid 2-letter code
          2. At least LANG_EN.BIN is present (FAT stores names uppercase)
        """
        # --- 1. Config file ---
        output = disco_run(
            "repl", "exec",
            "import json; f=open('/flash/i18n/language_config.json','r'); "
            "print(f.read()); f.close()",
        )
        data = json.loads(output)
        assert "selected_language" in data, (
            f"[1] Config missing 'selected_language': {data}"
        )
        lang = data["selected_language"]
        assert len(lang) == 2 and lang.isalpha(), (
            f"[1] Invalid language code in config: {lang!r}"
        )

        # --- 2. Binary language pack ---
        listing = disco_run("repl", "ls", "/flash/i18n")
        assert "LANG_EN.BIN" in listing or "lang_en.bin" in listing, (
            f"[2] lang_en.bin not found in /flash/i18n/. Listing:\n{listing}"
        )


class TestI18nFunctional:
    """Functional test — UI navigation, language switch, persistence.

    This is a single scenario that walks through the full workflow:
    main menu → settings → device menu → language menu → switch to German →
    verify → soft-reset → verify persistence → switch back to English.
    """

    def test_language_navigation_switch_persistence(self):
        """Full round-trip: navigate, switch to non-default language,
        verify persistence across soft reset, restore English.

        Navigation path: Main → Settings (gear icon) → Select Language (EN)
        (handled by navigate_to_language_menu() in conftest.py)

        Sub-checks:
          1. Language menu shows 'English' and 'Deutsch'
          2. Switching to German updates the main menu title
          3. German language survives a soft reset (Ctrl-D reboot)
          4. Switching back to English restores the UI
        """
        # --- 1. Language menu ---
        navigate_to_language_menu(LANG_EN)
        labels = find_labels()
        assert _ENGLISH in labels, (
            f"[1] '{_ENGLISH}' not in language menu. Labels: {labels}"
        )
        assert _DEUTSCH in labels, (
            f"[1] '{_DEUTSCH}' not in language menu. Labels: {labels}"
        )

        # --- 2. Switch to German (non-default!) ---
        click_by_label(_DEUTSCH)
        time.sleep(2)
        ensure_main_menu()
        labels = find_labels()
        assert _MAIN_MENU_TITLE_DE in labels, (
            f"[2] German title missing after switch. Labels: {labels}"
        )

        # --- 3. Persistence: German survives soft reset ---
        soft_reset(wait=15)
        ensure_main_menu()
        labels = find_labels()
        assert _MAIN_MENU_TITLE_DE in labels, (
            f"[3] German title not restored after soft reset. Labels: {labels}"
        )
        # Also verify via config file on flash
        output = disco_run(
            "repl", "exec",
            "import json; f=open('/flash/i18n/language_config.json','r'); "
            "d=json.load(f); f.close(); print(d['selected_language'])",
        )
        lang = output.strip().split("\n")[-1].strip()
        assert lang == LANG_DE, (
            f"[3] Config should be {LANG_DE} after reset, got: {lang!r}"
        )

        # --- 4. Switch back to English ---
        # Force a GC cycle to reclaim heap accumulated from repeated find_labels()
        # JSON parsing. The navigation path is now 3 levels deep (vs 1 before),
        # so significantly more garbage builds up. A soft reset would also work
        # but gc.collect() is much faster.
        disco_run("repl", "exec", "import gc; gc.collect()")
        navigate_to_language_menu(LANG_DE)
        click_by_label(_ENGLISH)
        time.sleep(2)
        ensure_main_menu()

        labels = find_labels()
        assert _MAIN_MENU_TITLE_EN in labels, (
            f"[4] English title missing after switching back. Labels: {labels}"
        )
