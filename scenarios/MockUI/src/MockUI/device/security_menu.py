from ..basic import GenericMenu
from ..basic.symbol_lib import BTC_ICONS
import lvgl as lv

def SecurityMenu(parent, *args, **kwargs):
    # Get translation function from i18n manager (always available via NavigationController)
    t = parent.i18n.t
    
    state = getattr(parent, "specter_state", None)

    menu_items = [
        (BTC_ICONS.PASSWORD, t("SECURITY_MENU_CHANGE_PIN"), "change_pin", None),
        (BTC_ICONS.CHECK, t("SECURITY_MENU_SELF_TEST"), "self_test", None),
        (None, t("SECURITY_MENU_PIN_RETRIES"), "set_allowed_pin_retries", None),
        (None, t("SECURITY_MENU_PIN_ACTION"), "set_exceeded_pin_action", None),
        (None, t("SECURITY_MENU_DURESS_PIN"), "set_duress_pin", None),
        (None, t("SECURITY_MENU_DURESS_ACTION"), "set_duress_pin_action", None),
    ]

    return GenericMenu("manage_security", t("MENU_MANAGE_SECURITY"), menu_items, parent, *args, **kwargs)
