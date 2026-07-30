# Backward compatibility: many screens still import assorted constants/helpers
# from `MockUI.basic` directly.
from .utils import *
from .components import confirm_delete_wallet, make_delete_active_handler
from .symbol_lib import BTC_ICONS
from .templates.specter_gui_base import SpecterGuiElement, t
from .templates.titled_screen import TitledScreen
from .templates.menu import GenericMenu
from .templates.action_screen import ActionScreen
from .ui_state import UIState
from .widgets import (
    make_icon, 
    MenuItem, 
    Btn, 
    make_label, body_label, 
    make_textarea, make_password_textarea,
    make_switch,
    ACCEPTED_CHARS,
    WalletCard,
)
from .theming import apply_style, remove_style, ColorMode, to_lv_color, to_hex_color_str
from .specter_gui import SpecterGui

__all__ = [
    "AUTO_GROW_MENU_BUTTONS",
    "BTC_ICONS",
     # widgets
    "Btn", "MenuItem", "make_icon", 
    "make_label", "body_label",
    "make_textarea", "make_password_textarea",
    "make_switch",
    "WalletCard",
    "confirm_delete_wallet", "make_delete_active_handler",
    # utils
    "shuffle",
    "delete_all_children_of", 
    "set_size", "get_size", "set_pos", "get_pos", 
    "set_scroll", "set_align", "set_propagate_events",
     # theming API
    # ui_consts re-exports used outside basic/
    # classes used outside basic/
    "TitledScreen",
    "ActionScreen", "GenericMenu",
    "SpecterGui",
    "UIState",
    #keyboard manager used outside basic/
    "Layout",
    # theming API used outside basic/
    "apply_style", "remove_style", "to_lv_color", "to_hex_color_str", "ColorMode",
    # Specter GUI base
    "SpecterGuiElement", "t",
]