"""Wallet model widget helpers — reusable LVGL building blocks for wallet display.
"""

from ..symbol_lib import BTC_ICONS
from ..ui_consts import WHITE_HEX, GREY_HEX
from .icon_widgets import make_icon


def wallet_signing_color(wallet, device_state):
    """Return WHITE_HEX when all required keys are loaded, GREY_HEX otherwise.

    Used to colour the wallet type icon and any associated text (e.g. multisig
    threshold label) consistently everywhere wallets are displayed.
    """
    matched, required = device_state.signing_match_count(wallet)
    return WHITE_HEX if (required > 0 and matched >= required) else GREY_HEX


_NET_MAP = {"mainnet": "main", "testnet": "test", "signet": "sig", "regtest": "reg"}


def wallet_net_text(wallet):
    """Return the short network label for *wallet* (e.g. ``'test'``).
    """
    return _NET_MAP.get(wallet.net)


def wallet_account_text(wallet):
    """Return the account label string for *wallet* (e.g. ``'#2'``).
    """
    return "#" + str(wallet.account)


def add_wallet_type_icon(parent, wallet, device_state):
    """Append a wallet type icon to *parent* with colour indicating signing readiness.

    Returns the ``lv.image`` widget.
    """
    if not wallet.is_standard():
        icon = BTC_ICONS.CONSOLE
    elif wallet.isMultiSig:
        icon = BTC_ICONS.TWO_KEYS
    else:
        icon = BTC_ICONS.KEY
    color = wallet_signing_color(wallet, device_state)
    return make_icon(parent, icon, color)
