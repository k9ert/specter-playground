from ..basic import GenericMenu
from ..basic.symbol_lib import BTC_ICONS
from ..basic.widgets import MenuItem


class PreferencesMenu(GenericMenu):
    """Menu for UI preferences: display, sounds, tour restart."""

    TITLE_KEY = "MENU_MANAGE_PREFERENCES"

    def get_menu_items(self, t, state):
        return [
            MenuItem(BTC_ICONS.MAGIC_WAND, t("DEVICE_MENU_ANIMATIONS"), 
                     get_value=lambda: self.ui_state.are_animations_enabled,
                     set_value=lambda v: setattr(self.ui_state, "are_animations_enabled", v)),
            MenuItem(BTC_ICONS.PHOTO, t("DEVICE_MENU_DISPLAY"), "display_settings"),
            MenuItem(BTC_ICONS.BELL, t("DEVICE_MENU_SOUNDS"), "sound_settings"),
            MenuItem(BTC_ICONS.REFRESH, t("DEVICE_MENU_RESTART_TOUR"), "start_intro_tour"),
        ]
