"""Fixtures for on-device tests on an STM32F469 Discovery board.

The tests drive the board through specter-devtools (the devtools/ submodule).
Widget trees and taps go through its control contract: a tap works like a
finger, refuses covered widgets, and replies once the UI has settled. Resets,
flashing, and REPL checks use its f469/disco tool. Set devtools up once as
described in devtools/README.md.

By default the session builds MockUI firmware with German and the dev preset
(ADD_LANG=de MOCKUI_PRESET=dev) and flashes it. Pass --no-build-flash to keep
the firmware already on the board.
"""
import json
import os
import subprocess
import sys

import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_DEVTOOLS = os.path.join(_REPO_ROOT, "devtools")
sys.path.insert(0, os.path.join(_DEVTOOLS, "src"))

from specter_devtools.artifacts import visible_labels  # noqa: E402
from specter_devtools.targets import F469Target  # noqa: E402

DISCO = os.environ.get("DISCO_SCRIPT", os.path.join(_DEVTOOLS, "f469", "disco"))
_board = F469Target(DISCO)

_FIRMWARE = os.path.join(_REPO_ROOT, "bin", "mockui.bin")
_LANG_DIR = os.path.join(
    _REPO_ROOT, "scenarios", "MockUI", "src", "MockUI", "basic", "i18n", "languages",
)

# =========================================================================
# Language label loading — single source of truth from the JSON files.
# =========================================================================

def _supported_lang_codes() -> list[str]:
    """Return all language codes found in the language JSON directory."""
    codes = []
    for name in sorted(os.listdir(_LANG_DIR)):
        if name.startswith("specter_ui_") and name.endswith(".json"):
            codes.append(name[len("specter_ui_"):-len(".json")])
    return codes


def _load_metadata(key: str, *lang_codes: str) -> tuple[str, ...]:
    """Return the *_metadata* value for *key* from each requested language file."""
    results = []
    for lang in lang_codes:
        path = os.path.join(_LANG_DIR, f"specter_ui_{lang}.json")
        try:
            with open(path) as f:
                data = json.load(f)
            v = data.get("_metadata", {}).get(key)
            if v:
                results.append(v)
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass
    return tuple(results)


def _load_label(key: str, *lang_codes: str) -> tuple[str, ...]:
    """Return the translated text for *key* from each requested language file.

    Unknown keys or missing files are silently skipped so the tuple always
    contains only real strings.
    """
    results = []
    for lang in lang_codes:
        path = os.path.join(_LANG_DIR, f"specter_ui_{lang}.json")
        try:
            with open(path) as f:
                data = json.load(f)
            v = data.get("translations", {}).get(key)
            if v is not None:
                text = v.get("text", v) if isinstance(v, dict) else v
                if text:
                    results.append(text)
        except (FileNotFoundError, KeyError, json.JSONDecodeError):
            pass
    return tuple(results)


def pytest_addoption(parser):
    parser.addoption(
        "--no-build-flash",
        action="store_true",
        default=False,
        help=(
            "Skip the build + flash step. Use only if you have already flashed "
            "a MockUI binary built with ADD_LANG=de MOCKUI_PRESET=dev."
        ),
    )


# =========================================================================
# Board access through devtools
# =========================================================================

def disco_run(*args: str, timeout: int = 120) -> str:
    """Run devtools' ``disco <args>``, assert exit code 0, return stripped stdout."""
    result = subprocess.run([DISCO, *args], capture_output=True, text=True, timeout=timeout)
    assert result.returncode == 0, (
        f"disco {' '.join(args)} failed (rc={result.returncode}):\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    return result.stdout.strip()


def ui(request: dict) -> dict:
    """Send one devtools control request; the test fails if the board refuses it.

    A busy board (garbage collection) can outlast the default 3 s settle wait;
    then wait once more before the next request taps a widget mid-animation.
    """
    result = _board.request(request)
    assert result.get("ok"), f"{request} failed: {result.get('error')}"
    if result.get("settled") is False:
        settled = _board.request({"action": "wait", "timeout_ms": 10000}).get("settled")
        assert settled, f"UI still animating 10 s after {request}"
    return result


def flash_firmware() -> None:
    """Flash bin/mockui.bin and wait until the board's REPL answers again."""
    print("[device-tests] Flashing firmware ...")
    disco_run("flash", "program", _FIRMWARE, timeout=300)
    disco_run("repl", "wait")


def reset_board() -> None:
    """Hard-reset the board (never a soft reset) and wait for its REPL."""
    disco_run("repl", "reset")


def unlock() -> None:
    """Unlock MockUI, which boots locked, and open the main menu."""
    ui({"action": "set_state", "attr": "is_locked", "value": False})
    ui({"action": "navigate", "target": "main"})


def restart_board() -> None:
    """Hard-reset the board and get back to an unlocked main menu.

    The dev preset locks the device and marks the tour as pending on every boot.
    """
    reset_board()
    unlock()
    dismiss_tour_if_present()
    ensure_main_menu()


def _read_flash_json(path: str) -> dict:
    """Read a JSON file from the board's flash."""
    return json.loads(disco_run("repl", "cat", path))


# =========================================================================
# Widget trees and taps
# =========================================================================

def screen_tree(layer: str = "screen") -> list[dict]:
    """Return the children of the active screen (or the top layer) as devtools reports them."""
    return ui({"action": "tree", "layer": layer})["tree"]["root"]["children"]


def walk_with_path(nodes):
    """Yield (path, node) pairs in breadth-first order; paths look like '1.0.2'."""
    queue = [(str(i), n) for i, n in enumerate(nodes)]
    while queue:
        path, node = queue.pop(0)
        yield path, node
        for i, child in enumerate(node.get("children", [])):
            queue.append((path + "." + str(i), child))


def node_at(index_str: str, layer: str = "screen") -> dict:
    """Return the tree node at a dot-separated index such as '2.0.1'."""
    for path, node in walk_with_path(screen_tree(layer)):
        if path == index_str:
            return node
    raise AssertionError(f"No widget at {index_str!r} on the {layer} layer")


def _labels(layer: str) -> list[str]:
    root = ui({"action": "tree", "layer": layer})["tree"]["root"]
    return [text for text in visible_labels(root) if len(text) > 1]


def find_labels() -> list[str]:
    """Return all text labels (len > 1) on the active screen."""
    return _labels("screen")


def find_labels_overlay() -> list[str]:
    """Return all text labels (len > 1) on the top layer (overlays)."""
    return _labels("top")


def click_by_label(label: str, layer: str = "screen") -> None:
    """Assert *label* is shown, then tap it and wait until the UI has settled."""
    labels = _labels(layer)
    assert label in labels, f"Cannot find {label!r} on the {layer} layer. Labels: {labels}"
    ui({"action": "click", "text": label, "layer": layer})


def click_by_index(index_str: str, layer: str = "screen") -> None:
    """Tap the widget at a dot-separated tree index (e.g. '1.0.2')."""
    ui({"action": "click", "path": [int(p) for p in index_str.split(".")], "layer": layer})


def focus_text_field(index_str: str) -> None:
    """Tap a text field to open the keyboard.

    Its blinking cursor is an endless LVGL animation, so the UI never counts as
    settled while the field has focus; allow 1 s for the keyboard to appear.
    """
    request = {"action": "click", "path": [int(p) for p in index_str.split(".")], "timeout_ms": 1000}
    result = _board.request(request)
    assert result.get("ok"), f"{request} failed: {result.get('error')}"


def click_by_partial_label(partial: str) -> None:
    """Tap the first label on the screen that contains *partial*."""
    labels = find_labels()
    matches = [lbl for lbl in labels if partial in lbl]
    assert matches, f"No label containing {partial!r}. Visible labels: {labels}"
    ui({"action": "click", "text": matches[0]})


def click_overlay_by_label(label: str) -> None:
    click_by_label(label, layer="top")


def click_overlay_by_index(index_str: str) -> None:
    """Tap an overlay widget by tree index, e.g. an icon-only button."""
    click_by_index(index_str, layer="top")


def first_index_by_type(widget_type: str):
    """Return the first widget index of the given type, or None."""
    for path, node in walk_with_path(screen_tree()):
        if node.get("type") == widget_type:
            return path
    return None


def first_textarea_index_and_text() -> tuple[str, str]:
    """Return (index, text) of the first textarea on the screen."""
    for path, node in walk_with_path(screen_tree()):
        if node.get("type") == "textarea":
            return path, node.get("text", "")
    raise AssertionError("No textarea found on current screen")


def set_textarea_text(index_str: str, text: str) -> None:
    """Replace a textarea's text through devtools' write_text."""
    ui({"action": "write_text", "path": [int(p) for p in index_str.split(".")], "text": text})


def obj_expr(index_str: str) -> str:
    """Build a lv.screen_active().get_child(...) expression for a tree index."""
    expr = "lv.screen_active()"
    for part in index_str.split("."):
        expr += ".get_child({})".format(part)
    return expr


def send_keyboard_event(index_str: str, event_name: str) -> None:
    """Send a lv.EVENT.* to the keyboard, then wait until the UI has settled.

    LVGL draws the keyboard's keys inside one widget, so devtools cannot tap
    READY or CANCEL individually; the event stands in for that key.
    """
    code = "import lvgl as lv; kb={}; kb.send_event(lv.EVENT.{},None); print('OK')".format(
        obj_expr(index_str), event_name
    )
    out = disco_run("repl", "exec", code)
    assert out.strip().splitlines()[-1] == "OK", out
    ui({"action": "wait"})


def keyboard_is_hidden(index_str: str) -> bool:
    """Return True if the keyboard at index has the HIDDEN flag set."""
    code = "import lvgl as lv; kb={}; print(kb.has_flag(lv.obj.FLAG.HIDDEN))".format(obj_expr(index_str))
    out = disco_run("repl", "exec", code)
    return out.strip().splitlines()[-1] == "True"


# =========================================================================
# MockUI navigation
# =========================================================================

def _on_main_menu() -> bool:
    return ui({"action": "get_state"})["ui"]["current_menu_id"] == "main"


def ensure_main_menu(max_depth: int = 10) -> None:
    """Go back through MockUI's menu history to the main menu, like the back button."""
    for _ in range(max_depth):
        if _on_main_menu():
            return
        if not ui({"action": "get_state"})["ui"]["history"]:
            break
        ui({"action": "navigate", "target": "back"})
    if not _on_main_menu():
        ui({"action": "navigate", "target": "main"})
    assert _on_main_menu(), f"Could not reach the main menu. Labels: {find_labels()}"


# MockUI's navigation bar (screen child 1) wraps each button in a container:
# Back 1.0.0, Seed 1.1.0, Home 1.2.0, Wallet 1.3.0, Device (gear) 1.4.0.
_DEVICE_BUTTON = "1.4.0"


def navigate_to_settings_menu() -> None:
    """Tap the navigation bar's Device (gear) button, which opens the settings menu."""
    ensure_main_menu()
    click_by_index(_DEVICE_BUTTON)
    assert ui({"action": "get_state"})["ui"]["current_menu_id"] == "manage_settings"


def navigate_to_language_menu(lang: str) -> None:
    """Navigate from the main menu to the language selection menu.

    *lang* is the language code currently active on the device (e.g. "en", "de").
    The Language button shows a dynamic label (e.g. "Select Language (EN)"),
    so we match on the base translation string only.
    """
    navigate_to_settings_menu()
    click_by_partial_label(_load_label("MENU_LANGUAGE", lang)[0])


def navigate_to_device_menu(lang: str = "en") -> None:
    """Navigate from the main menu to the Security settings menu."""
    navigate_to_settings_menu()
    click_by_label(_load_label("MENU_SETTINGS_SECURITY", lang)[0])


def navigate_to_preferences_menu(lang: str = "en") -> None:
    """Navigate from the main menu to the Preferences menu."""
    navigate_to_settings_menu()
    click_by_label(_load_label("MENU_MANAGE_PREFERENCES", lang)[0])


def dismiss_tour_if_present() -> None:
    """Skip every tour overlay on the top layer, topmost first, in any language.

    MockUI starts another tour each time the main menu opens while the tour
    is pending, so overlays can stack.
    """
    skip_labels = set(_load_label("TOUR_SKIP_BTN", *_supported_lang_codes()))
    for _ in range(20):
        overlays = screen_tree("top")
        topmost = str(len(overlays) - 1)
        skip = [path for path, node in walk_with_path(overlays)
                if node.get("text") in skip_labels and path.split(".")[0] == topmost]
        if not skip:
            return
        click_by_index(skip[0], layer="top")
    assert not find_labels_overlay(), f"Tour overlays did not close: {find_labels_overlay()}"


def ensure_english() -> None:
    """Ensure the device UI is in English, switching if needed.

    Detects the current language from visible main-menu labels and, if not
    English, navigates to the language menu and selects English.
    """
    ensure_main_menu()
    en_title = _load_label("MAIN_MENU_TITLE", "en")[0]
    if en_title in find_labels():
        return
    for lang in _supported_lang_codes():
        if lang == "en":
            continue
        if _load_label("MAIN_MENU_TITLE", lang)[0] in find_labels():
            navigate_to_language_menu(lang)
            click_by_label(_load_metadata("language_name", "en")[0])
            ensure_main_menu()
            return
    raise RuntimeError(f"Cannot determine current UI language. Labels: {find_labels()}")


# =========================================================================
# Fixtures
# =========================================================================

@pytest.fixture(scope="session", autouse=True)
def _require_device(request):
    """Build firmware with German and the dev preset and flash it, then open an unlocked main menu.

    The build+flash step is skipped only when --no-build-flash is passed.
    """
    if not request.config.getoption("--no-build-flash"):
        print("\n[device-tests] Building MockUI firmware with ADD_LANG=de MOCKUI_PRESET=dev ...")
        subprocess.run(
            ["nix", "develop", "-c", "make", "mockui", "ADD_LANG=de", "MOCKUI_PRESET=dev"],
            cwd=_REPO_ROOT,
            check=True,
        )
        flash_firmware()
    else:
        disco_run("repl", "wait")

    assert ui({"action": "capabilities"})["application"], (
        "MockUI is not running on the board: its REPL has no `scr` object"
    )
    unlock()
    dismiss_tour_if_present()
    ensure_main_menu()
    ensure_english()
    yield


@pytest.fixture(scope="module", autouse=True)
def _fresh_board(_require_device):
    """Start each test module from a reset board: a clean heap and the dev preset's test data."""
    restart_board()
