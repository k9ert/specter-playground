"""On-device integration tests for shared on-screen keyboard flows.

The keyboard edits a textarea; the screen around it decides what happens to
the text. On the passphrase screen, READY only fills the field (trimmed) and
the passphrase is stored on the active seed when the screen's OK is tapped.

A seed is active only inside its context: opening the main menu clears it.
The passphrase tests therefore pick a seed like a user, through the
navigation bar's Seed button and the seed drop-up, and stay in that context.
"""
from conftest import (
    _load_label,
    first_index_by_type,
    first_textarea_index_and_text,
    keyboard_is_hidden,
    click_by_index,
    focus_text_field,
    screen_tree,
    walk_with_path,
    click_by_label,
    disco_run,
    ensure_main_menu,
    send_keyboard_event,
    set_textarea_text,
    ui,
)


def _open(menu_id: str) -> None:
    ensure_main_menu()
    ui({"action": "navigate", "target": menu_id})


def _repl_value(expr: str) -> str:
    return disco_run("repl", "exec", f"print(repr({expr}))").strip().splitlines()[-1]


def _passphrase() -> str:
    return _repl_value("scr.ui_state.active_seed.passphrase")


# Seed from main.py's test data; the navigation bar's Seed button opens the seed drop-up.
_SEED = "Cold A"
_SEED_BUTTON = "1.1.0"


def _open_seed_menu() -> None:
    """Make _SEED the active seed by choosing it in the seed drop-up."""
    ensure_main_menu()
    click_by_index(_SEED_BUTTON)
    click_by_label(_SEED, layer="top")
    assert ui({"action": "get_state"})["ui"]["current_menu_id"] == "manage_seedphrase"
    assert _repl_value("scr.ui_state.active_seed.label") == repr(_SEED)


def _open_passphrase_menu() -> None:
    """From the seed menu, open the passphrase entry for the active seed.

    Its label changes once the seed has a passphrase.
    """
    if ui({"action": "get_state"})["ui"]["current_menu_id"] != "manage_seedphrase":
        _open_seed_menu()
    key = "MENU_CHANGE_CLEAR_PASSPHRASE" if _passphrase() not in ("None", "''") else "MENU_SET_PASSPHRASE"
    click_by_label(_load_label(key, "en")[0])


def _passphrase_field() -> str:
    """The passphrase field is the last textarea; the context bar's seed name comes first."""
    fields = [path for path, node in walk_with_path(screen_tree()) if node.get("type") == "textarea"]
    assert fields, "No textarea on the passphrase screen"
    return fields[-1]


def _type_into_passphrase(text: str, key: str) -> str:
    """Open the keyboard on the passphrase field, type *text*, press READY or CANCEL."""
    textarea_idx = _passphrase_field()
    focus_text_field(textarea_idx)
    kb_idx = first_index_by_type("keyboard")
    assert kb_idx is not None, "Keyboard should open on passphrase textarea"
    set_textarea_text(textarea_idx, text)
    send_keyboard_event(kb_idx, key)
    assert "alive" in disco_run("repl", "exec", "print('alive')"), f"Device became unresponsive after {key}"
    return kb_idx


def test_generate_seed_keyboard_open_commit_cancel():
    _open("generate_seedphrase")

    textarea_idx, original_text = first_textarea_index_and_text()

    focus_text_field(textarea_idx)
    kb_idx = first_index_by_type("keyboard")
    assert kb_idx is not None, "Keyboard should be visible after clicking textarea"

    set_textarea_text(textarea_idx, "  New Wallet_1  ")
    send_keyboard_event(kb_idx, "READY")

    kb_after_ready = first_index_by_type("keyboard")
    assert kb_after_ready is not None, "Keyboard widget should persist between edits (single manager instance)"
    assert keyboard_is_hidden(kb_after_ready), "Keyboard should be hidden after READY"

    _, committed_text = first_textarea_index_and_text()
    assert committed_text == "  New Wallet_1  ", committed_text

    focus_text_field(textarea_idx)
    kb_idx = first_index_by_type("keyboard")
    assert kb_idx is not None, "Keyboard should reopen"

    set_textarea_text(textarea_idx, "TemporaryName")
    send_keyboard_event(kb_idx, "CANCEL")

    assert keyboard_is_hidden(kb_idx), "Keyboard should be hidden after CANCEL"

    _, text_after_cancel = first_textarea_index_and_text()
    assert text_after_cancel == "  New Wallet_1  ", (
        "Cancel should restore last committed value",
        text_after_cancel,
    )

    if original_text != "  New Wallet_1  ":
        click_by_label(_load_label("COMMON_CREATE", "en")[0])


def test_passphrase_keyboard_commit_and_abort_no_freeze():
    _open_seed_menu()

    _open_passphrase_menu()
    _type_into_passphrase("  abc  ", "READY")
    click_by_label(_load_label("COMMON_OK", "en")[0])
    assert _passphrase() == "'abc'", _passphrase()

    _open_passphrase_menu()
    kb_idx = _type_into_passphrase("will_abort", "CANCEL")
    assert keyboard_is_hidden(kb_idx), "Keyboard should be hidden after abort"
    click_by_label(_load_label("COMMON_CANCEL", "en")[0])
    assert _passphrase() == "'abc'", _passphrase()


def test_passphrase_keyboard_repeated_commits_no_reset():
    """Regression test: repeated passphrase edit cycles must not crash the device."""
    _open_seed_menu()

    for i in range(4):
        value = "loop_{}".format(i)
        _open_passphrase_menu()
        _type_into_passphrase(value, "READY")
        click_by_label(_load_label("COMMON_OK", "en")[0])
        assert _passphrase() == "'{}'".format(value), "iteration {}: {}".format(i, _passphrase())
