from ..basic import GenericMenu
from ..basic.symbol_lib import BTC_ICONS
from ..basic.widgets import MenuItem


class FirmwareMenu(GenericMenu):
    """Menu for firmware management."""

    TITLE_KEY = "MENU_MANAGE_FIRMWARE"

    def get_menu_items(self, t, state):
        fw_version = state.fw_version

        menu_items = [
            MenuItem(text=t("FIRMWARE_MENU_CURRENT_VERSION") + str(fw_version) + t("FIRMWARE_MENU_UPDATE_VIA")),
        ]

        if state.SD_detected():
            menu_items.append(MenuItem(BTC_ICONS.SD_CARD, t("HARDWARE_SD_CARD"), "update_fw_sd"))

        if state.USB_enabled():
            menu_items.append(MenuItem(BTC_ICONS.USB, t("HARDWARE_USB"), "update_fw_usb"))

        if state.QR_enabled():
            menu_items.append(MenuItem(BTC_ICONS.QR_CODE, t("HARDWARE_QR_CODE"), "update_fw_qr"))

        return menu_items
