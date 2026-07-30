"""Seed placeholder used by the MockUI state.

Represents a loaded MasterKey (seedphrase) in memory.
Ephemeral — never persisted across power cycles in working memory.
"""
import urandom

class Seed:
    """Tiny seed placeholder used by DeviceState.

    Attributes:
        label: user-given display name (e.g., "My Key")
        fingerprint: master fingerprint hex string (e.g., "a1b2c3d4")
        passphrase: optional BIP-39 passphrase (None if not set)
    """

    def __init__(self, label, fingerprint=None, passphrase=None,
                 passphrase_active=False, is_backed_up=False, has_been_synched=False):
        self.label = label
        self.fingerprint = fingerprint or self._generate_dummy_fingerprint()
        self.passphrase = passphrase
        self.passphrase_active = passphrase_active
        self.is_backed_up = is_backed_up
        self.has_been_synched = has_been_synched #used to log synching of default wallet per seed

    @staticmethod
    def _generate_dummy_fingerprint():
        """Generate a fake fingerprint for mock purposes."""
        h = hex(urandom.getrandbits(32))[:]
        return h
    
    def get_fingerprint(self):
        """Return the fingerprint of this seed."""
        if self.passphrase is not None and self.passphrase_active:
            # In a real implementation, the fingerprint would change if a passphrase is active.
            # For this mock, we'll just reverse the hex digits (keeping any 0x prefix).
            # Note: MicroPython does not support step=-1 slices, so use reversed().
            fp = self.fingerprint
            if fp.startswith("0x") or fp.startswith("0X"):
                return fp[:2] + "".join(reversed(fp[2:]))
            return "".join(reversed(fp))
        else:   
            return self.fingerprint

    @staticmethod
    def get_fingerprints(seeds):
        """Return list of fingerprints for a list of seeds."""
        return [seed.get_fingerprint() for seed in seeds]