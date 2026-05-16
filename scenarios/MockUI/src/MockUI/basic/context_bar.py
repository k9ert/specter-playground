"""ContextBar — active-seed / active-wallet info strip at the top of screens.
"""

import lvgl as lv

from .ui_consts import (
    TITLE_ROW_HEIGHT,
    SCREEN_WIDTH,
)
from .specter_gui_base import SpecterGuiElement
from .ui_utils import delete_all_children_of, configure_as_bare
from .symbol_lib import BTC_ICONS
from .widgets.seed_widgets import build_seed_card
from .widgets.wallet_widgets import build_wallet_card, wallet_net_text
from .keyboard_manager import Layout
from ..stubs.ui_state import Context


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

    def __init__(self, screen, width=SCREEN_WIDTH, height=TITLE_ROW_HEIGHT, context=None):
        """
        Args:
            screen: The :class:`Screen` instance that owns this bar.
        """
        super().__init__(screen)
        self.gui = screen.gui

        configure_as_bare(self, width=width, height=height)
        self.set_scroll_dir(lv.DIR.NONE)
        self.align(lv.ALIGN.TOP_LEFT, 0, 0)

        if context is None:
            context = self.context
        self.bar_context = context

        self._build()

    # ── Internal build helpers ────────────────────────────────────────────

    def _build(self):
        """Create child widgets for the current context."""
        ctx = self.bar_context
        if ctx == Context.SEED:
            self._build_seed()
        elif ctx == Context.WALLET:
            self._build_wallet()

    def _build_seed(self):
        seed = self.active_seed
        if not seed:
            return

        def _on_name_click(ta):
            def _on_commit(val):
                if val and self.active_seed:
                    ta.remove_state(lv.STATE.FOCUSED)
                    self.active_seed.label = val
                    self.gui.refresh_ui()
            self.gui.keyboard_manager.bind(ta, Layout.FULL, _on_commit)

        self.ta = build_seed_card(
            self,
            seed,
            height=self.get_height(),
            width=self.get_width(),
            slots=("leading_icon", "name", "passphrase", "fingerprint"),
            leading_icon=BTC_ICONS.KEY_OUTLINE,
            on_name_click=_on_name_click,
            gui=self.gui,
            border=False,
        )

    def _build_wallet(self):
        wallet = self.active_wallet
        if not wallet:
            return

        has_account = wallet.account != 0
        net_text = wallet_net_text(wallet)
        show_net = net_text not in (None, "main")

        active_slots = ["leading_icon", "name", "type_icon"]
        if has_account:
            active_slots.append("account")
        if show_net:
            active_slots.append("net")

        def _on_name_click(ta):
            def _on_commit(val):
                if val and self.active_wallet:
                    ta.remove_state(lv.STATE.FOCUSED)
                    self.active_wallet.label = val
                    self.gui.refresh_ui()
            self.gui.keyboard_manager.bind(ta, Layout.FULL, _on_commit)

        self.ta = build_wallet_card(
            self,
            wallet,
            self.device_state,
            height=self.get_height(),
            width=self.get_width(),
            slots=active_slots,
            leading_icon=BTC_ICONS.WALLET_OUTLINE,
            on_name_click=_on_name_click,
            border=False,
        )
    # ── Public API ────────────────────────────────────────────────────────

    def refresh(self):
        """Rebuild context bar content after seed / wallet data changes."""
        # Guard: don't rebuild while the user is actively editing the name field.
        # self.ta is set by _build_seed / _build_wallet from row.ta (the textarea
        # exposed by the card builder). Use keyboard_manager.textarea for the live
        # check — it is auto-cleared on DELETE, whereas self.ta could be a stale
        # reference after delete_all_children_of() removed the widget.
        ta = getattr(self, "ta", None)
        if ta is not None and self.keyboard_manager.textarea is ta:
            return
        self.ta = None
        delete_all_children_of(self)
        self._build()

