# MockUI/__init__.py
from .basic import BTN_HEIGHT, BTN_WIDTH, MENU_PCT, SMALL_PAD, SWITCH_HEIGHT, SWITCH_WIDTH, STATUS_BTN_HEIGHT, STATUS_BTN_WIDTH, GREEN, ORANGE, RED
from .basic import MainMenu, LockedMenu, ActionScreen, GenericMenu
from .basic import SpecterGui
from .tour import UIExplainer, GuidedTour

from .stubs import UIState, DeviceState, Wallet, Seed

from .wallet import (
    WalletMenu,
    AddWalletMenu,
    ConnectWalletsMenu,
)
from .seed import (
    SeedPhraseMenu,
    GenerateSeedMenu,
    PassphraseMenu,
)

from .device import (
    SecuritySettingsMenu,
    FirmwareMenu,
    InterfacesMenu,
    BackupsMenu,
    SecurityFeaturesMenu,
    StorageMenu,
    SettingsMenu,
    PreferencesMenu,
)

from .tour import GuidedTour

__all__ = [
    "BTN_HEIGHT", "BTN_WIDTH",
    "MENU_PCT",
    "SMALL_PAD",
    "SWITCH_HEIGHT", "SWITCH_WIDTH",
    "STATUS_BTN_HEIGHT", "STATUS_BTN_WIDTH",
    "GREEN", "ORANGE", "RED",
    "MainMenu",
    "WalletMenu",
    "SecuritySettingsMenu",
    "DeviceState",
    "Wallet",
    "Seed",
    "ActionScreen",
    "UIState",
    "SeedPhraseMenu",
    "SecurityFeaturesMenu",
    "InterfacesMenu",
    "BackupsMenu",
    "FirmwareMenu",
    "ConnectWalletsMenu",
    "AddWalletMenu",
    "LockedMenu",
    "GenerateSeedMenu",
    "StorageMenu",
    "SettingsMenu",
    "PassphraseMenu",
    "SpecterGui",
    "UIExplainer",
    "GuidedTour",
]