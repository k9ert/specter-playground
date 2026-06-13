from ..basic import GenericMenu, BTC_ICONS, MenuItem

class ClearSeedphraseMenu(GenericMenu):
    """Sub-menu for choosing where to clear the seedphrase from."""

    TITLE_KEY = "SEEDPHRASE_MENU_CLEAR_FROM"

    def get_menu_items(self, t, state):
        menu_items = []

        if state.SmartCard_hasSeed():
            menu_items.append(MenuItem(BTC_ICONS.SMARTCARD, t("HARDWARE_SMARTCARD"), "clear_from_smartcard", modifier="Danger"))
        if state.SD_hasSeed():
            menu_items.append(MenuItem(BTC_ICONS.SD_CARD, t("HARDWARE_SD_CARD"), "clear_from_sd", modifier="Danger"))
        menu_items += [
            MenuItem(BTC_ICONS.FILE, t("HARDWARE_INTERNAL_FLASH"), "clear_from_flash", modifier="Danger"),
            MenuItem(BTC_ICONS.TRASH, t("SEEDPHRASE_MENU_CLEAR_ALL"), "clear_all_storage", modifier="Danger"),
        ]

        return menu_items
