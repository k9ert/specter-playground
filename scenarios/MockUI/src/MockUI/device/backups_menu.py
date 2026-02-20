from ..basic import ORANGE_HEX, RED_HEX, GenericMenu
import lvgl as lv
from ..basic.symbol_lib import BTC_ICONS

class BackupsMenu(GenericMenu):
    """Menu for managing backups on SD Card.

    menu_id: "manage_backups"
    """

    def __init__(self, parent, *args, **kwargs):
        # Get translation function from i18n manager (always available via NavigationController)
        t = parent.i18n.t
        
        state = getattr(parent, "specter_state", None)

        menu_items = [
            (BTC_ICONS.RECEIVE, t("BACKUPS_MENU_BACKUP_TO_SD"), "backup_to_sd", None),
            (BTC_ICONS.SEND, t("BACKUPS_MENU_RESTORE_FROM_SD"), "restore_from_sd", None),
            (BTC_ICONS.CROSS, t("BACKUPS_MENU_REMOVE_FROM_SD"), "remove_backup_from_sd", RED_HEX),
        ]

        title = t("MENU_MANAGE_BACKUPS")

        super().__init__("manage_backups", title, menu_items, parent, *args, **kwargs)
