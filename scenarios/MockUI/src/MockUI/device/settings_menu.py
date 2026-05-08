import lvgl as lv
from ..basic.menu import GenericMenu
from ..basic.titled_screen import TitledScreen
from ..basic.symbol_lib import BTC_ICONS
from ..basic.widgets import MenuItem
from ..basic.ui_consts import BTC_ICON_WIDTH, STATUS_BTN_HEIGHT, GREEN_HEX, WHITE_HEX, GREY_HEX
from ..basic.widgets.icon_widgets import make_icon


class SettingsMenu(GenericMenu):
    TITLE_KEY = "MENU_MANAGE_SETTINGS"

    def __init__(self, parent):
        # Call TitledScreen.__init__ directly so we control build order:
        # interface icon row first, then menu items (no move_to_index needed).
        TitledScreen.__init__(self, "", parent)

        t = self.i18n.t
        state = self.device_state

        self.body.set_layout(lv.LAYOUT.FLEX)
        self.body.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.body.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)

        # 1. Interface icon row at the top
        self._build_iface_row(state)

        # 2. Menu items below
        menu_items = self.get_menu_items(t, state)
        self._build_menu_items(menu_items)

        self.post_init(t, state)
        self._configure_scroll()

    def _build_iface_row(self, state):
        row = lv.obj(self.body)
        row.set_width(lv.pct(100))
        row.set_height(STATUS_BTN_HEIGHT)
        row.set_layout(lv.LAYOUT.FLEX)
        row.set_flex_flow(lv.FLEX_FLOW.ROW)
        row.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        row.set_style_pad_all(0, 0)
        row.set_style_border_width(0, 0)
        row.set_style_radius(0, 0)

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
            self.gui.show_menu("interfaces")

    def get_menu_items(self, t, state):
        lang_code = self.i18n.get_language()
        lang_label = t("MENU_LANGUAGE") + " (" + lang_code.upper() + ")"

        return [
            MenuItem(BTC_ICONS.SHIELD, t("MENU_SETTINGS_SECURITY"), "manage_security_settings", is_submenu=True),
            MenuItem(BTC_ICONS.FILE, t("MENU_MANAGE_STORAGE"), "manage_storage", is_submenu=True),
            MenuItem(BTC_ICONS.CONTACTS, t("MENU_MANAGE_PREFERENCES"), "manage_preferences", is_submenu=True),
            MenuItem(BTC_ICONS.GLOBE, lang_label, "select_language", is_submenu=True),
        ]
