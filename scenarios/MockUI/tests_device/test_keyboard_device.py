"""On-device integration tests for shared on-screen keyboard flows."""
from conftest import (
    _load_label,
    first_index_by_type,
    first_textarea_index_and_text,
    keyboard_is_hidden,
    click_by_index,
    click_by_label,
    disco_run,
    ensure_main_menu,
    send_keyboard_event,
    set_textarea_text,
    find_labels,
)


def _ensure_wallet_exists_for_manage_menu():
    ensure_main_menu()
    labels = find_labels()
    if _load_label("MENU_MANAGE_WALLET", "en")[0] in labels:
        return

    click_by_label(_load_label("MENU_ADD_WALLET", "en")[0])
    click_by_label(_load_label("MENU_GENERATE_SEEDPHRASE", "en")[0])
    click_by_label(_load_label("COMMON_CREATE", "en")[0])
    ensure_main_menu()


def _open_generate_seed_menu():
    ensure_main_menu()
    click_by_label(_load_label("MENU_ADD_WALLET", "en")[0])
    click_by_label(_load_label("MENU_GENERATE_SEEDPHRASE", "en")[0])


def _open_passphrase_menu():
    ensure_main_menu()
    click_by_label(_load_label("MENU_MANAGE_WALLET", "en")[0])
    click_by_label(_load_label("MENU_SET_PASSPHRASE", "en")[0])


def test_generate_seed_keyboard_open_commit_cancel():
    _open_generate_seed_menu()

    textarea_idx, original_text = first_textarea_index_and_text()

    click_by_index(textarea_idx)
    kb_idx = first_index_by_type("keyboard")
    assert kb_idx is not None, "Keyboard should be visible after clicking textarea"

    set_textarea_text(textarea_idx, "  New Wallet_1  ")
    send_keyboard_event(kb_idx, "READY")

    kb_after_ready = first_index_by_type("keyboard")
    assert kb_after_ready is not None, "Keyboard widget should persist between edits (single manager instance)"
    assert keyboard_is_hidden(kb_after_ready), "Keyboard should be hidden after READY"

    _, committed_text = first_textarea_index_and_text()
    assert committed_text == "  New Wallet_1  ", committed_text

    click_by_index(textarea_idx)
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
    _ensure_wallet_exists_for_manage_menu()
    _open_passphrase_menu()

    textarea_idx, _ = first_textarea_index_and_text()

    click_by_index(textarea_idx)
    kb_idx = first_index_by_type("keyboard")
    assert kb_idx is not None, "Keyboard should open on passphrase textarea"

    set_textarea_text(textarea_idx, "  abc  ")
    send_keyboard_event(kb_idx, "READY")

    alive = disco_run("repl", "exec", "print('alive')")
    assert "alive" in alive, "Device became unresponsive after READY"

    value = disco_run("repl", "exec", "print(repr(specter_state.active_wallet.active_passphrase))")
    assert value.strip().splitlines()[-1] == "'abc'", value

    click_by_label(_load_label("MENU_SET_PASSPHRASE", "en")[0])
    textarea_idx, _ = first_textarea_index_and_text()
    click_by_index(textarea_idx)
    kb_idx = first_index_by_type("keyboard")
    assert kb_idx is not None, "Keyboard should reopen for abort check"

    set_textarea_text(textarea_idx, "will_abort")
    send_keyboard_event(kb_idx, "CANCEL")

    assert keyboard_is_hidden(kb_idx), "Keyboard should be hidden after abort"

    value_after_cancel = disco_run("repl", "exec", "print(repr(specter_state.active_wallet.active_passphrase))")
    assert value_after_cancel.strip().splitlines()[-1] == "'abc'", value_after_cancel


def test_passphrase_keyboard_repeated_commits_no_reset():
    """Regression test: repeated passphrase edit cycles must not crash the device.

    After each commit, on_navigate(None) returns to WalletMenu. We stay there
    and re-open the passphrase menu directly rather than bouncing to main,
    which avoids a navigation round-trip that obscures whether the wallet survived.
    """
    _ensure_wallet_exists_for_manage_menu()
    _open_passphrase_menu()  # first open: main -> wallet menu -> passphrase

    for i in range(4):
        textarea_idx, _ = first_textarea_index_and_text()

        click_by_index(textarea_idx)
        kb_idx = first_index_by_type("keyboard")
        assert kb_idx is not None, "Keyboard should open (iteration {})".format(i)

        value = "loop_{}".format(i)
        set_textarea_text(textarea_idx, value)
        send_keyboard_event(kb_idx, "READY")

        alive = disco_run("repl", "exec", "print('alive')")
        assert "alive" in alive, "Device became unresponsive at iteration {}".format(i)

        state_value = disco_run("repl", "exec", "print(repr(specter_state.active_wallet.active_passphrase))")
        assert state_value.strip().splitlines()[-1] == "'{}'".format(value), state_value

        # After commit, on_navigate(None) returned us to WalletMenu.
        # Re-enter passphrase directly from there for the next iteration.
        if i < 3:
            click_by_label(_load_label("MENU_SET_PASSPHRASE", "en")[0])
