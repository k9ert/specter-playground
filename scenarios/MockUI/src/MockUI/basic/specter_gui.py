import lvgl as lv

from .ui_consts import CONTENT_PCT, SCREEN_HEIGHT, TITLE_ROW_HEIGHT, BATTERY_OFFSET_X
from ..stubs import UIState, SpecterState
from ..stubs.battery import Battery
from ..stubs.ui_state import Context
from ..i18n import I18nManager
from ..tour import GuidedTour
from .keyboard_manager import KeyboardManager
from .animations import create_anims_for_transition
from .context_bar import ContextBar

from .navigation_bar import NavigationBar
from .widgets.containers import flex_col

# Pixel heights computed from percentages so we can shift content down
# when the context bar is active.
_CONTENT_H = SCREEN_HEIGHT * CONTENT_PCT // 100  # 736 px
_BATT_Y = (TITLE_ROW_HEIGHT - 20) // 2           # centre 20px battery in title row
from .action_screen import ActionScreen
from .main_menu import MainMenu
from .locked_menu import LockedMenu
from ..wallet import (
    WalletMenu,
    ConnectWalletsMenu,
    AddWalletMenu,
    CreateCustomWalletMenu,
    ViewSignersScreen,
)
from ..seed import (
    AddSeedMenu,
    SeedPhraseMenu,
    StoreSeedphraseMenu,
    ClearSeedphraseMenu,
    GenerateSeedMenu,
    PassphraseMenu,
    RelatedWalletsForSeedMenu,
)
from ..device import (
    SecuritySettingsMenu,
    BackupsMenu,
    FirmwareMenu,
    InterfacesMenu,
    StorageMenu,
    SecurityFeaturesMenu,
    LanguageMenu,
    SettingsMenu,
    PreferencesMenu,
)


class SpecterGui(lv.obj):
    # Static tour step definitions: (element_spec, i18n_key, position)
    # element_spec is None, a dotted attribute-path string, or a (x, y, w, h) tuple.
    # Resolved to runtime objects by GuidedTour.resolve_steps() before use.
    INTRO_TOUR_STEPS = [
        (None,                          "TOUR_INTRO",       "center"),
        ("navigation_bar",              "TOUR_WALLET_BAR",  "above"),
        ((435, 143, 28, 28),            "TOUR_HELP_ICON",   "left"),
    ]

    def __init__(self, specter_state=None, ui_state=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_scroll_dir(lv.DIR.NONE)

        self.on_navigate = self.show_menu
        
        # Initialize i18n manager
        self.i18n = I18nManager()

        if specter_state:
            self.device_state = specter_state
        else:
            self.device_state = SpecterState()

        if ui_state:
            self.ui_state = ui_state
        else:
            self.ui_state = UIState()

        self.current_screen = None
        self.keyboard_manager = KeyboardManager(self)
        self._animating = False   # True while a slide animation is running
        self._anim_refs = None    # holds Python callbacks + anim objects alive

        # Navigation bar at bottom
        self.navigation_bar = NavigationBar(self)
        self.navigation_bar.align(lv.ALIGN.BOTTOM_MID, 0, 0)

        # Context bar — created/destroyed by _sync_context_bar(); never animates
        self.context_bar = None

        # Battery — persistent child of SpecterGui, always at top-right
        if self.device_state.has_battery:
            self._battery = Battery(self)
            self._battery.VALUE = self.device_state.battery_pct
            self._battery.update()
            self._battery.align(lv.ALIGN.TOP_RIGHT, BATTERY_OFFSET_X, _BATT_Y)
        else:
            self._battery = None

        # Content area: pixel-sized so we can shift it when context bar appears
        self.content = flex_col(self, width=lv.pct(100), height=_CONTENT_H)
        self.content.set_style_radius(0, 0)
        self.content.align(lv.ALIGN.TOP_MID, 0, 0)
        self.content.set_scroll_dir(lv.DIR.NONE)

        # initially show the current menu of ui_state (i.e. "main" by default unless loaded differently)
        self.show_menu(self.ui_state.current_menu_id)
        
        # Start guided tour on first startup (after UI is fully constructed)
        if self.ui_state.is_run_tour_on_startup:
            GuidedTour(self, GuidedTour.resolve_steps(self.INTRO_TOUR_STEPS, self)).start()

        # periodic refresh every 30 seconds [e.g. to update battery level]
        def _tick(timer):
            self.refresh_ui()
        lv.timer_create(_tick, 30_000, None)

    def change_language(self, lang_code):
        """
        Change the active language.
        
        Args:
            lang_code: ISO 639-1 language code (e.g., 'en', 'de')
        """
        # Switch language in i18n manager
        self.i18n.set_language(lang_code)

    def refresh_ui(self):
        """Centralized refresh method for all UI components."""
        self.current_screen.refresh()
        self.navigation_bar.refresh()
        if self.context_bar:
            self.context_bar.refresh()
        if self._battery:
            self._battery.VALUE = self.device_state.battery_pct
            self._battery.update()

    def show_menu(self, target_menu_id=None):
        # Drop all input while animating
        if self._animating:
            return

        going_back = target_menu_id in [None, "back"]
        if target_menu_id == "locked":
            self.device_state.lock()

        # Update UIState navigation history
        if going_back:
            anim = self.ui_state.pop_menu()
        elif target_menu_id in ["start_intro_tour", "main"]:
            anim = self.ui_state.clear_history()
            self.ui_state.current_menu_id = target_menu_id
        else:
            anim = self.ui_state.push_menu(target_menu_id)

        curr_menu = self.ui_state.current_menu_id

        if anim is not None and self.ui_state.are_animations_enabled:
            self._do_transition(anim)
        else:
            if self.current_screen:
                self.current_screen.delete()
                self.current_screen = None
            self._sync_context_bar()
            self._build_screen(curr_menu)
            self.refresh_ui()

        if self.ui_state.current_menu_id == "start_intro_tour":
            self.ui_state.current_menu_id = "main"
            GuidedTour(self, GuidedTour.resolve_steps(self.INTRO_TOUR_STEPS, self)).start()

    def _build_screen(self, current=None):
        """Instantiate the correct screen class for *current* menu_id."""
        if current is None:
            current = self.ui_state.current_menu_id

        # If the device is locked, always show the locked screen
        if self.device_state.is_locked:
            self.ui_state.clear_history()
            self.ui_state.current_menu_id = "locked"
            self.current_screen = LockedMenu(self)
            return

        if current in ("main", "start_intro_tour"):
            self.current_screen = MainMenu(self)
        elif current == "manage_wallet":
            self.current_screen = WalletMenu(self)
        elif current == "view_signers":
            self.current_screen = ViewSignersScreen(self)
        elif current == "manage_security_settings":
            self.current_screen = SecuritySettingsMenu(self)
        elif current == "manage_backups":
            self.current_screen = BackupsMenu(self)
        elif current == "manage_firmware":
            self.current_screen = FirmwareMenu(self)
        elif current == "connect_sw_wallet":
            self.current_screen = ConnectWalletsMenu(self)
        elif current == "add_seed":
            self.current_screen = AddSeedMenu(self)
        elif current == "add_wallet":
            self.current_screen = AddWalletMenu(self)
        elif current == "manage_security_features":
            self.current_screen = SecurityFeaturesMenu(self)
        elif current == "interfaces":
            self.current_screen = InterfacesMenu(self)
        elif current == "manage_seedphrase":
            self.current_screen = SeedPhraseMenu(self)
        elif current == "related_wallets_for_seed":
            self.current_screen = RelatedWalletsForSeedMenu(self)
        elif current == "store_seedphrase":
            self.current_screen = StoreSeedphraseMenu(self)
        elif current == "clear_seedphrase":
            self.current_screen = ClearSeedphraseMenu(self)
        elif current == "generate_seedphrase":
            self.current_screen = GenerateSeedMenu(self)
        elif current == "set_passphrase":
            self.current_screen = PassphraseMenu(self)
        elif current == "create_custom_wallet":
            self.current_screen = CreateCustomWalletMenu(self)
        elif current == "manage_storage":
            self.current_screen = StorageMenu(self)
        elif current == "select_language":
            self.current_screen = LanguageMenu(self)
        elif current == "manage_preferences":
            self.current_screen = PreferencesMenu(self)
        elif current == "manage_settings":
            self.current_screen = SettingsMenu(self)
        else:
            self.current_screen = ActionScreen(current, self)

    def _sync_context_bar(self):
        """Create or destroy the GUI-level context bar and adjust content geometry.

        Called before building a new screen (both animated and non-animated).
        The context bar never participates in animations; it stays fixed at y=0.
        """
        ctx = self.ui_state.active_context
        needs_bar = (
            (ctx == Context.SEED and self.ui_state.active_seed is not None)
            or (ctx == Context.WALLET and self.ui_state.active_wallet is not None)
        )

        if needs_bar and self.context_bar is None:
            self.context_bar = ContextBar(self)
            # Raise context bar above content so it is never obscured during
            # the slide animation (content children slide underneath it).
            self.context_bar.move_foreground()
            # Push battery in front of context bar too
            if self._battery:
                self._battery.move_foreground()
            # Shift content down to leave room for context bar
            self.content.set_height(_CONTENT_H - TITLE_ROW_HEIGHT)
            self.content.align(lv.ALIGN.TOP_MID, 0, TITLE_ROW_HEIGHT)

        elif not needs_bar and self.context_bar is not None:
            self.context_bar.delete()
            self.context_bar = None
            # Restore full content area
            self.content.set_height(_CONTENT_H)
            self.content.align(lv.ALIGN.TOP_MID, 0, 0)

    def _do_transition(self, anim_type):
        """Animate from the current screen to a freshly-built new screen."""
        self._animating = True

        # Sync context bar first so content geometry is correct before the
        # new screen is built and before the animation starts.
        self._sync_context_bar()

        # Switch content to absolute layout so we can position screens manually
        self.content.set_layout(lv.LAYOUT.NONE)

        old_screen = self.current_screen
        self.current_screen = None
        # Build the incoming screen (parented into self.content)
        self._build_screen()
        new_screen = self.current_screen

        def _on_done(anim):
            self._animating = False
            self._anim_refs = None
            self.content.set_layout(lv.LAYOUT.FLEX)
            self.content.set_flex_flow(lv.FLEX_FLOW.COLUMN)

            old_screen.delete()
            self.refresh_ui()

        self._anim_refs = create_anims_for_transition(old_screen, new_screen, anim_type, on_done_cb=_on_done)
        for a in self._anim_refs:
            a.start()
