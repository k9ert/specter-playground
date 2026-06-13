# Init Files Report

Scope: static analysis of Python packages under `scenarios/MockUI/src/MockUI`.

Method: AST-based import/export scan across all package `__init__.py` files and all `.py` modules; checks include package API usage, missing exports, potential non-API exports, and import style (package-level vs direct-module).

Notes:
- This is static analysis; dynamic imports/metaprogramming are not resolved.
- `possibly_non_api_exports` are candidates for pruning, not automatic deletions.
- Internal code should generally prefer direct-module imports; package-level imports are best reserved for curated public APIs.

## Inventory Summary

- Total Python files analyzed: 160
- Total packages (`__init__.py`) analyzed: 17
- Total import-appropriateness findings: 336

## Package-Level Analysis

### Package `MockUI`

- Directory: `scenarios/MockUI/src/MockUI`
- `__init__.py`: `scenarios/MockUI/src/MockUI/__init__.py`
- Python files in package (excluding `__init__.py`): 0
- Externally used API names imported from package: 0
- Names exported by package `__init__.py`: 5
  - DeviceState, Seed, SpecterGui, UIState, Wallet
- Missing exports (used from package but not exported): 0
- Possibly non-API exports in `__init__.py` (not imported via package inside scanned tree): 5
  - DeviceState, Seed, SpecterGui, UIState, Wallet

### Package `MockUI.basic`

- Directory: `scenarios/MockUI/src/MockUI/basic`
- `__init__.py`: `scenarios/MockUI/src/MockUI/basic/__init__.py`
- Python files in package (excluding `__init__.py`): 2
- Externally used API names imported from package: 33
  - ACCEPTED_CHARS, BTC_ICONS, BTN_HEIGHT, BTN_WIDTH, BTN_WIDTH_PCT, Btn, GenericMenu, Layout, MenuItem, PIN_BTN_HEIGHT, PIN_BTN_WIDTH, SCREEN_WIDTH, SMALL_PAD, STATUS_BTN_HEIGHT, SWITCH_HEIGHT, SWITCH_WIDTH, TitledScreen, WalletCard, apply_style, body_label, confirm_delete_wallet, delete_all_children_of, flex_col, flex_row, form_label, form_textarea, make_delete_active_handler, make_icon, section_header, set_propagate_events, shuffle, style_as_flex_container, title_label
- Names exported by package `__init__.py`: 46
  - ACCEPTED_CHARS, ActionScreen, BTC_ICONS, BTN_HEIGHT, BTN_WIDTH, Btn, ColorMode, GenericMenu, Layout, MENU_WIDTH, MenuItem, PIN_BTN_HEIGHT, PIN_BTN_WIDTH, SMALL_PAD, STATUS_BTN_HEIGHT, STATUS_BTN_WIDTH, SWITCH_HEIGHT, SWITCH_WIDTH, SpecterGui, TitledScreen, UIState, WalletCard, apply_style, body_label, confirm_delete_wallet, delete_all_children_of, flex_col, flex_row, form_label, form_textarea, make_delete_active_handler, make_icon, menu_label, remove_style, reset_style, section_header, set_align, set_pos, set_propagate_events, set_scroll, set_size, shuffle, style_as_flex_container, title_label, to_hex_color_str, to_lv_color
- Missing exports (used from package but not exported): 2
  - BTN_WIDTH_PCT, SCREEN_WIDTH
- Possibly non-API exports in `__init__.py` (not imported via package inside scanned tree): 15
  - ActionScreen, ColorMode, MENU_WIDTH, STATUS_BTN_WIDTH, SpecterGui, UIState, menu_label, remove_style, reset_style, set_align, set_pos, set_scroll, set_size, to_hex_color_str, to_lv_color

### Package `MockUI.basic.components`

- Directory: `scenarios/MockUI/src/MockUI/basic/components`
- `__init__.py`: `scenarios/MockUI/src/MockUI/basic/components/__init__.py`
- Python files in package (excluding `__init__.py`): 6
- Externally used API names imported from package: 2
  - AppScreen, NavigationBar
- Names exported by package `__init__.py`: 9
  - AppScreen, ContextBar, DropUpState, NavigationBar, SeedDropUp, WalletDropUp, confirm_delete_seed, confirm_delete_wallet, make_delete_active_handler
- Missing exports (used from package but not exported): 0
- Possibly non-API exports in `__init__.py` (not imported via package inside scanned tree): 7
  - ContextBar, DropUpState, SeedDropUp, WalletDropUp, confirm_delete_seed, confirm_delete_wallet, make_delete_active_handler

### Package `MockUI.basic.fonts`

- Directory: `scenarios/MockUI/src/MockUI/basic/fonts`
- `__init__.py`: `scenarios/MockUI/src/MockUI/basic/fonts/__init__.py`
- Python files in package (excluding `__init__.py`): 2
- Externally used API names imported from package: 0
- Names exported by package `__init__.py`: 4
  - font_loader_de, font_manager, get_font_de, set_default_font_de
- Missing exports (used from package but not exported): 0
- Possibly non-API exports in `__init__.py` (not imported via package inside scanned tree): 4
  - font_loader_de, font_manager, get_font_de, set_default_font_de

### Package `MockUI.basic.i18n`

- Directory: `scenarios/MockUI/src/MockUI/basic/i18n`
- `__init__.py`: `scenarios/MockUI/src/MockUI/basic/i18n/__init__.py`
- Python files in package (excluding `__init__.py`): 3
- Externally used API names imported from package: 1
  - I18nManager
- Names exported by package `__init__.py`: 1
  - I18nManager
- Missing exports (used from package but not exported): 0
- Possibly non-API exports in `__init__.py` (not imported via package inside scanned tree): 0

### Package `MockUI.basic.symbol_lib`

- Directory: `scenarios/MockUI/src/MockUI/basic/symbol_lib`
- `__init__.py`: `scenarios/MockUI/src/MockUI/basic/symbol_lib/__init__.py`
- Python files in package (excluding `__init__.py`): 2
- Externally used API names imported from package: 2
  - BTC_ICONS, Icon
- Names exported by package `__init__.py`: 2
  - BTC_ICONS, Icon
- Missing exports (used from package but not exported): 0
- Possibly non-API exports in `__init__.py` (not imported via package inside scanned tree): 0

### Package `MockUI.basic.symbol_lib.icons`

- Directory: `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons`
- `__init__.py`: `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/__init__.py`
- Python files in package (excluding `__init__.py`): 68
- Externally used API names imported from package: 0
- Names exported by package `__init__.py`: 0
- Missing exports (used from package but not exported): 0
- Possibly non-API exports in `__init__.py` (not imported via package inside scanned tree): 0

### Package `MockUI.basic.templates`

- Directory: `scenarios/MockUI/src/MockUI/basic/templates`
- `__init__.py`: `scenarios/MockUI/src/MockUI/basic/templates/__init__.py`
- Python files in package (excluding `__init__.py`): 7
- Externally used API names imported from package: 0
- Names exported by package `__init__.py`: 4
  - SettingFileManager, SettingsFileCompiler, collect_int_constants, read_cstring
- Missing exports (used from package but not exported): 0
- Possibly non-API exports in `__init__.py` (not imported via package inside scanned tree): 4
  - SettingFileManager, SettingsFileCompiler, collect_int_constants, read_cstring

### Package `MockUI.basic.theming`

- Directory: `scenarios/MockUI/src/MockUI/basic/theming`
- `__init__.py`: `scenarios/MockUI/src/MockUI/basic/theming/__init__.py`
- Python files in package (excluding `__init__.py`): 7
- Externally used API names imported from package: 7
  - SpecterFontPalette, ThemeManager, apply_style, get_font, get_palette_entries, get_style, remove_style
- Names exported by package `__init__.py`: 15
  - ColorMode, SpecterColorPalette, SpecterFontPalette, SpecterStylePalette, ThemeManager, apply_style, get_color, get_font, get_palette_entries, get_style, get_theme_manager, remove_style, reset_style, to_hex_color_str, to_lv_color
- Missing exports (used from package but not exported): 0
- Possibly non-API exports in `__init__.py` (not imported via package inside scanned tree): 8
  - ColorMode, SpecterColorPalette, SpecterStylePalette, get_color, get_theme_manager, reset_style, to_hex_color_str, to_lv_color

### Package `MockUI.basic.tour`

- Directory: `scenarios/MockUI/src/MockUI/basic/tour`
- `__init__.py`: `scenarios/MockUI/src/MockUI/basic/tour/__init__.py`
- Python files in package (excluding `__init__.py`): 2
- Externally used API names imported from package: 2
  - GuidedTour, INTRO_TOUR_STEPS
- Names exported by package `__init__.py`: 3
  - GuidedTour, INTRO_TOUR_STEPS, UIExplainer
- Missing exports (used from package but not exported): 0
- Possibly non-API exports in `__init__.py` (not imported via package inside scanned tree): 1
  - UIExplainer

### Package `MockUI.basic.utils`

- Directory: `scenarios/MockUI/src/MockUI/basic/utils`
- `__init__.py`: `scenarios/MockUI/src/MockUI/basic/utils/__init__.py`
- Python files in package (excluding `__init__.py`): 5
- Externally used API names imported from package: 46
  - ANIM_MS_HORIZONTAL, ANIM_MS_VERTICAL, BATTERY_WIDTH, BIG_PAD, BTC_ICON_WIDTH, BTN_HEIGHT, BTN_WIDTH_PCT, CARD_H, CONFIRMATION_SLIDER_HEIGHT, CONTENT_H, CONTENT_PCT, EXPLAINER_HEIGHT, EXPLAINER_WIDTH, FINGERPRINT_LBL_WIDTH, FORM_TA_HEIGHT, GUIAnimations, GUI_REFRESH_MS, KeyboardManager, Layout, MAX_HISTORY_DEPTH, MODAL_HEIGHT, MODAL_WIDTH, PAD, SCREEN_HEIGHT, SCREEN_WIDTH, SMALL_PAD, STATUS_BAR_PCT, STATUS_BTN_HEIGHT, SWITCH_HEIGHT, SWITCH_WIDTH, TITLE_HEIGHT, TITLE_PADDING, TITLE_ROW_HEIGHT_PCT, best_fonttype_for_size, delete_all_children_of, get_size, set_align, set_pos, set_propagate_events, set_scale, set_scroll, set_size, slide_x, slide_y, style_as_flex_container, style_as_screen_backdrop
- Names exported by package `__init__.py`: 54
  - ANIM_MS_HORIZONTAL, ANIM_MS_VERTICAL, BACK_BTN_HEIGHT, BACK_BTN_WIDTH, BATTERY_WIDTH, BIG_PAD, BTC_ICON_WIDTH, BTN_HEIGHT, BTN_WIDTH, CARD_H, CONFIRMATION_SLIDER_HEIGHT, CONTENT_PCT, EXPLAINER_HEIGHT_PCT, EXPLAINER_WIDTH_PCT, FINGERPRINT_LBL_WIDTH, FORM_TA_HEIGHT, GUIAnimations, GUI_REFRESH_MS, KeyboardManager, Layout, MAX_HISTORY_DEPTH, MENU_WIDTH, MODAL_HEIGHT_PCT, MODAL_WIDTH_PCT, PAD, PIN_BTN_HEIGHT, PIN_BTN_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH, SMALL_PAD, STATUS_BAR_PCT, STATUS_BTN_HEIGHT, STATUS_BTN_WIDTH, SWITCH_HEIGHT, SWITCH_WIDTH, TITLE_HEIGHT, TITLE_PADDING, TITLE_TA_WIDTH, best_fonttype_for_size, create_anims_for_transition, delete_all_children_of, get_size, set_align, set_pos, set_propagate_events, set_scale, set_scroll, set_size, shuffle, slide_x, slide_y, style_as_flex_container, style_as_screen_backdrop, text_width
- Missing exports (used from package but not exported): 7
  - BTN_WIDTH_PCT, CONTENT_H, EXPLAINER_HEIGHT, EXPLAINER_WIDTH, MODAL_HEIGHT, MODAL_WIDTH, TITLE_ROW_HEIGHT_PCT
- Possibly non-API exports in `__init__.py` (not imported via package inside scanned tree): 15
  - BACK_BTN_HEIGHT, BACK_BTN_WIDTH, BTN_WIDTH, EXPLAINER_HEIGHT_PCT, EXPLAINER_WIDTH_PCT, MENU_WIDTH, MODAL_HEIGHT_PCT, MODAL_WIDTH_PCT, PIN_BTN_HEIGHT, PIN_BTN_WIDTH, STATUS_BTN_WIDTH, TITLE_TA_WIDTH, create_anims_for_transition, shuffle, text_width

### Package `MockUI.basic.widgets`

- Directory: `scenarios/MockUI/src/MockUI/basic/widgets`
- `__init__.py`: `scenarios/MockUI/src/MockUI/basic/widgets/__init__.py`
- Python files in package (excluding `__init__.py`): 12
- Externally used API names imported from package: 18
  - Battery, Btn, MenuItem, SeedCard, WalletCard, body_label, button_modal, flex_col, flex_container, flex_row, make_icon, menu_label, modal_overlay, screen_backdrop, section_header, slider_confirm_modal, title_label, wallet_net_text
- Names exported by package `__init__.py`: 30
  - ACCEPTED_CHARS, Battery, Btn, MenuItem, MenuItemSuffix, MultisigKeyIcon, SeedCard, WalletCard, body_label, button_modal, confirmation_slider, fingerprint_badge, flex_col, flex_container, flex_row, form_label, form_textarea, make_icon, make_label, menu_label, modal_overlay, passphrase_toggle, screen_backdrop, section_header, slider_confirm_modal, title_label, title_textarea, wallet_account_text, wallet_net_text, wallet_type_icon
- Missing exports (used from package but not exported): 0
- Possibly non-API exports in `__init__.py` (not imported via package inside scanned tree): 12
  - ACCEPTED_CHARS, MenuItemSuffix, MultisigKeyIcon, confirmation_slider, fingerprint_badge, form_label, form_textarea, make_label, passphrase_toggle, title_textarea, wallet_account_text, wallet_type_icon

### Package `MockUI.device_screens`

- Directory: `scenarios/MockUI/src/MockUI/device_screens`
- `__init__.py`: `scenarios/MockUI/src/MockUI/device_screens/__init__.py`
- Python files in package (excluding `__init__.py`): 10
- Externally used API names imported from package: 10
  - BackupsMenu, FirmwareMenu, InterfacesMenu, LanguageMenu, PreferencesMenu, SecurityFeaturesMenu, SecuritySettingsMenu, SettingsMenu, StorageMenu, ThemeMenu
- Names exported by package `__init__.py`: 10
  - BackupsMenu, FirmwareMenu, InterfacesMenu, LanguageMenu, PreferencesMenu, SecurityFeaturesMenu, SecuritySettingsMenu, SettingsMenu, StorageMenu, ThemeMenu
- Missing exports (used from package but not exported): 0
- Possibly non-API exports in `__init__.py` (not imported via package inside scanned tree): 0

### Package `MockUI.main_screens`

- Directory: `scenarios/MockUI/src/MockUI/main_screens`
- `__init__.py`: `scenarios/MockUI/src/MockUI/main_screens/__init__.py`
- Python files in package (excluding `__init__.py`): 2
- Externally used API names imported from package: 2
  - LockedMenu, MainMenu
- Names exported by package `__init__.py`: 2
  - LockedMenu, MainMenu
- Missing exports (used from package but not exported): 0
- Possibly non-API exports in `__init__.py` (not imported via package inside scanned tree): 0

### Package `MockUI.seed_screens`

- Directory: `scenarios/MockUI/src/MockUI/seed_screens`
- `__init__.py`: `scenarios/MockUI/src/MockUI/seed_screens/__init__.py`
- Python files in package (excluding `__init__.py`): 7
- Externally used API names imported from package: 7
  - AddSeedMenu, ClearSeedphraseMenu, GenerateSeedMenu, PassphraseMenu, RelatedWalletsForSeedMenu, SeedPhraseMenu, StoreSeedphraseMenu
- Names exported by package `__init__.py`: 7
  - AddSeedMenu, ClearSeedphraseMenu, GenerateSeedMenu, PassphraseMenu, RelatedWalletsForSeedMenu, SeedPhraseMenu, StoreSeedphraseMenu
- Missing exports (used from package but not exported): 0
- Possibly non-API exports in `__init__.py` (not imported via package inside scanned tree): 0

### Package `MockUI.stubs`

- Directory: `scenarios/MockUI/src/MockUI/stubs`
- `__init__.py`: `scenarios/MockUI/src/MockUI/stubs/__init__.py`
- Python files in package (excluding `__init__.py`): 3
- Externally used API names imported from package: 3
  - DeviceState, Seed, Wallet
- Names exported by package `__init__.py`: 3
  - DeviceState, Seed, Wallet
- Missing exports (used from package but not exported): 0
- Possibly non-API exports in `__init__.py` (not imported via package inside scanned tree): 0

### Package `MockUI.wallet_screens`

- Directory: `scenarios/MockUI/src/MockUI/wallet_screens`
- `__init__.py`: `scenarios/MockUI/src/MockUI/wallet_screens/__init__.py`
- Python files in package (excluding `__init__.py`): 5
- Externally used API names imported from package: 5
  - AddWalletMenu, ConnectWalletsMenu, CreateCustomWalletMenu, ViewSignersMenu, WalletMenu
- Names exported by package `__init__.py`: 5
  - AddWalletMenu, ConnectWalletsMenu, CreateCustomWalletMenu, ViewSignersMenu, WalletMenu
- Missing exports (used from package but not exported): 0
- Possibly non-API exports in `__init__.py` (not imported via package inside scanned tree): 0

## Per-File Analysis

Legend:
- `public_defs`: top-level public classes/functions/constants in file
- `package_imports`: imports from package roots (potentially broad/re-export based)
- `direct_module_imports`: imports from concrete modules
- `findings`: per-import appropriateness checks

### File `scenarios/MockUI/src/MockUI/__init__.py`

- Module: `MockUI`
- public_defs (0): (none)
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/__init__.py`

- Module: `MockUI.basic`
- public_defs (0): (none)
- package_imports (0):
  - none
- direct_module_imports (11):
  - line 1: from `MockUI.utils` import BTN_HEIGHT, BTN_WIDTH, SMALL_PAD, SWITCH_HEIGHT, SWITCH_WIDTH, STATUS_BTN_HEIGHT, STATUS_BTN_WIDTH, MENU_WIDTH, PIN_BTN_WIDTH, PIN_BTN_HEIGHT, shuffle, style_as_flex_container, Layout, delete_all_children_of, set_size, set_pos, set_scroll, set_align, set_propagate_events
  - line 15: from `MockUI.utils` import *
  - line 16: from `MockUI.components` import confirm_delete_wallet, make_delete_active_handler
  - line 17: from `MockUI.symbol_lib` import BTC_ICONS
  - line 18: from `MockUI.templates.titled_screen` import TitledScreen
  - line 19: from `MockUI.templates.menu` import GenericMenu
  - line 20: from `MockUI.templates.action_screen` import ActionScreen
  - line 21: from `MockUI.ui_state` import UIState
  - line 22: from `MockUI.widgets` import make_icon, MenuItem, Btn, body_label, menu_label, form_label, title_label, section_header, flex_row, flex_col, form_textarea, ACCEPTED_CHARS, WalletCard
  - line 32: from `MockUI.theming` import apply_style, remove_style, reset_style, ColorMode, to_lv_color, to_hex_color_str
  - line 33: from `MockUI.specter_gui` import SpecterGui
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/components/__init__.py`

- Module: `MockUI.basic.components`
- public_defs (0): (none)
- package_imports (0):
  - none
- direct_module_imports (7):
  - line 1: from `MockUI.basic.app_screen` import AppScreen
  - line 2: from `MockUI.basic.confirm_modals` import confirm_delete_seed, confirm_delete_wallet, make_delete_active_handler
  - line 3: from `MockUI.basic.context_bar` import ContextBar
  - line 4: from `MockUI.basic.navigation_bar` import NavigationBar
  - line 5: from `MockUI.basic.seed_dropup` import SeedDropUp
  - line 6: from `MockUI.basic.wallet_dropup` import WalletDropUp
  - line 7: from `MockUI.templates.dropup` import DropUpState
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/components/app_screen.py`

- Module: `MockUI.basic.components.app_screen`
- public_defs (1): AppScreen
- package_imports (2):
  - line 13: from `MockUI.basic.utils` import SCREEN_WIDTH, SCREEN_HEIGHT, CONTENT_PCT, TITLE_ROW_HEIGHT_PCT, BATTERY_WIDTH, set_pos, set_scroll, set_align, style_as_screen_backdrop
  - line 19: from `MockUI.basic.widgets` import flex_col, Battery
- direct_module_imports (3):
  - line 12: from `MockUI.basic.components.context_bar` import ContextBar
  - line 18: from `MockUI.basic.templates.specter_gui_base` import SpecterGuiElement
  - line 20: from `MockUI.basic.ui_state` import Context
- findings (11):
  - Line 13: imports `SCREEN_WIDTH` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 13: imports `SCREEN_HEIGHT` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 13: imports `CONTENT_PCT` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 13: imports `TITLE_ROW_HEIGHT_PCT` from package `MockUI.basic.utils` but name not exported there (likely fragile / runtime error risk).
  - Line 13: imports `BATTERY_WIDTH` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 13: imports `set_pos` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 13: imports `set_scroll` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 13: imports `set_align` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 13: imports `style_as_screen_backdrop` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 19: imports `flex_col` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.containers:flex_col`); prefer direct module import internally.
  - Line 19: imports `Battery` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.battery:Battery`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/components/confirm_modals.py`

- Module: `MockUI.basic.components.confirm_modals`
- public_defs (3): confirm_delete_seed, confirm_delete_wallet, make_delete_active_handler
- package_imports (2):
  - line 3: from `MockUI.basic.widgets` import slider_confirm_modal
  - line 4: from `MockUI.basic.symbol_lib` import BTC_ICONS
- direct_module_imports (0):
  - none
- findings (2):
  - Line 3: imports `slider_confirm_modal` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.action_modal:slider_confirm_modal`); prefer direct module import internally.
  - Line 4: imports `BTC_ICONS` from package `MockUI.basic.symbol_lib` (re-export from `MockUI.basic.symbol_lib.btc_icons:BTC_ICONS`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/components/context_bar.py`

- Module: `MockUI.basic.components.context_bar`
- public_defs (1): ContextBar
- package_imports (4):
  - line 6: from `MockUI.basic.utils` import TITLE_ROW_HEIGHT_PCT, SCREEN_WIDTH, delete_all_children_of, set_size, set_scroll, set_align, get_size, Layout
  - line 13: from `MockUI.basic.theming` import apply_style
  - line 14: from `MockUI.basic.symbol_lib` import BTC_ICONS
  - line 15: from `MockUI.basic.widgets` import SeedCard, WalletCard, wallet_net_text
- direct_module_imports (2):
  - line 12: from `MockUI.basic.templates.specter_gui_base` import SpecterGuiElement
  - line 16: from `MockUI.basic.ui_state` import Context
- findings (13):
  - Line 6: imports `TITLE_ROW_HEIGHT_PCT` from package `MockUI.basic.utils` but name not exported there (likely fragile / runtime error risk).
  - Line 6: imports `SCREEN_WIDTH` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 6: imports `delete_all_children_of` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 6: imports `set_size` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 6: imports `set_scroll` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 6: imports `set_align` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 6: imports `get_size` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 6: imports `Layout` from package `MockUI.basic.utils` (re-export from `MockUI.basic.utils.keyboard_manager:Layout`); prefer direct module import internally.
  - Line 13: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.
  - Line 14: imports `BTC_ICONS` from package `MockUI.basic.symbol_lib` (re-export from `MockUI.basic.symbol_lib.btc_icons:BTC_ICONS`); prefer direct module import internally.
  - Line 15: imports `SeedCard` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.seed_widgets:SeedCard`); prefer direct module import internally.
  - Line 15: imports `WalletCard` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.wallet_widgets:WalletCard`); prefer direct module import internally.
  - Line 15: imports `wallet_net_text` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.wallet_widgets:wallet_net_text`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/components/navigation_bar.py`

- Module: `MockUI.basic.components.navigation_bar`
- public_defs (1): NavigationBar
- package_imports (4):
  - line 30: from `MockUI.basic.utils` import SCREEN_WIDTH, SCREEN_HEIGHT, STATUS_BTN_HEIGHT, STATUS_BAR_PCT, style_as_screen_backdrop
  - line 34: from `MockUI.basic.symbol_lib` import BTC_ICONS
  - line 35: from `MockUI.basic.widgets` import Btn, modal_overlay, make_icon
  - line 38: from `MockUI.basic.theming` import apply_style
- direct_module_imports (5):
  - line 28: from `MockUI.basic.components.seed_dropup` import SeedDropUp
  - line 29: from `MockUI.basic.components.wallet_dropup` import WalletDropUp
  - line 36: from `MockUI.basic.templates.specter_gui_base` import SpecterGuiElement
  - line 37: from `MockUI.basic.templates.dropup` import DropUpState
  - line 39: from `MockUI.basic.ui_state` import Context
- findings (10):
  - Line 30: imports `SCREEN_WIDTH` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 30: imports `SCREEN_HEIGHT` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 30: imports `STATUS_BTN_HEIGHT` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 30: imports `STATUS_BAR_PCT` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 30: imports `style_as_screen_backdrop` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 34: imports `BTC_ICONS` from package `MockUI.basic.symbol_lib` (re-export from `MockUI.basic.symbol_lib.btc_icons:BTC_ICONS`); prefer direct module import internally.
  - Line 35: imports `Btn` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.btn:Btn`); prefer direct module import internally.
  - Line 35: imports `modal_overlay` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.modal_overlay:modal_overlay`); prefer direct module import internally.
  - Line 35: imports `make_icon` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.icon_widgets:make_icon`); prefer direct module import internally.
  - Line 38: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/components/seed_dropup.py`

- Module: `MockUI.basic.components.seed_dropup`
- public_defs (1): SeedDropUp
- package_imports (2):
  - line 3: from `MockUI.basic.widgets` import MenuItem, SeedCard, button_modal
  - line 6: from `MockUI.basic.theming` import apply_style
- direct_module_imports (3):
  - line 4: from `MockUI.basic.ui_state` import Context
  - line 5: from `MockUI.basic.templates.dropup` import DropUp
  - line 7: from `MockUI.basic.components.confirm_modals` import confirm_delete_seed
- findings (4):
  - Line 3: imports `MenuItem` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.menu_item:MenuItem`); prefer direct module import internally.
  - Line 3: imports `SeedCard` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.seed_widgets:SeedCard`); prefer direct module import internally.
  - Line 3: imports `button_modal` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.action_modal:button_modal`); prefer direct module import internally.
  - Line 6: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/components/wallet_dropup.py`

- Module: `MockUI.basic.components.wallet_dropup`
- public_defs (1): WalletDropUp
- package_imports (2):
  - line 3: from `MockUI.basic.widgets` import WalletCard
  - line 6: from `MockUI.basic.theming` import apply_style
- direct_module_imports (3):
  - line 4: from `MockUI.basic.ui_state` import Context
  - line 5: from `MockUI.basic.templates.dropup` import DropUp
  - line 7: from `MockUI.basic.components.confirm_modals` import confirm_delete_wallet
- findings (2):
  - Line 3: imports `WalletCard` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.wallet_widgets:WalletCard`); prefer direct module import internally.
  - Line 6: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/fonts/__init__.py`

- Module: `MockUI.basic.fonts`
- public_defs (0): (none)
- package_imports (0):
  - none
- direct_module_imports (2):
  - line 1: from `MockUI.basic.font_loader_de` import font_loader_de, get_font_de, set_default_font_de
  - line 2: from `MockUI.basic.font_manager` import font_manager
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/fonts/font_loader_de.py`

- Module: `MockUI.basic.fonts.font_loader_de`
- public_defs (3): FontLoaderDE, get_font_de, set_default_font_de
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/fonts/font_manager.py`

- Module: `MockUI.basic.fonts.font_manager`
- public_defs (1): FontManager
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/i18n/__init__.py`

- Module: `MockUI.basic.i18n`
- public_defs (0): (none)
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 3: from `MockUI.basic.i18n_manager` import I18nManager
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/i18n/i18n_manager.py`

- Module: `MockUI.basic.i18n.i18n_manager`
- public_defs (3): I18nManager, get_i18n_manager, t
- package_imports (0):
  - none
- direct_module_imports (3):
  - line 9: from `MockUI.basic.i18n.translation_keys` import Keys
  - line 10: from `MockUI.basic.i18n.lang_compiler` import LangCompiler
  - line 11: from `MockUI.basic.templates.settings_file_manager` import SettingFileManager
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/i18n/lang_compiler.py`

- Module: `MockUI.basic.i18n.lang_compiler`
- public_defs (2): LangCompiler, main
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/i18n/translation_keys.py`

- Module: `MockUI.basic.i18n.translation_keys`
- public_defs (2): KEY_COUNT, Keys
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/specter_gui.py`

- Module: `MockUI.basic.specter_gui`
- public_defs (2): SpecterGui, get_gui
- package_imports (10):
  - line 3: from `MockUI.basic.utils` import SCREEN_WIDTH, CONTENT_H, ANIM_MS_HORIZONTAL, ANIM_MS_VERTICAL, GUI_REFRESH_MS, KeyboardManager, slide_x, slide_y, GUIAnimations, set_scroll, get_size, set_size, set_pos
  - line 10: from `MockUI.basic.i18n` import I18nManager
  - line 11: from `MockUI.basic.theming` import ThemeManager
  - line 12: from `MockUI.basic.tour` import GuidedTour, INTRO_TOUR_STEPS
  - line 13: from `MockUI.basic.components` import NavigationBar, AppScreen
  - line 16: from `MockUI.main_screens` import MainMenu, LockedMenu
  - line 20: from `MockUI.wallet_screens` import WalletMenu, ConnectWalletsMenu, AddWalletMenu, CreateCustomWalletMenu, ViewSignersMenu
  - line 27: from `MockUI.seed_screens` import AddSeedMenu, SeedPhraseMenu, StoreSeedphraseMenu, ClearSeedphraseMenu, GenerateSeedMenu, PassphraseMenu, RelatedWalletsForSeedMenu
  - line 36: from `MockUI.device_screens` import SecuritySettingsMenu, BackupsMenu, FirmwareMenu, InterfacesMenu, StorageMenu, SecurityFeaturesMenu, LanguageMenu, SettingsMenu, PreferencesMenu, ThemeMenu
  - line 49: from `MockUI.stubs` import DeviceState
- direct_module_imports (2):
  - line 9: from `MockUI.basic.ui_state` import UIState, Context
  - line 14: from `MockUI.basic.templates.action_screen` import ActionScreen
- findings (44):
  - Line 3: imports `SCREEN_WIDTH` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `CONTENT_H` from package `MockUI.basic.utils` but name not exported there (likely fragile / runtime error risk).
  - Line 3: imports `ANIM_MS_HORIZONTAL` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `ANIM_MS_VERTICAL` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `GUI_REFRESH_MS` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `KeyboardManager` from package `MockUI.basic.utils` (re-export from `MockUI.basic.utils.keyboard_manager:KeyboardManager`); prefer direct module import internally.
  - Line 3: imports `slide_x` from package `MockUI.basic.utils` (re-export from `MockUI.basic.utils.animations:slide_x`); prefer direct module import internally.
  - Line 3: imports `slide_y` from package `MockUI.basic.utils` (re-export from `MockUI.basic.utils.animations:slide_y`); prefer direct module import internally.
  - Line 3: imports `GUIAnimations` from package `MockUI.basic.utils` (re-export from `MockUI.basic.utils.animations:GUIAnimations`); prefer direct module import internally.
  - Line 3: imports `set_scroll` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `get_size` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `set_size` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `set_pos` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 10: imports `I18nManager` from package `MockUI.basic.i18n` (re-export from `MockUI.basic.i18n.i18n_manager:I18nManager`); prefer direct module import internally.
  - Line 11: imports `ThemeManager` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:ThemeManager`); prefer direct module import internally.
  - Line 12: imports `GuidedTour` from package `MockUI.basic.tour` (re-export from `MockUI.basic.tour.guided_tour:GuidedTour`); prefer direct module import internally.
  - Line 12: imports `INTRO_TOUR_STEPS` from package `MockUI.basic.tour` (re-export from `MockUI.basic.tour.guided_tour:INTRO_TOUR_STEPS`); prefer direct module import internally.
  - Line 13: imports `NavigationBar` from package `MockUI.basic.components` (re-export from `MockUI.basic.components.navigation_bar:NavigationBar`); prefer direct module import internally.
  - Line 13: imports `AppScreen` from package `MockUI.basic.components` (re-export from `MockUI.basic.components.app_screen:AppScreen`); prefer direct module import internally.
  - Line 16: imports `MainMenu` from package `MockUI.main_screens` (re-export from `MockUI.main_screens.main_menu:MainMenu`); prefer direct module import internally.
  - Line 16: imports `LockedMenu` from package `MockUI.main_screens` (re-export from `MockUI.main_screens.locked_menu:LockedMenu`); prefer direct module import internally.
  - Line 20: imports `WalletMenu` from package `MockUI.wallet_screens` (re-export from `MockUI.wallet_screens.wallet_menu:WalletMenu`); prefer direct module import internally.
  - Line 20: imports `ConnectWalletsMenu` from package `MockUI.wallet_screens` (re-export from `MockUI.wallet_screens.connect_wallets_menu:ConnectWalletsMenu`); prefer direct module import internally.
  - Line 20: imports `AddWalletMenu` from package `MockUI.wallet_screens` (re-export from `MockUI.wallet_screens.add_wallet_menu:AddWalletMenu`); prefer direct module import internally.
  - Line 20: imports `CreateCustomWalletMenu` from package `MockUI.wallet_screens` (re-export from `MockUI.wallet_screens.create_custom_wallet_menu:CreateCustomWalletMenu`); prefer direct module import internally.
  - Line 20: imports `ViewSignersMenu` from package `MockUI.wallet_screens` (re-export from `MockUI.wallet_screens.view_signers_menu:ViewSignersMenu`); prefer direct module import internally.
  - Line 27: imports `AddSeedMenu` from package `MockUI.seed_screens` (re-export from `MockUI.seed_screens.add_seed_menu:AddSeedMenu`); prefer direct module import internally.
  - Line 27: imports `SeedPhraseMenu` from package `MockUI.seed_screens` (re-export from `MockUI.seed_screens.seedphrase_menu:SeedPhraseMenu`); prefer direct module import internally.
  - Line 27: imports `StoreSeedphraseMenu` from package `MockUI.seed_screens` (re-export from `MockUI.seed_screens.store_seedphrase_menu:StoreSeedphraseMenu`); prefer direct module import internally.
  - Line 27: imports `ClearSeedphraseMenu` from package `MockUI.seed_screens` (re-export from `MockUI.seed_screens.clear_seedphrase_menu:ClearSeedphraseMenu`); prefer direct module import internally.
  - Line 27: imports `GenerateSeedMenu` from package `MockUI.seed_screens` (re-export from `MockUI.seed_screens.generate_seedphrase_menu:GenerateSeedMenu`); prefer direct module import internally.
  - Line 27: imports `PassphraseMenu` from package `MockUI.seed_screens` (re-export from `MockUI.seed_screens.passphrase_menu:PassphraseMenu`); prefer direct module import internally.
  - Line 27: imports `RelatedWalletsForSeedMenu` from package `MockUI.seed_screens` (re-export from `MockUI.seed_screens.related_wallets_for_seed_menu:RelatedWalletsForSeedMenu`); prefer direct module import internally.
  - Line 36: imports `SecuritySettingsMenu` from package `MockUI.device_screens` (re-export from `MockUI.device_screens.security_settings_menu:SecuritySettingsMenu`); prefer direct module import internally.
  - Line 36: imports `BackupsMenu` from package `MockUI.device_screens` (re-export from `MockUI.device_screens.backups_menu:BackupsMenu`); prefer direct module import internally.
  - Line 36: imports `FirmwareMenu` from package `MockUI.device_screens` (re-export from `MockUI.device_screens.firmware_menu:FirmwareMenu`); prefer direct module import internally.
  - Line 36: imports `InterfacesMenu` from package `MockUI.device_screens` (re-export from `MockUI.device_screens.interfaces_menu:InterfacesMenu`); prefer direct module import internally.
  - Line 36: imports `StorageMenu` from package `MockUI.device_screens` (re-export from `MockUI.device_screens.storage_menu:StorageMenu`); prefer direct module import internally.
  - Line 36: imports `SecurityFeaturesMenu` from package `MockUI.device_screens` (re-export from `MockUI.device_screens.security_features_menu:SecurityFeaturesMenu`); prefer direct module import internally.
  - Line 36: imports `LanguageMenu` from package `MockUI.device_screens` (re-export from `MockUI.device_screens.language_menu:LanguageMenu`); prefer direct module import internally.
  - Line 36: imports `SettingsMenu` from package `MockUI.device_screens` (re-export from `MockUI.device_screens.settings_menu:SettingsMenu`); prefer direct module import internally.
  - Line 36: imports `PreferencesMenu` from package `MockUI.device_screens` (re-export from `MockUI.device_screens.preferences_menu:PreferencesMenu`); prefer direct module import internally.
  - Line 36: imports `ThemeMenu` from package `MockUI.device_screens` (re-export from `MockUI.device_screens.theme_menu:ThemeMenu`); prefer direct module import internally.
  - Line 49: imports `DeviceState` from package `MockUI.stubs` (re-export from `MockUI.stubs.device_state:DeviceState`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/__init__.py`

- Module: `MockUI.basic.symbol_lib`
- public_defs (0): (none)
- package_imports (0):
  - none
- direct_module_imports (2):
  - line 3: from `MockUI.basic.icon` import Icon
  - line 4: from `MockUI.basic.btc_icons` import BTC_ICONS
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/btc_icons.py`

- Module: `MockUI.basic.symbol_lib.btc_icons`
- public_defs (1): BTC_ICONS
- package_imports (0):
  - none
- direct_module_imports (68):
  - line 14: from `MockUI.basic.symbol_lib.icons.address_book` import ADDRESS_BOOK
  - line 16: from `MockUI.basic.symbol_lib.icons.alert_circle` import ALERT_CIRCLE
  - line 23: from `MockUI.basic.symbol_lib.icons.battery_2_outline` import BATTERY_2_OUTLINE
  - line 25: from `MockUI.basic.symbol_lib.icons.battery_3_outline` import BATTERY_3_OUTLINE
  - line 27: from `MockUI.basic.symbol_lib.icons.battery_4_outline` import BATTERY_4_OUTLINE
  - line 28: from `MockUI.basic.symbol_lib.icons.battery_empty` import BATTERY_EMPTY
  - line 29: from `MockUI.basic.symbol_lib.icons.battery_empty_outline` import BATTERY_EMPTY_OUTLINE
  - line 31: from `MockUI.basic.symbol_lib.icons.battery_full_outline` import BATTERY_FULL_OUTLINE
  - line 32: from `MockUI.basic.symbol_lib.icons.bell` import BELL
  - line 34: from `MockUI.basic.symbol_lib.icons.bitcoin` import BITCOIN
  - line 39: from `MockUI.basic.symbol_lib.icons.brush` import BRUSH
  - line 45: from `MockUI.basic.symbol_lib.icons.caret_left` import CARET_LEFT
  - line 46: from `MockUI.basic.symbol_lib.icons.caret_right` import CARET_RIGHT
  - line 52: from `MockUI.basic.symbol_lib.icons.check` import CHECK
  - line 54: from `MockUI.basic.symbol_lib.icons.clear_character` import CLEAR_CHARACTER
  - line 57: from `MockUI.basic.symbol_lib.icons.code` import CODE
  - line 63: from `MockUI.basic.symbol_lib.icons.confirmations_4` import CONFIRMATIONS_4
  - line 66: from `MockUI.basic.symbol_lib.icons.console` import CONSOLE
  - line 67: from `MockUI.basic.symbol_lib.icons.contacts` import CONTACTS
  - line 68: from `MockUI.basic.symbol_lib.icons.copy` import COPY
  - line 70: from `MockUI.basic.symbol_lib.icons.cross` import CROSS
  - line 72: from `MockUI.basic.symbol_lib.icons.dice` import DICE
  - line 81: from `MockUI.basic.symbol_lib.icons.export` import EXPORT
  - line 83: from `MockUI.basic.symbol_lib.icons.file` import FILE
  - line 84: from `MockUI.basic.symbol_lib.icons.fingerprint` import FINGERPRINT
  - line 85: from `MockUI.basic.symbol_lib.icons.flip_horizontal` import FLIP_HORIZONTAL
  - line 87: from `MockUI.basic.symbol_lib.icons.gear` import GEAR
  - line 88: from `MockUI.basic.symbol_lib.icons.gear_outline` import GEAR_OUTLINE
  - line 90: from `MockUI.basic.symbol_lib.icons.globe` import GLOBE
  - line 94: from `MockUI.basic.symbol_lib.icons.hat_and_glasses` import HAT_AND_GLASSES
  - line 96: from `MockUI.basic.symbol_lib.icons.home` import HOME
  - line 97: from `MockUI.basic.symbol_lib.icons.home_outline` import HOME_OUTLINE
  - line 102: from `MockUI.basic.symbol_lib.icons.key` import KEY
  - line 103: from `MockUI.basic.symbol_lib.icons.key_multi_back` import KEY_MULTI_BACK
  - line 104: from `MockUI.basic.symbol_lib.icons.key_multi_front` import KEY_MULTI_FRONT
  - line 105: from `MockUI.basic.symbol_lib.icons.key_outline` import KEY_OUTLINE
  - line 106: from `MockUI.basic.symbol_lib.icons.keyboard` import KEYBOARD
  - line 107: from `MockUI.basic.symbol_lib.icons.lightning` import LIGHTNING
  - line 109: from `MockUI.basic.symbol_lib.icons.link` import LINK
  - line 111: from `MockUI.basic.symbol_lib.icons.lock` import LOCK
  - line 112: from `MockUI.basic.symbol_lib.icons.magic_wand` import MAGIC_WAND
  - line 113: from `MockUI.basic.symbol_lib.icons.menu` import MENU
  - line 122: from `MockUI.basic.symbol_lib.icons.mnemonic` import MNEMONIC
  - line 123: from `MockUI.basic.symbol_lib.icons.moon` import MOON
  - line 134: from `MockUI.basic.symbol_lib.icons.password` import PASSWORD
  - line 135: from `MockUI.basic.symbol_lib.icons.photo` import PHOTO
  - line 137: from `MockUI.basic.symbol_lib.icons.plus` import PLUS
  - line 139: from `MockUI.basic.symbol_lib.icons.point_of_sale` import POINT_OF_SALE
  - line 143: from `MockUI.basic.symbol_lib.icons.qr_code` import QR_CODE
  - line 145: from `MockUI.basic.symbol_lib.icons.question_circle` import QUESTION_CIRCLE
  - line 147: from `MockUI.basic.symbol_lib.icons.receive` import RECEIVE
  - line 149: from `MockUI.basic.symbol_lib.icons.refresh` import REFRESH
  - line 150: from `MockUI.basic.symbol_lib.icons.relay` import RELAY
  - line 152: from `MockUI.basic.symbol_lib.icons.safe` import SAFE
  - line 156: from `MockUI.basic.symbol_lib.icons.scan` import SCAN
  - line 157: from `MockUI.basic.symbol_lib.icons.sd_card` import SD_CARD
  - line 159: from `MockUI.basic.symbol_lib.icons.send` import SEND
  - line 162: from `MockUI.basic.symbol_lib.icons.shared_wallet` import SHARED_WALLET
  - line 163: from `MockUI.basic.symbol_lib.icons.shield` import SHIELD
  - line 164: from `MockUI.basic.symbol_lib.icons.sign` import SIGN
  - line 165: from `MockUI.basic.symbol_lib.icons.siren` import SIREN
  - line 166: from `MockUI.basic.symbol_lib.icons.smartcard` import SMARTCARD
  - line 176: from `MockUI.basic.symbol_lib.icons.trash` import TRASH
  - line 181: from `MockUI.basic.symbol_lib.icons.usb` import USB
  - line 182: from `MockUI.basic.symbol_lib.icons.verify` import VERIFY
  - line 183: from `MockUI.basic.symbol_lib.icons.visible` import VISIBLE
  - line 188: from `MockUI.basic.symbol_lib.icons.wallet` import WALLET
  - line 189: from `MockUI.basic.symbol_lib.icons.wallet_outline` import WALLET_OUTLINE
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icon.py`

- Module: `MockUI.basic.symbol_lib.icon`
- public_defs (2): Icon, create_icon_from_bitmap
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/__init__.py`

- Module: `MockUI.basic.symbol_lib.icons`
- public_defs (0): (none)
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/address_book.py`

- Module: `MockUI.basic.symbol_lib.icons.address_book`
- public_defs (1): ADDRESS_BOOK
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/alert_circle.py`

- Module: `MockUI.basic.symbol_lib.icons.alert_circle`
- public_defs (1): ALERT_CIRCLE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/battery_2_outline.py`

- Module: `MockUI.basic.symbol_lib.icons.battery_2_outline`
- public_defs (1): BATTERY_2_OUTLINE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/battery_3_outline.py`

- Module: `MockUI.basic.symbol_lib.icons.battery_3_outline`
- public_defs (1): BATTERY_3_OUTLINE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/battery_4_outline.py`

- Module: `MockUI.basic.symbol_lib.icons.battery_4_outline`
- public_defs (1): BATTERY_4_OUTLINE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/battery_empty.py`

- Module: `MockUI.basic.symbol_lib.icons.battery_empty`
- public_defs (1): BATTERY_EMPTY
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/battery_empty_outline.py`

- Module: `MockUI.basic.symbol_lib.icons.battery_empty_outline`
- public_defs (1): BATTERY_EMPTY_OUTLINE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/battery_full_outline.py`

- Module: `MockUI.basic.symbol_lib.icons.battery_full_outline`
- public_defs (1): BATTERY_FULL_OUTLINE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/bell.py`

- Module: `MockUI.basic.symbol_lib.icons.bell`
- public_defs (1): BELL
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/bitcoin.py`

- Module: `MockUI.basic.symbol_lib.icons.bitcoin`
- public_defs (1): BITCOIN
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/brush.py`

- Module: `MockUI.basic.symbol_lib.icons.brush`
- public_defs (1): BRUSH
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/caret_left.py`

- Module: `MockUI.basic.symbol_lib.icons.caret_left`
- public_defs (1): CARET_LEFT
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/caret_right.py`

- Module: `MockUI.basic.symbol_lib.icons.caret_right`
- public_defs (1): CARET_RIGHT
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/check.py`

- Module: `MockUI.basic.symbol_lib.icons.check`
- public_defs (1): CHECK
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/clear_character.py`

- Module: `MockUI.basic.symbol_lib.icons.clear_character`
- public_defs (1): CLEAR_CHARACTER
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/code.py`

- Module: `MockUI.basic.symbol_lib.icons.code`
- public_defs (1): CODE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/confirmations_4.py`

- Module: `MockUI.basic.symbol_lib.icons.confirmations_4`
- public_defs (1): CONFIRMATIONS_4
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/console.py`

- Module: `MockUI.basic.symbol_lib.icons.console`
- public_defs (1): CONSOLE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/contacts.py`

- Module: `MockUI.basic.symbol_lib.icons.contacts`
- public_defs (1): CONTACTS
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/copy.py`

- Module: `MockUI.basic.symbol_lib.icons.copy`
- public_defs (1): COPY
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/cross.py`

- Module: `MockUI.basic.symbol_lib.icons.cross`
- public_defs (1): CROSS
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/dice.py`

- Module: `MockUI.basic.symbol_lib.icons.dice`
- public_defs (1): DICE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/export.py`

- Module: `MockUI.basic.symbol_lib.icons.export`
- public_defs (1): EXPORT
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/file.py`

- Module: `MockUI.basic.symbol_lib.icons.file`
- public_defs (1): FILE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/fingerprint.py`

- Module: `MockUI.basic.symbol_lib.icons.fingerprint`
- public_defs (1): FINGERPRINT
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/flip_horizontal.py`

- Module: `MockUI.basic.symbol_lib.icons.flip_horizontal`
- public_defs (1): FLIP_HORIZONTAL
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/gear.py`

- Module: `MockUI.basic.symbol_lib.icons.gear`
- public_defs (1): GEAR
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/gear_outline.py`

- Module: `MockUI.basic.symbol_lib.icons.gear_outline`
- public_defs (1): GEAR_OUTLINE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/globe.py`

- Module: `MockUI.basic.symbol_lib.icons.globe`
- public_defs (1): GLOBE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/hat_and_glasses.py`

- Module: `MockUI.basic.symbol_lib.icons.hat_and_glasses`
- public_defs (1): HAT_AND_GLASSES
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/home.py`

- Module: `MockUI.basic.symbol_lib.icons.home`
- public_defs (1): HOME
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/home_outline.py`

- Module: `MockUI.basic.symbol_lib.icons.home_outline`
- public_defs (1): HOME_OUTLINE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/key.py`

- Module: `MockUI.basic.symbol_lib.icons.key`
- public_defs (1): KEY
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/key_multi_back.py`

- Module: `MockUI.basic.symbol_lib.icons.key_multi_back`
- public_defs (1): KEY_MULTI_BACK
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/key_multi_front.py`

- Module: `MockUI.basic.symbol_lib.icons.key_multi_front`
- public_defs (1): KEY_MULTI_FRONT
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/key_outline.py`

- Module: `MockUI.basic.symbol_lib.icons.key_outline`
- public_defs (1): KEY_OUTLINE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/keyboard.py`

- Module: `MockUI.basic.symbol_lib.icons.keyboard`
- public_defs (1): KEYBOARD
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/lightning.py`

- Module: `MockUI.basic.symbol_lib.icons.lightning`
- public_defs (1): LIGHTNING
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/link.py`

- Module: `MockUI.basic.symbol_lib.icons.link`
- public_defs (1): LINK
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/lock.py`

- Module: `MockUI.basic.symbol_lib.icons.lock`
- public_defs (1): LOCK
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/magic_wand.py`

- Module: `MockUI.basic.symbol_lib.icons.magic_wand`
- public_defs (1): MAGIC_WAND
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/menu.py`

- Module: `MockUI.basic.symbol_lib.icons.menu`
- public_defs (1): MENU
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/mnemonic.py`

- Module: `MockUI.basic.symbol_lib.icons.mnemonic`
- public_defs (1): MNEMONIC
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/moon.py`

- Module: `MockUI.basic.symbol_lib.icons.moon`
- public_defs (1): MOON
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/password.py`

- Module: `MockUI.basic.symbol_lib.icons.password`
- public_defs (1): PASSWORD
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/photo.py`

- Module: `MockUI.basic.symbol_lib.icons.photo`
- public_defs (1): PHOTO
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/plus.py`

- Module: `MockUI.basic.symbol_lib.icons.plus`
- public_defs (1): PLUS
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/point_of_sale.py`

- Module: `MockUI.basic.symbol_lib.icons.point_of_sale`
- public_defs (1): POINT_OF_SALE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/qr_code.py`

- Module: `MockUI.basic.symbol_lib.icons.qr_code`
- public_defs (1): QR_CODE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/question_circle.py`

- Module: `MockUI.basic.symbol_lib.icons.question_circle`
- public_defs (1): QUESTION_CIRCLE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/receive.py`

- Module: `MockUI.basic.symbol_lib.icons.receive`
- public_defs (1): RECEIVE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/refresh.py`

- Module: `MockUI.basic.symbol_lib.icons.refresh`
- public_defs (1): REFRESH
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/relay.py`

- Module: `MockUI.basic.symbol_lib.icons.relay`
- public_defs (1): RELAY
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/safe.py`

- Module: `MockUI.basic.symbol_lib.icons.safe`
- public_defs (1): SAFE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/scan.py`

- Module: `MockUI.basic.symbol_lib.icons.scan`
- public_defs (1): SCAN
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/sd_card.py`

- Module: `MockUI.basic.symbol_lib.icons.sd_card`
- public_defs (1): SD_CARD
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/send.py`

- Module: `MockUI.basic.symbol_lib.icons.send`
- public_defs (1): SEND
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/shared_wallet.py`

- Module: `MockUI.basic.symbol_lib.icons.shared_wallet`
- public_defs (1): SHARED_WALLET
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/shield.py`

- Module: `MockUI.basic.symbol_lib.icons.shield`
- public_defs (1): SHIELD
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/sign.py`

- Module: `MockUI.basic.symbol_lib.icons.sign`
- public_defs (1): SIGN
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/siren.py`

- Module: `MockUI.basic.symbol_lib.icons.siren`
- public_defs (1): SIREN
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/smartcard.py`

- Module: `MockUI.basic.symbol_lib.icons.smartcard`
- public_defs (1): SMARTCARD
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/trash.py`

- Module: `MockUI.basic.symbol_lib.icons.trash`
- public_defs (1): TRASH
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/usb.py`

- Module: `MockUI.basic.symbol_lib.icons.usb`
- public_defs (1): USB
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/verify.py`

- Module: `MockUI.basic.symbol_lib.icons.verify`
- public_defs (1): VERIFY
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/visible.py`

- Module: `MockUI.basic.symbol_lib.icons.visible`
- public_defs (1): VISIBLE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/wallet.py`

- Module: `MockUI.basic.symbol_lib.icons.wallet`
- public_defs (1): WALLET
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/symbol_lib/icons/wallet_outline.py`

- Module: `MockUI.basic.symbol_lib.icons.wallet_outline`
- public_defs (1): WALLET_OUTLINE
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 2: from `MockUI.basic.symbol_lib.icon` import Icon
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/templates/__init__.py`

- Module: `MockUI.basic.templates`
- public_defs (0): (none)
- package_imports (0):
  - none
- direct_module_imports (2):
  - line 1: from `MockUI.basic.settings_file_compiler` import SettingsFileCompiler, collect_int_constants, read_cstring
  - line 6: from `MockUI.basic.settings_file_manager` import SettingFileManager
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/templates/action_screen.py`

- Module: `MockUI.basic.templates.action_screen`
- public_defs (1): ActionScreen
- package_imports (2):
  - line 3: from `MockUI.basic.utils` import set_align, set_pos
  - line 4: from `MockUI.basic.widgets` import Btn, body_label
- direct_module_imports (1):
  - line 2: from `MockUI.basic.templates.titled_screen` import TitledScreen
- findings (4):
  - Line 3: imports `set_align` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `set_pos` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 4: imports `Btn` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.btn:Btn`); prefer direct module import internally.
  - Line 4: imports `body_label` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.labels:body_label`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/templates/dropup.py`

- Module: `MockUI.basic.templates.dropup`
- public_defs (2): DropUp, DropUpState
- package_imports (4):
  - line 16: from `MockUI.basic.widgets` import Btn, flex_col, flex_row
  - line 17: from `MockUI.basic.utils` import STATUS_BTN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, STATUS_BAR_PCT, CARD_H, ANIM_MS_VERTICAL, slide_y, delete_all_children_of, set_size, set_pos, set_scroll, set_propagate_events
  - line 24: from `MockUI.basic.symbol_lib` import BTC_ICONS
  - line 25: from `MockUI.basic.theming` import apply_style
- direct_module_imports (2):
  - line 13: from `MockUI.basic.templates.micropython` import const
  - line 15: from `MockUI.basic.templates.specter_gui_base` import SpecterGuiMixin
- findings (17):
  - Line 16: imports `Btn` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.btn:Btn`); prefer direct module import internally.
  - Line 16: imports `flex_col` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.containers:flex_col`); prefer direct module import internally.
  - Line 16: imports `flex_row` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.containers:flex_row`); prefer direct module import internally.
  - Line 17: imports `STATUS_BTN_HEIGHT` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 17: imports `SCREEN_WIDTH` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 17: imports `SCREEN_HEIGHT` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 17: imports `STATUS_BAR_PCT` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 17: imports `CARD_H` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 17: imports `ANIM_MS_VERTICAL` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 17: imports `slide_y` from package `MockUI.basic.utils` (re-export from `MockUI.basic.utils.animations:slide_y`); prefer direct module import internally.
  - Line 17: imports `delete_all_children_of` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 17: imports `set_size` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 17: imports `set_pos` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 17: imports `set_scroll` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 17: imports `set_propagate_events` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 24: imports `BTC_ICONS` from package `MockUI.basic.symbol_lib` (re-export from `MockUI.basic.symbol_lib.btc_icons:BTC_ICONS`); prefer direct module import internally.
  - Line 25: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/templates/menu.py`

- Module: `MockUI.basic.templates.menu`
- public_defs (1): GenericMenu
- package_imports (4):
  - line 3: from `MockUI.basic.utils` import BTN_HEIGHT, BTN_WIDTH_PCT, SWITCH_HEIGHT, SWITCH_WIDTH, PAD, SMALL_PAD, delete_all_children_of, style_as_flex_container, set_size, set_pos, set_scroll, set_align
  - line 9: from `MockUI.basic.symbol_lib` import Icon, BTC_ICONS
  - line 10: from `MockUI.basic.theming` import apply_style
  - line 11: from `MockUI.basic.widgets` import button_modal, Btn, body_label, menu_label, section_header, flex_row, make_icon
- direct_module_imports (1):
  - line 2: from `MockUI.basic.templates.titled_screen` import TitledScreen
- findings (22):
  - Line 3: imports `BTN_HEIGHT` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `BTN_WIDTH_PCT` from package `MockUI.basic.utils` but name not exported there (likely fragile / runtime error risk).
  - Line 3: imports `SWITCH_HEIGHT` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `SWITCH_WIDTH` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `PAD` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `SMALL_PAD` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `delete_all_children_of` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `style_as_flex_container` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `set_size` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `set_pos` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `set_scroll` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `set_align` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 9: imports `Icon` from package `MockUI.basic.symbol_lib` (re-export from `MockUI.basic.symbol_lib.icon:Icon`); prefer direct module import internally.
  - Line 9: imports `BTC_ICONS` from package `MockUI.basic.symbol_lib` (re-export from `MockUI.basic.symbol_lib.btc_icons:BTC_ICONS`); prefer direct module import internally.
  - Line 10: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.
  - Line 11: imports `button_modal` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.action_modal:button_modal`); prefer direct module import internally.
  - Line 11: imports `Btn` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.btn:Btn`); prefer direct module import internally.
  - Line 11: imports `body_label` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.labels:body_label`); prefer direct module import internally.
  - Line 11: imports `menu_label` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.labels:menu_label`); prefer direct module import internally.
  - Line 11: imports `section_header` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.labels:section_header`); prefer direct module import internally.
  - Line 11: imports `flex_row` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.containers:flex_row`); prefer direct module import internally.
  - Line 11: imports `make_icon` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.icon_widgets:make_icon`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/templates/settings_file_compiler.py`

- Module: `MockUI.basic.templates.settings_file_compiler`
- public_defs (9): HEADER_SIZE, KEY_COUNT_SIZE, MAGIC_SIZE, NAME_FIELD_SIZE, OFFSET_SIZE, SettingsFileCompiler, VERSION_SIZE, collect_int_constants, read_cstring
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/templates/settings_file_manager.py`

- Module: `MockUI.basic.templates.settings_file_manager`
- public_defs (1): SettingFileManager
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/templates/specter_gui_base.py`

- Module: `MockUI.basic.templates.specter_gui_base`
- public_defs (2): SpecterGuiElement, SpecterGuiMixin
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/templates/titled_screen.py`

- Module: `MockUI.basic.templates.titled_screen`
- public_defs (1): TitledScreen
- package_imports (4):
  - line 28: from `MockUI.basic.theming` import apply_style
  - line 29: from `MockUI.basic.utils` import TITLE_HEIGHT, TITLE_PADDING, SCREEN_HEIGHT, CONTENT_H, SMALL_PAD, TITLE_ROW_HEIGHT_PCT, style_as_screen_backdrop, set_pos, set_scroll, set_align
  - line 34: from `MockUI.basic.widgets` import title_label, Btn, flex_row, screen_backdrop
  - line 35: from `MockUI.basic.symbol_lib` import BTC_ICONS
- direct_module_imports (1):
  - line 27: from `MockUI.basic.templates.specter_gui_base` import SpecterGuiElement
- findings (16):
  - Line 28: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.
  - Line 29: imports `TITLE_HEIGHT` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 29: imports `TITLE_PADDING` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 29: imports `SCREEN_HEIGHT` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 29: imports `CONTENT_H` from package `MockUI.basic.utils` but name not exported there (likely fragile / runtime error risk).
  - Line 29: imports `SMALL_PAD` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 29: imports `TITLE_ROW_HEIGHT_PCT` from package `MockUI.basic.utils` but name not exported there (likely fragile / runtime error risk).
  - Line 29: imports `style_as_screen_backdrop` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 29: imports `set_pos` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 29: imports `set_scroll` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 29: imports `set_align` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 34: imports `title_label` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.labels:title_label`); prefer direct module import internally.
  - Line 34: imports `Btn` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.btn:Btn`); prefer direct module import internally.
  - Line 34: imports `flex_row` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.containers:flex_row`); prefer direct module import internally.
  - Line 34: imports `screen_backdrop` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.containers:screen_backdrop`); prefer direct module import internally.
  - Line 35: imports `BTC_ICONS` from package `MockUI.basic.symbol_lib` (re-export from `MockUI.basic.symbol_lib.btc_icons:BTC_ICONS`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/theming/__init__.py`

- Module: `MockUI.basic.theming`
- public_defs (0): (none)
- package_imports (0):
  - none
- direct_module_imports (4):
  - line 5: from `MockUI.basic.theme_schema` import SpecterColorPalette, SpecterFontPalette, SpecterStylePalette
  - line 6: from `MockUI.basic.color_palette_compiler` import to_lv_color, to_hex_color_str, ColorMode
  - line 7: from `MockUI.basic.theme_manager` import apply_style, remove_style, reset_style, get_theme_manager, ThemeManager, get_style, get_color, get_font
  - line 8: from `MockUI.templates.settings_file_compiler` import collect_int_constants
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/theming/color_palette_compiler.py`

- Module: `MockUI.basic.theming.color_palette_compiler`
- public_defs (8): ColorMode, ColorPaletteCompiler, color_ref_to_palette_idx, is_hex_RGB_color, main, shade, to_hex_color_str, to_lv_color
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/theming/font_palette_compiler.py`

- Module: `MockUI.basic.theming.font_palette_compiler`
- public_defs (3): FontPaletteCompiler, font_ref_to_palette_idx, main
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/theming/style_palette_compiler.py`

- Module: `MockUI.basic.theming.style_palette_compiler`
- public_defs (10): PROP_STYLE_INHERIT, StylePaletteCompiler, VAL_COLOR_PAL, VAL_FONT_PAL, VAL_LIT, VAL_STYLE_PAL, key_to_style_index, main, read_lit_dict_from_binary, style_ref_to_palette_idx
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/theming/theme_compiler.py`

- Module: `MockUI.basic.theming.theme_compiler`
- public_defs (2): ThemeCompiler, main
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/theming/theme_manager.py`

- Module: `MockUI.basic.theming.theme_manager`
- public_defs (8): ThemeManager, apply_style, get_color, get_font, get_style, get_theme_manager, remove_style, reset_style
- package_imports (0):
  - none
- direct_module_imports (3):
  - line 26: from `MockUI.basic.theming.theme_compiler` import ThemeCompiler, SpecterStylePalette, ColorMode
  - line 27: from `MockUI.basic.templates.settings_file_compiler` import collect_int_constants
  - line 28: from `MockUI.basic.templates.settings_file_manager` import SettingFileManager
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/theming/theme_schema.py`

- Module: `MockUI.basic.theming.theme_schema`
- public_defs (3): SpecterColorPalette, SpecterFontPalette, SpecterStylePalette
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/theming/theme_section_compiler.py`

- Module: `MockUI.basic.theming.theme_section_compiler`
- public_defs (1): ThemeSectionCompiler
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/tour/__init__.py`

- Module: `MockUI.basic.tour`
- public_defs (0): (none)
- package_imports (0):
  - none
- direct_module_imports (2):
  - line 3: from `MockUI.basic.guided_tour` import GuidedTour, INTRO_TOUR_STEPS
  - line 4: from `MockUI.basic.ui_explainer` import UIExplainer
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/tour/guided_tour.py`

- Module: `MockUI.basic.tour.guided_tour`
- public_defs (2): GuidedTour, INTRO_TOUR_STEPS
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 7: from `MockUI.basic.tour.ui_explainer` import UIExplainer
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/tour/ui_explainer.py`

- Module: `MockUI.basic.tour.ui_explainer`
- public_defs (1): UIExplainer
- package_imports (4):
  - line 9: from `MockUI.basic.utils` import EXPLAINER_WIDTH, EXPLAINER_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT, get_size, set_size, set_pos, set_scroll
  - line 15: from `MockUI.basic.symbol_lib` import BTC_ICONS
  - line 16: from `MockUI.basic.theming` import apply_style
  - line 17: from `MockUI.basic.widgets` import Btn, flex_row, flex_col, flex_container, body_label, modal_overlay
- direct_module_imports (0):
  - none
- findings (16):
  - Line 9: imports `EXPLAINER_WIDTH` from package `MockUI.basic.utils` but name not exported there (likely fragile / runtime error risk).
  - Line 9: imports `EXPLAINER_HEIGHT` from package `MockUI.basic.utils` but name not exported there (likely fragile / runtime error risk).
  - Line 9: imports `SCREEN_WIDTH` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 9: imports `SCREEN_HEIGHT` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 9: imports `get_size` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 9: imports `set_size` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 9: imports `set_pos` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 9: imports `set_scroll` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 15: imports `BTC_ICONS` from package `MockUI.basic.symbol_lib` (re-export from `MockUI.basic.symbol_lib.btc_icons:BTC_ICONS`); prefer direct module import internally.
  - Line 16: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.
  - Line 17: imports `Btn` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.btn:Btn`); prefer direct module import internally.
  - Line 17: imports `flex_row` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.containers:flex_row`); prefer direct module import internally.
  - Line 17: imports `flex_col` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.containers:flex_col`); prefer direct module import internally.
  - Line 17: imports `flex_container` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.containers:flex_container`); prefer direct module import internally.
  - Line 17: imports `body_label` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.labels:body_label`); prefer direct module import internally.
  - Line 17: imports `modal_overlay` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.modal_overlay:modal_overlay`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/ui_state.py`

- Module: `MockUI.basic.ui_state`
- public_defs (3): CONFIG_FILE, Context, UIState
- package_imports (1):
  - line 10: from `MockUI.basic.utils` import GUIAnimations, MAX_HISTORY_DEPTH
- direct_module_imports (1):
  - line 8: from `MockUI.basic.micropython` import const
- findings (2):
  - Line 10: imports `GUIAnimations` from package `MockUI.basic.utils` (re-export from `MockUI.basic.utils.animations:GUIAnimations`); prefer direct module import internally.
  - Line 10: imports `MAX_HISTORY_DEPTH` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.

### File `scenarios/MockUI/src/MockUI/basic/utils/__init__.py`

- Module: `MockUI.basic.utils`
- public_defs (0): (none)
- package_imports (0):
  - none
- direct_module_imports (4):
  - line 1: from `MockUI.basic.ui_consts` import *
  - line 2: from `MockUI.basic.ui_utils` import *
  - line 3: from `MockUI.basic.keyboard_manager` import KeyboardManager, Layout
  - line 4: from `MockUI.basic.animations` import GUIAnimations, slide_x, slide_y, create_anims_for_transition
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/utils/animations.py`

- Module: `MockUI.basic.utils.animations`
- public_defs (4): GUIAnimations, create_anims_for_transition, slide_x, slide_y
- package_imports (0):
  - none
- direct_module_imports (2):
  - line 19: from `MockUI.basic.utils.micropython` import const
  - line 21: from `MockUI.basic.utils.ui_consts` import SCREEN_WIDTH, CONTENT_H, ANIM_MS_HORIZONTAL, ANIM_MS_VERTICAL
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/utils/keyboard_layouts.py`

- Module: `MockUI.basic.utils.keyboard_layouts`
- public_defs (0): (none)
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/utils/keyboard_manager.py`

- Module: `MockUI.basic.utils.keyboard_manager`
- public_defs (2): KeyboardManager, Layout
- package_imports (1):
  - line 3: from `MockUI.basic.theming` import apply_style
- direct_module_imports (1):
  - line 2: from `MockUI.basic.utils.keyboard_layouts` import _full_layout, _alnum_layout
- findings (1):
  - Line 3: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/utils/ui_consts.py`

- Module: `MockUI.basic.utils.ui_consts`
- public_defs (44): ANIM_MS_HORIZONTAL, ANIM_MS_VERTICAL, BACK_BTN_HEIGHT, BACK_BTN_WIDTH, BATTERY_WIDTH, BIG_PAD, BTC_ICON_WIDTH, BTN_HEIGHT, BTN_WIDTH, BTN_WIDTH_PCT, CARD_H, CONFIRMATION_SLIDER_HEIGHT, CONTENT_H, CONTENT_PCT, EXPLAINER_HEIGHT, EXPLAINER_HEIGHT_PCT, EXPLAINER_WIDTH, EXPLAINER_WIDTH_PCT, FINGERPRINT_LBL_WIDTH, FORM_TA_HEIGHT, GUI_REFRESH_MS, MAX_HISTORY_DEPTH, MENU_PCT, MENU_WIDTH, MODAL_HEIGHT, MODAL_HEIGHT_PCT, MODAL_WIDTH, MODAL_WIDTH_PCT, PAD, PIN_BTN_HEIGHT, PIN_BTN_WIDTH, SCREEN_HEIGHT, SCREEN_WIDTH, SMALL_PAD, STATUS_BAR_H, STATUS_BAR_PCT, STATUS_BTN_HEIGHT, STATUS_BTN_WIDTH, SWITCH_HEIGHT, SWITCH_WIDTH, TITLE_HEIGHT, TITLE_PADDING, TITLE_ROW_HEIGHT_PCT, TITLE_TA_WIDTH
- package_imports (0):
  - none
- direct_module_imports (1):
  - line 1: from `MockUI.basic.utils.micropython` import const
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/utils/ui_utils.py`

- Module: `MockUI.basic.utils.ui_utils`
- public_defs (14): best_fonttype_for_size, configure_flex, delete_all_children_of, get_size, set_align, set_pos, set_propagate_events, set_scale, set_scroll, set_size, shuffle, style_as_flex_container, style_as_screen_backdrop, text_width
- package_imports (1):
  - line 10: from `MockUI.basic.theming` import apply_style, get_font, get_palette_entries, SpecterFontPalette
- direct_module_imports (1):
  - line 9: from `MockUI.basic.utils.ui_consts` import SCREEN_WIDTH, SCREEN_HEIGHT
- findings (4):
  - Line 10: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.
  - Line 10: imports `get_font` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:get_font`); prefer direct module import internally.
  - Line 10: imports `get_palette_entries` from package `MockUI.basic.theming` (re-export from `MockUI.basic.templates.settings_file_compiler:collect_int_constants`); prefer direct module import internally.
  - Line 10: imports `SpecterFontPalette` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_schema:SpecterFontPalette`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/widgets/__init__.py`

- Module: `MockUI.basic.widgets`
- public_defs (0): (none)
- package_imports (0):
  - none
- direct_module_imports (11):
  - line 1: from `MockUI.basic.action_modal` import button_modal, slider_confirm_modal
  - line 2: from `MockUI.basic.battery` import Battery
  - line 3: from `MockUI.basic.btn` import Btn
  - line 4: from `MockUI.basic.containers` import flex_container, flex_col, flex_row, screen_backdrop
  - line 5: from `MockUI.basic.icon_widgets` import make_icon
  - line 6: from `MockUI.basic.inputs` import title_textarea, form_textarea, confirmation_slider, ACCEPTED_CHARS
  - line 7: from `MockUI.basic.labels` import make_label, body_label, form_label, section_header, menu_label, title_label
  - line 8: from `MockUI.basic.menu_item` import MenuItem, MenuItemSuffix
  - line 9: from `MockUI.basic.modal_overlay` import modal_overlay
  - line 10: from `MockUI.basic.seed_widgets` import fingerprint_badge, passphrase_toggle, SeedCard
  - line 11: from `MockUI.basic.wallet_widgets` import wallet_net_text, wallet_account_text, MultisigKeyIcon, wallet_type_icon, WalletCard
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/widgets/action_modal.py`

- Module: `MockUI.basic.widgets.action_modal`
- public_defs (2): button_modal, slider_confirm_modal
- package_imports (2):
  - line 9: from `MockUI.basic.theming` import apply_style
  - line 10: from `MockUI.basic.utils` import CONFIRMATION_SLIDER_HEIGHT, MODAL_WIDTH, MODAL_HEIGHT, BTN_HEIGHT
- direct_module_imports (7):
  - line 2: from `MockUI.basic.widgets.modal_overlay` import modal_overlay
  - line 3: from `MockUI.basic.widgets.btn` import Btn
  - line 4: from `MockUI.basic.widgets.containers` import flex_row, flex_container
  - line 5: from `MockUI.basic.widgets.labels` import body_label
  - line 6: from `MockUI.basic.widgets.icon_widgets` import make_icon
  - line 7: from `MockUI.basic.widgets.menu_item` import MenuItem
  - line 8: from `MockUI.basic.widgets.inputs` import confirmation_slider
- findings (5):
  - Line 9: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.
  - Line 10: imports `CONFIRMATION_SLIDER_HEIGHT` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 10: imports `MODAL_WIDTH` from package `MockUI.basic.utils` but name not exported there (likely fragile / runtime error risk).
  - Line 10: imports `MODAL_HEIGHT` from package `MockUI.basic.utils` but name not exported there (likely fragile / runtime error risk).
  - Line 10: imports `BTN_HEIGHT` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.

### File `scenarios/MockUI/src/MockUI/basic/widgets/battery.py`

- Module: `MockUI.basic.widgets.battery`
- public_defs (2): ALL_STATES, Battery
- package_imports (3):
  - line 3: from `MockUI.basic.utils` import BTC_ICON_WIDTH, set_size, set_align
  - line 4: from `MockUI.basic.symbol_lib` import BTC_ICONS
  - line 5: from `MockUI.basic.theming` import apply_style
- direct_module_imports (1):
  - line 2: from `MockUI.basic.widgets.icon_widgets` import make_icon, apply_icon
- findings (5):
  - Line 3: imports `BTC_ICON_WIDTH` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `set_size` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 3: imports `set_align` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 4: imports `BTC_ICONS` from package `MockUI.basic.symbol_lib` (re-export from `MockUI.basic.symbol_lib.btc_icons:BTC_ICONS`); prefer direct module import internally.
  - Line 5: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/widgets/btn.py`

- Module: `MockUI.basic.widgets.btn`
- public_defs (1): Btn
- package_imports (1):
  - line 19: from `MockUI.basic.theming` import apply_style
- direct_module_imports (4):
  - line 16: from `MockUI.basic.widgets.icon_widgets` import apply_icon, make_icon
  - line 17: from `MockUI.basic.widgets.labels` import make_label
  - line 18: from `MockUI.basic.templates.specter_gui_base` import SpecterGuiElement
  - line 20: from `MockUI.basic.utils.ui_utils` import configure_flex, set_size
- findings (1):
  - Line 19: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/widgets/card_helpers.py`

- Module: `MockUI.basic.widgets.card_helpers`
- public_defs (3): build_delete_slot, build_name_slot, compute_name_width
- package_imports (3):
  - line 11: from `MockUI.basic.symbol_lib` import BTC_ICONS
  - line 12: from `MockUI.basic.utils` import BIG_PAD, best_fonttype_for_size
  - line 13: from `MockUI.basic.theming` import get_font, apply_style
- direct_module_imports (4):
  - line 7: from `MockUI.basic.widgets.icon_widgets` import make_icon
  - line 8: from `MockUI.basic.widgets.labels` import make_label
  - line 9: from `MockUI.basic.widgets.inputs` import title_textarea
  - line 10: from `MockUI.basic.widgets.btn` import Btn
- findings (5):
  - Line 11: imports `BTC_ICONS` from package `MockUI.basic.symbol_lib` (re-export from `MockUI.basic.symbol_lib.btc_icons:BTC_ICONS`); prefer direct module import internally.
  - Line 12: imports `BIG_PAD` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 12: imports `best_fonttype_for_size` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 13: imports `get_font` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:get_font`); prefer direct module import internally.
  - Line 13: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/widgets/containers.py`

- Module: `MockUI.basic.widgets.containers`
- public_defs (4): flex_col, flex_container, flex_row, screen_backdrop
- package_imports (1):
  - line 8: from `MockUI.basic.utils` import style_as_flex_container, style_as_screen_backdrop
- direct_module_imports (1):
  - line 7: from `MockUI.basic.templates.specter_gui_base` import SpecterGuiElement
- findings (2):
  - Line 8: imports `style_as_flex_container` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 8: imports `style_as_screen_backdrop` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.

### File `scenarios/MockUI/src/MockUI/basic/widgets/icon_widgets.py`

- Module: `MockUI.basic.widgets.icon_widgets`
- public_defs (2): apply_icon, make_icon
- package_imports (1):
  - line 4: from `MockUI.basic.utils` import BTC_ICON_WIDTH, set_size, set_scale
- direct_module_imports (0):
  - none
- findings (3):
  - Line 4: imports `BTC_ICON_WIDTH` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 4: imports `set_size` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 4: imports `set_scale` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.

### File `scenarios/MockUI/src/MockUI/basic/widgets/inputs.py`

- Module: `MockUI.basic.widgets.inputs`
- public_defs (4): ACCEPTED_CHARS, confirmation_slider, form_textarea, title_textarea
- package_imports (2):
  - line 4: from `MockUI.basic.utils` import CONFIRMATION_SLIDER_HEIGHT, FORM_TA_HEIGHT, set_size
  - line 9: from `MockUI.basic.theming` import apply_style
- direct_module_imports (0):
  - none
- findings (4):
  - Line 4: imports `CONFIRMATION_SLIDER_HEIGHT` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 4: imports `FORM_TA_HEIGHT` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 4: imports `set_size` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 9: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/widgets/labels.py`

- Module: `MockUI.basic.widgets.labels`
- public_defs (6): body_label, form_label, make_label, menu_label, section_header, title_label
- package_imports (2):
  - line 4: from `MockUI.basic.utils` import set_size, set_align
  - line 5: from `MockUI.basic.theming` import apply_style
- direct_module_imports (0):
  - none
- findings (3):
  - Line 4: imports `set_size` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 4: imports `set_align` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 5: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/widgets/menu_item.py`

- Module: `MockUI.basic.widgets.menu_item`
- public_defs (2): MenuItem, MenuItemSuffix
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/basic/widgets/modal_overlay.py`

- Module: `MockUI.basic.widgets.modal_overlay`
- public_defs (1): modal_overlay
- package_imports (1):
  - line 3: from `MockUI.basic.theming` import apply_style
- direct_module_imports (3):
  - line 2: from `MockUI.basic.templates.specter_gui_base` import SpecterGuiElement
  - line 4: from `MockUI.basic.utils.ui_consts` import SCREEN_WIDTH, SCREEN_HEIGHT
  - line 5: from `MockUI.basic.utils.ui_utils` import set_size, set_pos, set_scroll
- findings (1):
  - Line 3: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/basic/widgets/seed_widgets.py`

- Module: `MockUI.basic.widgets.seed_widgets`
- public_defs (4): SEED_SLOTS, SeedCard, fingerprint_badge, passphrase_toggle
- package_imports (3):
  - line 10: from `MockUI.basic.symbol_lib` import BTC_ICONS
  - line 11: from `MockUI.basic.theming` import apply_style
  - line 12: from `MockUI.basic.utils` import BTC_ICON_WIDTH, SCREEN_WIDTH, CARD_H, FINGERPRINT_LBL_WIDTH, style_as_flex_container
- direct_module_imports (5):
  - line 5: from `MockUI.basic.widgets.icon_widgets` import make_icon
  - line 6: from `MockUI.basic.widgets.containers` import flex_row
  - line 7: from `MockUI.basic.widgets.labels` import make_label
  - line 8: from `MockUI.basic.widgets.card_helpers` import build_name_slot, build_delete_slot, compute_name_width
  - line 9: from `MockUI.basic.templates.specter_gui_base` import SpecterGuiElement
- findings (7):
  - Line 10: imports `BTC_ICONS` from package `MockUI.basic.symbol_lib` (re-export from `MockUI.basic.symbol_lib.btc_icons:BTC_ICONS`); prefer direct module import internally.
  - Line 11: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.
  - Line 12: imports `BTC_ICON_WIDTH` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 12: imports `SCREEN_WIDTH` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 12: imports `CARD_H` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 12: imports `FINGERPRINT_LBL_WIDTH` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 12: imports `style_as_flex_container` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.

### File `scenarios/MockUI/src/MockUI/basic/widgets/wallet_widgets.py`

- Module: `MockUI.basic.widgets.wallet_widgets`
- public_defs (7): MultisigKeyIcon, WALLET_SLOTS, WalletCard, wallet_account_text, wallet_net_text, wallet_signing_status_modifier, wallet_type_icon
- package_imports (3):
  - line 9: from `MockUI.basic.symbol_lib` import BTC_ICONS
  - line 10: from `MockUI.basic.theming` import apply_style, remove_style, get_style
  - line 13: from `MockUI.basic.utils` import set_size, set_align, style_as_flex_container
- direct_module_imports (6):
  - line 5: from `MockUI.basic.widgets.icon_widgets` import make_icon
  - line 6: from `MockUI.basic.widgets.containers` import flex_row
  - line 7: from `MockUI.basic.widgets.labels` import make_label
  - line 8: from `MockUI.basic.widgets.card_helpers` import build_name_slot, build_delete_slot, compute_name_width
  - line 11: from `MockUI.basic.utils.ui_consts` import BTC_ICON_WIDTH, SCREEN_WIDTH, CARD_H
  - line 12: from `MockUI.basic.templates.specter_gui_base` import SpecterGuiElement
- findings (7):
  - Line 9: imports `BTC_ICONS` from package `MockUI.basic.symbol_lib` (re-export from `MockUI.basic.symbol_lib.btc_icons:BTC_ICONS`); prefer direct module import internally.
  - Line 10: imports `apply_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:apply_style`); prefer direct module import internally.
  - Line 10: imports `remove_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:remove_style`); prefer direct module import internally.
  - Line 10: imports `get_style` from package `MockUI.basic.theming` (re-export from `MockUI.basic.theming.theme_manager:get_style`); prefer direct module import internally.
  - Line 13: imports `set_size` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 13: imports `set_align` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.
  - Line 13: imports `style_as_flex_container` from package `MockUI.basic.utils`; acceptable only if `MockUI.basic.utils` is intended public API layer.

### File `scenarios/MockUI/src/MockUI/device_screens/__init__.py`

- Module: `MockUI.device_screens`
- public_defs (0): (none)
- package_imports (0):
  - none
- direct_module_imports (10):
  - line 1: from `MockUI.security_settings_menu` import SecuritySettingsMenu
  - line 2: from `MockUI.firmware_menu` import FirmwareMenu
  - line 3: from `MockUI.interfaces_menu` import InterfacesMenu
  - line 4: from `MockUI.backups_menu` import BackupsMenu
  - line 5: from `MockUI.security_features_menu` import SecurityFeaturesMenu
  - line 6: from `MockUI.storage_menu` import StorageMenu
  - line 7: from `MockUI.language_menu` import LanguageMenu
  - line 8: from `MockUI.settings_menu` import SettingsMenu
  - line 9: from `MockUI.preferences_menu` import PreferencesMenu
  - line 10: from `MockUI.theme_menu` import ThemeMenu
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/device_screens/backups_menu.py`

- Module: `MockUI.device_screens.backups_menu`
- public_defs (1): BackupsMenu
- package_imports (1):
  - line 1: from `MockUI.basic` import GenericMenu, BTC_ICONS, MenuItem
- direct_module_imports (0):
  - none
- findings (3):
  - Line 1: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 1: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 1: imports `MenuItem` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:MenuItem`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/device_screens/firmware_menu.py`

- Module: `MockUI.device_screens.firmware_menu`
- public_defs (1): FirmwareMenu
- package_imports (1):
  - line 1: from `MockUI.basic` import GenericMenu, BTC_ICONS, MenuItem
- direct_module_imports (0):
  - none
- findings (3):
  - Line 1: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 1: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 1: imports `MenuItem` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:MenuItem`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/device_screens/interfaces_menu.py`

- Module: `MockUI.device_screens.interfaces_menu`
- public_defs (1): InterfacesMenu
- package_imports (1):
  - line 1: from `MockUI.basic` import GenericMenu, BTC_ICONS, MenuItem
- direct_module_imports (0):
  - none
- findings (3):
  - Line 1: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 1: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 1: imports `MenuItem` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:MenuItem`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/device_screens/language_menu.py`

- Module: `MockUI.device_screens.language_menu`
- public_defs (1): LanguageMenu
- package_imports (1):
  - line 2: from `MockUI.basic` import GenericMenu, BTC_ICONS, MenuItem
- direct_module_imports (0):
  - none
- findings (3):
  - Line 2: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 2: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 2: imports `MenuItem` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:MenuItem`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/device_screens/preferences_menu.py`

- Module: `MockUI.device_screens.preferences_menu`
- public_defs (1): PreferencesMenu
- package_imports (1):
  - line 1: from `MockUI.basic` import GenericMenu, BTC_ICONS, MenuItem
- direct_module_imports (1):
  - line 2: from `MockUI.basic.theming.theme_manager` import ColorMode
- findings (3):
  - Line 1: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 1: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 1: imports `MenuItem` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:MenuItem`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/device_screens/security_features_menu.py`

- Module: `MockUI.device_screens.security_features_menu`
- public_defs (1): SecurityFeaturesMenu
- package_imports (1):
  - line 1: from `MockUI.basic` import GenericMenu, BTC_ICONS, MenuItem
- direct_module_imports (0):
  - none
- findings (3):
  - Line 1: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 1: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 1: imports `MenuItem` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:MenuItem`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/device_screens/security_settings_menu.py`

- Module: `MockUI.device_screens.security_settings_menu`
- public_defs (1): SecuritySettingsMenu
- package_imports (1):
  - line 2: from `MockUI.basic` import GenericMenu, BTC_ICONS, MenuItem
- direct_module_imports (0):
  - none
- findings (3):
  - Line 2: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 2: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 2: imports `MenuItem` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:MenuItem`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/device_screens/settings_menu.py`

- Module: `MockUI.device_screens.settings_menu`
- public_defs (1): SettingsMenu
- package_imports (1):
  - line 2: from `MockUI.basic` import GenericMenu, BTC_ICONS, MenuItem, STATUS_BTN_HEIGHT, make_icon, flex_row, apply_style
- direct_module_imports (0):
  - none
- findings (7):
  - Line 2: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 2: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 2: imports `MenuItem` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:MenuItem`); prefer direct module import internally.
  - Line 2: imports `STATUS_BTN_HEIGHT` from package `MockUI.basic` (re-export from `MockUI.basic.utils:STATUS_BTN_HEIGHT`); prefer direct module import internally.
  - Line 2: imports `make_icon` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:make_icon`); prefer direct module import internally.
  - Line 2: imports `flex_row` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:flex_row`); prefer direct module import internally.
  - Line 2: imports `apply_style` from package `MockUI.basic` (re-export from `MockUI.basic.theming:apply_style`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/device_screens/storage_menu.py`

- Module: `MockUI.device_screens.storage_menu`
- public_defs (1): StorageMenu
- package_imports (1):
  - line 1: from `MockUI.basic` import GenericMenu, BTC_ICONS, MenuItem
- direct_module_imports (0):
  - none
- findings (3):
  - Line 1: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 1: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 1: imports `MenuItem` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:MenuItem`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/device_screens/theme_menu.py`

- Module: `MockUI.device_screens.theme_menu`
- public_defs (1): ThemeMenu
- package_imports (1):
  - line 2: from `MockUI.basic` import GenericMenu, BTC_ICONS, MenuItem
- direct_module_imports (0):
  - none
- findings (3):
  - Line 2: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 2: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 2: imports `MenuItem` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:MenuItem`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/main_screens/__init__.py`

- Module: `MockUI.main_screens`
- public_defs (0): (none)
- package_imports (0):
  - none
- direct_module_imports (2):
  - line 1: from `MockUI.main_menu` import MainMenu
  - line 2: from `MockUI.locked_menu` import LockedMenu
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/main_screens/locked_menu.py`

- Module: `MockUI.main_screens.locked_menu`
- public_defs (1): LockedMenu
- package_imports (1):
  - line 2: from `MockUI.basic` import TitledScreen, BTC_ICONS, PIN_BTN_WIDTH, PIN_BTN_HEIGHT, SCREEN_WIDTH, shuffle, Btn, flex_row, body_label, title_label, style_as_flex_container, apply_style
- direct_module_imports (0):
  - none
- findings (12):
  - Line 2: imports `TitledScreen` from package `MockUI.basic` (re-export from `MockUI.basic.templates.titled_screen:TitledScreen`); prefer direct module import internally.
  - Line 2: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 2: imports `PIN_BTN_WIDTH` from package `MockUI.basic` (re-export from `MockUI.basic.utils:PIN_BTN_WIDTH`); prefer direct module import internally.
  - Line 2: imports `PIN_BTN_HEIGHT` from package `MockUI.basic` (re-export from `MockUI.basic.utils:PIN_BTN_HEIGHT`); prefer direct module import internally.
  - Line 2: imports `SCREEN_WIDTH` from package `MockUI.basic` but name not exported there (likely fragile / runtime error risk).
  - Line 2: imports `shuffle` from package `MockUI.basic` (re-export from `MockUI.basic.utils:shuffle`); prefer direct module import internally.
  - Line 2: imports `Btn` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:Btn`); prefer direct module import internally.
  - Line 2: imports `flex_row` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:flex_row`); prefer direct module import internally.
  - Line 2: imports `body_label` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:body_label`); prefer direct module import internally.
  - Line 2: imports `title_label` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:title_label`); prefer direct module import internally.
  - Line 2: imports `style_as_flex_container` from package `MockUI.basic` (re-export from `MockUI.basic.utils:style_as_flex_container`); prefer direct module import internally.
  - Line 2: imports `apply_style` from package `MockUI.basic` (re-export from `MockUI.basic.theming:apply_style`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/main_screens/main_menu.py`

- Module: `MockUI.main_screens.main_menu`
- public_defs (1): MainMenu
- package_imports (1):
  - line 2: from `MockUI.basic` import GenericMenu, MenuItem, BTC_ICONS
- direct_module_imports (1):
  - line 3: from `MockUI.seed_screens.add_seed_menu` import make_add_seed_items
- findings (3):
  - Line 2: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 2: imports `MenuItem` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:MenuItem`); prefer direct module import internally.
  - Line 2: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/seed_screens/__init__.py`

- Module: `MockUI.seed_screens`
- public_defs (0): (none)
- package_imports (0):
  - none
- direct_module_imports (7):
  - line 1: from `MockUI.add_seed_menu` import AddSeedMenu
  - line 2: from `MockUI.seedphrase_menu` import SeedPhraseMenu
  - line 3: from `MockUI.store_seedphrase_menu` import StoreSeedphraseMenu
  - line 4: from `MockUI.clear_seedphrase_menu` import ClearSeedphraseMenu
  - line 5: from `MockUI.generate_seedphrase_menu` import GenerateSeedMenu
  - line 6: from `MockUI.passphrase_menu` import PassphraseMenu
  - line 7: from `MockUI.related_wallets_for_seed_menu` import RelatedWalletsForSeedMenu
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/seed_screens/add_seed_menu.py`

- Module: `MockUI.seed_screens.add_seed_menu`
- public_defs (2): AddSeedMenu, make_add_seed_items
- package_imports (1):
  - line 1: from `MockUI.basic` import GenericMenu, BTC_ICONS, MenuItem
- direct_module_imports (0):
  - none
- findings (3):
  - Line 1: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 1: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 1: imports `MenuItem` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:MenuItem`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/seed_screens/clear_seedphrase_menu.py`

- Module: `MockUI.seed_screens.clear_seedphrase_menu`
- public_defs (1): ClearSeedphraseMenu
- package_imports (1):
  - line 1: from `MockUI.basic` import GenericMenu, BTC_ICONS, MenuItem
- direct_module_imports (0):
  - none
- findings (3):
  - Line 1: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 1: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 1: imports `MenuItem` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:MenuItem`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/seed_screens/generate_seedphrase_menu.py`

- Module: `MockUI.seed_screens.generate_seedphrase_menu`
- public_defs (1): GenerateSeedMenu
- package_imports (2):
  - line 4: from `MockUI.basic` import TitledScreen, Btn, BTN_HEIGHT, BTN_WIDTH_PCT, Layout, flex_row, style_as_flex_container, form_label, form_textarea, body_label
  - line 12: from `MockUI.stubs` import Seed
- direct_module_imports (0):
  - none
- findings (11):
  - Line 4: imports `TitledScreen` from package `MockUI.basic` (re-export from `MockUI.basic.templates.titled_screen:TitledScreen`); prefer direct module import internally.
  - Line 4: imports `Btn` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:Btn`); prefer direct module import internally.
  - Line 4: imports `BTN_HEIGHT` from package `MockUI.basic` (re-export from `MockUI.basic.utils:BTN_HEIGHT`); prefer direct module import internally.
  - Line 4: imports `BTN_WIDTH_PCT` from package `MockUI.basic` but name not exported there (likely fragile / runtime error risk).
  - Line 4: imports `Layout` from package `MockUI.basic` (re-export from `MockUI.basic.utils:Layout`); prefer direct module import internally.
  - Line 4: imports `flex_row` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:flex_row`); prefer direct module import internally.
  - Line 4: imports `style_as_flex_container` from package `MockUI.basic` (re-export from `MockUI.basic.utils:style_as_flex_container`); prefer direct module import internally.
  - Line 4: imports `form_label` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:form_label`); prefer direct module import internally.
  - Line 4: imports `form_textarea` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:form_textarea`); prefer direct module import internally.
  - Line 4: imports `body_label` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:body_label`); prefer direct module import internally.
  - Line 12: imports `Seed` from package `MockUI.stubs` (re-export from `MockUI.stubs.seed:Seed`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/seed_screens/passphrase_menu.py`

- Module: `MockUI.seed_screens.passphrase_menu`
- public_defs (1): PassphraseMenu
- package_imports (1):
  - line 2: from `MockUI.basic` import TitledScreen, BTN_WIDTH, BTN_HEIGHT, SMALL_PAD, Layout, ACCEPTED_CHARS, Btn, BTC_ICONS, flex_row, flex_col, style_as_flex_container, form_label, form_textarea
- direct_module_imports (0):
  - none
- findings (13):
  - Line 2: imports `TitledScreen` from package `MockUI.basic` (re-export from `MockUI.basic.templates.titled_screen:TitledScreen`); prefer direct module import internally.
  - Line 2: imports `BTN_WIDTH` from package `MockUI.basic` (re-export from `MockUI.basic.utils:BTN_WIDTH`); prefer direct module import internally.
  - Line 2: imports `BTN_HEIGHT` from package `MockUI.basic` (re-export from `MockUI.basic.utils:BTN_HEIGHT`); prefer direct module import internally.
  - Line 2: imports `SMALL_PAD` from package `MockUI.basic` (re-export from `MockUI.basic.utils:SMALL_PAD`); prefer direct module import internally.
  - Line 2: imports `Layout` from package `MockUI.basic` (re-export from `MockUI.basic.utils:Layout`); prefer direct module import internally.
  - Line 2: imports `ACCEPTED_CHARS` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:ACCEPTED_CHARS`); prefer direct module import internally.
  - Line 2: imports `Btn` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:Btn`); prefer direct module import internally.
  - Line 2: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 2: imports `flex_row` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:flex_row`); prefer direct module import internally.
  - Line 2: imports `flex_col` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:flex_col`); prefer direct module import internally.
  - Line 2: imports `style_as_flex_container` from package `MockUI.basic` (re-export from `MockUI.basic.utils:style_as_flex_container`); prefer direct module import internally.
  - Line 2: imports `form_label` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:form_label`); prefer direct module import internally.
  - Line 2: imports `form_textarea` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:form_textarea`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/seed_screens/related_wallets_for_seed_menu.py`

- Module: `MockUI.seed_screens.related_wallets_for_seed_menu`
- public_defs (1): RelatedWalletsForSeedMenu
- package_imports (1):
  - line 2: from `MockUI.basic` import TitledScreen, delete_all_children_of, set_propagate_events, style_as_flex_container, BTC_ICONS, Btn, BTN_HEIGHT, BTN_WIDTH, SCREEN_WIDTH, section_header, WalletCard
- direct_module_imports (1):
  - line 12: from `MockUI.stubs.wallet` import WalletType, _wallet_type_rank
- findings (11):
  - Line 2: imports `TitledScreen` from package `MockUI.basic` (re-export from `MockUI.basic.templates.titled_screen:TitledScreen`); prefer direct module import internally.
  - Line 2: imports `delete_all_children_of` from package `MockUI.basic` (re-export from `MockUI.basic.utils:delete_all_children_of`); prefer direct module import internally.
  - Line 2: imports `set_propagate_events` from package `MockUI.basic` (re-export from `MockUI.basic.utils:set_propagate_events`); prefer direct module import internally.
  - Line 2: imports `style_as_flex_container` from package `MockUI.basic` (re-export from `MockUI.basic.utils:style_as_flex_container`); prefer direct module import internally.
  - Line 2: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 2: imports `Btn` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:Btn`); prefer direct module import internally.
  - Line 2: imports `BTN_HEIGHT` from package `MockUI.basic` (re-export from `MockUI.basic.utils:BTN_HEIGHT`); prefer direct module import internally.
  - Line 2: imports `BTN_WIDTH` from package `MockUI.basic` (re-export from `MockUI.basic.utils:BTN_WIDTH`); prefer direct module import internally.
  - Line 2: imports `SCREEN_WIDTH` from package `MockUI.basic` but name not exported there (likely fragile / runtime error risk).
  - Line 2: imports `section_header` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:section_header`); prefer direct module import internally.
  - Line 2: imports `WalletCard` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:WalletCard`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/seed_screens/seedphrase_menu.py`

- Module: `MockUI.seed_screens.seedphrase_menu`
- public_defs (1): SeedPhraseMenu
- package_imports (3):
  - line 1: from `MockUI.basic` import GenericMenu, BTC_ICONS, MenuItem
  - line 2: from `MockUI.basic.symbol_lib` import BTC_ICONS
  - line 4: from `MockUI.basic.widgets` import MenuItem
- direct_module_imports (1):
  - line 3: from `MockUI.basic.components.confirm_modals` import confirm_delete_seed, make_delete_active_handler
- findings (5):
  - Line 1: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 1: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 1: imports `MenuItem` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:MenuItem`); prefer direct module import internally.
  - Line 2: imports `BTC_ICONS` from package `MockUI.basic.symbol_lib` (re-export from `MockUI.basic.symbol_lib.btc_icons:BTC_ICONS`); prefer direct module import internally.
  - Line 4: imports `MenuItem` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.menu_item:MenuItem`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/seed_screens/store_seedphrase_menu.py`

- Module: `MockUI.seed_screens.store_seedphrase_menu`
- public_defs (1): StoreSeedphraseMenu
- package_imports (3):
  - line 1: from `MockUI.basic` import GenericMenu
  - line 2: from `MockUI.basic.symbol_lib` import BTC_ICONS
  - line 3: from `MockUI.basic.widgets` import MenuItem
- direct_module_imports (0):
  - none
- findings (3):
  - Line 1: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 2: imports `BTC_ICONS` from package `MockUI.basic.symbol_lib` (re-export from `MockUI.basic.symbol_lib.btc_icons:BTC_ICONS`); prefer direct module import internally.
  - Line 3: imports `MenuItem` from package `MockUI.basic.widgets` (re-export from `MockUI.basic.widgets.menu_item:MenuItem`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/stubs/__init__.py`

- Module: `MockUI.stubs`
- public_defs (0): (none)
- package_imports (0):
  - none
- direct_module_imports (3):
  - line 1: from `MockUI.device_state` import DeviceState
  - line 2: from `MockUI.wallet` import Wallet
  - line 3: from `MockUI.seed` import Seed
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/stubs/device_state.py`

- Module: `MockUI.stubs.device_state`
- public_defs (1): DeviceState
- package_imports (0):
  - none
- direct_module_imports (2):
  - line 8: from `MockUI.stubs.wallet` import Wallet
  - line 9: from `MockUI.stubs.seed` import Seed
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/stubs/seed.py`

- Module: `MockUI.stubs.seed`
- public_defs (1): Seed
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/stubs/wallet.py`

- Module: `MockUI.stubs.wallet`
- public_defs (2): Wallet, WalletType
- package_imports (0):
  - none
- direct_module_imports (0):
  - none
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/wallet_screens/__init__.py`

- Module: `MockUI.wallet_screens`
- public_defs (0): (none)
- package_imports (0):
  - none
- direct_module_imports (5):
  - line 1: from `MockUI.wallet_menu` import WalletMenu
  - line 2: from `MockUI.add_wallet_menu` import AddWalletMenu
  - line 3: from `MockUI.connect_wallets_menu` import ConnectWalletsMenu
  - line 4: from `MockUI.create_custom_wallet_menu` import CreateCustomWalletMenu
  - line 5: from `MockUI.view_signers_menu` import ViewSignersMenu
- findings (0):
  - none

### File `scenarios/MockUI/src/MockUI/wallet_screens/add_wallet_menu.py`

- Module: `MockUI.wallet_screens.add_wallet_menu`
- public_defs (1): AddWalletMenu
- package_imports (1):
  - line 1: from `MockUI.basic` import GenericMenu, BTC_ICONS, MenuItem
- direct_module_imports (0):
  - none
- findings (3):
  - Line 1: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 1: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 1: imports `MenuItem` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:MenuItem`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/wallet_screens/connect_wallets_menu.py`

- Module: `MockUI.wallet_screens.connect_wallets_menu`
- public_defs (1): ConnectWalletsMenu
- package_imports (1):
  - line 2: from `MockUI.basic` import GenericMenu, MenuItem
- direct_module_imports (0):
  - none
- findings (2):
  - Line 2: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 2: imports `MenuItem` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:MenuItem`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/wallet_screens/create_custom_wallet_menu.py`

- Module: `MockUI.wallet_screens.create_custom_wallet_menu`
- public_defs (1): CreateCustomWalletMenu
- package_imports (2):
  - line 4: from `MockUI.basic` import TitledScreen, Btn, BTN_HEIGHT, BTN_WIDTH, SWITCH_HEIGHT, SWITCH_WIDTH, SMALL_PAD, Layout, form_label, form_textarea, flex_row, style_as_flex_container
  - line 13: from `MockUI.stubs` import Wallet
- direct_module_imports (0):
  - none
- findings (13):
  - Line 4: imports `TitledScreen` from package `MockUI.basic` (re-export from `MockUI.basic.templates.titled_screen:TitledScreen`); prefer direct module import internally.
  - Line 4: imports `Btn` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:Btn`); prefer direct module import internally.
  - Line 4: imports `BTN_HEIGHT` from package `MockUI.basic` (re-export from `MockUI.basic.utils:BTN_HEIGHT`); prefer direct module import internally.
  - Line 4: imports `BTN_WIDTH` from package `MockUI.basic` (re-export from `MockUI.basic.utils:BTN_WIDTH`); prefer direct module import internally.
  - Line 4: imports `SWITCH_HEIGHT` from package `MockUI.basic` (re-export from `MockUI.basic.utils:SWITCH_HEIGHT`); prefer direct module import internally.
  - Line 4: imports `SWITCH_WIDTH` from package `MockUI.basic` (re-export from `MockUI.basic.utils:SWITCH_WIDTH`); prefer direct module import internally.
  - Line 4: imports `SMALL_PAD` from package `MockUI.basic` (re-export from `MockUI.basic.utils:SMALL_PAD`); prefer direct module import internally.
  - Line 4: imports `Layout` from package `MockUI.basic` (re-export from `MockUI.basic.utils:Layout`); prefer direct module import internally.
  - Line 4: imports `form_label` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:form_label`); prefer direct module import internally.
  - Line 4: imports `form_textarea` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:form_textarea`); prefer direct module import internally.
  - Line 4: imports `flex_row` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:flex_row`); prefer direct module import internally.
  - Line 4: imports `style_as_flex_container` from package `MockUI.basic` (re-export from `MockUI.basic.utils:style_as_flex_container`); prefer direct module import internally.
  - Line 13: imports `Wallet` from package `MockUI.stubs` (re-export from `MockUI.stubs.wallet:Wallet`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/wallet_screens/view_signers_menu.py`

- Module: `MockUI.wallet_screens.view_signers_menu`
- public_defs (1): ViewSignersMenu
- package_imports (2):
  - line 2: from `MockUI.basic` import GenericMenu, BTC_ICONS, MenuItem
  - line 3: from `MockUI.stubs` import Seed
- direct_module_imports (0):
  - none
- findings (4):
  - Line 2: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 2: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 2: imports `MenuItem` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:MenuItem`); prefer direct module import internally.
  - Line 3: imports `Seed` from package `MockUI.stubs` (re-export from `MockUI.stubs.seed:Seed`); prefer direct module import internally.

### File `scenarios/MockUI/src/MockUI/wallet_screens/wallet_menu.py`

- Module: `MockUI.wallet_screens.wallet_menu`
- public_defs (1): WalletMenu
- package_imports (1):
  - line 1: from `MockUI.basic` import GenericMenu, BTC_ICONS, MenuItem, confirm_delete_wallet, make_delete_active_handler
- direct_module_imports (0):
  - none
- findings (5):
  - Line 1: imports `GenericMenu` from package `MockUI.basic` (re-export from `MockUI.basic.templates.menu:GenericMenu`); prefer direct module import internally.
  - Line 1: imports `BTC_ICONS` from package `MockUI.basic` (re-export from `MockUI.basic.symbol_lib:BTC_ICONS`); prefer direct module import internally.
  - Line 1: imports `MenuItem` from package `MockUI.basic` (re-export from `MockUI.basic.widgets:MenuItem`); prefer direct module import internally.
  - Line 1: imports `confirm_delete_wallet` from package `MockUI.basic` (re-export from `MockUI.basic.components:confirm_delete_wallet`); prefer direct module import internally.
  - Line 1: imports `make_delete_active_handler` from package `MockUI.basic` (re-export from `MockUI.basic.components:make_delete_active_handler`); prefer direct module import internally.

## Consolidated Plan To Align With Thin-Init / Direct-Import Guidelines

### Phase 1 — Define API Surfaces
1. For each package, decide if it is:
   - internal-only (no broad package API), or
   - public façade (curated package API intended).
2. Keep `__init__.py` exports only for curated façade packages.
3. Record per-package API contracts in docstrings or `__all__`.

### Phase 2 — Normalize Imports
1. Convert internal imports that pull re-exported names from package roots to direct module imports.
2. Keep package-root imports only where the package is intentionally the public API.
3. Remove wildcard imports from package roots.

### Phase 3 — Thin `__init__.py` Files
1. Remove side-effect imports and heavy graph stitching in package `__init__.py`.
2. Keep only metadata + curated re-exports + `__all__`.
3. For compatibility, provide temporary aliases with deprecation comments and expiry milestone.

### Phase 4 — Iterative Consistency Loop (Repeat Until Stable)
1. Run static scan again (same checks as this report).
2. Run runtime smoke path (`make ... simulate` and relevant tests).
3. Fix newly exposed missing exports/import paths.
4. Repeat until:
   - no missing exports in intended façade packages,
   - no unintended package-root import findings for internal modules,
   - runtime import graph is cycle-free on startup path.

### Phase 5 — Guardrails
1. Add lint/check script enforcing:
   - disallow package-root imports in internal modules (except approved list),
   - disallow wildcard imports,
   - assert `__init__.py` export lists match curated API spec.
2. Run this check in CI.

## Immediate High-Priority Candidates (From Current Findings)

- `MockUI.basic.utils`: missing_exports=7, possibly_non_api_exports=15, externally_used=46
- `MockUI.basic`: missing_exports=2, possibly_non_api_exports=15, externally_used=33
- `MockUI.basic.widgets`: missing_exports=0, possibly_non_api_exports=12, externally_used=18
- `MockUI.basic.theming`: missing_exports=0, possibly_non_api_exports=8, externally_used=7
- `MockUI.basic.components`: missing_exports=0, possibly_non_api_exports=7, externally_used=2
- `MockUI`: missing_exports=0, possibly_non_api_exports=5, externally_used=0
- `MockUI.basic.templates`: missing_exports=0, possibly_non_api_exports=4, externally_used=0
- `MockUI.basic.fonts`: missing_exports=0, possibly_non_api_exports=4, externally_used=0
- `MockUI.basic.tour`: missing_exports=0, possibly_non_api_exports=1, externally_used=2
- `MockUI.wallet_screens`: missing_exports=0, possibly_non_api_exports=0, externally_used=5
