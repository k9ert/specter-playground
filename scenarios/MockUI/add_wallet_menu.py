import lvgl as lv
from .menu import GenericMenu


class AddWalletMenu(GenericMenu):
    """Menu to create or import a wallet.

    Menu items:
    - Generate New Seedphrase
    - Import Seedphrase from: SmartCard, QR Code, SD Card, internal Flash, Keyboard
      Conditional items included according to parent.specter_state flags.
    """

    def __init__(self, parent, *args, **kwargs):
        state = getattr(parent, "specter_state", None)

        menu_items = [
            ("Generate New Seedphrase", "generate_seedphrase"),
            ("Import Seedphrase from", None),
        ]

        # conditional import sources
        if state and state.hasSmartCard and state.enabledSmartCard and state.detectedSmartCard:
            menu_items.append(("SmartCard", "import_from_smartcard"))

        if state and state.hasQR and state.enabledQR:
            menu_items.append(("QR Code", "import_from_qr"))

        if state and state.hasSD and state.enabledSD and state.detectedSD:
            menu_items.append(("SD Card", "import_from_sd"))

        menu_items += [
            ("internal Flash", "import_from_flash"),
            ("Keyboard (manual)", "import_from_keyboard"),
        ]

        super().__init__("add_wallet", "Add Wallet", menu_items, parent, *args, **kwargs)
