from ..basic import RED_HEX, GenericMenu
from ..basic.symbol_lib import BTC_ICONS
from ..basic.widgets import MenuItem

class BackupsMenu(GenericMenu):
    """Menu for managing backups on SD Card."""

    TITLE_KEY = "MENU_MANAGE_BACKUPS"

    def get_menu_items(self, t, state):
        if state.SD_detected():
            return [
                MenuItem(BTC_ICONS.RECEIVE, t("BACKUPS_MENU_BACKUP_TO_SD"), "backup_to_sd"),
                MenuItem(BTC_ICONS.SEND, t("BACKUPS_MENU_RESTORE_FROM_SD"), "restore_from_sd"),
                MenuItem(BTC_ICONS.CROSS, t("BACKUPS_MENU_REMOVE_FROM_SD"), "remove_backup_from_sd", color=RED_HEX),
            ]
        else:
            return [MenuItem(text=t("BACKUPS_MENU_NO_SD_DETECTED"))]
