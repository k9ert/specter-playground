from .menu import GenericMenu


class ConnectWalletsMenu(GenericMenu):
    """Menu to connect or export to software wallets.

    menu_id: "connect_sw_wallet"
    """

    def __init__(self, parent, *args, **kwargs):
        # the actual connection logic is out of scope here; provide menu entries
        menu_items = [
            ("Sparrow", "connect_sparrow"),
            ("Nunchuck", "connect_nunchuck"),
            ("BlueWallet", "connect_bluewallet"),
            ("Other...", "connect_other"),
        ]

        title = "Connect/Export"
        super().__init__("connect_sw_wallet", title, menu_items, parent, *args, **kwargs)
