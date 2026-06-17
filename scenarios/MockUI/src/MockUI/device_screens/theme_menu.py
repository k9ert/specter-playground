import lvgl as lv
from ..basic import GenericMenu, BTC_ICONS, MenuItem


class ThemeMenu(GenericMenu):
    """Menu to select the active UI theme."""

    TITLE_KEY = "DEVICE_MENU_THEME"

    def get_menu_items(self, t, state):
        themes = self.theme.get_available_files()
        active = self.theme.current
        show_check = len(themes) > 1

        items = []
        for name in themes:
            items.append(MenuItem(
                BTC_ICONS.CHECK if show_check and name == active else None,
                self.theme.get_file_name(name),
                self._make_select_cb(name),
            ))

        if state.SD_detected():
            items.append(MenuItem(
                BTC_ICONS.PLUS, t("MENU_LOAD_NEW_THEME"), "load_theme",
            ))

        return items

    def _make_select_cb(self, name):
        def cb(e):
            if e.get_code() == lv.EVENT.CLICKED:
                self.gui.change_theme(name)
                self.on_navigate(None)
        return cb
