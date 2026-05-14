import lvgl as lv
from ..basic.titled_screen import TitledScreen
from ..basic.specter_gui_base import delete_all_children_of
from ..basic.ui_consts import BTN_HEIGHT, BTN_WIDTH, SCREEN_WIDTH
from ..basic.widgets.btn import Btn
from ..basic.widgets.labels import section_header
from ..basic.widgets.wallet_widgets import build_wallet_card
from ..basic.symbol_lib import BTC_ICONS

class WalletType:
    SINGLE_SIG_DEFAULT = 0
    SINGLE_SIG = 1
    MULTISIG = 2
    CUSTOM = 3

def _wallet_type_rank(wallet):
    """Return (type_rank, n, m, account) for sort ordering."""
    if not wallet.is_standard():
        type_rank = WalletType.CUSTOM  # custom / miniscript
    elif wallet.isMultiSig:
        type_rank = WalletType.MULTISIG  # multisig
    elif wallet.is_default_wallet():
        type_rank = WalletType.SINGLE_SIG_DEFAULT  # single-sig default wallet
    else:
        type_rank = WalletType.SINGLE_SIG  # non default singleSig
    n = len(wallet.required_fingerprints) if wallet.isMultiSig else 0
    m = wallet.threshold if wallet.isMultiSig else 0
    return (type_rank, n, m, getattr(wallet, "account", 0))


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
        title = parent.i18n.t("SEEDPHRASE_MENU_RELATED_WALLETS")
        super().__init__(title, parent)

        self.body.set_layout(lv.LAYOUT.FLEX)
        self.body.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.body.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)

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
            section_header(self.body, self.t("COMMON_SINGLESIG"))

        for [i, wallet] in enumerate(wallets):
            if i > 0 and type[i] != type[i-1] and type[i] != WalletType.SINGLE_SIG:  # section header detection based on sorted order
                if type[i] == WalletType.MULTISIG:
                    heading = self.t("COMMON_MULTISIG")
                elif type[i] == WalletType.CUSTOM:
                    heading = self.t("COMMON_MINISCRIPT")
                section_header(self.body, heading)

            def _make_cb(w):
                def _cb(e):
                    if e.get_code() == lv.EVENT.CLICKED:
                        self.on_navigate("manage_wallet", target_wallet=w)
                return _cb

            btn = Btn(
                self.body,
                size=(lv.pct(BTN_WIDTH), BTN_HEIGHT)
            )
            btn._btn.set_style_pad_all(0, 0)
            card = build_wallet_card(
                btn._btn,
                wallet,
                self.device_state,
                slots=active_slots,
                on_card_click=_make_cb(wallet),
                width=SCREEN_WIDTH,
                height=BTN_HEIGHT,
                border=False,
                event_bubble=True,
            )

        self._configure_scroll()

    def refresh(self):
        self._fill()
