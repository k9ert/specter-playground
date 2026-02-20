"""Wallet placeholder used by the MockUI state.

Keep this small and replace with the project's real Wallet model when ready.
"""


class Wallet:
    """Tiny wallet placeholder used by SpecterState.

    Attributes:
        name: display name
        xpub: optional master xpub
        isMultiSig: boolean flag indicating multisig wallet
    """

    def __init__(self, name, xpub=None, isMultiSig=False, net="mainnet"):
        self.name = name
        self.xpub = xpub
        self.isMultiSig = isMultiSig
        self.net = net
        self.active_passphrase = None
