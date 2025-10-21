"""Simple in-memory state holder for the mock UI.

Lightweight and runtime-friendly: avoids typing imports and annotations so
it works cleanly in the MicroPython host/simulator environment.
"""


from .wallet import Wallet


class SpecterState:
    """Mutable application state used by the mock UI.

    All attributes are intentionally public and mutable for simplicity.
    """

    def __init__(self):
        # load/availability
        self.seed_loaded = False
        self.active_wallet = None
        self.registered_wallets = []

        # device features
        self.has_battery = False
        self.active_passphrase = None
        self.is_locked = False
        self.pin = None

        # peripherals
        self.hasQR = False
        self.enabledQR = False
        self.hasSD = False
        self.enabledSD = False
        self.enabledUSB = False
        self.hasSmartCard = False
        self.enabledSmartCard = False

        # misc
        self.language = None

    # convenience helpers
    def register_wallet(self, wallet):
        self.registered_wallets.append(wallet)

    def set_active_wallet(self, wallet):
        self.active_wallet = wallet

    def clear_wallets(self):
        self.registered_wallets.clear()

    def lock(self):
        self.is_locked = True

    def unlock(self, pin=None):
        # naive PIN check for mock; in real code use secure compare
        if self.pin is None or pin == self.pin:
            self.is_locked = False
            return True
        return False

    def set_pin(self, pin):
        self.pin = pin

    def enable_qr(self, enable):
        self.enabledQR = enable

    def enable_sd(self, enable):
        self.enabledSD = enable

    def enable_smartcard(self, enable):
        self.enabledSmartCard = enable

    def set_language(self, lang):
        self.language = lang
