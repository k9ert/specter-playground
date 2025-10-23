import lvgl as lv
from .menu import GenericMenu


class StorageMenu(GenericMenu):
    """Menu to manage storage devices (SD / SmartCard).

    menu_id: "manage_storage"
    """

    def __init__(self, parent, *args, **kwargs):
        # Build the menu items depending on available/enabled/detected devices
        on_navigate = getattr(parent, "on_navigate", None)
        state = getattr(parent, "specter_state", None)

        menu_items = [("Manage Storage", None)]

        if state and state.hasSmartCard and state.enabledSmartCard and state.detectedSmartCard:
            menu_items.append(("Manage SmartCard", "smartcard"))

        if state and state.hasSD and state.enabledSD and state.detectedSD:
            menu_items.append(("Manage SD Card", "sdcard"))

        super().__init__("manage_storage", "Manage Storage", menu_items, parent, *args, **kwargs)
