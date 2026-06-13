import lvgl as lv

from .utils import (
    SCREEN_WIDTH, CONTENT_H, ANIM_MS_HORIZONTAL, ANIM_MS_VERTICAL, GUI_REFRESH_MS,
    KeyboardManager,
    slide_x, slide_y, GUIAnimations,
    set_scroll, get_size, set_size, set_pos
)
from .ui_state import UIState, Context
from .i18n import I18nManager
from .theming import ThemeManager
from .tour import GuidedTour, INTRO_TOUR_STEPS
from .components import NavigationBar, AppScreen
from .templates.action_screen import ActionScreen
from .templates.specter_gui_base import bind_gui

from ..main_screens import (
    MainMenu,
    LockedMenu,
)
from ..wallet_screens import (
    WalletMenu,
    ConnectWalletsMenu,
    AddWalletMenu,
    CreateCustomWalletMenu,
    ViewSignersMenu,
)
from ..seed_screens import (
    AddSeedMenu,
    SeedPhraseMenu,
    StoreSeedphraseMenu,
    ClearSeedphraseMenu,
    GenerateSeedMenu,
    PassphraseMenu,
    RelatedWalletsForSeedMenu,
)
from ..device_screens import (
    SecuritySettingsMenu,
    BackupsMenu,
    FirmwareMenu,
    InterfacesMenu,
    StorageMenu,
    SecurityFeaturesMenu,
    LanguageMenu,
    SettingsMenu,
    PreferencesMenu,
    ThemeMenu,
)

from ..stubs import DeviceState

_VIEW_MAP = {
    "locked":                   LockedMenu,
    "main":                     MainMenu,
    "start_intro_tour":         MainMenu,
    "manage_wallet":            WalletMenu,
    "view_signers":             ViewSignersMenu,
    "manage_security_settings": SecuritySettingsMenu,
    "manage_backups":           BackupsMenu,
    "manage_firmware":          FirmwareMenu,
    "connect_sw_wallet":        ConnectWalletsMenu,
    "add_seed":                 AddSeedMenu,
    "add_wallet":               AddWalletMenu,
    "manage_security_features": SecurityFeaturesMenu,
    "interfaces":               InterfacesMenu,
    "manage_seedphrase":        SeedPhraseMenu,
    "related_wallets_for_seed": RelatedWalletsForSeedMenu,
    "store_seedphrase":         StoreSeedphraseMenu,
    "clear_seedphrase":         ClearSeedphraseMenu,
    "generate_seedphrase":      GenerateSeedMenu,
    "set_passphrase":           PassphraseMenu,
    "create_custom_wallet":     CreateCustomWalletMenu,
    "manage_storage":           StorageMenu,
    "select_language":          LanguageMenu,
    "select_theme":             ThemeMenu,
    "manage_preferences":       PreferencesMenu,
    "manage_settings":          SettingsMenu,
}


class SpecterGui(lv.obj):

    def __init__(self, specter_state=None, ui_state=None, *args, **kwargs):
        lv.display_get_default().set_theme(None)
        #register the global GUI instance before calling super().__init__ 
        # so that any early calls to get_gui() (e.g. from widget constructors) succeed
        bind_gui(self)
        super().__init__(*args, **kwargs)
        set_scroll(self, horizontal=False, vertical=False)

        self.on_navigate = self.navigate_to

        # Initialize i18n manager
        self.i18n = I18nManager()

        # Initialize theme manager — singleton already warmed up at boot
        self.theme = ThemeManager.get_instance()

        if specter_state:
            self.device_state = specter_state
        else:
            self.device_state = DeviceState()

        if ui_state:
            self.ui_state = ui_state
        else:
            self.ui_state = UIState()

        self.keyboard_manager = KeyboardManager(self)
        self._animating = False   # True while a slide animation is running
        self._anim_refs = None    # holds Python callbacks + anim objects alive

        # Active AppScreen (screen.view holds the active TitledScreen widget)
        self.screen = None

        # Navigation bar at bottom — always present, owned by SpecterGui
        self.navigation_bar = NavigationBar(self)
        self.navigation_bar.align(lv.ALIGN.BOTTOM_MID, 0, 0)

        self.navigate_to(self.ui_state.current_menu_id)

        # Periodic refresh (e.g. to update battery level)
        def _tick(timer):
            self.device_state.debug_cycle_battery()
            self.refresh_ui()
        lv.timer_create(_tick, GUI_REFRESH_MS, None)
        

    def change_language(self, lang_code):
        """Change the active language and rebuild the current screen."""
        self.i18n.set_language(lang_code)
        self.refresh_ui()

    def change_theme(self, theme_name, mode=None):
        """Change the active theme (and optionally mode) and rebuild the current screen."""
        self.theme.set_theme(theme_name, mode)
        self.refresh_ui()

    def change_mode(self, mode):
        """Toggle dark/light mode and rebuild the current screen."""
        self.theme.set_mode(mode)
        self.refresh_ui()

    def refresh_ui(self):
        """Centralized refresh method for all UI components."""
        if self.screen:
            self.screen.refresh()
        if self.navigation_bar:
            self.navigation_bar.refresh()

    def navigate_to(self, target_menu_id=None, target_seed="unset", target_wallet="unset"):
        # Drop all input while animating
        if self._animating:
            return
        
        if target_menu_id == "main" and self.ui_state.is_run_tour_on_startup:
            target_menu_id = "start_intro_tour"

        if target_menu_id == "locked":
            self.device_state.lock()
        if self.device_state.is_locked:
            target_menu_id = "locked"

        going_back = target_menu_id in [None, "back"]

        # Update UIState navigation history
        if target_menu_id in ["start_intro_tour", "main", "locked"]:
            anim = self.ui_state.clear_history()
            self.ui_state.current_menu_id = target_menu_id
        elif going_back:
            anim = self.ui_state.pop_menu()
        else:
            anim = self.ui_state.push_menu(target_menu_id)

        if target_seed != "unset":
            self.ui_state.set_active_seed(target_seed)
        if target_wallet != "unset":
            self.ui_state.set_active_wallet(target_wallet)

        if anim is not None and self.ui_state.are_animations_enabled:
            self._do_transition(anim)
        else:
            if self.screen:
                self.screen.delete()
            self.screen = self._make_screen()
            self.refresh_ui()

        if self.ui_state.current_menu_id == "start_intro_tour":
            self.ui_state.current_menu_id = "main"
            GuidedTour(self, GuidedTour.resolve_steps(INTRO_TOUR_STEPS, self)).start()

    def _make_screen(self):
        """Create a new AppScreen for the current ui_state and populate it with a view.

        Returns the new AppScreen.  Does NOT delete any old screen.
        """
        screen = AppScreen(self)
        screen.view = self._build_view(screen, self.ui_state.current_menu_id)
        return screen

    def _build_view(self, screen, menu_id):
        """Instantiate and return the correct view class for *menu_id* into *screen*."""
        class_name = _VIEW_MAP.get(menu_id)
        if class_name is not None:
            return class_name(screen.content)
        return ActionScreen(menu_id, screen.content)

    def _do_transition(self, anim_type):
        """Animate from the current screen to a freshly-built new screen.

        Dispatches to one of two cases:
          • Case 3 (within SEED/WALLET context, context bar stays): animate
            only the view widget horizontally inside ``screen.content``.
          • Cases 1/2 (between contexts, or context without bar): animate the
            entire Screen unit (bar + battery + content move together).
        """
        self._animating = True

        ctx = self.ui_state.active_context  # already updated by navigate_to
        ctx_has_bar = self.screen.context_bar is not None
        is_horizontal = anim_type in (
            GUIAnimations.horizontal_slide_in,
            GUIAnimations.horizontal_slide_out,
            GUIAnimations.horizontal_push_in,
            GUIAnimations.horizontal_push_out,
        )
        within_ctx_with_bar = (
            ctx_has_bar
            and is_horizontal
            and (ctx == Context.SEED or ctx == Context.WALLET)
        )

        if within_ctx_with_bar:
            self._transition_within_context(anim_type)
        else:
            self._transition_full_screen(anim_type)

    def _transition_within_context(self, anim_type):
        """Case 3: slide only the view widget inside the existing screen.content."""
        old_screen = self.screen
        old_view = old_screen.view
        content = old_screen.content
        (content_w, content_h) = get_size(content)
        content.set_layout(lv.LAYOUT.NONE)
        set_pos(old_view, 0, 0)
        set_size(old_view, SCREEN_WIDTH, content_h)

        # Build new view into the same screen (added to content as 2nd child)
        new_view = self._build_view(old_screen, self.ui_state.current_menu_id)
        old_screen.view = new_view
        set_size(new_view, SCREEN_WIDTH, content_h)

        anims = []
        W = SCREEN_WIDTH

        def _cleanup_case3():
            self._animating = False
            self._anim_refs = None
            old_view.delete()
            content.set_layout(lv.LAYOUT.FLEX)
            content.set_flex_flow(lv.FLEX_FLOW.COLUMN)
            self.refresh_ui()

        if anim_type == GUIAnimations.horizontal_slide_in:
            new_view.set_x(W)
            anims.append(slide_x(new_view, W, 0, ANIM_MS_HORIZONTAL,
                                on_done_cb=lambda a: _cleanup_case3()))
        elif anim_type == GUIAnimations.horizontal_slide_out:
            new_view.set_x(0)
            old_view.move_foreground()
            anims.append(slide_x(old_view, 0, W, ANIM_MS_HORIZONTAL,
                                on_done_cb=lambda a: _cleanup_case3()))

        for a in anims:
            a.start()
        self._anim_refs = anims

    def _transition_full_screen(self, anim_type):
        """Cases 1/2: slide the entire Screen unit (bar + content) via a clip container."""
        old_screen = self.screen
        new_screen = self._make_screen()
        self.screen = new_screen

        # temporary clip container: same size as the content zone
        # (480×_CONTENT_H).
        # Both screens are reparented into it so LVGL's default parent-clip
        # prevents them from ever painting over the navigation bar below.
        
        
        anim_clip = lv.obj(self)
        set_size(anim_clip, SCREEN_WIDTH, CONTENT_H)
        set_pos(anim_clip, 0, 0)
        set_scroll(anim_clip, horizontal=False, vertical=False)
        anim_clip.set_layout(lv.LAYOUT.NONE)

        # Reparent both screens; their coords were (0,0) relative to
        # SpecterGui which is identical to (0,0) inside anim_clip.
        old_screen.set_parent(anim_clip)
        set_pos(old_screen, 0, 0)
        new_screen.set_parent(anim_clip)
        set_pos(new_screen, 0, 0)

        # Navigation bar must remain above the clip container.
        self.navigation_bar.move_foreground()

        def _cleanup_whole():
            self._animating = False
            self._anim_refs = None
            # Reparent new_screen back to SpecterGui before deleting the
            # clip (which would otherwise take new_screen with it).
            new_screen.set_parent(self)
            set_pos(new_screen, 0, 0)
            anim_clip.delete()   # also deletes old_screen
            self.navigation_bar.move_foreground()
            self.refresh_ui()

        anims = []
        W = SCREEN_WIDTH

        if anim_type == GUIAnimations.horizontal_slide_in:
            anims.append(slide_x(new_screen, W, 0, ANIM_MS_HORIZONTAL,
                                on_done_cb=lambda a: _cleanup_whole()))
        elif anim_type == GUIAnimations.horizontal_slide_out:
            old_screen.move_foreground()   # old on top within anim_clip
            anims.append(slide_x(old_screen, 0, W, ANIM_MS_HORIZONTAL,
                                on_done_cb=lambda a: _cleanup_whole()))
        elif anim_type == GUIAnimations.horizontal_push_in:
            anims.append(slide_x(new_screen, W, 0, ANIM_MS_HORIZONTAL))
            anims.append(slide_x(old_screen, 0, -W, ANIM_MS_HORIZONTAL,
                                on_done_cb=lambda a: _cleanup_whole()))
        elif anim_type == GUIAnimations.horizontal_push_out:
            anims.append(slide_x(new_screen, -W, 0, ANIM_MS_HORIZONTAL))
            anims.append(slide_x(old_screen, 0, W, ANIM_MS_HORIZONTAL,
                                on_done_cb=lambda a: _cleanup_whole()))
        elif anim_type == GUIAnimations.vertical_slide_in:
            anims.append(slide_y(new_screen, _CONTENT_H, 0, ANIM_MS_VERTICAL,
                                on_done_cb=lambda a: _cleanup_whole()))
        elif anim_type == GUIAnimations.vertical_slide_out:
            old_screen.move_foreground()   # old on top within anim_clip
            anims.append(slide_y(old_screen, 0, _CONTENT_H, ANIM_MS_VERTICAL,
                                on_done_cb=lambda a: _cleanup_whole()))

        for a in anims:
            a.start()
        self._anim_refs = anims