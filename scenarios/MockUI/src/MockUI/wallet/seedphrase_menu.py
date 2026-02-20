from ..basic import ORANGE, ORANGE_HEX, RED_HEX, GenericMenu
from ..basic.symbol_lib import BTC_ICONS
import lvgl as lv

def SeedPhraseMenu(parent, *args, **kwargs):
    # Get translation function from i18n manager (always available via NavigationController)
    t = parent.i18n.t
    
    on_navigate = getattr(parent, "on_navigate", None)
    state = getattr(parent, "specter_state", None)

    menu_items = []

    # Show the seedphrase (requires confirmation in a real device)
    menu_items.append((BTC_ICONS.VISIBLE, t("SEEDPHRASE_MENU_SHOW"), "show_seedphrase", ORANGE_HEX))

    # Store Seedphrase group (label)
    menu_items.append((None, lv.SYMBOL.DOWNLOAD + " " + t("SEEDPHRASE_MENU_STORE_TO"), None, None))
    if state and state.hasSmartCard and state.enabledSmartCard and state.detectedSmartCard:
        menu_items.append((BTC_ICONS.SMARTCARD, t("HARDWARE_SMARTCARD"), "store_to_smartcard", None))
    if state and state.hasSD and state.enabledSD and state.detectedSD:
        menu_items.append((BTC_ICONS.SD_CARD, t("HARDWARE_SD_CARD"), "store_to_sd", None))
    menu_items.append((BTC_ICONS.FILE, t("HARDWARE_INTERNAL_FLASH"), "store_to_flash", None))

    # Clear Seedphrase group (label)
    menu_items.append((None, ORANGE + " " + lv.SYMBOL.CLOSE + " " + t("SEEDPHRASE_MENU_CLEAR_FROM") + "#", None, None))
    if state and state.hasSmartCard and state.enabledSmartCard and state.detectedSmartCard:
        menu_items.append((BTC_ICONS.SMARTCARD, t("HARDWARE_SMARTCARD"), "clear_from_smartcard", RED_HEX))
    if state and state.hasSD and state.enabledSD and state.detectedSD:
        menu_items.append((BTC_ICONS.SD_CARD, t("HARDWARE_SD_CARD"), "clear_from_sd", RED_HEX))
    menu_items.append((BTC_ICONS.FILE, t("HARDWARE_INTERNAL_FLASH"), "clear_from_flash", RED_HEX))
    menu_items.append((BTC_ICONS.TRASH, t("SEEDPHRASE_MENU_CLEAR_ALL"), "clear_all_storage", RED_HEX))

    # Derive new via BIP-85
    menu_items.append((None, t("SEEDPHRASE_MENU_ADVANCED"), None, None))
    menu_items.append((BTC_ICONS.SHARED_WALLET, t("SEEDPHRASE_MENU_BIP85"), "derive_bip85", None))

    return GenericMenu("manage_seedphrase", t("MENU_MANAGE_SEEDPHRASE"), menu_items, parent, *args, **kwargs)
