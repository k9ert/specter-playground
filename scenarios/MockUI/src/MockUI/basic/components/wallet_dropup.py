"""WalletDropUp — bottom-sheet overlay listing all registered wallets."""

from ..widgets import WalletCard
from ..ui_state import Context
from ..templates.dropup import DropUp
from ..theming import apply_style
from .confirm_modals import confirm_delete_wallet


class WalletDropUp(DropUp):
    """Drop-up overlay listing registered wallets as a hierarchy."""

    EXPANSION_CONTEXT = Context.WALLET

    def _get_selectable_items(self):
        return self.device_state.registered_wallets

    def _delete_from_gui(self, wallet):
        self.gui.delete_wallet(wallet)

    def _get_item_parent(self, wallet):
        return wallet.derivation_parent(self.device_state.registered_wallets)

    def _get_item_key(self, wallet):
        return str(wallet.descriptor)

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

        card = WalletCard(
            parent, wallet, state,
            slots=active_slots,
            on_card_click=self._make_on_row_click_cb(wallet, 
                                            Context.WALLET, 
                                            "active_wallet", 
                                            "set_active_wallet", 
                                            "manage_wallet", 
                                            "target_wallet"),
            on_delete=(
                (lambda: confirm_delete_wallet(
                    self.t, wallet.label,
                    lambda: self._delete_item(wallet)))
                if not_default else None),
        )
        apply_style(card, "CONTEXT.WALLET")
        return card
