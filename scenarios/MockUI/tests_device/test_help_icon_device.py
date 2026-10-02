"""On-device integration tests for the help icon popup.

Each help icon (?) on a menu row opens a button_modal in layer_top with:
  - a body label: the row's text, a blank line, and the translated HELP_* key
  - a close button (MODAL_CLOSE_BTN)

Test target: the 'Scan QR' row on the main menu (no navigation needed).
If QR is not currently visible the module fixture enables it via REPL and
re-renders the main menu before the first test runs.

Widget structure of a GenericMenu row (from source): the row is a button
holding [icon, label, right container, caret]; the right container holds
the help button, the only button nested inside the row.
"""
import pytest

from conftest import (
    _load_label,
    click_by_index,
    click_overlay_by_label,
    disco_run,
    ensure_main_menu,
    find_labels,
    find_labels_overlay,
    navigate_to_settings_menu,
    screen_tree,
    walk_with_path,
)

# =========================================================================
# Translation-key constants — if upstream renames a key, fix it here only.
# =========================================================================

_KEY_SCAN_QR   = "MAIN_MENU_SCAN_QR"   # label of the Scan QR button row
_KEY_HELP_SCAN = "HELP_SCAN_QR"        # body text shown in the help popup
_KEY_CLOSE     = "MODAL_CLOSE_BTN"     # close button inside the overlay

# =========================================================================
# Resolved labels — populated once by _setup_scan_qr, used by all tests.
# =========================================================================

_button_label: str = ""   # translated text of the Scan QR button
_close_label:  str = ""   # translated text of the Close button
_help_text:    str = ""   # full body text of the help popup


# =========================================================================
# Helper: click the help icon for a row identified by its text label.
# =========================================================================

def _click_help_icon_for(label: str) -> None:
    """Tap the help (?) icon on the menu row whose text matches *label*."""
    for path, node in walk_with_path(screen_tree()):
        children = node.get("children", [])
        if node.get("type") == "button" and any(c.get("text") == label for c in children):
            for help_path, inner in walk_with_path(children):
                if inner.get("type") == "button":
                    click_by_index(f"{path}.{help_path}")
                    return
            raise AssertionError(f"Row {label!r} has no help button")
    raise AssertionError(f"No menu row {label!r} found in screen tree")


# =========================================================================
# Module fixture: resolve labels and ensure Scan QR is visible.
# =========================================================================

@pytest.fixture(scope="module", autouse=True)
def _setup_scan_qr():
    """Resolve translated labels and ensure the Scan QR button is on screen.

    Runs once for the whole module.  If QR is disabled, activates it via REPL
    and navigates away/back to force the main menu to rebuild.
    """
    global _button_label, _close_label, _help_text
    _button_label = _load_label(_KEY_SCAN_QR,   "en")[0]
    _close_label  = _load_label(_KEY_CLOSE,     "en")[0]
    _help_text    = _load_label(_KEY_HELP_SCAN, "en")[0]

    ensure_main_menu()
    if _button_label not in find_labels():
        # Activate QR via REPL and navigate away/back via the gear button
        # to force the main menu to rebuild.
        disco_run(
            "repl", "exec",
            "specter_state._hasQR = True; specter_state._enabledQR = True",
        )
        navigate_to_settings_menu()
        ensure_main_menu()


@pytest.fixture(autouse=True)
def _on_main_menu():
    """Before each test: return to the main menu."""
    ensure_main_menu()


# =========================================================================
# Tests
# =========================================================================

def test_help_popup():
    """Full help-icon scenario: open, verify content, close, reopen, close."""
    # --- open ---
    _click_help_icon_for(_button_label)

    labels = find_labels_overlay()
    assert any(lbl.startswith(_button_label) for lbl in labels), (
        f"Expected the row text {_button_label!r} in the overlay. Got: {labels}"
    )
    assert _close_label in labels, (
        f"Expected close button {_close_label!r} in overlay. Got: {labels}"
    )
    # Body text may be split across lines by LVGL; check the first line.
    first_line = _help_text.split("\n")[0]
    assert any(first_line in lbl for lbl in labels), (
        f"Expected help body starting with {first_line!r} in overlay. Got: {labels}"
    )

    # --- close ---
    click_overlay_by_label(_close_label)
    assert find_labels_overlay() == [], (
        f"Expected empty overlay after Close. Got: {find_labels_overlay()}"
    )

    # --- reopen ---
    _click_help_icon_for(_button_label)
    labels = find_labels_overlay()
    assert any(lbl.startswith(_button_label) for lbl in labels), f"Expected overlay to reopen. Got: {labels}"
    click_overlay_by_label(_close_label)
