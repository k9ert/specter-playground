"""SeedDropUp / WalletDropUp — bottom-sheet selection overlays.

Both classes share the same structure:
  - Rendered above everything via layer_top (ModalOverlay)
  - Anchored at the bottom of the screen (just above the NavigationBar)
  - Grow upward; scrollable if content exceeds available height

Public API (used by NavigationBar):
  dropup.get_state()        → DropUpState constant
  dropup.open(container)   → build and show the panel inside *container*
  dropup.close()           → animate panel out; fires _on_closed when done
  dropup.refresh()         → rebuild card list (called after state changes)

The panel fills from the nav bar top edge upward.
"""

import lvgl as lv
from micropython import const
from ..widgets.action_modal import ActionModal
from ..widgets.menu_item import MenuItem
from .confirm_modals import confirm_delete_seed, confirm_delete_wallet
from ..utils.ui_consts import (
    BTC_ICON_WIDTH, SMALL_TEXT_FONT, STATUS_BTN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT,
    STATUS_BAR_PCT, WHITE_HEX, ORANGE_HEX, BIG_PAD, CARD_H,
    DROPUP_DIVIDER_OPA, ANIM_MS_VERTICAL, TEXT_FONT
)
from ..symbol_lib import BTC_ICONS
from ..widgets.containers import flex_col, flex_row
from ..widgets.btn import Btn
from ..widgets.seed_widgets import build_seed_card
from ..widgets.wallet_widgets import build_wallet_card, wallet_net_text
from ..utils.animations import slide_y
from ..templates.specter_gui_base import SpecterGuiMixin
from ...stubs.ui_state import Context


# ── Layout constants ──────────────────────────────────────────────────────────
_NAV_BAR_H = SCREEN_HEIGHT * STATUS_BAR_PCT // 100   # navigation bar height (px)
_PANEL_MAX_H = SCREEN_HEIGHT - _NAV_BAR_H            # max panel height

_ADD_BTN_H = STATUS_BTN_HEIGHT                     # "Add …" button height


_CLOSED = const(0)
_OPENING = const(1)
_OPEN = const(2)
_CLOSING = const(3)
class DropUpState:
    """Valid states for a ``_DropUp`` instance."""
    CLOSED  = _CLOSED
    OPENING = _OPENING
    OPEN    = _OPEN
    CLOSING = _CLOSING


# ── Base class ────────────────────────────────────────────────────────────────

class _DropUp(SpecterGuiMixin):
    """Abstract base drop-up overlays."""

    # Subclass row-click behaviour, as a 5-tuple:
    #   (active_context, active_attr, setter_method, nav_target, nav_kwarg)
    _ROW_BEHAVIOR = None

    def __init__(self, gui):
        self.gui = gui
        self._panel = None    # lv.obj panel widget when open
        self._on_closed = None  # callback()/None — called after close animation
        self._animating = False
        self._closing = False  # True while close animation is running
        self._anim = None

    # ── Public API ────────────────────────────────────────────────────────────

    def get_state(self):
        """Return the current drop-up state as a ``DropUpState`` constant."""
        if self._panel is None:
            return DropUpState.CLOSED
        if self._animating:
            return DropUpState.CLOSING if self._closing else DropUpState.OPENING
        return DropUpState.OPEN

    def open(self, container):
        """Build and slide in the panel inside *container* (shared backdrop overlay)."""
        state = self.get_state()
        if state in (DropUpState.OPENING, DropUpState.CLOSING, DropUpState.OPEN):
            return state

        self._panel = flex_col(
            container,
            width=SCREEN_WIDTH,
            height=_PANEL_MAX_H,
            main_align=lv.FLEX_ALIGN.START,
            transparent_bg=False,
        )
        self._panel.set_style_radius(0, 0)
        self._panel.set_style_pad_row(0, 0)
        self._panel.set_scroll_dir(lv.DIR.VER)
        self._panel.set_scrollbar_mode(lv.SCROLLBAR_MODE.AUTO)
        self._panel.add_event_cb(lambda e: setattr(e, 'stop_bubbling', 1), lv.EVENT.CLICKED, None)

        self._fill_panel()
        # ── Slide-in animation ────────────────────────────────────────────────
        if self.ui_state.are_animations_enabled:        
            self._animating = True

            def _on_open_done(anim):
                self._animating = False
                self._anim = None

            panel_y = _PANEL_MAX_H - self._compute_panel_h()
            self._anim = slide_y(self._panel, _PANEL_MAX_H, panel_y, ANIM_MS_VERTICAL, on_done_cb=_on_open_done)
            self._anim.start()

        return self.get_state()

    def close(self):
        state = self.get_state()
        if state in (DropUpState.OPENING, DropUpState.CLOSING, DropUpState.CLOSED):
            return state  # animation in progress or already closed, do nothing

        def _on_close_done(anim):
            self._animating = False
            self._closing = False
            self._anim = None
            if self._panel is not None:
                self._panel.delete()
            self._panel = None
            if self._on_closed is not None:
                self._on_closed()

        if self.ui_state.are_animations_enabled:
            self._animating = True
            self._closing = True

            panel_y_now = self._panel.get_y()
            panel_y_end = _PANEL_MAX_H  # slide off-screen down

            self._anim = slide_y(self._panel, panel_y_now, panel_y_end, ANIM_MS_VERTICAL, on_done_cb=_on_close_done)
            self._anim.start()
        else:
            _on_close_done(None)

        return self.get_state()

    def refresh(self):
        """Rebuild cards in place (called after state changes)."""
        if self.get_state() != DropUpState.OPEN:
            return
        self._fill_panel()

    def _fill_panel(self):
        """Clear, repopulate, and resize/reposition the panel."""
        while self._panel.get_child_count() > 0:
            self._panel.get_child(0).delete()
        panel_h = self._compute_panel_h()

        #Create cards/items
        for item in self._get_items():
            self._build_card(self._panel, item)

        #Create Add Button
        row = flex_row(self._panel, width=SCREEN_WIDTH, height=_ADD_BTN_H,
                       main_align=lv.FLEX_ALIGN.CENTER)
        btn = Btn(
            row,
            icon=BTC_ICONS.PLUS,
            text=self._add_button_label(),
            size=(None, _ADD_BTN_H),
            callback=self._add_cb,
            font=TEXT_FONT,
        )
        btn.make_background_transparent()

        self._panel.set_size(SCREEN_WIDTH, panel_h)
        self._panel.set_pos(0, _PANEL_MAX_H - panel_h)

    # ── Subclass interface ────────────────────────────────────────────────────

    def _get_items(self):
        """Return list of items (seeds or wallets) to display."""
        raise NotImplementedError

    def _build_card(self, parent, item):
        """Build one item card inside parent."""
        raise NotImplementedError

    def _navigate_add(self):
        """Navigate to the add item screen."""
        raise NotImplementedError

    def _add_button_label(self):
        """Return text for the add button."""
        raise NotImplementedError

    # ── Private helpers ───────────────────────────────────────────────────────

    def _compute_panel_h(self):
        # Exact: pad_row is forced to 0 on the panel, so content = n*CARD_H + _ADD_BTN_H
        content_h = len(self._get_items()) * CARD_H + _ADD_BTN_H
        return min(content_h, _PANEL_MAX_H)

    def _add_cb(self, event=None):
        self.close()
        self._navigate_add()

    def _make_row_cb(self, item):
        """Row click handler: close, then switch active item or navigate.

        If the drop-up's context is already active (e.g. a seed is loaded while
        the seed drop-up is open), clicking a row switches to that item in place.
        Otherwise navigate to the manage screen for that item.
        """
        ctx, attr, setter, target, kwarg = self._ROW_BEHAVIOR
        def _cb(e):
            if e.get_code() != lv.EVENT.CLICKED:
                return
            self.close()
            if (self.ui_state.active_context == ctx
                    and getattr(self.ui_state, attr) is not None):
                getattr(self.ui_state, setter)(item)
                self.gui.refresh_ui()
            else:
                self.on_navigate(target, **{kwarg: item})
        return _cb


# ── Seed Drop-Up ──────────────────────────────────────────────────────────────

class SeedDropUp(_DropUp):
    """Drop-up overlay listing all loaded seeds with passphrase + edit buttons."""

    _ROW_BEHAVIOR = (Context.SEED, "active_seed", "set_active_seed",
                     "manage_seedphrase", "target_seed")

    def _get_items(self):
        return self.device_state.loaded_seeds

    def _add_button_label(self):
        return self.t("MENU_ADD_SEED")

    def _navigate_add(self):
        self.on_navigate("add_seed", target_seed=None)

    def _build_card(self, parent, seed):
        def _make_warn_cb(s):
            def _cb():
                t = self.t
                def _mark_backed_up():
                    s.is_backed_up = True
                    self.gui.refresh_ui()
                ActionModal(
                    text=t("MODAL_BACKUP_WARNING_TEXT"),
                    buttons=[
                        MenuItem(BTC_ICONS.CHECK, t("MODAL_BACKUP_CONFIRMED_BTN"), target=_mark_backed_up),
                        MenuItem(text=t("COMMON_OK")),
                    ],
                )
            return _cb

        def _make_delete_cb(s):
            def _cb():
                def _do_delete():
                    self.device_state.remove_seed(s)
                    if self.ui_state.active_seed is s:
                        self.ui_state.active_seed = None
                    if not self.device_state.loaded_seeds:
                        # Last seed gone: close the drop-up and return home;
                        # on_navigate("main") handles the refresh itself.
                        self.close()
                        self.on_navigate("main")
                    else:
                        self.gui.refresh_ui()
                confirm_delete_seed(self.t, s.label, _do_delete)
            return _cb

        build_seed_card(
            parent,
            seed,
            slots=("name", "backup_warning", "passphrase", "fingerprint", "delete"),
            on_card_click=self._make_row_cb(seed),
            on_backup_warning=_make_warn_cb(seed),
            on_delete=_make_delete_cb(seed),
            gui=self.gui,
        )



# ── Wallet Drop-Up ────────────────────────────────────────────────────────────

class WalletDropUp(_DropUp):
    """Drop-up overlay listing all registered wallets with type + edit buttons."""

    _ROW_BEHAVIOR = (Context.WALLET, "active_wallet", "set_active_wallet",
                     "manage_wallet", "target_wallet")

    def _get_items(self):
        return self.device_state.registered_wallets

    def _add_button_label(self):
        return self.t("MENU_ADD_WALLET")

    def _navigate_add(self):
        #clear active wallet to avoid accidentally pre-filling add form with previously selected wallet's data
        self.on_navigate("add_wallet", target_wallet=None)

    def _build_card(self, parent, wallet):
        state = self.device_state
        # Cross-wallet alignment: show account/net columns if any wallet uses them
        any_account = any(getattr(w, "account", 0) != 0 for w in state.registered_wallets)
        any_net     = any(w.net != "mainnet" for w in state.registered_wallets)

        active_slots = ["type_icon", "name", "threshold"]
        if any_account:
            active_slots.append("account")
        if any_net:
            active_slots.append("net")
        if not wallet.is_default_wallet():
            active_slots.append("delete")

        def _make_delete_cb(w):
            def _cb():
                def _do_delete():
                    # No empty-list path: the default wallet cannot be deleted
                    # (delete button is only shown when is_default_wallet is False),
                    # so registered_wallets always has at least the default entry.
                    self.device_state.remove_wallet(w)
                    if self.ui_state.active_wallet is w:
                        self.ui_state.active_wallet = None
                    self.gui.refresh_ui()
                confirm_delete_wallet(self.t, w.label, _do_delete)
            return _cb

        build_wallet_card(
            parent,
            wallet,
            state,
            slots=active_slots,
            on_card_click=self._make_row_cb(wallet),
            on_delete=_make_delete_cb(wallet) if not wallet.is_default_wallet() else None,
        )
