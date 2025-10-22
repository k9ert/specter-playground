from .menu import GenericMenu


class BackupsMenu(GenericMenu):
    """Menu for managing backups on SD Card.

    menu_id: "manage_backups"
    """

    def __init__(self, parent, *args, **kwargs):
        state = getattr(parent, "specter_state", None)

        menu_items = [
            ("Backup device to SD Card", "backup_to_sd"),
            ("Restore device from SD Card", "restore_from_sd"),
            ("Remove Backup from SD Card", "remove_backup_from_sd"),
        ]

        title = "Manage Backups"

        super().__init__("manage_backups", title, menu_items, parent, *args, **kwargs)
