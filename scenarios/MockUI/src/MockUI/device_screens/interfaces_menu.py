from ..basic import GenericMenu, BTC_ICONS, MenuItem


class InterfacesMenu(GenericMenu):
    """Menu to enable/disable hardware interfaces."""

    TITLE_KEY = "MENU_ENABLE_DISABLE_INTERFACES"

    def get_menu_items(self, t, state):
        items = []
        if state.hasQR():
            items.append(MenuItem(
                BTC_ICONS.QR_CODE, t("HARDWARE_QR_CODE"),
                get_value=lambda: state.QR_enabled(),
                set_value=state.set_QR_enabled,
            ))
        if state.hasUSB():
            items.append(MenuItem(
                BTC_ICONS.USB, t("HARDWARE_USB"),
                get_value=lambda: state.USB_enabled(),
                set_value=state.set_USB_enabled,
            ))
        if state.hasSD():
            items.append(MenuItem(
                BTC_ICONS.SD_CARD, t("HARDWARE_SD_CARD"),
                get_value=lambda: state.SD_enabled(),
                set_value=state.set_SD_enabled,
            ))
        if state.hasSmartCard():
            items.append(MenuItem(
                BTC_ICONS.SMARTCARD, t("HARDWARE_SMARTCARD"),
                get_value=lambda: state.SmartCard_enabled(),
                set_value=state.set_SmartCard_enabled,
            ))
        return items
