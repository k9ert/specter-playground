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

        QR_enabled = state.QR_enabled()
        SD_detected = state.SD_detected()
        none_ready = not (QR_enabled or SD_detected)
        both_ready = QR_enabled and SD_detected

        #prefer SD over QR if detected, assuming user put it in intentionally
        Interfaces_modifier = "Highlight" if none_ready else None
        SD_modifier = "Highlight" if SD_detected else None
        QR_modifier = "Highlight" if QR_enabled and not SD_detected else None

        # Import section
        menu_items.append(MenuItem(text=t("ADD_WALLET_IMPORT_FROM")))

        if QR_enabled:
            menu_items.append(MenuItem(BTC_ICONS.QR_CODE, t("HARDWARE_QR_CODE"),
                                        target="import_from_qr",
                                        modifier=QR_modifier))

        if SD_detected:
            menu_items.append(MenuItem(BTC_ICONS.SD_CARD, t("HARDWARE_SD_CARD"),
                                        target="import_from_sd", 
                                        modifier=SD_modifier))

        if not both_ready:            
            menu_items.append(MenuItem(BTC_ICONS.FLIP_HORIZONTAL, text=t("ADD_WALLET_ENABLE_INTERFACES"),
                                       target="interfaces", 
                                       modifier=Interfaces_modifier))


        # TODO: Customize section [DUMMY DURING DEVELOPMENT, remove once hw in integrated]
        menu_items += [
            MenuItem(text=t("ADD_WALLET_CUSTOMIZE")),
            MenuItem(BTC_ICONS.CONSOLE, t("ADD_WALLET_CREATE_CUSTOM"), "create_custom_wallet", is_submenu=True),
        ]

        return menu_items
