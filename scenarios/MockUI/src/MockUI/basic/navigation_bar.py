"""NavigationBar — permanent bottom navigation bar for Specter MockUI.

Layout (left-to-right, full width, STATUS_BAR_PCT% height):
    ┌────────────────────────────────────────────────────┐
    │  [Back]   [Seed]   [Home]   [Wallet]   [Device]    │
    │  pos 1    pos 2    pos 3    pos 4      pos 5       │
    └────────────────────────────────────────────────────┘

All five slots have fixed positions (SCREEN_WIDTH / 5 each).

Filled vs outline icon rules
─────────────────────────────
- Home   → filled when current_menu_id == "main"
- Seed   → filled when current_menu_id is in _SEED_MENUS
- Wallet → filled when current_menu_id is in _WALLET_MENUS
- Device → filled when current_menu_id is in _DEVICE_MENUS
- Back   → always filled (CARET_LEFT, no outline variant)

Drop-up ownership
─────────────────
NavigationBar creates SeedDropUp and WalletDropUp in __init__ and owns
their full lifecycle.  A single shared ModalOverlay backdrop is created
lazily on the first open and destroyed once both drop-ups are closed.
"""

import lvgl as lv
from .ui_consts import (
    SCREEN_WIDTH, SCREEN_HEIGHT, STATUS_BTN_HEIGHT, STATUS_BAR_PCT,
    DEFAULT_MODAL_BG_OPA
)
from .symbol_lib import BTC_ICONS
from .widgets.btn import Btn
from .widgets.modal_overlay import ModalOverlay
from .specter_gui_base import SpecterGuiElement, configure_as_bare
from .dropup import SeedDropUp, WalletDropUp, DropUpState
from ..stubs.ui_state import Context

class NavigationBar(SpecterGuiElement):
    """Permanent bottom navigation bar with 5 fixed-position icon buttons."""

    def __init__(self, gui):
        super().__init__(gui)

        self.gui = gui

        # Shared semi-transparent backdrop (one ModalOverlay for both drop-ups)
        self._backdrop = None

        # Create drop-ups — NavigationBar owns their lifecycle
        self._seed_dropup = SeedDropUp(gui)
        self._seed_dropup._on_closed = self._on_any_panel_closed
        self._wallet_dropup = WalletDropUp(gui)
        self._wallet_dropup._on_closed = self._on_any_panel_closed

        # ── Bar container style ───────────────────────────────────────────────
        configure_as_bare(self, width=lv.pct(100), height=lv.pct(STATUS_BAR_PCT))
        self.set_layout(lv.LAYOUT.NONE)   # absolute child positioning
        self.set_scroll_dir(lv.DIR.NONE)

        h = STATUS_BTN_HEIGHT
        w = SCREEN_WIDTH // 5

        names = ["Back", "Seed", "Home", "Wallet", "Device"]
        icons = [BTC_ICONS.CARET_LEFT,
                 BTC_ICONS.KEY_OUTLINE,
                 BTC_ICONS.HOME_OUTLINE,
                 BTC_ICONS.WALLET_OUTLINE,
                 BTC_ICONS.GEAR_OUTLINE]
        cbs = [self._back_cb, self._seed_cb, self._home_cb, self._wallet_cb, self._device_cb]

        self.buttons = {}
        for i, (name, icon, cb) in enumerate(zip(names, icons, cbs)):
            self.buttons[name] = Btn(self, icon=icon, size=(w, h), callback=cb)
            self.buttons[name].make_background_transparent()
            self.buttons[name].align(lv.ALIGN.LEFT_MID, i * w, 0)

    # ── Drop-up management ────────────────────────────────────────────────────────

    def _ensure_backdrop(self):
        """Create shared backdrop if not already present; return its container."""
        if self._backdrop is not None:
            return self._backdrop.overlay
        _panel_max_h = SCREEN_HEIGHT - SCREEN_HEIGHT * STATUS_BAR_PCT // 100
        self._backdrop = ModalOverlay(bg_opa=DEFAULT_MODAL_BG_OPA,
                                      width=SCREEN_WIDTH, height=_panel_max_h)
        self._backdrop.overlay.add_event_cb(self._backdrop_tap_cb, lv.EVENT.CLICKED, None)
        return self._backdrop.overlay

    def _release_backdrop_if_idle(self):
        """Destroy shared backdrop once both drop-ups are fully closed."""
        if self._backdrop is None:
            return
        if (self._seed_dropup.get_state() == DropUpState.CLOSED
                and self._wallet_dropup.get_state() == DropUpState.CLOSED):
            self._backdrop.close()
            self._backdrop = None

    def _on_any_panel_closed(self):
        """Called by a drop-up after its close animation completes."""
        self._release_backdrop_if_idle()
        self.gui.refresh_ui()

    def _backdrop_tap_cb(self, event):
        if event.get_code() == lv.EVENT.CLICKED:
            self.close_dropups()

    def _open_dropup(self, dropup):
        """Ensure the shared backdrop exists and open *dropup* inside it."""
        container = self._ensure_backdrop()
        dropup.open(container)

    def _close_dropup(self, dropup):
        """Close a specific drop-up."""
        if dropup.get_state() in (DropUpState.OPENING, DropUpState.OPEN):
            dropup.close()

    # ── Public API ────────────────────────────────────────────────────────────

    def close_dropups(self):
        """Close any open drop-ups."""
        self._close_dropup(self._seed_dropup)
        self._close_dropup(self._wallet_dropup)

    def refresh(self):
        """Update filled/outline icons and Back button visibility.

        Should be called whenever the current menu changes.
        Reads gui.ui_state.current_menu_id directly.
        """
        if self.device_state.is_locked:
            # If device is locked, nav bar shows no icons and no back button
            for btn in self.buttons.values():
                btn.set_visible(False)
        else:
            # Back button: visible unless we are at the root / home menu
            self.buttons["Back"].set_visible(not self.current_menu == "main")

            seed_open = self._seed_dropup.get_state() in (DropUpState.OPENING, DropUpState.OPEN)
            wallet_open = self._wallet_dropup.get_state() in (DropUpState.OPENING, DropUpState.OPEN)

            # Home icon: filled only when on main and no dropup is open
            if self.current_menu == "main" and not seed_open and not wallet_open:
                self.buttons["Home"].update_icon(BTC_ICONS.HOME)
            else:
                self.buttons["Home"].update_icon(BTC_ICONS.HOME_OUTLINE)
            self.buttons["Home"].set_visible(True)  # Home is always visible when not locked

            # Seed icon: filled when dropup open OR when in a seed menu
            if (self.context == Context.SEED and not wallet_open) or seed_open:
                self.buttons["Seed"].update_icon(BTC_ICONS.KEY)
            else:
                self.buttons["Seed"].update_icon(BTC_ICONS.KEY_OUTLINE)
            #Seed icon: invisible when no seed loaded
            self.buttons["Seed"].set_visible(self.gui.device_state and len(self.gui.device_state.loaded_seeds) > 0)

            # Wallet icon: filled when dropup open OR when in a wallet menu
            if (self.context == Context.WALLET and not seed_open) or wallet_open:
                self.buttons["Wallet"].update_icon(BTC_ICONS.WALLET)
            else:
                self.buttons["Wallet"].update_icon(BTC_ICONS.WALLET_OUTLINE)
            #Wallet icon: invisible when no seed loaded
            self.buttons["Wallet"].set_visible(
                self.gui.device_state and 
                ((len(self.gui.device_state.loaded_seeds) > 0) or
                 (len(self.gui.device_state.registered_wallets) > 1))
            )

            # Device icon
            if self.context == Context.DEVICE and not seed_open and not wallet_open:
                self.buttons["Device"].update_icon(BTC_ICONS.GEAR)
            else:
                self.buttons["Device"].update_icon(BTC_ICONS.GEAR_OUTLINE)
            self.buttons["Device"].set_visible(True)  # Device is always visible when not locked

            # Rebuild drop-up card lists if open (e.g. after passphrase/wallet state change)
            if self._seed_dropup.get_state() == DropUpState.OPEN:
                self._seed_dropup.refresh()
            if self._wallet_dropup.get_state() == DropUpState.OPEN:
                self._wallet_dropup.refresh()

    # ── Button callbacks ──────────────────────────────────────────────────────

    def _dropup_button_cb(self, own_dropup, other_dropup):
        """Shared logic for Seed and Wallet nav buttons.

        - Closes ``other_dropup`` first (mutual exclusion).
        - If already inside ``own_menus``: exit context root or jump to it.
        - Otherwise: toggle ``own_dropup`` open/closed.
        """
        self._close_dropup(other_dropup)
        if own_dropup.get_state() in (DropUpState.OPENING, DropUpState.OPEN):
            self._close_dropup(own_dropup)
        else:
            self._open_dropup(own_dropup)
        self.refresh()

    def _any_animation_ongoing(self):
        """Helper to check if any drop-up is currently animating."""
        return (
            getattr(self.gui, '_animating', True) 
            or self._seed_dropup.get_state() in (DropUpState.OPENING, DropUpState.CLOSING)
            or self._wallet_dropup.get_state() in (DropUpState.OPENING, DropUpState.CLOSING)
        )

    def _back_cb(self, event=None):
        if self._any_animation_ongoing():
            return
        # If a drop-up is open, close it first, then navigate back
        self.close_dropups()
        self.on_navigate(None)

    def _seed_cb(self, event=None):
        if self._any_animation_ongoing():
            return
        self._dropup_button_cb(self._seed_dropup, self._wallet_dropup)

    def _home_cb(self, event=None):
        if self._any_animation_ongoing():
            return
        # History clearing is handled inside on_navigate/show_menu for target="main"
        self.close_dropups()
        self.gui.on_navigate("main")

    def _wallet_cb(self, event=None):
        if self._any_animation_ongoing():
            return
        self._dropup_button_cb(self._wallet_dropup, self._seed_dropup)

    def _device_cb(self, event=None):
        if self._any_animation_ongoing():
            return

        #always close drop ups if they are open
        self.close_dropups()
        
        if self.context != Context.DEVICE:
            self.on_navigate("manage_settings")
        self.refresh()
