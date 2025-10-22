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
        # seedphrase related
        self.seed_loaded = False
        self.active_wallet = None
        self.registered_wallets = []
        self.active_passphrase = None

        # device features
        self.has_battery = False
        self.battery_pct = None
        
        self.is_locked = False
        self.pin = None

        # peripherals
        self.hasQR = False
        self.enabledQR = False

        self.hasSD = False
        self.enabledSD = False
        self.detectedSD = False

        self.hasUSB = True
        self.enabledUSB = False

        self.hasSmartCard = False
        self.enabledSmartCard = False
        self.detectedSmartCard = False

        # misc
        self.language = "eng"

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
