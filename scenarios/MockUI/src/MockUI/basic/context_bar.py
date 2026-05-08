"""ContextBar — active-seed / active-wallet info strip at the top of screens.
"""

import lvgl as lv

from .ui_consts import (
    TITLE_ROW_HEIGHT, WHITE_HEX,
    SMALL_TEXT_FONT, SCREEN_WIDTH,
    BTC_ICON_WIDTH, FINGERPRINT_LBL_WIDTH,
)
from .specter_gui_base import SpecterGuiElement, delete_all_children_of, configure_as_bare
from .symbol_lib import BTC_ICONS
from .widgets.containers import flex_row
from .widgets.labels import body_label, best_font_for_size
from .widgets.inputs import title_textarea
from .widgets.icon_widgets import make_icon
from .widgets.seed_widgets import fingerprint_badge, passphrase_toggle
from .widgets.wallet_widgets import add_wallet_type_icon, wallet_account_text, wallet_net_text
from .keyboard_manager import Layout
from ..stubs.ui_state import Context

# Pixels reserved on the right side for the battery widget
_BATT_RESERVE = 50

# Row width available for content
_ROW_W = SCREEN_WIDTH - _BATT_RESERVE

# Fixed-width budget constants (match dropup.py values)
_ICON_W = BTC_ICON_WIDTH   # 42 — leading icon, type icon, passphrase icon, relay icon
_FP_W   = FINGERPRINT_LBL_WIDTH  # 40 — 4-char fingerprint text
_ACC_W  = 36               # account "#N" label
_NET_W  = 42               # net label "test"/"sig" etc.


class ContextBar(SpecterGuiElement):
    """Top info strip rendered when a seed or wallet context is active.

    It renders:

      SEED context:
        [KEY icon] [name textarea*] [PASSPHRASE icon†] [FINGERPRINT]

      WALLET context:
        [WALLET icon] [name textarea*] [type icon] [Acc:n?] [net label?]

      * Editable: tap to open keyboard, commit to rename seed / wallet.
      † Passphrase icon visible only when passphrase is set; white = active,
        grey = inactive; tap to toggle ``passphrase_active``.
    """

    def __init__(self, gui):
        """
        Args:
            gui: The :class:`SpecterGui` instance that owns this bar.
        """
        super().__init__(gui)
        self.gui = gui

        configure_as_bare(self, width=lv.pct(100), height=TITLE_ROW_HEIGHT)
        self.set_scroll_dir(lv.DIR.NONE)
        self.align(lv.ALIGN.TOP_MID, 0, 0)

        # Store the context type at creation time so _do_transition can tell
        # old bar type from new, even after ui_state has advanced to the new context.
        self._context_type = self.context

        self._build()

    # ── Internal build helpers ────────────────────────────────────────────

    def _build(self):
        """Create child widgets for the current context."""
        # Flex row — leaves _BATT_RESERVE px on the right so the battery
        # widget (owned by SpecterGui, floating above) doesn't overlap content.
        row = flex_row(
            self,
            width=SCREEN_WIDTH - _BATT_RESERVE,
            height=TITLE_ROW_HEIGHT,
            pad=0,
            main_align=lv.FLEX_ALIGN.START,
        )

        ctx = self.context
        if ctx == Context.SEED:
            self._build_seed(row)
        elif ctx == Context.WALLET:
            self._build_wallet(row)

    def _build_seed(self, row):
        make_icon(row, BTC_ICONS.KEY_OUTLINE, color=WHITE_HEX)

        seed = self.ui_state.active_seed
        if not seed:
            return

        has_passphrase = seed.passphrase is not None
        fixed = _ICON_W + _ICON_W + (_ICON_W if has_passphrase else 0) + _FP_W
        name_w = _ROW_W - fixed

        font, display_text = best_font_for_size(seed.label, name_w, TITLE_ROW_HEIGHT)

        self._name_ta = title_textarea(row)
        self._name_ta.set_width(name_w)
        self._name_ta.set_style_text_font(font, 0)
        self._name_ta.set_text(display_text)

        def _on_commit_name(val):
            if val and self.ui_state.active_seed:
                self.ui_state.active_seed.label = val
                self.gui.refresh_ui()

        self._name_ta.add_event_cb(
            lambda e: self.gui.keyboard_manager.bind(
                self._name_ta, Layout.FULL, _on_commit_name
            ),
            lv.EVENT.CLICKED,
            None,
        )

        passphrase_toggle(row, seed, self.gui)
        fingerprint_badge(row, seed, digits=4)

    def _build_wallet(self, row):
        make_icon(row, BTC_ICONS.WALLET_OUTLINE, color=WHITE_HEX)

        wallet = self.ui_state.active_wallet
        if not wallet:
            return

        has_account = wallet.account != 0
        net_text = wallet_net_text(wallet)
        show_net = net_text != "main"
        fixed = _ICON_W + _ICON_W + (_ACC_W if has_account else 0) + (_NET_W if show_net else 0)
        name_w = _ROW_W - fixed

        font, display_text = best_font_for_size(wallet.label, name_w, TITLE_ROW_HEIGHT)

        if wallet.is_default_wallet():
            # show "Default" as non-editable text
            body_label(row, display_text, font=font, width=name_w)
        else:
            # Custom wallet: editable name textarea
            self._name_ta = title_textarea(row)
            self._name_ta.set_width(name_w)
            self._name_ta.set_style_text_font(font, 0)
            self._name_ta.set_text(display_text)

            def _on_commit_name(val):
                if val and self.ui_state.active_wallet:
                    self.ui_state.active_wallet.label = val
                    self.gui.refresh_ui()

            self._name_ta.add_event_cb(
                lambda e: self.gui.keyboard_manager.bind(
                    self._name_ta, Layout.FULL, _on_commit_name
                ),
                lv.EVENT.CLICKED,
                None,
            )

        add_wallet_type_icon(row, wallet, self.device_state)

        if has_account:
            body_label(
                row, wallet_account_text(wallet),
                font=SMALL_TEXT_FONT, width=lv.SIZE_CONTENT,
            )

        if show_net:
            body_label(
                row, net_text,
                font=SMALL_TEXT_FONT, width=lv.SIZE_CONTENT,
            )

    # ── Public API ────────────────────────────────────────────────────────

    def refresh(self):
        """Rebuild context bar content after seed / wallet data changes."""
        delete_all_children_of(self)
        self._build()

