"""Fixtures for device integration tests using the disco tool.

The disco tool lives outside this repo for now.  Update DISCO_SCRIPT
when it is merged into the main branch.

Requirements:
  - STM32F469 Discovery board connected via USB
  - MockUI firmware flashed (``nix develop -c make mockui`` + flash)
  - disco tool dependencies installed in the active venv (mpremote, click, pyserial)
"""
import json
import os
import subprocess
import sys
import time

import pytest

# =========================================================================
# Path to the disco CLI script.
# TODO: Update this once disco is merged into specter-playground.
# =========================================================================
DISCO_SCRIPT = os.environ.get(
    "DISCO_SCRIPT",
    "/home/marco/DATA/01_Texte/BitCoin/Specter/f469-disco_disco_tool/scripts/disco",
)

# Run through sys.executable so the test venv (with mpremote etc.) is used.
_CMD = [sys.executable, DISCO_SCRIPT]


def disco_run(*args: str, timeout: int = 15, retries: int = 2) -> str:
    """Run ``disco <args>``, assert exit-code 0, return stripped stdout.

    Retries on transient serial errors (OSError, I/O error).
    """
    last_result = None
    for attempt in range(1 + retries):
        result = subprocess.run(
            [*_CMD, *args],
            capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        # Retry on transient serial errors (various messages from pyserial/mpremote)
        err = result.stderr
        if any(s in err for s in ("OSError", "Input/output error", "Serial error",
                                   "readiness to read", "device disconnected")):
            last_result = result
            time.sleep(3)
            continue
        last_result = result
        break
    assert last_result.returncode == 0, (
        f"disco {' '.join(args)} failed (rc={last_result.returncode}):\n"
        f"stdout: {last_result.stdout}\nstderr: {last_result.stderr}"
    )
    return last_result.stdout.strip()


def find_labels() -> list[str]:
    """Return all visible text labels (len > 1) from the LVGL widget tree."""
    tree = json.loads(disco_run("ui", "screen", "--json"))
    labels = []

    def _walk(node):
        text = node.get("text")
        if text and len(text) > 1:
            labels.append(text)
        for child in node.get("children", []):
            _walk(child)

    for node in (tree if isinstance(tree, list) else [tree]):
        _walk(node)
    return labels


def go_back(delay: float = 1.0):
    """Click the back button (top-left, index 1.0.0) and wait.

    Returns True on success, False if the click failed (no back button).
    """
    result = subprocess.run(
        [*_CMD, "ui", "click", "--index", "1.0.0"],
        capture_output=True, text=True, timeout=15,
    )
    time.sleep(delay)
    return result.returncode == 0


def soft_reset(wait: float = 12.0, poll_interval: float = 2.0):
    """Soft-reset the device and wait for it to be responsive again.

    ``disco repl reset`` sends Ctrl-C + Ctrl-D over pyserial.  The device
    reboots (USB disconnects/reconnects), so the command *always* exits
    with rc=1 and a "Serial error" — that is expected and ignored.

    After firing the reset we poll with ``disco repl exec`` until the
    device is back (up to *wait* seconds).
    """
    # Fire-and-forget: the serial error is expected because USB disconnects.
    subprocess.run(
        [*_CMD, "repl", "reset"],
        capture_output=True, text=True, timeout=10,
    )
    # Wait for the device to reboot and reconnect USB CDC.
    deadline = time.monotonic() + wait
    while time.monotonic() < deadline:
        time.sleep(poll_interval)
        result = subprocess.run(
            [*_CMD, "repl", "exec", "print('pytest-alive')"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and "pytest-alive" in result.stdout:
            time.sleep(3)  # settle time for UI to finish rendering
            return
    raise RuntimeError(
        f"Device did not come back after soft_reset within {wait}s"
    )


_MAIN_MENU_MARKERS = ("What do you want to do?", "Was möchtest du tun?")


def ensure_main_menu(max_depth: int = 5):
    """Navigate back until we're on the main menu.

    Tries go_back() repeatedly.  If the UI is unreachable or go_back()
    fails, falls back to a soft reset (Ctrl-D, USB reconnect).
    """
    for _ in range(max_depth):
        try:
            labels = find_labels()
        except (AssertionError, json.JSONDecodeError):
            # UI command failed — device may still be booting after a reset.
            time.sleep(3)
            continue
        if any(t in labels for t in _MAIN_MENU_MARKERS):
            return
        if not go_back():
            # No back button — soft reset to get to a clean main menu.
            soft_reset()
            continue

    # Final check after exhausting retries.
    labels = find_labels()
    assert any(t in labels for t in _MAIN_MENU_MARKERS), (
        f"Could not navigate to main menu. Labels: {labels}"
    )


# =========================================================================
# Fixtures
# =========================================================================

@pytest.fixture(scope="session", autouse=True)
def _require_device():
    """Fail hard if the board is not reachable — these tests need real hardware."""
    result = subprocess.run(
        [*_CMD, "repl", "exec", "print('pytest-ping')"],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode == 0 and "pytest-ping" in result.stdout, (
        f"Device not reachable via disco tool.\n"
        f"  DISCO_SCRIPT={DISCO_SCRIPT}\n"
        f"  stdout: {result.stdout.strip()}\n"
        f"  stderr: {result.stderr.strip()}"
    )
    # Navigate to main menu (device may be on any screen from a previous run)
    time.sleep(2)
    ensure_main_menu()
    yield
