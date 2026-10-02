# main.py - MockUI entry point (STM32F469 Discovery + unix simulator)
import gc
import sys
import display
import lvgl as lv
import utime as time

# Detect platform: sys.platform is 'linux'/'darwin' on unix simulator,
# 'pyboard' on STM32 hardware. (import pyb is NOT reliable — a stub exists for unix.)
_ON_HARDWARE = sys.platform not in ('linux', 'darwin')

# --- Simulator environment setup (the only place with platform-specific logic) ---
if not _ON_HARDWARE:
    import os
    # Mount build/flash_image as /flash so firmware code sees the same path as on
    # hardware. make build-i18n places lang_*.bin files in build/flash_image/i18n/.
    # os.getcwd() is the project root when launched via `make simulate`.
    os.mount(os.VfsPosix(os.getcwd() + '/build/flash_image'), '/flash')
    # Mount a host directory as /sd so the dummy SD import sees the same path as
    # on hardware.  Files dropped into build/sd_image/ appear on the virtual card.
    # TODO: DUMMY CODE — replace with the real SD stack.
    _sd_dir = os.getcwd() + '/build/sd_image'
    if 'sd_image' not in os.listdir(os.getcwd() + '/build'):
        os.mkdir(_sd_dir)
    os.mount(os.VfsPosix(_sd_dir), '/sd')
    # Disable SDL autoupdate so our manual loop drives it.
    display.init(False)
else:
    # Hardware: display.init() drives LVGL from a 30 Hz timer, so main.py must not loop.
    display.init()
# --- End simulator setup ---

from MockUI import SpecterGui, DeviceState, UIState, Wallet, Seed

gc.collect()

# ── Preset: initial device and UI state ──────────────────────────────────────
# Optional; production firmware has none and starts from the defaults.
# `make` copies scenarios/mockui_fw/presets/<MOCKUI_PRESET>.json here.
# Format (see presets/dev.json): "device_state"/"ui_state" set attributes,
# "seeds"/"wallets" list the keyword arguments for Seed/Wallet.
PRESET_FILE = "/flash/presets/mockui.json"


def _load_preset():
    import json
    try:
        with open(PRESET_FILE) as f:
            return json.load(f)
    except OSError:
        return {}


def _apply_attrs(obj, attrs):
    for name, value in attrs.items():
        if hasattr(obj, name):
            setattr(obj, name, value)
        else:
            print("Preset: skipping unknown attribute", name)


def _build_state(preset):
    device_state = DeviceState()
    _apply_attrs(device_state, preset.get("device_state", {}))
    for fields in preset.get("seeds", []):
        device_state.add_seed(Seed(**fields))
    for fields in preset.get("wallets", []):
        device_state.register_wallet(Wallet(**fields))
    ui_state = UIState()
    _apply_attrs(ui_state, preset.get("ui_state", {}))
    return device_state, ui_state


try:
    specter_state, ui_state = _build_state(_load_preset())
except Exception as e:
    print("Preset", PRESET_FILE, "is invalid, using defaults:", repr(e))
    specter_state, ui_state = DeviceState(), UIState()
# SD detection reflects the files actually present in /sd (dummy SD import).
if not _ON_HARDWARE:
    specter_state.attach_sd_reader('/sd')

gc.collect()

scr = SpecterGui(specter_state, ui_state)


# Start TCP control server when --control flag is passed (simulator only)
if not _ON_HARDWARE and '--control' in sys.argv:
    from sim_control import ControlServer
    ControlServer(scr)

if not _ON_HARDWARE:
    while True:
        display.update(30)
        time.sleep_ms(30)
