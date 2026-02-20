from ..basic import GenericMenu
from ..basic.symbol_lib import BTC_ICONS
import lvgl as lv

class StorageMenu(GenericMenu):
    """Menu to manage storage devices (SD / SmartCard).

    menu_id: "manage_storage"
    """

    def __init__(self, parent, *args, **kwargs):
        # Get translation function from i18n manager (always available via NavigationController)
        t = parent.i18n.t
        
        # Build the menu items depending on available/enabled/detected devices
        on_navigate = getattr(parent, "on_navigate", None)
        state = getattr(parent, "specter_state", None)

        menu_items = [(None, t("MENU_MANAGE_STORAGE"), None, None)]
        menu_items.append((BTC_ICONS.FILE, t("STORAGE_MENU_INTERNAL_FLASH"), "internal_flash", None))

        if state and state.hasSmartCard and state.enabledSmartCard and state.detectedSmartCard:
            menu_items.append((BTC_ICONS.SMARTCARD, t("STORAGE_MENU_SMARTCARD"), "smartcard", None))

        if state and state.hasSD and state.enabledSD and state.detectedSD:
            menu_items.append((BTC_ICONS.SD_CARD, t("STORAGE_MENU_SD_CARD"), "sdcard", None))

        super().__init__("manage_storage", t("MENU_MANAGE_STORAGE"), menu_items, parent, *args, **kwargs)
