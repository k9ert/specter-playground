from ..basic import RED_HEX, ORANGE, GenericMenu
from ..basic.symbol_lib import BTC_ICONS
import lvgl as lv

def DeviceMenu(parent, *args, **kwargs):
    # Get translation function from i18n manager (always available via NavigationController)
    t = parent.i18n.t
    
    on_navigate = getattr(parent, "on_navigate", None)
    state = getattr(parent, "specter_state", None)

    menu_items = [(None, t("MENU_MANAGE_DEVICE"), None, None)]

    if state and state.hasSD and state.enabledSD and state.detectedSD:
        menu_items.append((BTC_ICONS.COPY, t("MENU_MANAGE_BACKUPS"), "manage_backups", None))

    if state and ((state.hasQR and state.enabledQR) or (state.hasSD and state.enabledSD and state.detectedSD) or (state.hasUSB and state.enabledUSB)):
        menu_items.append((BTC_ICONS.CODE, t("MENU_MANAGE_FIRMWARE"), "manage_firmware", None))

    menu_items += [
        (BTC_ICONS.SHIELD, t("MENU_MANAGE_SECURITY"), "manage_security", None),
        (BTC_ICONS.FLIP_HORIZONTAL, t("MENU_ENABLE_DISABLE_INTERFACES"), "interfaces", None),
        (BTC_ICONS.PHOTO, t("DEVICE_MENU_DISPLAY"), "display_settings", None),
        (lv.SYMBOL.VOLUME_MAX, t("DEVICE_MENU_SOUNDS"), "sound_settings", None),
        (BTC_ICONS.MESSAGE, t("MENU_LANGUAGE"), "select_language", None)
    ]

    menu_items += [
        (None, ORANGE + " " + lv.SYMBOL.WARNING+ " " + t("DEVICE_MENU_DANGERZONE") + "#", None, None),
        (BTC_ICONS.ALERT_CIRCLE, t("DEVICE_MENU_WIPE"), "wipe_device", RED_HEX)
    ]


    return GenericMenu("manage_device", t("MENU_MANAGE_DEVICE"), menu_items, parent, *args, **kwargs)
