"""ContextBar — active-seed / active-wallet info strip at the top of screens.
"""

import lvgl as lv

from ..utils import (
    TITLE_HEIGHT,
    SCREEN_WIDTH,
    delete_all_children_of, set_size, set_scroll, set_align, get_size,
    Layout
)
from ..templates.specter_gui_base import SpecterGuiElement
from ..theming import apply_style
from ..symbol_lib import BTC_ICONS
from ..widgets import SeedCard, WalletCard, wallet_net_text
from ..ui_state import Context


class ContextBar(SpecterGuiElement):
    """Top info strip rendered when a seed or wallet context is active.

    It renders:

      SEED context:
        [KEY icon] [name textarea*] [PASSPHRASE icon**] [FINGERPRINT]

      WALLET context:
        [WALLET icon] [name textarea*] [type icon] [Acc:n?] [net label?]

      * Editable: tap to open keyboard, commit to rename seed / wallet.
     ** Passphrase icon visible only when passphrase is set; white = active,
        grey = inactive; tap to toggle ``passphrase_active``.
    """

    def __init__(self, parent, width=SCREEN_WIDTH, height=TITLE_HEIGHT, context=None):
        super().__init__(parent)

        set_size(self, width, height)
        set_scroll(self, horizontal=False, vertical=False)
        set_align(self, lv.ALIGN.TOP_LEFT)
        apply_style(self, ["CONTAINER.CONTEXT_BAR"])

        if context is None:
            context = self.context
        self.bar_context = context

        self._build(width, height)

    # ── Internal build helpers ────────────────────────────────────────────

    def _build(self, width, height):
        """Create child widgets for the current context."""
        ctx = self.bar_context
        if ctx == Context.SEED:
            seed = self.active_seed
            if not seed:
                return

            self.card = SeedCard(
                self,
                seed,
                height=height,
                width=width,
                slots=("leading_icon", "name", "passphrase", "fingerprint"),
                leading_icon=BTC_ICONS.KEY_OUTLINE,
                on_name_click=self._make_name_commit_handler("active_seed"),
            )
            apply_style(self.card, ["CONTAINER.CONTEXT_BAR", "CONTEXT.SEED"])
        elif ctx == Context.WALLET:
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

            self.card = WalletCard(
                self,
                wallet,
                self.device_state,
                height=height,
                width=width,
                slots=active_slots,
                leading_icon=BTC_ICONS.WALLET_OUTLINE,
                on_name_click=self._make_name_commit_handler("active_wallet"),
            )
            apply_style(self.card, ["CONTAINER.CONTEXT_BAR", "CONTEXT.WALLET"])

    def _make_name_commit_handler(self, target_attr):
        """Return an ``on_name_click`` handler that commits edits to ``target_attr``.

        The returned handler binds the keyboard to the name textarea and, on
        commit, writes the new label back to ``self.<target_attr>`` (e.g.
        ``active_seed`` or ``active_wallet``) and refreshes the UI.  When the
        target is ``None`` at commit time the edit is silently dropped.
        """
        def _on_name_click(ta):
            def _on_commit(val):
                target = getattr(self, target_attr)
                if val and target:
                    ta.remove_state(lv.STATE.FOCUSED)
                    target.label = val
                    self.gui.refresh_ui()
            self.gui.keyboard_manager.bind(ta, Layout.FULL, _on_commit)
        return _on_name_click

    # ── Public API ────────────────────────────────────────────────────────

    def refresh(self):
        """Rebuild context bar content after seed / wallet data changes."""
        # Guard: don't rebuild while the user is actively editing the name field.
        # self.text_edit is set by _build_seed / _build_wallet from row.text_edit (the textarea
        # exposed by the card builder). Use keyboard_manager.textarea for the live
        # check — it is auto-cleared on DELETE, whereas self.text_edit could be a stale
        # reference after delete_all_children_of() removed the widget.
        text_edit = getattr(self.card, "text_edit", None)
        if text_edit is not None and self.keyboard_manager.textarea is text_edit:
            return
        self.card.text_edit = None
        delete_all_children_of(self)
        w, h = get_size(self)
        self._build(w, h)

