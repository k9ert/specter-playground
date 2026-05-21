"""Simple in-memory state holder for the mock UI.

Lightweight and runtime-friendly: avoids typing imports and annotations so
it works cleanly in the MicroPython host/simulator environment.
"""


from .wallet import Wallet
from .seed import Seed


class DeviceState:
    """Mutable application state used by the mock UI.

    All attributes are intentionally public and mutable for simplicity.
    """

    def __init__(self):

       # device features
        self.has_battery = False
        self.battery_pct = None
        self.is_charging = False
        
        self.is_locked = False
        self.pin = None

        # Seed related — ephemeral, cleared on power cycle
        self.loaded_seeds = []

        # Wallet (descriptor) related — persisted in flash
        self.registered_wallets = []

        #KeyStores
        self._SmartCard_hasSeed = False
        self._SD_hasSeed = False
        self._Flash_hasSeed = False

        # peripherals        
        self._hasQR = False
        self._enabledQR = False

        self._hasSD = False
        self._enabledSD = False
        self._detectedSD = False

        self._hasUSB = True
        self._enabledUSB = False

        self._hasSmartCard = False
        self._enabledSmartCard = False
        self._detectedSmartCard = False

        # misc
        self.language = "eng"
        self.fw_version = "1.0"

    
    # ── Interface for UI state queries ───────────────────────────────
    def hasSmartCard(self):
        return self._hasSmartCard
    def SmartCard_enabled(self):
        return self.hasSmartCard() and self._enabledSmartCard
    def SmartCard_detected(self):
        return self.SmartCard_enabled() and self._detectedSmartCard
    def SmartCard_hasSeed(self):
        return self.SmartCard_detected() and self._SmartCard_hasSeed
    def hasSD(self):
        return self._hasSD
    def SD_enabled(self):
        return self.hasSD() and self._enabledSD
    def SD_detected(self):
        return self.SD_enabled() and self._detectedSD
    def SD_hasSeed(self):
        return self.SD_detected() and self._SD_hasSeed
    def hasQR(self):
        return self._hasQR
    def QR_enabled(self):
        return self.hasQR() and self._enabledQR
    def Flash_hasSeed(self):
        return self._Flash_hasSeed
    def hasUSB(self):
        return self._hasUSB
    def USB_enabled(self):
        return self.hasUSB() and self._enabledUSB

    # ── Interface enable setters ─────────────────────────────────────
    def set_QR_enabled(self, enabled):
        self._enabledQR = bool(enabled)
    def set_USB_enabled(self, enabled):
        self._enabledUSB = bool(enabled)
    def set_SD_enabled(self, enabled):
        self._enabledSD = bool(enabled)
    def set_SmartCard_enabled(self, enabled):
        self._enabledSmartCard = bool(enabled)

    # ── Seed helpers ─────────────────────────────────────────────────
    def add_seed(self, seed):
        """Load a seed into memory. Returns the default wallet (created if needed)."""
        self.loaded_seeds.append(seed)
        return self._ensure_default_wallet()

    def remove_seed(self, seed):
        """Remove a seed from loaded seeds."""
        if seed in self.loaded_seeds:
            self.loaded_seeds.remove(seed)

    def wallets_for_seed(self, seed):
        """Return wallets that match this seed (including the shared Default Wallet)."""
        if seed is None:
            return None
        fp = seed.get_fingerprint()
        return [wallet for wallet in self.registered_wallets
                if wallet.is_default_wallet() or fp in wallet.required_fingerprints]

    def seed_matches_wallet(self, seed, wallet):
        """Check if a seed's fingerprint is in the wallet's required signers."""
        if not seed or not wallet:
            return False
        return wallet in self.wallets_for_seed(seed)

    # ── Wallet helpers ───────────────────────────────────────────────
    def register_wallet(self, wallet, imported=False):
        """Register a wallet descriptor. Returns the wallet.

        Args:
            wallet: Wallet instance to register.
            imported: If True, mark has_been_exported=True because the
                wallet was received from a companion app (QR scan / SD card)
                and therefore already "connected".
        """
        if imported:
            wallet.has_been_exported = True
        self.registered_wallets.append(wallet)
        return wallet

    def remove_wallet(self, wallet):
        """Remove a wallet descriptor."""
        if wallet in self.registered_wallets:
            self.registered_wallets.remove(wallet)

    def _ensure_default_wallet(self):
        """Ensure the shared Default Wallet exists.
        There is only ONE Default Wallet that fits any loaded key."""
        for wallet in self.registered_wallets:
            if wallet.is_default_wallet():
                return wallet
        # Create the singleton Default Wallet
        wallet = Wallet(
            label="Default",
            descriptor="default",
            isMultiSig=False,
            net="mainnet",
            required_fingerprints=[],
        )
        self.registered_wallets.append(wallet)
        return wallet

    def seeds_for_wallet(self, wallet):
        """Return seeds that match this wallet (including the shared Default Wallet)."""
        if wallet is None:
            return None
        if wallet.is_default_wallet():
            # Default wallet matches any seed
            return self.loaded_seeds
        
        fps = set(wallet.required_fingerprints)
        return [seed for seed in self.loaded_seeds
                if seed.get_fingerprint() in fps] 

    def signing_match_count(self, wallet):
        """Return (matched_count, required_count) for the given wallet."""
        if not wallet:
            return (0, 0)
        # Default wallet: 1-of-1 whenever any seed is loaded
        if wallet.is_default_wallet():
            return (1, 1) if self.loaded_seeds else (0, 1)

        if wallet.is_standard():
            loaded_fps = set(seed.get_fingerprint() for seed in self.loaded_seeds)
            matched = len(loaded_fps & set(wallet.required_fingerprints))
            return (matched, len(wallet.required_fingerprints))
        else:
            # For non-standard wallets, we can't analyze the descriptor, so just return dummy values
            return (1, 1) if self.loaded_seeds else (0, 1)

    # ── Lock helpers ─────────────────────────────────────────────────
    def lock(self):
        self.is_locked = True

    def unlock(self, pin=None):
        # naive PIN check for mock; in real code use secure compare
        if self.pin is None or pin == self.pin:
            self.is_locked = False
            return True
        return False

    # ── Debug helpers ────────────────────────────────────────────────
    def debug_cycle_battery(self):
        """Advance the simulated battery level by one step (for testing).

        TODO: DUMMY CODE — replace with actual device battery read logic.
        """
        if self.has_battery:
            if self.is_charging:
                self.battery_pct = min(100, self.battery_pct + 10)
                if self.battery_pct == 100:
                    self.is_charging = False
            else:
                self.battery_pct = max(0, self.battery_pct - 10)
                if self.battery_pct == 0:
                    self.is_charging = True

