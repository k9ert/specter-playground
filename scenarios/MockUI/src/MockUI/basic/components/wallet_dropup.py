"""WalletDropUp — bottom-sheet overlay listing all registered wallets."""

from ..widgets import WalletCard, TreeList, make_label
from ..ui_state import Context
from ..templates.dropup import DropUp, DropUpGroup
from ..templates.specter_gui_base import SpecterGuiElement
from ..theming import apply_style
from ..utils import build_forest
from .confirm_modals import confirm_delete_wallet
from ...stubs.wallet import wallet_sort_key


class WalletDropUpGroup(DropUpGroup):
    """Custom DropUpGroup for WalletDropUp."""
    def __init__(self, items, isMultisigGroup=False, heading=None):
        super().__init__(items, heading)
        self.isMultisigGroup = isMultisigGroup

class WalletDropUp(DropUp):
    """Drop-up overlay listing registered wallets as a hierarchy."""

    EXPANSION_CONTEXT = Context.WALLET

    def _get_selectable_items(self):
        return self.device_state.registered_wallets

    def _get_raw_DropUpGroups(self):
        ### INIT
        groups = []
        # To collect wallets that belong to the same set of signers
        groups_by_key = {}

        wallets = self._get_selectable_items()
        default_wallet = self.device_state.get_default_wallet()

        seeds = self.device_state.get_sorted_loaded_seeds()
        labels_by_fingerprint = {
            seed.get_fingerprint(): str(seed.label)
            for seed in seeds
        }

        ### CREATE SEED WALLET GROUPS with the default wallet as the initial item
        for seed in seeds:
            groups_by_key[seed] = WalletDropUpGroup(
                items=[default_wallet],
                isMultisigGroup=False,
                heading=str(seed.label)
            )
            groups.append(groups_by_key[seed])


        ### DISTRIBUTE WALLETS INTO LISTS/GROUPS
        for wallet in sorted(wallets, key=wallet_sort_key):
            if wallet is default_wallet:
                #skip. already used to initialize the seed wallets
                continue

            owners = self.device_state.seeds_for_wallet(wallet) or []
            # Skip/Ignore wallets that are not associated with any loaded seed
            if not owners:
                continue

            signers = wallet.get_signers()
            if wallet.isMultiSig:
                group_key = signers
            elif len(owners) == 1:
                group_key = owners[0]
            else:
                print(f"Wallet {wallet} has multiple owners but is not multisig: {owners}")
                continue

            group = groups_by_key.get(group_key, None)
            if group is None:
                group = WalletDropUpGroup(
                    items=[],
                    isMultisigGroup=True,
                    heading=", ".join(
                        labels_by_fingerprint.get(signer, signer)
                        for signer in signers),
                )
                groups_by_key[group_key] = group
                groups.append(group)

            group.items.append(wallet)

        return groups

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

        active_slots = []
        if wallet.isMultiSig or not wallet.is_standard():
            active_slots.append("type_icon")

        active_slots.extend(["name", "threshold"])
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
