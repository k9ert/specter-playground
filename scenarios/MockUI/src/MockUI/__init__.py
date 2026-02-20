# MockUI/__init__.py
from .basic import BTN_HEIGHT, BTN_WIDTH, MENU_PCT, PAD_SIZE, SWITCH_HEIGHT, SWITCH_WIDTH, STATUS_BTN_HEIGHT, STATUS_BTN_WIDTH, ONE_LETTER_SYMBOL_WIDTH, TWO_LETTER_SYMBOL_WIDTH, THREE_LETTER_SYMBOL_WIDTH, GREEN, ORANGE, RED
from .basic import MainMenu, LockedMenu, StatusBar, ActionScreen, GenericMenu
from .basic import NavigationController

from .helpers import UIState, SpecterState, Wallet

from .wallet import (
    WalletMenu,
    AddWalletMenu,
    ChangeWalletMenu,
    ConnectWalletsMenu,
    SeedPhraseMenu,
    GenerateSeedMenu,
    PassphraseMenu,
)

from .device import (
    DeviceMenu,
    FirmwareMenu,
    InterfacesMenu,
    BackupsMenu,
    SecurityMenu,
    StorageMenu,
)

__all__ = [
    "BTN_HEIGHT", "BTN_WIDTH",
    "MENU_PCT",
    "PAD_SIZE",
    "SWITCH_HEIGHT", "SWITCH_WIDTH",
    "STATUS_BTN_HEIGHT", "STATUS_BTN_WIDTH",
    "ONE_LETTER_SYMBOL_WIDTH", "TWO_LETTER_SYMBOL_WIDTH", "THREE_LETTER_SYMBOL_WIDTH",
    "GREEN", "ORANGE", "RED",
    "MainMenu",
    "WalletMenu",
    "DeviceMenu",
    "SpecterState",
    "Wallet",
    "ActionScreen",
    "UIState",
    "StatusBar",
    "SeedPhraseMenu",
    "SecurityMenu",
    "InterfacesMenu",
    "BackupsMenu",
    "FirmwareMenu",
    "ConnectWalletsMenu",
    "ChangeWalletMenu",
    "AddWalletMenu",
    "LockedMenu",
    "GenerateSeedMenu",
    "StorageMenu",
    "PassphraseMenu",
    "NavigationController",
]