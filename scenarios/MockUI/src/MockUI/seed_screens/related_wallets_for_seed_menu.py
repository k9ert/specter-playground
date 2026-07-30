import lvgl as lv
from ..basic import (
    TitledScreen,
    delete_all_children_of, set_propagate_events,
    Btn,
    make_label,
    WalletCard,
    apply_style,
    t,
)
from ..stubs.wallet import WalletType, _wallet_type_rank

class RelatedWalletsForSeedMenu(TitledScreen):
    """Lists wallets associated with the active seed.

    Uses device_state.wallets_for_seed() which includes the Default Wallet and
    all wallets whose required signers contain the seed's fingerprint.

    Sorted by type (singleSig → multisig → custom), then for multisig by N
    (number of signers), then by M (threshold), then by account number.
    Clicking a wallet button navigates to the wallet menu for that wallet.

    menu_id: "related_wallets_for_seed"
    """

    def __init__(self, parent):
        super().__init__(t("SEEDPHRASE_MENU_RELATED_WALLETS"), parent)
        apply_style(self.body, "CONTAINER.MENU_CONTAINER")
        self._fill()

    def _fill(self):
        delete_all_children_of(self.body)

        wallets = sorted(
            self.device_state.wallets_for_seed(self.ui_state.active_seed) or [],
            key=_wallet_type_rank,
        )

        # Cross-wallet column alignment
        any_account = any(getattr(w, "account", 0) != 0 for w in wallets)
        any_net     = any(w.net != "mainnet" for w in wallets)
        any_non_singlesig = any(w.isMultiSig for w in wallets)
        active_slots = ["name"]
        if any_non_singlesig:
            active_slots.insert(0, "type_icon")
            active_slots.append("threshold")
        if any_account:
            active_slots.append("account")
        if any_net:
            active_slots.append("net")

        type = [_wallet_type_rank(w)[0] for w in wallets]
        only_singlesig = all(t in (WalletType.SINGLE_SIG, WalletType.SINGLE_SIG_DEFAULT) for t in type)
        if not only_singlesig:
            head_lbl = make_label(self.body, self.t("COMMON_SINGLESIG"))
            apply_style(head_lbl, "WIDGET.MENU_SECTION_HEADER")

        for [i, wallet] in enumerate(wallets):
            if i > 0 and type[i] != type[i-1] and type[i] != WalletType.SINGLE_SIG:  # section header detection based on sorted order
                if type[i] == WalletType.MULTISIG:
                    heading = self.t("COMMON_MULTISIG")
                elif type[i] == WalletType.CUSTOM:
                    heading = self.t("COMMON_MINISCRIPT")
                head_lbl = make_label(self.body, heading)
                apply_style(head_lbl, "WIDGET.MENU_SECTION_HEADER")

            def _make_cb(w):
                def _cb(e):
                    if e.get_code() == lv.EVENT.CLICKED:
                        self.on_navigate("manage_wallet", target_wallet=w)
                return _cb

            btn = Btn(self.body, background_style="WIDGET.MENU_BUTTON")
            card = WalletCard(
                btn._btn,
                wallet,
                self.device_state,
                slots=active_slots,
                on_card_click=_make_cb(wallet),
            )
            apply_style(card, "CONTAINER.DROP_UP_ROW")
            set_propagate_events(card, True)

        self._configure_scroll()

    def refresh(self):
        self._fill()
