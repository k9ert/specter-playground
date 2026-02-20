from ..basic import GenericMenu
from ..basic.symbol_lib import BTC_ICONS
import lvgl as lv

class AddWalletMenu(GenericMenu):
    """Menu to create or import a wallet.

    Menu items:
    - Generate New Seedphrase
    - Import Seedphrase from: SmartCard, QR Code, SD Card, internal Flash, Keyboard
      Conditional items included according to parent.specter_state flags.
    """

    def __init__(self, parent, *args, **kwargs):
        # Get translation function from i18n manager (always available via NavigationController)
        t = parent.i18n.t
        
        state = getattr(parent, "specter_state", None)

        menu_items = [
            (BTC_ICONS.MNEMONIC, t("MENU_GENERATE_NEW_SEEDPHRASE"), "generate_seedphrase", None),
            (None, t("ADD_WALLET_IMPORT_FROM"), None, None),
        ]

        # Add SmartCard import if available
        if state and state.hasSmartCard and state.enabledSmartCard and state.detectedSmartCard:
            menu_items.append((BTC_ICONS.SMARTCARD, t("HARDWARE_SMARTCARD"), "import_from_smartcard", None))

        if state and state.hasQR and state.enabledQR:
            menu_items.append((BTC_ICONS.QR_CODE, t("HARDWARE_QR_CODE"), "import_from_qr", None))

        if state and state.hasSD and state.enabledSD and state.detectedSD:
            menu_items.append((BTC_ICONS.SD_CARD, t("HARDWARE_SD_CARD"), "import_from_sd", None))

        menu_items += [
            (BTC_ICONS.FILE, t("HARDWARE_INTERNAL_FLASH"), "import_from_flash", None),
            (lv.SYMBOL.KEYBOARD, t("ADD_WALLET_KEYBOARD"), "import_from_keyboard", None),
        ]

        super().__init__("add_wallet", t("ADD_WALLET_TITLE"), menu_items, parent, *args, **kwargs)
