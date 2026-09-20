"""Wallet (descriptor) placeholder used by the MockUI state.

Keep this small and replace with the project's real Wallet model when ready.
Represents a persistent wallet descriptor — stored in flash, auto-loaded on boot.
"""

from micropython import const

class Wallet:
    """Wallet descriptor placeholder used by DeviceState.

    Attributes:
        name: user-facing display name
        descriptor: output descriptor string (for advanced view)
        net: network ("mainnet" | "testnet" | "signet")
        isMultiSig: boolean flag indicating multisig wallet
        required_fingerprints: list of key fingerprints needed for signing
        threshold: multisig m-of-n (m value); None for singlesig
        has_been_synched: whether this wallet has been synced with a companion app
        is_custom: whether this is a non-standard custom policy
    """

    def __init__(self, label, descriptor=None, isMultiSig=False, net="mainnet",
                 required_fingerprints=None, threshold=None,
                 has_been_synched=False, account=0, derivation_path=None,
                 is_custom=False):
        self.label = label
        self.descriptor = descriptor
        self.isMultiSig = isMultiSig
        self.is_custom = bool(is_custom)
        self.net = net
        self.threshold = threshold
        self.required_fingerprints = required_fingerprints or []
        assert (not isMultiSig) or (threshold and len(self.required_fingerprints) >= threshold), "Invalid multisig config"

        # True when wallet was imported from companion app (QR/SD) or
        # explicitly exported via Connect Companion App flow.
        self.has_been_synched = has_been_synched
        self.account = account
        # BIP32-style path string (e.g. "m/84'/0'/0'"); mock only for now.
        self.derivation_path = derivation_path

    def get_signers(self):
        """Return signer fingerprints as a stable, immutable collection."""
        return tuple(sorted(self.required_fingerprints))

    def derivation_parent(self, all_wallets):
        """Mock parent discovery via derivation sub-paths.

        A candidate must have the same signer fingerprints, irrespective of
        their descriptor order. Of those candidates, return the wallet whose
        derivation path is the longest strict prefix of this wallet's path
        (segment-wise), or ``None``. Later replaced by real descriptor
        analysis.
        """
        if not self.derivation_path:
            return None
        mine = self.derivation_path.split("/")
        mine_signers = self.get_signers()
        best = None
        best_len = 0
        for other in all_wallets:
            if other is self or not other.derivation_path:
                continue
            if other.get_signers() != mine_signers:
                continue
            theirs = other.derivation_path.split("/")
            if (len(theirs) < len(mine)
                    and len(theirs) > best_len
                    and mine[:len(theirs)] == theirs):
                best = other
                best_len = len(theirs)
        return best

    def is_standard(self):
        """Return whether this wallet uses a standard descriptor policy."""
        return not self.is_custom

    def is_default_wallet(self):
        """Check if this wallet is the default "Standard" wallet."""
        return self.label == "Default" and self.descriptor == "default"


class WalletType:
    SINGLE_SIG_DEFAULT = const(0)
    SINGLE_SIG = const(1)
    MULTISIG = const(2)
    CUSTOM = const(3)

def _wallet_type_rank(wallet):
    """Return (type_rank, n, m, account) for sort ordering."""
    if wallet.isMultiSig:
        type_rank = WalletType.MULTISIG  # multisig
    elif wallet.is_default_wallet():
        type_rank = WalletType.SINGLE_SIG_DEFAULT  # single-sig default wallet
    elif wallet.is_standard():
        type_rank = WalletType.SINGLE_SIG  # non default singleSig
    else:
        type_rank = WalletType.CUSTOM  # custom / miniscript
    n = len(wallet.get_signers()) if wallet.isMultiSig else 0
    m = wallet.threshold if wallet.isMultiSig else 0
    return (type_rank, n, m, getattr(wallet, "account", 0))

_NETWORK_INFO = {
    "mainnet": (0, "main"),
    "testnet": (1, "test"),
    "signet":  (2, "sig"),
    "regtest": (3, "reg"),
}

def wallet_network_rank(network):
    """Return the stable display-order rank for a network name."""
    return _NETWORK_INFO.get(network, (len(_NETWORK_INFO), None))[0]

def wallet_network_text(network):
    """Return the short display text for a network name."""
    return _NETWORK_INFO.get(network, (None, None))[1]


def _wallet_policy_rank(wallet):
    if wallet.is_default_wallet():
        return 0
    elif wallet.is_standard():
        return 1
    else:
        return 2

def wallet_sort_key(wallet):
    """Return the canonical ordering key for wallet presentation."""
    signers = wallet.get_signers()

    return (
        len(signers),
        signers,
        wallet.threshold if wallet.isMultiSig else 1,
        _wallet_policy_rank(wallet),
        getattr(wallet, "account", 0),
        wallet_network_rank(wallet.net),
        str(wallet.label).lower(),
    )
