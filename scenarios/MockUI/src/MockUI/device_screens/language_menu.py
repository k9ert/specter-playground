import lvgl as lv
from ..basic import GenericMenu, BTC_ICONS, MenuItem


class LanguageMenu(GenericMenu):
    """Menu to select UI language, with option to load new language files."""
    TITLE_KEY = "MENU_LANGUAGE"

    def get_menu_items(self, t, state):
        languages = self.i18n.get_available_languages()
        active = self.i18n.get_language()
        show_check = len(languages) > 1

        items = []
        for lang_code in languages:
            items.append(MenuItem(
                BTC_ICONS.CHECK if show_check and lang_code == active else None,
                self.i18n.get_language_name(lang_code),
                self._make_select_cb(lang_code),
            ))

        if state.SD_detected():
            items.append(MenuItem(
                BTC_ICONS.PLUS, t("MENU_LOAD_NEW_LANGUAGE"), "load_language",
            ))

        return items

    def _make_select_cb(self, lang_code):
        def cb(e):
            if e.get_code() == lv.EVENT.CLICKED:
                self.gui.change_language(lang_code)
                self.gui.refresh_ui()
                self.on_navigate(None)
        return cb