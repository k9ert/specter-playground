from ..basic import GenericMenu
from ..basic.symbol_lib import BTC_ICONS
import lvgl as lv


class FirmwareMenu(GenericMenu):
    """Menu for firmware management.

    menu_id: "manage_firmware"
    """

    def __init__(self, parent, *args, **kwargs):
        # Get translation function from i18n manager (always available via NavigationController)
        t = parent.i18n.t
        
        state = parent.specter_state

        # menu items (firmware version will be shown separately as a small label)
        # support either `fw_version` or `firmware_version` on the state object
        fw_version = state.fw_version

        menu_items = [
            (None, t("FIRMWARE_MENU_CURRENT_VERSION") + str(fw_version) + t("FIRMWARE_MENU_UPDATE_VIA"), None, None),
        ]

        # conditional sources (guard against missing attributes)
        if state and getattr(state, 'hasSD', False) and getattr(state, 'enabledSD', False) and getattr(state, 'detectedSD', False):
            menu_items.append((BTC_ICONS.SD_CARD, t("HARDWARE_SD_CARD"), "update_fw_sd", None))

        if state and getattr(state, 'hasUSB', False) and getattr(state, 'enabledUSB', False):
            menu_items.append((BTC_ICONS.USB, t("HARDWARE_USB"), "update_fw_usb", None))

        if state and getattr(state, 'hasQR', False) and getattr(state, 'enabledQR', False):
            menu_items.append((BTC_ICONS.QR_CODE, t("HARDWARE_QR_CODE"), "update_fw_qr", None))


        title = t("MENU_MANAGE_FIRMWARE")
        super().__init__("manage_firmware", title, menu_items, parent, *args, **kwargs)
