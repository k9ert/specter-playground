import lvgl as lv
from ..basic.menu import GenericMenu
from ..basic.symbol_lib import BTC_ICONS
from ..basic.widgets import MenuItem
from ..basic.ui_consts import BTC_ICON_WIDTH, STATUS_BTN_HEIGHT, GREEN_HEX, WHITE_HEX, GREY_HEX
from ..basic.widgets.icon_widgets import make_icon
from ..basic.widgets.containers import flex_row


class SettingsMenu(GenericMenu):
    TITLE_KEY = "MENU_MANAGE_SETTINGS"

    def pre_init(self, t, state):
        self._build_iface_row(state)

    def _build_iface_row(self, state):
        row = flex_row(self.body, width=lv.pct(100), height=STATUS_BTN_HEIGHT, main_align=lv.FLEX_ALIGN.CENTER)

        def _add_ico(icon, color):
            img = make_icon(row, icon, color)
            img.add_flag(lv.obj.FLAG.CLICKABLE)
            img.add_event_cb(self._iface_ico_cb, lv.EVENT.CLICKED, None)

        if state.hasQR():
            _add_ico(BTC_ICONS.QR_CODE, GREEN_HEX if state.QR_enabled() else GREY_HEX)
        if state.hasUSB():
            _add_ico(BTC_ICONS.USB, WHITE_HEX if state.USB_enabled() else GREY_HEX)
        if state.hasSD():
            col = (GREEN_HEX if state.SD_detected() else WHITE_HEX) if state.SD_enabled() else GREY_HEX
            _add_ico(BTC_ICONS.SD_CARD, col)
        if state.hasSmartCard():
            col = (GREEN_HEX if state.SmartCard_detected() else WHITE_HEX) if state.SmartCard_enabled() else GREY_HEX
            _add_ico(BTC_ICONS.SMARTCARD, col)

    def _iface_ico_cb(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            self.gui.navigate_to("interfaces")

    def get_menu_items(self, t, state):
        lang_code = self.i18n.get_language()
        lang_label = t("MENU_LANGUAGE") + " (" + lang_code.upper() + ")"

        return [
            MenuItem(BTC_ICONS.SHIELD, t("MENU_SETTINGS_SECURITY"), "manage_security_settings", is_submenu=True),
            MenuItem(BTC_ICONS.FILE, t("MENU_MANAGE_STORAGE"), "manage_storage", is_submenu=True),
            MenuItem(BTC_ICONS.CONTACTS, t("MENU_MANAGE_PREFERENCES"), "manage_preferences", is_submenu=True),
            MenuItem(BTC_ICONS.GLOBE, lang_label, "select_language", is_submenu=True),
        ]
