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

specter_state = DeviceState()
specter_state.has_battery = True
specter_state.battery_pct = 100
specter_state.charging = False

specter_state._hasQR = True
specter_state._enabledQR = True

specter_state._hasSD = True
specter_state._enabledSD = True
# SD detection reflects the files actually present in /sd (dummy SD import).
if not _ON_HARDWARE:
    specter_state.attach_sd_reader('/sd')
else:
    specter_state._detectedSD = True
    specter_state._SD_hasSeed = True

specter_state._hasSmartCard = True
specter_state._enabledSmartCard = True
specter_state._detectedSmartCard = True
specter_state._SmartCard_hasSeed = True

specter_state._Flash_hasSeed = True

specter_state.pin = "21"
specter_state.lock()

ui_state = UIState()
ui_state.reset_tour_completed()

# ── Test data: a small interconnected seed/wallet fixture ────────────────────
TEST_DATA = True
if TEST_DATA:
    # Seeds: mock BIP85 discovery links active fingerprints sharing a 3-char
    # prefix when the child sorts after the parent (see Seed.known_bip85_derivations).
    _seed_cold = Seed(label="Cold A", fingerprint="c01da001", is_backed_up=True)
    specter_state.add_seed(_seed_cold)
    specter_state.add_seed(Seed(label="Cold A2", fingerprint="c01da002", is_backed_up=True))
    specter_state.add_seed(Seed(label="Cold A2b", fingerprint="c01da02b", is_backed_up=True))

    _seed_hot = Seed(label="Hot B", fingerprint="b07b0001",
                    passphrase="correct horse")
    _seed_hot.passphrase_active = False
    specter_state.add_seed(_seed_hot)
    specter_state.add_seed(Seed(label="Hot B2", fingerprint="b07b0002", is_backed_up=True))
    specter_state.add_seed(Seed(label="Hot B2b", fingerprint="b07b000b", is_backed_up=True))

    # Wallets: mock parent discovery links derivation sub-paths
    # (see Wallet.derivation_parent).
    specter_state.register_wallet(Wallet(
        label="Savings", descriptor="savings", derivation_path="m/84'/0'/0'",
        required_fingerprints=["c01da001"], threshold=1, has_been_synched=True))
    specter_state.register_wallet(Wallet(
        label="Savings Change", descriptor="savings-change",
        derivation_path="m/84'/0'/0'/1'",
        required_fingerprints=["c01da001"], threshold=1))
    specter_state.register_wallet(Wallet(
        label="Savings Receive", descriptor="savings-receive",
        derivation_path="m/84'/0'/0'/0'",
        required_fingerprints=["c01da001"], threshold=1))
    specter_state.register_wallet(Wallet(
        label="Savings Change 2", descriptor="savings-change-2",
        derivation_path="m/84'/0'/0'/1'/2'",
        required_fingerprints=["c01da001"], threshold=1))
    specter_state.register_wallet(Wallet(
        label="Trading", descriptor="trading", derivation_path="m/49'/0'/0'",
        required_fingerprints=["b07b0001"], threshold=1))
    specter_state.register_wallet(Wallet(
        label="Trading Change", descriptor="trading-change",
        derivation_path="m/49'/0'/0'/1'",
        required_fingerprints=["b07b0001"], threshold=1))

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
