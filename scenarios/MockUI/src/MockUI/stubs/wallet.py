"""Wallet (descriptor) placeholder used by the MockUI state.

Keep this small and replace with the project's real Wallet model when ready.
Represents a persistent wallet descriptor — stored in flash, auto-loaded on boot.
"""


class Wallet:
    """Wallet descriptor placeholder used by SpecterState.

    Attributes:
        name: user-facing display name
        descriptor: output descriptor string (for advanced view)
        net: network ("mainnet" | "testnet" | "signet")
        isMultiSig: boolean flag indicating multisig wallet
        required_fingerprints: list of key fingerprints needed for signing
        threshold: multisig m-of-n (m value); None for singlesig
        has_been_synched: whether this wallet has been synced with a companion app
    """

    def __init__(self, label, descriptor=None, isMultiSig=False, net="mainnet",
                 required_fingerprints=None, threshold=None,
                 has_been_synched=False, account=0):
        self.label = label
        self.descriptor = descriptor
        self.isMultiSig = isMultiSig
        self.net = net
        self.threshold = threshold
        self.required_fingerprints = required_fingerprints or []
        assert (not isMultiSig) or (threshold and len(self.required_fingerprints) >= threshold), "Invalid multisig config"

        # True when wallet was imported from companion app (QR/SD) or
        # explicitly exported via Connect Companion App flow.
        self.has_been_synched = has_been_synched
        self.account = account

    def is_standard(self):
        """Check if this is the default "Standard" wallet (which has no descriptor)."""
        return self.descriptor != "fancy script"

    def is_default_wallet(self):
        """Check if this wallet is the default "Standard" wallet."""
        return self.label == "Default" and self.descriptor == "default"


class WalletType:
    SINGLE_SIG_DEFAULT = 0
    SINGLE_SIG = 1
    MULTISIG = 2
    CUSTOM = 3


def _wallet_type_rank(wallet):
    """Return (type_rank, n, m, account) for sort ordering."""
    if not wallet.is_standard():
        type_rank = WalletType.CUSTOM  # custom / miniscript
    elif wallet.isMultiSig:
        type_rank = WalletType.MULTISIG  # multisig
    elif wallet.is_default_wallet():
        type_rank = WalletType.SINGLE_SIG_DEFAULT  # single-sig default wallet
    else:
        type_rank = WalletType.SINGLE_SIG  # non default singleSig
    n = len(wallet.required_fingerprints) if wallet.isMultiSig else 0
    m = wallet.threshold if wallet.isMultiSig else 0
    return (type_rank, n, m, getattr(wallet, "account", 0))
