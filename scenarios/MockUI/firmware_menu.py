import lvgl as lv
from .menu import GenericMenu


class FirmwareMenu(GenericMenu):
    """Menu for firmware management.

    menu_id: "manage_firmware"
    """

    def __init__(self, parent, *args, **kwargs):
        state = parent.specter_state

        # menu items (firmware version will be shown separately as a small label)
        # support either `fw_version` or `firmware_version` on the state object
        fw_version = state.fw_version

        menu_items = [
            ("Current version " + str(fw_version) + ". Update via", None),
        ]

        # conditional sources (guard against missing attributes)
        if state and getattr(state, 'hasSD', False) and getattr(state, 'enabledSD', False) and getattr(state, 'detectedSD', False):
            menu_items.append(("SD Card", "update_fw_sd"))

        if state and getattr(state, 'hasUSB', False) and getattr(state, 'enabledUSB', False):
            menu_items.append(("USB", "update_fw_usb"))

        if state and getattr(state, 'hasQR', False) and getattr(state, 'enabledQR', False):
            menu_items.append(("QR", "update_fw_qr"))


        title = "Manage Firmware"
        super().__init__("manage_firmware", title, menu_items, parent, *args, **kwargs)


