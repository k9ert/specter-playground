from ..basic import GenericMenu
import lvgl as lv

class ConnectWalletsMenu(GenericMenu):
    """Menu to connect or export to software wallets.

    menu_id: "connect_sw_wallet"
    """

    def __init__(self, parent, *args, **kwargs):
        # Get translation function from i18n manager (always available via NavigationController)
        t = parent.i18n.t
        
        # the actual connection logic is out of scope here; provide menu entries
        menu_items = [
            (None, t("CONNECT_WALLETS_SPARROW"), "connect_sparrow", None),
            (None, t("CONNECT_WALLETS_NUNCHUCK"), "connect_nunchuck", None),
            (None, t("CONNECT_WALLETS_BLUEWALLET"), "connect_bluewallet", None),
            (None, t("CONNECT_WALLETS_OTHER"), "connect_other", None),
        ]

        super().__init__("connect_sw_wallet", t("MENU_CONNECT_SW_WALLET"), menu_items, parent, *args, **kwargs)
