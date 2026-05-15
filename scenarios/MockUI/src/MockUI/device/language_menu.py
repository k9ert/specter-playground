from ..basic import SwitchAddMenu

class LanguageMenu(SwitchAddMenu):
    """Menu to select UI language, with option to load new language files."""
    TITLE_KEY = "MENU_LANGUAGE"

    def get_menu_items(self, t, state):
        return super()._build_switch_items(
            elements=self.i18n.get_available_languages(),
            label_creation_cb=lambda lang_code: self.i18n.get_language_name(lang_code),
            active_element=self.i18n.get_language(),
            activation_cb= lambda lang_code: self.gui.change_language(lang_code),
            add_target_behavior= "load_language" if state.SD_detected() else None,
            add_string= t("MENU_LOAD_NEW_LANGUAGE") if state.SD_detected() else None
        )