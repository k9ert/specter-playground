from ..basic import GenericMenu, BTC_ICONS, MenuItem, t

class SecurityFeaturesMenu(GenericMenu):
    TITLE_KEY = "MENU_MANAGE_SECURITY"

    def get_menu_items(self):
        return [
            MenuItem(BTC_ICONS.VERIFY, t("SECURITY_MENU_SELF_TEST"), "self_test"),
            MenuItem(BTC_ICONS.POINT_OF_SALE, t("SECURITY_MENU_CHANGE_PIN"), "change_pin"),
            MenuItem(BTC_ICONS.CONFIRMATIONS_4, t("SECURITY_MENU_PIN_RETRIES"), "set_allowed_pin_retries"),
            MenuItem(BTC_ICONS.SAFE, t("SECURITY_MENU_PIN_ACTION"), "set_exceeded_pin_action"),
            MenuItem(BTC_ICONS.HAT_AND_GLASSES, t("SECURITY_MENU_DURESS_PIN"), "set_duress_pin"),
            MenuItem(BTC_ICONS.MAGIC_WAND, t("SECURITY_MENU_DURESS_ACTION"), "set_duress_pin_action"),
        ]
