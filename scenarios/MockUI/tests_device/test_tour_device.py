"""On-device integration tests for the guided tour.

Two scenario-based tests, each a complete sequential user journey:

  test_tour_skip_scenario     — initial boot tour: overlay mechanics + skip path
  test_tour_complete_scenario — manual restart: regression check + full completion

The module-scoped ``_fresh_tour_state`` fixture flashes the firmware before the
tests run.  A freshly flashed device has no ui_state_config.json, so the tour
starts when the unlocked main menu first opens — no manual state setup
required.  This also verifies the real out-of-the-box first-boot experience.
The fixture boots the dev preset without its forced tour, so a completed tour
stays completed across resets, and restores the dev preset afterwards.

Scenario 2 relies on scenario 1 having left the device in a clean state
(tour_completed=True, at the main menu).  Running them in isolation is not
supported — execute the full module together.

Index paths within layer_top (confirmed via live tree dump):
  layer_top → [0] overlay_obj → [last] content_obj
    [0] text_box   (label with step description)
    [1] nav_container
      [0] prev_btn
      [1] skip_btn / checkmark_btn
      [2] next_btn
"""
import ast
import json
import os
import tempfile

import pytest

from conftest import (
    _load_label,
    _read_flash_json,
    click_overlay_by_index,
    disco_run,
    dismiss_tour_if_present,
    ensure_main_menu,
    find_labels_overlay,
    click_by_label,
    click_overlay_by_label,
    flash_firmware,
    navigate_to_device_menu,
    navigate_to_preferences_menu,
    reset_board,
    screen_tree,
    unlock,
)

# ---------------------------------------------------------------------------
# Static extraction of INTRO_TOUR_STEPS — no MicroPython needed.
# ---------------------------------------------------------------------------

_NAV_SRC = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "src", "MockUI", "basic", "tour", "guided_tour.py"
))
_DEV_PRESET = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..", "mockui_fw", "presets", "dev.json"
))


def _extract_intro_tour_steps(path: str) -> list:
    """Parse INTRO_TOUR_STEPS from guided_tour.py using ast (no imports)."""
    tree = ast.parse(open(path).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "INTRO_TOUR_STEPS":
                    return ast.literal_eval(node.value)
    raise RuntimeError("INTRO_TOUR_STEPS not found in guided_tour.py")


STEP_KEYS = [step[1] for step in _extract_intro_tour_steps(_NAV_SRC)]


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------

def _tour_overlay_content_idx() -> int:
    """Return the child index of the content box within the tour overlay wrapper.

    ModalOverlay prepends dim strips, so the content box is always the LAST
    child of layer_top.child(0).  Asserts an overlay is present.
    """
    overlays = screen_tree("top")
    assert overlays, "_tour_overlay_content_idx: no overlay present"
    return len(overlays[0]["children"]) - 1


def _click_tour_nav(button: str) -> None:
    """Tap a tour navigation button: 'prev', 'skip', or 'next'."""
    btn_idx = {"prev": 0, "skip": 1, "next": 2}.get(button)
    if btn_idx is None:
        raise ValueError(f"button must be 'prev', 'skip', or 'next', got {button!r}")
    click_overlay_by_index(f"0.{_tour_overlay_content_idx()}.1.{btn_idx}")


def _tour_completed() -> bool:
    data = _read_flash_json("/flash/ui_state_config.json")
    return data.get("tour_completed", False)


def _restart_tour_from_preferences() -> None:
    """Navigate to the Preferences menu and click 'Restart Tour'."""
    restart_label = _load_label("DEVICE_MENU_RESTART_TOUR", "en")[0]
    navigate_to_preferences_menu("en")
    click_by_label(restart_label)


def _dev_preset() -> dict:
    with open(_DEV_PRESET) as f:
        return json.load(f)


def _install_preset(preset: dict) -> None:
    """Make *preset* the board's MockUI preset; it applies at the next reset."""
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(preset, f)
    try:
        disco_run("repl", "cp", f.name, ":/flash/presets/mockui.json")
    finally:
        os.unlink(f.name)


# ---------------------------------------------------------------------------
# Module fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module", autouse=True)
def _fresh_tour_state():
    """Flash firmware, boot the dev preset without its forced tour, then unlock.

    A freshly flashed device has no ui_state_config.json on the filesystem,
    so the tour starts when the main menu first opens, without any manual
    state manipulation.  This also verifies the out-of-the-box first-boot
    experience.
    """
    flash_firmware()
    preset = _dev_preset()
    del preset["ui_state"]["_run_tour_on_startup"]
    _install_preset(preset)
    reset_board()
    unlock()
    yield
    _install_preset(_dev_preset())


# ---------------------------------------------------------------------------
# Scenario 1: initial boot tour — overlay mechanics + skip path
#
# Device state on entry : tour_completed=False, tour overlay visible (set by fixture)
# Device state on exit  : tour_completed=True, at main menu
# ---------------------------------------------------------------------------

def test_tour_skip_scenario():
    """Full skip-path user journey starting from initial boot.

    Covers:
    - tour auto-starts on boot when tour_completed=False
    - prev does nothing at step 0 (its button is invisible there)
    - NEXT advances and PREV returns to step 0
    - Skip dismisses the overlay and sets tour_completed=True
    """
    intro_text  = _load_label("TOUR_INTRO",    "en")[0]
    step1_text  = _load_label(STEP_KEYS[1],    "en")[0]
    skip_text   = _load_label("TOUR_SKIP_BTN", "en")[0]

    # --- tour auto-starts on boot ---
    labels = find_labels_overlay()
    assert intro_text in labels, (
        f"Expected tour intro text in overlay on boot. Got: {labels}"
    )

    # --- prev does nothing at step 0 ---
    _click_tour_nav("prev")
    assert intro_text in find_labels_overlay(), (
        f"Expected to stay at step 0 after PREV. Got: {find_labels_overlay()}"
    )

    # --- NEXT advances to step 1; PREV returns to step 0 ---
    _click_tour_nav("next")
    assert step1_text in find_labels_overlay(), (
        f"Expected step 1 text after NEXT. Got: {find_labels_overlay()}"
    )
    _click_tour_nav("prev")
    assert intro_text in find_labels_overlay(), (
        f"Expected step 0 text after PREV. Got: {find_labels_overlay()}"
    )

    # --- skip dismisses overlay, sets tour_completed=True ---
    click_overlay_by_label(skip_text)
    assert find_labels_overlay() == [], (
        f"Expected empty overlay after skip. Got: {find_labels_overlay()}"
    )
    assert _tour_completed(), "tour_completed should be True after skip"


# ---------------------------------------------------------------------------
# Scenario 2: manual restart — regression check + full completion path
#
# Device state on entry : tour_completed=True, at main menu (left by scenario 1)
# Device state on exit  : tour_completed=True, at main menu
#
# The no-retrigger regression is placed here (not scenario 1) because it only
# manifests when the tour is launched from within an existing navigation context
# (i.e. there is a real back-stack when start_intro_tour fires).  On initial
# boot the history is empty, so the retrigger path cannot occur there.
# ---------------------------------------------------------------------------

def test_tour_complete_scenario():
    """Manual restart: regression check + full completion user journey.

    Covers:
    - Restart Tour from Preferences menu re-launches the overlay
    - Skipping a manually-restarted tour does NOT retrigger when navigating
      away and back (regression: start_intro_tour left in history stack)
    - All tour steps are reachable by walking NEXT from step 0
    - Checkmark on the last step completes the tour
    """
    intro_text = _load_label("TOUR_INTRO",    "en")[0]
    skip_text  = _load_label("TOUR_SKIP_BTN", "en")[0]

    # --- restart tour from preferences, verify overlay appears ---
    assert _tour_completed(), "Expected tour_completed=True at start of scenario 2 (left by scenario 1)"
    _restart_tour_from_preferences()
    assert intro_text in find_labels_overlay(), (
        f"Expected tour intro after restart. Got: {find_labels_overlay()}"
    )

    # --- skip the restarted tour ---
    click_overlay_by_label(skip_text)
    assert find_labels_overlay() == [], (
        f"Expected empty overlay after skip. Got: {find_labels_overlay()}"
    )

    # --- regression: no retrigger after navigate away + back to main ---
    # The tour was launched from within a navigation context (Preferences →
    # main), so start_intro_tour is on the back-stack.  The fix ensures
    # current_menu_id is reset to "main" before launching the overlay, so
    # popping back does not re-fire the tour.
    navigate_to_device_menu()
    ensure_main_menu()
    assert find_labels_overlay() == [], (
        "Tour overlay re-appeared after skip + navigate away + back to main "
        "(regression: start_intro_tour left in history stack)"
    )

    # --- restart tour again for the full completion walk ---
    _restart_tour_from_preferences()
    assert intro_text in find_labels_overlay(), (
        f"Expected tour intro for full walk. Got: {find_labels_overlay()}"
    )

    # --- all steps reachable via NEXT ---
    for i, key in enumerate(STEP_KEYS):
        step_text = _load_label(key, "en")[0]
        labels = find_labels_overlay()
        assert step_text in labels, (
            f"Step {i} ({key}): expected {step_text!r} in overlay. Got: {labels}"
        )
        if i < len(STEP_KEYS) - 1:
            _click_tour_nav("next")

    # --- checkmark on last step completes the tour ---
    _click_tour_nav("skip")
    assert find_labels_overlay() == [], (
        f"Expected empty overlay after checkmark. Got: {find_labels_overlay()}"
    )
    assert _tour_completed(), "tour_completed should be True after checkmark"


# ---------------------------------------------------------------------------
# Persistence across a reset
# ---------------------------------------------------------------------------

def test_tour_completion_survives_reset():
    """A completed tour stays completed after a hard reset."""
    assert _tour_completed(), "Expected tour_completed=True (left by scenario 2)"
    reset_board()
    unlock()
    try:
        assert find_labels_overlay() == [], "Tour reappeared after reset"
        assert _tour_completed(), "tour_completed did not persist across reset"
    finally:
        dismiss_tour_if_present()
        ensure_main_menu()
