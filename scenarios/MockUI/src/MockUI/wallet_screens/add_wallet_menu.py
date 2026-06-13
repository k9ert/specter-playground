from ..basic import GenericMenu, BTC_ICONS, MenuItem

class AddWalletMenu(GenericMenu):
    """Menu to import or create a custom wallet/descriptor.

    The default/standard wallet is auto-created when a key is loaded,
    so no "Use Standard Wallet" option is needed here.

    menu_id: "add_wallet"
    """

    TITLE_KEY = "MENU_ADD_WALLET"

    def get_menu_items(self, t, state):
        menu_items = []

        # Import section
        menu_items.append(MenuItem(text=t("ADD_WALLET_IMPORT_FROM")))

        if state.QR_enabled():
            menu_items.append(MenuItem(BTC_ICONS.SCAN, t("HARDWARE_QR_CODE"), "import_from_qr"))

        if state.SD_detected():
            menu_items.append(MenuItem(BTC_ICONS.SD_CARD, t("HARDWARE_SD_CARD"), "import_from_sd"))

        # Customize section
        menu_items += [
            MenuItem(text=t("ADD_WALLET_CUSTOMIZE")),
            MenuItem(BTC_ICONS.CONSOLE, t("ADD_WALLET_CREATE_CUSTOM"), "create_custom_wallet", is_submenu=True),
        ]

        return menu_items
