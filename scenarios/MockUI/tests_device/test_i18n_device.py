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

from conftest import disco_run, find_labels, go_back, ensure_main_menu, soft_reset


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
            "from MockUI.i18n import I18nManager; "
            "mgr = I18nManager(); print(mgr.get_language())",
        )
        lang = output.strip().split("\n")[-1].strip()
        assert len(lang) == 2 and lang.isalpha(), (
            f"[1] Unexpected language code: {lang!r}\nFull output: {output}"
        )

        # --- 2. Translate string key ---
        output = disco_run(
            "repl", "exec",
            "from MockUI.i18n import I18nManager; "
            "mgr = I18nManager(); print(repr(mgr.t('MAIN_MENU_TITLE')))",
        )
        assert "[MISSING]" not in output, f"[2] Translation missing: {output}"
        assert "[UNKNOWN_KEY]" not in output, f"[2] Unknown key: {output}"
        assert len(output.strip()) > 2, f"[2] Empty translation: {output}"

        # --- 3. Translate integer key ---
        output = disco_run(
            "repl", "exec",
            "from MockUI.i18n import I18nManager; "
            "from MockUI.i18n.translation_keys import Keys; "
            "mgr = I18nManager(); print(repr(mgr.t(Keys.MAIN_MENU_TITLE)))",
        )
        assert "[MISSING]" not in output, f"[3] Missing with integer key: {output}"
        assert "[UNKNOWN_KEY]" not in output, f"[3] Unknown integer key: {output}"

        # --- 4. Available languages include English ---
        output = disco_run(
            "repl", "exec",
            "from MockUI.i18n import I18nManager; "
            "mgr = I18nManager(); print(mgr.get_available_languages())",
        )
        assert "'en'" in output, f"[4] English not in available languages: {output}"

        # --- 5. Language name for 'en' ---
        output = disco_run(
            "repl", "exec",
            "from MockUI.i18n import I18nManager; "
            "mgr = I18nManager(); print(mgr.get_language_name('en'))",
        )
        assert "English" in output, f"[5] Expected 'English', got: {output}"

        # --- 6. Unknown string key → [UNKNOWN_KEY] ---
        output = disco_run(
            "repl", "exec",
            "from MockUI.i18n import I18nManager; "
            "mgr = I18nManager(); print(mgr.t('NONEXISTENT_KEY_12345'))",
        )
        assert "[UNKNOWN_KEY]" in output, f"[6] Expected [UNKNOWN_KEY]: {output}"

        # --- 7. Out-of-range integer key → [MISSING] ---
        output = disco_run(
            "repl", "exec",
            "from MockUI.i18n import I18nManager; "
            "mgr = I18nManager(); print(mgr.t(99999))",
        )
        assert "[MISSING]" in output, f"[7] Expected [MISSING]: {output}"

        # --- 8. t(None) doesn't crash ---
        output = disco_run(
            "repl", "exec",
            "from MockUI.i18n import I18nManager; "
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
    main menu → device menu → language menu → switch to German →
    verify → soft-reset → verify persistence → switch back to English.
    """

    def test_language_navigation_switch_persistence(self):
        """Full round-trip: navigate, switch to non-default language,
        verify persistence across soft reset, restore English.

        Sub-checks:
          1. Main menu shows English title and 'Manage Device'
          2. Device menu shows 'Select Language'
          3. Language menu shows 'English' and 'Deutsch'
          4. Switching to German updates the UI title
          5. German language survives a soft reset (Ctrl-D reboot)
          6. Switching back to English restores the UI
        """
        # --- 1. Main menu (English) ---
        ensure_main_menu()
        labels = find_labels()
        assert "What do you want to do?" in labels, (
            f"[1] English main menu title missing. Labels: {labels}"
        )
        assert "Manage Device" in labels, (
            f"[1] 'Manage Device' missing from main menu. Labels: {labels}"
        )

        # --- 2. Device menu ---
        disco_run("ui", "click", "Manage Device")
        time.sleep(1)
        labels = find_labels()
        assert "Select Language" in labels, (
            f"[2] 'Select Language' not in device menu. Labels: {labels}"
        )

        # --- 3. Language menu ---
        disco_run("ui", "click", "Select Language")
        time.sleep(1)
        labels = find_labels()
        assert "English" in labels, (
            f"[3] 'English' not in language menu. Labels: {labels}"
        )
        assert "Deutsch" in labels, (
            f"[3] 'Deutsch' not in language menu. Labels: {labels}"
        )

        # --- 4. Switch to German (non-default!) ---
        disco_run("ui", "click", "Deutsch")
        time.sleep(2)
        # After switch, UI rebuilds on device menu. Go back to main.
        go_back()
        labels = find_labels()
        assert "Was möchtest du tun?" in labels, (
            f"[4] German title missing after switch. Labels: {labels}"
        )

        # --- 5. Persistence: German survives soft reset ---
        soft_reset(wait=15)
        ensure_main_menu()
        labels = find_labels()
        assert "Was möchtest du tun?" in labels, (
            f"[5] German title not restored after soft reset. Labels: {labels}"
        )
        # Also verify via config file on flash
        output = disco_run(
            "repl", "exec",
            "import json; f=open('/flash/i18n/language_config.json','r'); "
            "d=json.load(f); f.close(); print(d['selected_language'])",
        )
        lang = output.strip().split("\n")[-1].strip()
        assert lang == "de", (
            f"[5] Config should be 'de' after reset, got: {lang!r}"
        )

        # --- 6. Switch back to English ---
        labels = find_labels()
        manage_label = next(
            (l for l in labels if "Gerät" in l), None,
        )
        assert manage_label, f"[6] Cannot find German 'Manage Device'. Labels: {labels}"
        disco_run("ui", "click", manage_label)
        time.sleep(1)

        labels = find_labels()
        lang_label = next(
            (l for l in labels if "Sprache" in l), None,
        )
        assert lang_label, f"[6] Cannot find German 'Select Language'. Labels: {labels}"
        disco_run("ui", "click", lang_label)
        time.sleep(1)

        disco_run("ui", "click", "English")
        time.sleep(2)
        go_back()  # device menu -> main

        labels = find_labels()
        assert "What do you want to do?" in labels, (
            f"[6] English title missing after switching back. Labels: {labels}"
        )
