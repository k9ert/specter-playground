from ..basic import RED_HEX, ORANGE_HEX, GenericMenu
from ..basic.symbol_lib import BTC_ICONS
from ..basic.widgets import MenuItem
import lvgl as lv

class SecuritySettingsMenu(GenericMenu):
    """Security hub: security features, firmware, backups, danger zone."""

    TITLE_KEY = "MENU_SETTINGS_SECURITY"

    def get_menu_items(self, t, state):
        menu_items = [
            MenuItem(BTC_ICONS.LOCK, t("SECURITY_MENU_LOCK_DEVICE"), "locked"),
            MenuItem(BTC_ICONS.SHIELD, t("MENU_MANAGE_SECURITY"), "manage_security_features", is_submenu=True),
            MenuItem(BTC_ICONS.FLIP_HORIZONTAL, t("MENU_ENABLE_DISABLE_INTERFACES"), "interfaces", is_submenu=True),
        ]

        if state.SD_detected() or state.USB_enabled() or state.QR_enabled():
            menu_items.append(MenuItem(BTC_ICONS.CODE, t("MENU_MANAGE_FIRMWARE"), "manage_firmware", is_submenu=True))

        if state.SD_detected():
            menu_items.append(MenuItem(BTC_ICONS.COPY, t("MENU_MANAGE_BACKUPS"), "manage_backups", is_submenu=True))

        menu_items += [
            MenuItem(BTC_ICONS.SIREN, text=t("DEVICE_MENU_DANGERZONE"), font_color=ORANGE_HEX),
            MenuItem(BTC_ICONS.ALERT_CIRCLE, t("DEVICE_MENU_WIPE"), "wipe_device", color=RED_HEX, help_key="HELP_DEVICE_MENU_WIPE"),
        ]

        return menu_items
