import lvgl as lv
from ..basic import GenericMenu
from ..basic.symbol_lib import BTC_ICONS
from ..basic.widgets import MenuItem
from ..basic.widgets.wallet_widgets import wallet_signing_color


def _wallet_type_rank(wallet):
    """Return (type_rank, n, m, account) for sort ordering."""
    if not wallet.is_standard():
        type_rank = 2  # custom / miniscript
    elif wallet.isMultiSig:
        type_rank = 1  # multisig
    else:
        type_rank = 0  # singleSig
    n = len(wallet.required_fingerprints) if wallet.isMultiSig else 0
    m = wallet.threshold if wallet.isMultiSig else 0
    return (type_rank, n, m, getattr(wallet, "account", 0))


class RelatedWalletsForSeedMenu(GenericMenu):
    """Lists wallets whose required signers include the active seed's fingerprint.

    Sorted by type (singleSig → multisig → custom), then for multisig by N
    (number of signers), then by M (threshold), then by account number.
    Clicking a wallet item opens the wallet menu for that wallet.

    menu_id: "related_wallets_for_seed"
    """

    TITLE_KEY = "SEEDPHRASE_MENU_RELATED_WALLETS"

    def get_menu_items(self, t, state):
        menu_items = []

        if not self.ui_state.active_seed:
            return menu_items

        fp = self.ui_state.active_seed.get_fingerprint()
        related = [
            w for w in state.registered_wallets
            if not w.is_default_wallet() and fp in w.required_fingerprints
        ]
        related.sort(key=_wallet_type_rank)

        for wallet in related:
            # Type icon + signing color
            if not wallet.is_standard():
                type_icon = BTC_ICONS.CONSOLE
            elif wallet.isMultiSig:
                type_icon = BTC_ICONS.TWO_KEYS
            else:
                type_icon = BTC_ICONS.KEY

            key_color = wallet_signing_color(wallet, state)

            # Right-side suffix: threshold, account, network
            suffix = []
            if wallet.isMultiSig and wallet.threshold is not None:
                n = len(wallet.required_fingerprints)
                suffix.append((None, None, str(wallet.threshold) + "/" + str(n)))
            if getattr(wallet, "account", 0) != 0:
                suffix.append((None, None, "#" + str(wallet.account)))
            if getattr(wallet, "net", "mainnet") != "mainnet":
                net_map = {"testnet": "test", "signet": "sig"}
                suffix.append((None, None, net_map.get(wallet.net, wallet.net)))

            def _make_cb(w):
                def _cb(e):
                    if e.get_code() != lv.EVENT.CLICKED:
                        return
                    self.ui_state.set_active_wallet(w)
                    self.on_navigate("manage_wallet")
                return _cb

            menu_items.append(MenuItem(
                type_icon,
                wallet.label,
                target=_make_cb(wallet),
                suffix=suffix if suffix else None,
            ))

        return menu_items
