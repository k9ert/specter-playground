"""WalletDropUp — bottom-sheet overlay listing all registered wallets."""

from ..widgets import WalletCard
from ..ui_state import Context
from ..templates.dropup import DropUp
from ..theming import apply_style
from .confirm_modals import confirm_delete_wallet


class WalletDropUp(DropUp):
    """Drop-up overlay listing all registered wallets with type + edit buttons."""

    def _get_items(self):
        return self.device_state.registered_wallets

    def _add_button_label(self):
        return self.t("MENU_ADD_WALLET")

    def _navigate_add(self):
        # Clear active wallet to avoid accidentally pre-filling add form with
        # previously selected wallet's data.
        self.on_navigate("add_wallet", target_wallet=None)

    def _build_card(self, parent, wallet):
        state = self.device_state
        # Cross-wallet alignment: show account/net columns if any wallet uses them.
        any_account = any(getattr(w, "account", 0) != 0 for w in state.registered_wallets)
        any_net     = any(w.net != "mainnet" for w in state.registered_wallets)
        not_default = not wallet.is_default_wallet()

        active_slots = ["type_icon", "name", "threshold"]
        if any_account:
            active_slots.append("account")
        if any_net:
            active_slots.append("net")
        if not_default:
            active_slots.append("delete")

        on_delete = (lambda: self._on_delete_wallet(wallet)) if not_default else None
        card = WalletCard(
            parent, wallet, state,
            slots=active_slots,
            on_card_click=self._make_on_row_click_cb(wallet, 
                                            Context.WALLET, 
                                            "active_wallet", 
                                            "set_active_wallet", 
                                            "manage_wallet", 
                                            "target_wallet"),
            on_delete=on_delete,
        )
        apply_style(card, "CONTEXT.WALLET")
        return card

    def _do_delete_wallet(self, wallet):
        # No empty-list path: the default wallet cannot be deleted,
        # so registered_wallets always has at least the default entry.
        self.device_state.remove_wallet(wallet)
        if self.ui_state.active_wallet is wallet:
            self.ui_state.active_wallet = None
        self.gui.refresh_ui()

    def _on_delete_wallet(self, wallet):
        confirm_delete_wallet(self.t, wallet.label, lambda: self._do_delete_wallet(wallet))
