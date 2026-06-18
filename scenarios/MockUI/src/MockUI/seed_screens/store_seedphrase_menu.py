from ..basic import GenericMenu
from ..basic.symbol_lib import BTC_ICONS
from ..basic.widgets import MenuItem


class StoreSeedphraseMenu(GenericMenu):
    """Sub-menu for choosing where to store the seedphrase."""

    TITLE_KEY = "SEEDPHRASE_MENU_STORE_TO"

    def get_menu_items(self, t, state):
        menu_items = []
        highlighted = False

        if state.SmartCard_detected():
            menu_items.append(MenuItem(BTC_ICONS.SMARTCARD, t("HARDWARE_SMARTCARD"), 
                                       target="store_to_smartcard",
                                       modifier="Highlight"))
            highlighted = True
        if state.SD_detected():
            menu_items.append(MenuItem(BTC_ICONS.SD_CARD, t("HARDWARE_SD_CARD"), 
                                       target="store_to_sd",
                                       modifier="Highlight" if not highlighted else None))
            highlighted = True
        menu_items.append(MenuItem(BTC_ICONS.FILE, t("HARDWARE_INTERNAL_FLASH"),
                                   target="store_to_flash",
                                   modifier="Warning"))

        return menu_items
