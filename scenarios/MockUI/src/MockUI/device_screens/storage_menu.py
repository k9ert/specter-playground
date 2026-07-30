from ..basic import GenericMenu, BTC_ICONS, MenuItem, t

class StorageMenu(GenericMenu):
    """Menu to manage storage devices (SD / SmartCard)."""

    TITLE_KEY = "MENU_MANAGE_STORAGE"

    def get_menu_items(self):
        state = self.device_state
        menu_items = [MenuItem(BTC_ICONS.FILE, t("STORAGE_MENU_INTERNAL_FLASH"), "internal_flash")]

        if state.SmartCard_detected():
            menu_items.append(MenuItem(BTC_ICONS.SMARTCARD, t("STORAGE_MENU_SMARTCARD"), "smartcard"))

        if state.SD_detected():
            menu_items += [
                MenuItem(BTC_ICONS.SD_CARD, t("STORAGE_MENU_SD_CARD"), "sdcard"),
                MenuItem(BTC_ICONS.COPY, t("MENU_MANAGE_BACKUPS"), "manage_backups", is_submenu=True),
            ]

        return menu_items
