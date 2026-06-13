from ..basic import GenericMenu, BTC_ICONS, MenuItem
from ..basic.theming.theme_manager import ColorMode


class PreferencesMenu(GenericMenu):
    """Menu for UI preferences: display, sounds, tour restart."""

    TITLE_KEY = "MENU_MANAGE_PREFERENCES"

    def _set_dark_mode(self, on):
        self.gui.change_mode(ColorMode.DARK if on else ColorMode.LIGHT)

    def get_menu_items(self, t, state):
        return [
            MenuItem(BTC_ICONS.MAGIC_WAND, t("DEVICE_MENU_ANIMATIONS"),
                     get_value=lambda: self.ui_state.are_animations_enabled,
                     set_value=lambda v: setattr(self.ui_state, "are_animations_enabled", v)),
            MenuItem(BTC_ICONS.MOON, t("DEVICE_MENU_DARK_MODE"),
                     get_value=lambda: self.theme.mode == ColorMode.DARK,
                     set_value=self._set_dark_mode),
            MenuItem(BTC_ICONS.BRUSH, t("DEVICE_MENU_THEME"), "select_theme"),
            MenuItem(BTC_ICONS.PHOTO, t("DEVICE_MENU_DISPLAY"), "display_settings"),
            MenuItem(BTC_ICONS.BELL, t("DEVICE_MENU_SOUNDS"), "sound_settings"),
            MenuItem(BTC_ICONS.REFRESH, t("DEVICE_MENU_RESTART_TOUR"), "start_intro_tour"),
        ]
