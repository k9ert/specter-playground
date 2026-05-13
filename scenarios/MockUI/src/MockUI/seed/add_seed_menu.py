from ..basic import GenericMenu
from ..basic.symbol_lib import BTC_ICONS
from ..basic.widgets import MenuItem
import lvgl as lv


class AddSeedMenu(GenericMenu):
    """Menu to create or import a MasterKey (seedphrase).

    menu_id: "add_seed"
    """

    TITLE_KEY = "MENU_ADD_SEED"

    def get_menu_items(self, t, state):
        menu_items = []

        # Generate section
        menu_items += [
            MenuItem(text=t("ADD_SEED_GENERATE_SECTION")),
            MenuItem(BTC_ICONS.DICE, t("ADD_SEED_GENERATE_SEED"), "generate_seedphrase", is_submenu=True),
        ]

        # Import section
        menu_items.append(MenuItem(text=t("ADD_SEED_IMPORT_SECTION")))

        # SmartCard (only when detected)
        if state.SmartCard_hasSeed():
            menu_items.append(MenuItem(BTC_ICONS.SMARTCARD, t("HARDWARE_SMARTCARD"), "import_from_smartcard"))

        # QR Code
        if state.QR_enabled():
            menu_items.append(MenuItem(BTC_ICONS.SCAN, t("HARDWARE_QR_CODE"), "import_from_qr"))

        # Keyboard (always available)
        menu_items.append(MenuItem(BTC_ICONS.KEYBOARD, t("COMMON_KEYBOARD"), "import_from_keyboard"))

        # SD Card (only if key data detected)
        if state.SD_hasSeed():
            menu_items.append(MenuItem(BTC_ICONS.SD_CARD, t("HARDWARE_SD_CARD"), "import_from_sd"))

        # Internal Flash (only if key data detected)
        if state.Flash_hasSeed():
            menu_items.append(MenuItem(BTC_ICONS.FILE, t("HARDWARE_INTERNAL_FLASH"), "import_from_flash"))

        return menu_items
