"""NavigationBar — permanent bottom navigation bar for Specter MockUI.

Layout (left-to-right, full width):
    ┌────────────────────────────────────────────────────┐
    │  [Back]   [Seed]   [Home]   [Wallet]   [Device]    │
    │  pos 1    pos 2    pos 3    pos 4      pos 5       │
    └────────────────────────────────────────────────────┘

The five buttons are flex-distributed (SPACE_AROUND) by CONTAINER.NAVBAR,
not placed at fixed pixel positions.

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

from .seed_dropup import SeedDropUp
from .wallet_dropup import WalletDropUp
from ..utils import (
    delete_all_children_of,
    set_scroll
)
from ..symbol_lib import BTC_ICONS
from ..widgets import Btn, modal_overlay
from ..templates.specter_gui_base import SpecterGuiElement
from ..templates.dropup import DropUpState
from ..theming import apply_style
from ..ui_state import Context

class NavigationBar(SpecterGuiElement):
    """Permanent bottom navigation bar with 5 flex-distributed icon buttons."""

    def __init__(self, gui):
        super().__init__(gui)
        # Shared semi-transparent backdrop (one modal_overlay for both drop-ups)
        self._backdrop = None
        self._build()

    def _build(self):
        # Create drop-ups — NavigationBar owns their lifecycle
        self._seed_dropup = SeedDropUp()
        self._seed_dropup._on_closed = self._on_any_panel_closed
        self._wallet_dropup = WalletDropUp()
        self._wallet_dropup._on_closed = self._on_any_panel_closed

        # ── Navbar container style ──────────────────────────────────────────────
        apply_style(self, "CONTAINER.NAVBAR")
        apply_style(self, "CONTAINER.SCREEN", lv.STATE.DISABLED)
        set_scroll(self, horizontal=False, vertical=False)

        # (name, initial icon, click callback)
        button_specs = [
            ("Back",   BTC_ICONS.CARET_LEFT,      self._back_cb),
            ("Seed",   BTC_ICONS.KEY_OUTLINE,     self._seed_cb),
            ("Home",   BTC_ICONS.HOME_OUTLINE,    self._home_cb),
            ("Wallet", BTC_ICONS.WALLET_OUTLINE,  self._wallet_cb),
            ("Device", BTC_ICONS.GEAR_OUTLINE,    self._device_cb),
        ]

        self.buttons = {}
        for name, icon, cb in button_specs:
            self.buttons[name] = Btn(self, 
                                     icon=icon, 
                                     callback=cb,
                                     background_style="WIDGET.NAVBAR_BUTTON",
                                     foreground_style="WIDGET.NAVBAR_BUTTON_FG")
            apply_style(self.buttons[name], "APPEARANCE.INVISIBLE", lv.STATE.DISABLED)

        self.refresh()  # initial state

    # ── Drop-up management ────────────────────────────────────────────────────────

    def _ensure_backdrop(self):
        """Create shared backdrop if not already present; return its container."""
        if self._backdrop is not None:
            return self._backdrop
        
        panel_h = self.gui.get_height() - self.get_height()
        self._backdrop = modal_overlay(height=panel_h)
        self._backdrop.add_event_cb(self._backdrop_tap_cb, lv.EVENT.CLICKED, None)
        return self._backdrop

    def _release_backdrop_if_idle(self):
        """Destroy shared backdrop once both drop-ups are fully closed."""
        if self._backdrop is None:
            return
        if (self._seed_dropup.get_state() == DropUpState.CLOSED
                and self._wallet_dropup.get_state() == DropUpState.CLOSED):
            self._backdrop.delete()
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
        backdrop = self._ensure_backdrop()
        dropup.open(backdrop)

    def _close_dropup(self, dropup):
        """Close a specific drop-up."""
        if dropup.get_state() in (DropUpState.OPENING, DropUpState.OPEN):
            dropup.close()

    # ── Public API ────────────────────────────────────────────────────────────

    def close_dropups(self):
        """Close any open drop-ups."""
        self._close_dropup(self._seed_dropup)
        self._close_dropup(self._wallet_dropup)
    
    def rebuild(self):
        """Rebuild the navigation bar and its drop-ups from scratch."""
        if self._seed_dropup:
            self._seed_dropup.cancel_animation()
        if self._wallet_dropup:
            self._wallet_dropup.cancel_animation()
        # Delete existing buttons and drop-ups (if any)
        if self._backdrop is not None:
            self._backdrop.delete()
            self._backdrop = None
        
        self._seed_dropup = None
        self._wallet_dropup = None
        
        delete_all_children_of(self)  # deletes the nav bar buttons
        
        # Rebuild everything
        self._build()

    def refresh(self):
        """Update filled/outline icons and Back button visibility.

        Should be called whenever the current menu changes.
        Reads gui.ui_state.current_menu_id directly.
        """
        if self.device_state.is_locked:
            # If device is locked, nav bar shows no buttons and looks like a screen backdrop
            self.set_state(lv.STATE.DISABLED, True)
            for btn in self.buttons.values():
                btn.set_state(lv.STATE.DISABLED, True)
        else:
            self.set_state(lv.STATE.DISABLED, False)

            # Back button: visible unless we are at the root / home menu
            self.buttons["Back"].set_state(lv.STATE.DISABLED, self.current_menu == "main")

            seed_open = self._seed_dropup.get_state() in (DropUpState.OPENING, DropUpState.OPEN)
            wallet_open = self._wallet_dropup.get_state() in (DropUpState.OPENING, DropUpState.OPEN)

            no_seed_loaded = (self.gui.device_state is None
                              or len(self.gui.device_state.loaded_seeds) == 0)

            # (name, filled icon, outline icon, is-filled condition, is-disabled condition)
            icon_table = [
                ("Home", BTC_ICONS.HOME, BTC_ICONS.HOME_OUTLINE,
                 self.current_menu == "main" and not seed_open and not wallet_open,
                 False),
                ("Seed", BTC_ICONS.KEY, BTC_ICONS.KEY_OUTLINE,
                 (self.context == Context.SEED and not wallet_open) or seed_open,
                 no_seed_loaded),
                ("Wallet", BTC_ICONS.WALLET, BTC_ICONS.WALLET_OUTLINE,
                 (self.context == Context.WALLET and not seed_open) or wallet_open,
                 no_seed_loaded),
                ("Device", BTC_ICONS.GEAR, BTC_ICONS.GEAR_OUTLINE,
                 self.context == Context.DEVICE and not seed_open and not wallet_open,
                 False),
            ]
            for name, icon_filled, icon_outline, is_filled, is_disabled in icon_table:
                self.buttons[name].update_icon(icon_filled if is_filled else icon_outline)
                self.buttons[name].set_state(lv.STATE.DISABLED, is_disabled)

            # Rebuild drop-up card lists if open (e.g. after passphrase/wallet state change)
            if self._seed_dropup.get_state() == DropUpState.OPEN:
                self._seed_dropup.refresh()
            if self._wallet_dropup.get_state() == DropUpState.OPEN:
                self._wallet_dropup.refresh()

    # ── Button callbacks ──────────────────────────────────────────────────────

    def _can_dispatch(self, name):
        """Check if animation is ongoing or the *name* button is disabled.
        """
        if (self.gui.ui_state._is_animating
                or self._seed_dropup.get_state() in (DropUpState.OPENING, DropUpState.CLOSING)
                or self._wallet_dropup.get_state() in (DropUpState.OPENING, DropUpState.CLOSING)):
            return False
        if (self.buttons[name].get_state() & lv.STATE.DISABLED) != 0:
            return False
        return True

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

    def _back_cb(self):
        if self._can_dispatch("Back"):
            self.close_dropups()
            self.on_navigate(None)

    def _seed_cb(self):
        if self._can_dispatch("Seed"):
            self._dropup_button_cb(self._seed_dropup, self._wallet_dropup)

    def _home_cb(self):
        if self._can_dispatch("Home"):
            self.close_dropups()
            self.gui.on_navigate("main")

    def _wallet_cb(self):
        if self._can_dispatch("Wallet"):
            self._dropup_button_cb(self._wallet_dropup, self._seed_dropup)

    def _device_cb(self):
        if self._can_dispatch("Device"):
            self.close_dropups()
            if self.context != Context.DEVICE:
                self.on_navigate("manage_settings")
            self.refresh()
