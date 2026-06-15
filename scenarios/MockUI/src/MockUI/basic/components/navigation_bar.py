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

from .seed_dropup import SeedDropUp
from .wallet_dropup import WalletDropUp
from ..utils import (
    SCREEN_WIDTH, SCREEN_HEIGHT, STATUS_BTN_HEIGHT, STATUS_BAR_H,
    BTC_ICON_WIDTH,
    style_as_flex_container
)
from ..symbol_lib import BTC_ICONS
from ..widgets import Btn, modal_overlay
from ..templates.specter_gui_base import SpecterGuiElement
from ..templates.dropup import DropUpState
from ..theming import apply_style
from ..ui_state import Context

class NavigationBar(SpecterGuiElement):
    """Permanent bottom navigation bar with 5 fixed-position icon buttons."""

    def __init__(self, gui):
        super().__init__(gui)
        # Shared semi-transparent backdrop (one modal_overlay for both drop-ups)
        self._backdrop = None

        # Create drop-ups — NavigationBar owns their lifecycle
        self._seed_dropup = SeedDropUp()
        self._seed_dropup._on_closed = self._on_any_panel_closed
        self._wallet_dropup = WalletDropUp()
        self._wallet_dropup._on_closed = self._on_any_panel_closed

        # ── Screen backdrop style ───────────────────────────────────────────────
        style_as_flex_container(self, flow=lv.FLEX_FLOW.ROW, 
                                width=SCREEN_WIDTH, height=STATUS_BAR_H,
                                main_align=lv.FLEX_ALIGN.SPACE_AROUND,
                                cross_align=lv.FLEX_ALIGN.CENTER,
                                scrollable=False)
        apply_style(self, "WIDGET.NAVBAR")
        apply_style(self, "WIDGET.SCREEN", lv.STATE.DISABLED)

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
        for (name, icon, cb) in zip(names, icons, cbs):
            self.buttons[name] = Btn(self, 
                                     icon=icon, 
                                     size=(BTC_ICON_WIDTH, BTC_ICON_WIDTH), 
                                     callback=cb,
                                     foreground_style="WIDGET.NAVBAR_BUTTON_FG")
            apply_style(self.buttons[name], "WIDGET.NAVBAR_BUTTON")
            apply_style(self.buttons[name], "APPEARANCE.INVISIBLE", lv.STATE.DISABLED)

    # ── Drop-up management ────────────────────────────────────────────────────────

    def _ensure_backdrop(self):
        """Create shared backdrop if not already present; return its container."""
        if self._backdrop is not None:
            return self._backdrop
        _panel_max_h = SCREEN_HEIGHT - STATUS_BAR_H
        self._backdrop = modal_overlay(width=SCREEN_WIDTH, height=_panel_max_h)
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

            # Home icon: filled only when on main and no dropup is open
            if self.current_menu == "main" and not seed_open and not wallet_open:
                self.buttons["Home"].update_icon(BTC_ICONS.HOME)
            else:
                self.buttons["Home"].update_icon(BTC_ICONS.HOME_OUTLINE)
            # Home is always visible when not locked
            self.buttons["Home"].set_state(lv.STATE.DISABLED, False)

            # Seed icon: filled when dropup open OR when in a seed menu
            if (self.context == Context.SEED and not wallet_open) or seed_open:
                self.buttons["Seed"].update_icon(BTC_ICONS.KEY)
            else:
                self.buttons["Seed"].update_icon(BTC_ICONS.KEY_OUTLINE)
            #Seed icon: invisible when no seed loaded
            self.buttons["Seed"].set_state(lv.STATE.DISABLED,
                                           self.gui.device_state is None or 
                                           len(self.gui.device_state.loaded_seeds) == 0)

            # Wallet icon: filled when dropup open OR when in a wallet menu
            if (self.context == Context.WALLET and not seed_open) or wallet_open:
                self.buttons["Wallet"].update_icon(BTC_ICONS.WALLET)
            else:
                self.buttons["Wallet"].update_icon(BTC_ICONS.WALLET_OUTLINE)
            #Wallet icon: invisible when no seed loaded
            self.buttons["Wallet"].set_state(lv.STATE.DISABLED, 
                                             self.gui.device_state is None or 
                                             len(self.gui.device_state.loaded_seeds) == 0)

            # Device icon
            if self.context == Context.DEVICE and not seed_open and not wallet_open:
                self.buttons["Device"].update_icon(BTC_ICONS.GEAR)
            else:
                self.buttons["Device"].update_icon(BTC_ICONS.GEAR_OUTLINE)
            # Device is always visible when not locked
            self.buttons["Device"].set_state(lv.STATE.DISABLED, False)

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
        if (self.buttons["Back"].get_state() & lv.STATE.DISABLED) != 0:
            return  # ignore clicks when Back button is disabled
        # If a drop-up is open, close it first, then navigate back
        self.close_dropups()
        self.on_navigate(None)

    def _seed_cb(self, event=None):
        if self._any_animation_ongoing():
            return
        if (self.buttons["Seed"].get_state() & lv.STATE.DISABLED) != 0:
            return  # ignore clicks when Seed button is disabled
        self._dropup_button_cb(self._seed_dropup, self._wallet_dropup)

    def _home_cb(self, event=None):
        if self._any_animation_ongoing():
            return
        if (self.buttons["Home"].get_state() & lv.STATE.DISABLED) != 0:
            return  # ignore clicks when Home button is disabled
        # History clearing is handled inside on_navigate/show_menu for target="main"
        self.close_dropups()
        self.gui.on_navigate("main")

    def _wallet_cb(self, event=None):
        if self._any_animation_ongoing():
            return
        if (self.buttons["Wallet"].get_state() & lv.STATE.DISABLED) != 0:
            return  # ignore clicks when Wallet button is disabled
        self._dropup_button_cb(self._wallet_dropup, self._seed_dropup)

    def _device_cb(self, event=None):
        if self._any_animation_ongoing():
            return
        
        if (self.buttons["Device"].get_state() & lv.STATE.DISABLED) != 0:
            return  # ignore clicks when Device button is disabled
        
        #always close drop ups if they are open
        self.close_dropups()
        
        if self.context != Context.DEVICE:
            self.on_navigate("manage_settings")
        self.refresh()
