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
from .widgets.action_modal import ActionModal
from .confirm_modals import confirm_delete_seed, confirm_delete_wallet
from .ui_consts import (
    BTC_ICON_WIDTH, SMALL_TEXT_FONT, STATUS_BTN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT,
    STATUS_BAR_PCT, WHITE_HEX, ORANGE_HEX, BIG_PAD,
    DROPUP_DIVIDER_OPA, ANIM_MS_VERTICAL, TEXT_FONT, SMALL_TEXT_FONT
)
from .symbol_lib import BTC_ICONS
from .widgets.containers import flex_col, flex_row
from .widgets.btn import Btn
from .widgets.labels import _make_label, best_font_for_name
from .widgets.icon_widgets import make_icon
from .widgets.seed_widgets import fingerprint_badge, passphrase_toggle
from .widgets.wallet_widgets import add_wallet_type_icon, wallet_signing_color, wallet_account_text, wallet_net_text
from .animations import slide_y
from .specter_gui_base import SpecterGuiMixin


# ── Layout constants ──────────────────────────────────────────────────────────
_NAV_BAR_H = SCREEN_HEIGHT * STATUS_BAR_PCT // 100   # navigation bar height (px)
_PANEL_MAX_H = SCREEN_HEIGHT - _NAV_BAR_H            # max panel height

_CARD_H = STATUS_BTN_HEIGHT + 2 * BIG_PAD + 2   # height per item card
_ADD_BTN_H = STATUS_BTN_HEIGHT                     # "Add …" button height

_FP_SLOT_W = BTC_ICON_WIDTH + 40   # RELAY icon + 4-char fingerprint label


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
        # Exact: pad_row is forced to 0 on the panel, so content = n*_CARD_H + _ADD_BTN_H
        content_h = len(self._get_items()) * _CARD_H + _ADD_BTN_H
        return min(content_h, _PANEL_MAX_H)

    def _add_cb(self, event=None):
        self.close()
        self._navigate_add()


def _card_row(parent):
    """Full-width horizontal flex row for a card, with left-aligned items."""
    row = flex_row(
        parent,
        width=SCREEN_WIDTH,
        height=_CARD_H,
        pad=BIG_PAD,
        main_align=lv.FLEX_ALIGN.START,
    )
    # pad_all also sets pad_column/pad_row, which adds inter-item gaps in flex
    # layout and causes horizontal overflow.  Zero it out explicitly.
    row.set_style_pad_column(0, 0)
    row.set_style_border_width(1, 0)
    row.set_style_border_side(lv.BORDER_SIDE.BOTTOM, 0)
    row.set_style_border_color(WHITE_HEX, 0)
    row.set_style_border_opa(DROPUP_DIVIDER_OPA, 0)
    row.set_scroll_dir(lv.DIR.NONE)
    row.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    return row


# ── Seed Drop-Up ──────────────────────────────────────────────────────────────

class SeedDropUp(_DropUp):
    """Drop-up overlay listing all loaded seeds with passphrase + edit buttons."""

    def _get_items(self):
        return self.device_state.loaded_seeds

    def _add_button_label(self):
        return self.t("MENU_ADD_SEED")

    def _navigate_add(self):
        self.on_navigate("add_seed")

    def _build_card(self, parent, seed):
        row = _card_row(parent)

        # ── Row click → navigate to seed manage menu ──────────────────────────
        def _make_row_cb(s):
            def _cb(e):
                if e.get_code() == lv.EVENT.CLICKED:
                    self.close()
                    self.ui_state.set_active_seed(s)
                    self.on_navigate("manage_seedphrase")
            return _cb
        row.add_event_cb(_make_row_cb(seed), lv.EVENT.CLICKED, None)

        # ── Seed name ─────────────────────────────────────────────────────────
        show_passphrase = seed.passphrase is not None
        show_warning = not seed.is_backed_up
        name_w = (
            SCREEN_WIDTH
            - 2 * BIG_PAD            # row padding
            - _FP_SLOT_W                # RELAY icon + 4-char fp
            - (BTC_ICON_WIDTH if show_passphrase else 0)
            - (BTC_ICON_WIDTH if show_warning else 0)
            - BTC_ICON_WIDTH            # delete button
        )
        name_lbl_w = max(10, name_w)
        name_font, seed_label = best_font_for_name(seed.label, name_lbl_w, _CARD_H)
        name_lbl = _make_label(row, seed_label, width=name_lbl_w, font=name_font)
        name_lbl.set_long_mode(lv.label.LONG_MODE.CLIP)

        # ── Backup warning (optional, clickable) ──────────────────────────────
        if show_warning:
            warn_img = make_icon(row, BTC_ICONS.ALERT_CIRCLE, ORANGE_HEX)
            warn_img.add_flag(lv.obj.FLAG.CLICKABLE)

            def _make_warn_cb(s):
                def _cb(e):
                    if e.get_code() == lv.EVENT.CLICKED:
                        e.stop_bubbling = 1  # don't trigger row navigation
                        t = self.t

                        def _mark_backed_up():
                            s.is_backed_up = True
                            self.gui.refresh_ui()

                        ActionModal(
                            text=t("MODAL_BACKUP_WARNING_TEXT"),
                            buttons=[
                                (BTC_ICONS.CHECK, t("MODAL_BACKUP_CONFIRMED_BTN"), None, _mark_backed_up),
                                (None,            t("COMMON_OK"),                  None, None),
                            ],
                        )
                return _cb
            warn_img.add_event_cb(_make_warn_cb(seed), lv.EVENT.CLICKED, None)

        # ── Passphrase indicator (optional, clickable) ────────────────────────
        passphrase_toggle(row, seed, self.gui, stop_bubbling=True)

        # ── Fingerprint: RELAY icon + first 4 hex chars ───────────────────────
        fingerprint_badge(row, seed, digits=4)

        # ── Delete button ─────────────────────────────────────────────────────
        def _make_delete_seed_cb(s):
            def _cb(event=None):
                if event is not None:
                    event.stop_bubbling = 1

                def _do_delete():
                    self.device_state.remove_seed(s)
                    if self.ui_state.active_seed is s:
                        self.ui_state.active_seed = None
                    if not self.device_state.loaded_seeds:
                        self.close()
                        self.on_navigate("main")
                    self.gui.refresh_ui()
                confirm_delete_seed(self.t, s.label, _do_delete)
            return _cb

        del_btn = Btn(
            row,
            icon=BTC_ICONS.TRASH,
            size=(BTC_ICON_WIDTH, _CARD_H),
            callback=_make_delete_seed_cb(seed),
        )
        del_btn.make_background_transparent()



# ── Wallet Drop-Up ────────────────────────────────────────────────────────────

class WalletDropUp(_DropUp):
    """Drop-up overlay listing all registered wallets with type + edit buttons."""

    def _get_items(self):
        return self.device_state.registered_wallets

    def _add_button_label(self):
        return self.t("MENU_ADD_WALLET")

    def _navigate_add(self):
        self.on_navigate("add_wallet")

    def _build_card(self, parent, wallet):
        row = _card_row(parent)

        # ── Row click → navigate to wallet manage menu ────────────────────────
        def _make_row_cb(w):
            def _cb(e):
                if e.get_code() == lv.EVENT.CLICKED:
                    self.close()
                    self.ui_state.set_active_wallet(w)
                    self.on_navigate("manage_wallet")
            return _cb
        row.add_event_cb(_make_row_cb(wallet), lv.EVENT.CLICKED, None)

        # ── Wallet type icon ──────────────────────────────────────────────────
        state = self.device_state
        add_wallet_type_icon(row, wallet, state)
        key_color = wallet_signing_color(wallet, state)

        # ── Wallet name ───────────────────────────────────────────────────────
        show_account = any(getattr(wallet, "account", 0) != 0 for wallet in state.registered_wallets)
        show_net = any(wallet.net != "mainnet" for wallet in state.registered_wallets)
        thresh_w = 40 if wallet.isMultiSig and wallet.threshold else 0
        acc_w = 36 if show_account else 0
        net_w = 42 if show_net else 0
        name_w = (
            SCREEN_WIDTH
            - 2 * BIG_PAD
            - BTC_ICON_WIDTH       # type icon
            - thresh_w
            - acc_w
            - net_w
            - BTC_ICON_WIDTH       # delete button
        )
        name_lbl_w = max(10, name_w)
        name_font, wallet_label = best_font_for_name(wallet.label, name_lbl_w, _CARD_H)
        name_lbl = _make_label(row, wallet_label, width=name_lbl_w, font=name_font)
        name_lbl.set_long_mode(lv.label.LONG_MODE.CLIP)

        # ── Multisig threshold ────────────────────────────────────────────────
        if wallet.isMultiSig and wallet.threshold is not None:
            n = len(wallet.required_fingerprints)
            thresh_lbl = _make_label(row, str(wallet.threshold) + "/" + str(n), width=thresh_w, font=SMALL_TEXT_FONT, color=key_color)
            thresh_lbl.set_long_mode(lv.label.LONG_MODE.CLIP)

        # ── Account number (optional) ─────────────────────────────────────────
        if show_account:
            acc_lbl = _make_label(row, wallet_account_text(wallet), width=acc_w, font=SMALL_TEXT_FONT)
            acc_lbl.set_long_mode(lv.label.LONG_MODE.CLIP)

        # ── Network (optional) ────────────────────────────────────────────────
        if show_net:
            net_lbl = _make_label(row, wallet_net_text(wallet), width=net_w, font=SMALL_TEXT_FONT)
            net_lbl.set_long_mode(lv.label.LONG_MODE.CLIP)

        # ── Delete button (not shown for default wallet) ──────────────────────
        if not wallet.is_default_wallet():
            def _make_delete_wallet_cb(w):
                def _cb(event=None):
                    if event is not None:
                        event.stop_bubbling = 1

                    def _do_delete():
                        self.device_state.remove_wallet(w)
                        if self.ui_state.active_wallet is w:
                            self.ui_state.active_wallet = None
                        self.gui.refresh_ui()

                    confirm_delete_wallet(self.t, w.label, _do_delete)
                return _cb

            del_btn = Btn(
                row,
                icon=BTC_ICONS.TRASH,
                size=(BTC_ICON_WIDTH, _CARD_H),
                callback=_make_delete_wallet_cb(wallet),
            )
            del_btn.make_background_transparent()
