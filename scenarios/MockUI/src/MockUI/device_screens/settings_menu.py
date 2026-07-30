import lvgl as lv
from ..basic import (
    GenericMenu, BTC_ICONS, MenuItem, SpecterGuiElement,
    make_icon, apply_style, t
)

class SettingsMenu(GenericMenu):
    TITLE_KEY = "MENU_MANAGE_SETTINGS"

    def pre_itemlist(self):
        state = self.device_state
        
        self.row = SpecterGuiElement(self.body)
        apply_style(self.row, "CONTAINER.INTERFACE_STATUS")

        def _add_ico(icon):
            img = make_icon(self.row, icon)
            apply_style(img, "WIDGET.INFO_ITEM")
            img.add_flag(lv.obj.FLAG.CLICKABLE)
            img.add_event_cb(self._iface_ico_cb, lv.EVENT.CLICKED, None)
            return img

        if state.hasQR():
            self.QR_ico = _add_ico(BTC_ICONS.QR_CODE)
            if not state.QR_enabled():
                apply_style(self.QR_ico, "MODIFIER.MUTED")
        if state.hasUSB():
            self.USB_ico = _add_ico(BTC_ICONS.USB)
            if not state.USB_enabled():
                apply_style(self.USB_ico, "MODIFIER.MUTED")
        if state.hasSD():
            self.SD_ico = _add_ico(BTC_ICONS.SD_CARD)
            if not state.SD_enabled():
                apply_style(self.SD_ico, "MODIFIER.MUTED")
            if state.SD_detected():
                apply_style(self.SD_ico, "FG.SUCCESS")
        if state.hasSmartCard():
            self.SmartCard_ico = _add_ico(BTC_ICONS.SMARTCARD)
            if not state.SmartCard_enabled():
                apply_style(self.SmartCard_ico, "MODIFIER.MUTED")
            if state.SmartCard_detected():
                apply_style(self.SmartCard_ico, "FG.SUCCESS")

    def _iface_ico_cb(self, e):
        self.gui.navigate_to("interfaces")

    def get_menu_items(self):
        lang_code = self.i18n.get_language()
        lang_label = t("MENU_LANGUAGE") + " (" + lang_code.upper() + ")"

        return [
            MenuItem(BTC_ICONS.SHIELD, t("MENU_SETTINGS_SECURITY"), "manage_security_settings", is_submenu=True),
            MenuItem(BTC_ICONS.FILE, t("MENU_MANAGE_STORAGE"), "manage_storage", is_submenu=True),
            MenuItem(BTC_ICONS.CONTACTS, t("MENU_MANAGE_PREFERENCES"), "manage_preferences", is_submenu=True),
            MenuItem(BTC_ICONS.GLOBE, lang_label, "select_language", is_submenu=True),
        ]
