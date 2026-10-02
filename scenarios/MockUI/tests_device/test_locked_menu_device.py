"""On-device integration tests for the locked menu (PIN screen).

Single scenario test covering all 8 checkpoints in one sequential run
to minimise board interactions and expensive setup/teardown.

LockedMenu tree layout (screen tree paths 2.0.*):
  scr                          # SpecterGui (lv.screen)
  └─ .content (child 2)
     └─ .current_screen        # LockedMenu (child 0 of content)
        ├─ title_bar (child 0)
        └─ body     (child 1)
           ├─ instr label  (child 0)
           ├─ mask_lbl     (child 1)
           ├─ row 0        (child 2)   [digit, digit, digit]
           ├─ row 1        (child 3)   [digit, digit, digit]
           ├─ row 2        (child 4)   [digit, digit, digit]
           └─ last row     (child 5)   [Del (icon), digit, OK (icon)]

DeviceBar tree layout (for lock-button discovery):
  screen[0]     DeviceBar
  ├─ [0] left_container
  │   └─ [0] lock_btn  ← target
  ├─ [1] center_container
  └─ [2] right_container

Checkpoints (in order):
  CP1   – lock button activates the PIN screen
  CP2   – key order is shuffled (not "0123456789")    [retry once on collision]
  CP3   – entering a digit shows * in the mask (not the digit in clear)
  CP4   – wrong PIN (empty buffer → OK) keeps device locked
  CP5   – Del removes the last digit
  CP6   – correct PIN unlocks the device
  CP7/8 – re-locking gives a different key order      [retry once on collision]
"""
import pytest

from conftest import (
    _load_label,
    _supported_lang_codes,
    click_by_index,
    ensure_main_menu,
    find_labels,
    node_at,
    screen_tree,
    ui,
    unlock,
    walk_with_path,
)


# ---------------------------------------------------------------------------
# Module-local helpers
# ---------------------------------------------------------------------------

def _get_digit_order() -> list[str]:
    """Return the 10 PIN-keypad digits in visual (tree BFS) order.

    Uses a local tree walk that includes single-character labels — the shared
    ``find_labels()`` helper filters those out (len > 1).
    """
    digits = []
    for _path, node in walk_with_path(screen_tree()):
        text = node.get("text", "")
        if len(text) == 1 and text in "0123456789":
            digits.append(text)
    return digits


def _get_mask_text() -> str:
    """Read the PIN mask label: content (2) → LockedMenu (0) → body (1) → mask_lbl (1)."""
    return node_at("2.0.1.1").get("text") or ""


def _get_device_pin() -> str:
    """Read the configured PIN from live device state — never hardcoded."""
    return ui({"action": "get_state"})["specter"]["pin"]

def _set_device_pin(pin: str) -> None:
    """Set the configured PIN on the live device."""
    ui({"action": "set_state", "attr": "pin", "value": pin})


def _find_lock_btn_index() -> str:
    """Return the tree index of the lock button (DeviceBar → left → lock_btn).

    Navigates children[0][0][0] of the screen tree dynamically so the test
    is resilient to future layout refactors.
    """
    tree = screen_tree()
    try:
        lock_btn = tree[0]["children"][0]["children"][0]
        assert lock_btn.get("type", "") == "button", (
            f"Expected button at 0.0.0, got: {lock_btn.get('type')}"
        )
        return "0.0.0"
    except (IndexError, KeyError):
        pass

    # Fallback: BFS search for first button in subtree 0.0
    for path, node in walk_with_path(screen_tree()):
        if path.startswith("0.0") and node.get("type", "") == "button":
            return path

    raise AssertionError("Could not locate lock button in screen tree")


def _click_digit(d: str) -> None:
    """Tap a PIN pad digit by its text label.

    Bypasses ``click_by_label``'s len > 1 filter — digits are single chars.
    """
    ui({"action": "click", "text": d})


def _click_del() -> None:
    """Tap Del (icon-only): child 0 of the last keypad row (body.child(5))."""
    click_by_index("2.0.1.5.0")


def _click_ok() -> None:
    """Tap OK (icon-only): child 2 of the last keypad row (body.child(5))."""
    click_by_index("2.0.1.5.2")


def _lock_device() -> bool:
    lock_idx = _find_lock_btn_index()
    click_by_index(lock_idx)
    return _locked_screen_visible()

def _unlock_device() -> bool:
    pin = _get_device_pin()
    for d in pin:
        _click_digit(d)
    _click_ok()
    return _main_menu_visible()


def _locked_screen_visible() -> bool:
    labels = find_labels()
    return any(
        t in labels
        for t in _load_label("LOCKED_MENU_TITLE", *_supported_lang_codes())
    )


def _main_menu_visible() -> bool:
    labels = find_labels()
    return any(
        t in labels
        for t in _load_label("MAIN_MENU_TITLE", *_supported_lang_codes())
    )

# ---------------------------------------------------------------------------
# Module fixture — runs once before the tests in this module
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
def _setup_locked_menu_test():
    """Ensure device is on the main menu and unlocked before the scenario."""
    # Guarantee unlocked state in case a previous run left the device locked.
    unlock()
    _set_device_pin("42")  # set a known PIN for the tests
    ensure_main_menu()
    yield


# ---------------------------------------------------------------------------
# The scenario
# ---------------------------------------------------------------------------

def test_locked_menu_scenario():
    """Full PIN-screen user journey — 8 sequential checkpoints in one run."""
    did_retry = False

    pin = _get_device_pin()
    assert len(pin) >= 2, f"Device PIN too short for device tests: {pin!r}"

    # ── CP1: lock button activates the PIN screen ────────────────────────────
    assert _lock_device(), (
        "CP1: PIN screen not shown after clicking lock button"
    )

    order1 = _get_digit_order()

    # ── CP2: key order is shuffled (not "0123456789"); allow one retry ───────
    if order1 == list("0123456789"):
        #Re-Try, verify other CPs along the way to not waste time
        assert _unlock_device(), (
            f"CP2.1: device not unlocked after entering correct PIN {pin!r}"
        )
        assert _lock_device(), (
            "CP2.2: failed to re-lock device on retry after natural order detected"
        )

        order1 = _get_digit_order()        
        assert order1 != list("0123456789"), (
            "CP2.2: digits appeared in natural order on two consecutive lock-screen activations — hardware RNG suspect" 
        )
        did_retry = True

    # ── CP3: entering one digit shows * in mask, not the digit in clear ──────
    _click_digit(pin[0])
    mask = _get_mask_text()
    assert mask == "*", (
        f"CP3: expected mask='*' after entering one digit, got {mask!r}"
    )
    assert mask != pin[0], (
        f"CP3: digit {pin[0]!r} shown in cleartext in mask label"
    )

    # ── CP4: Del removes the last digit ──────────────────────────────────────
    _click_del()
    assert _get_mask_text() == "", (
        "CP4: Del did not remove the digit from the mask"
    )

    # ── CP5: wrong PIN → OK: keeps device locked ───────────────
    # pin_buf currently empty; Pin is at least two digits; so enter one digit then OK = wrong PIN
    _click_digit(pin[0])
    _click_ok()
    assert _locked_screen_visible(), (
        "CP5: device unlocked on wrong PIN — unlock check is broken"
    )
    assert _get_mask_text() == "", (
        "CP5: pin buffer not cleared after failed unlock attempt"
    )


    # ── CP6: correct PIN unlocks the device ──────────────────────────────────
    if not did_retry:
        assert _unlock_device(), (
            f"CP6: device not unlocked after entering correct PIN {pin!r}"
        )

    # ── CP7: re-locking produces a different digit order; allow one retry ──
    if not did_retry:
        assert _lock_device(), (
            "CP7: failed to lock device for second time to check for different key order"
        )
        order2 = _get_digit_order()
        if order2 == order1:
            assert _unlock_device(), (
                "CP7.1: device not unlocked after entering correct PIN — unlock check is broken"
            )
            assert _lock_device(), (
                "CP7.2: failed to re-lock device on retry after identical key order detected"
            )
            order2 = _get_digit_order()
        
        assert order2 != order1, (
            "CP7: key order unchanged after re-locking twice — hardware RNG suspect"
        )
    
    # return to initial state for next test
    assert _unlock_device(), (
        f"Final step: device not unlocked after entering correct PIN {pin!r}"
    )
