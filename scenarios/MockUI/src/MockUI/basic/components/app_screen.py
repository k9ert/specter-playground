"""AppScreen — composite container that holds context_bar, battery and content.

One AppScreen is always active in SpecterGui.  It owns:

  - context_bar  (optional ContextBar, top row, only in SEED/WALLET contexts)
  - content      (plain lv.obj, grows to fill remaining height)
  - battery      (optional Battery, FLOATING overlay, only when has_battery)

The active view widget is a child of ``content``, created via ``_create_view()``
and swapped in-place for animated transitions via ``set_view_class()``.
"""

import lvgl as lv

from .context_bar import ContextBar
from ..templates.action_screen import ActionScreen
from ..utils import (
    set_pos, set_size, get_size, set_scroll,
    set_layout, set_flex_flow
)
from ..templates.specter_gui_base import SpecterGuiElement
from ..theming import apply_style
from ..widgets import Battery
from ..ui_state import Context


class AppScreen(SpecterGuiElement):
    """Self-contained screen unit: context_bar (optional) + content + battery (optional)."""

    # setup_self always builds _SUBELEMENTS from scratch based on runtime conditions.
    _SUBELEMENTS = []

    def setup_self(self):
        apply_style(self, "CONTAINER.APP_SCREEN")
        set_scroll(self, horizontal=False, vertical=False)  # not a style property

        # Defaults for optional slots.
        self.context_bar = None
        self.battery = None
        self.view = None

        needs_bar = (
            (self.context == Context.SEED and self.active_seed is not None)
            or (self.context == Context.WALLET and self.active_wallet is not None)
        )

        # Build a fresh ordered list in flex-column order.
        # Battery will be set to FLOATING so its position doesn't affect layout.
        slots = []
        if needs_bar:
            slots.append(("context_bar", ContextBar))
        slots.append(("content", SpecterGuiElement))
        if self.device_state.has_battery:
            slots.append(("battery", Battery))
        self._SUBELEMENTS = slots

    def post_init(self):
        # FLAG.FLOATING must be set before any layout pass so the battery is
        # excluded from flex space distribution.
        if self.battery:
            self.battery.add_flag(lv.obj.FLAG.FLOATING)

        # Style the plain SpecterGuiElement content slot created by _init_grid.
        apply_style(self.content, "CONTAINER.CONTENT")
        set_scroll(self.content, horizontal=False, vertical=False)  # not a style property

        # Create the initial view before the single layout pass below.
        self._create_view()

        # Resolve parent-size and flex styles before reading live dimensions.
        self.update_layout()

        self._update_context_bar_size()

    def _update_context_bar_size(self):
        """Set ContextBar width from the resolved screen and battery widths."""
        if self.context_bar:
            screen_w, _ = get_size(self)
            if self.battery:
                battery_w, _ = get_size(self.battery)
                set_size(self.context_bar, width=max(0, screen_w - battery_w))
            else:
                set_size(self.context_bar, width=screen_w)

    # ── View management ──────────────────────────────────────────────────────

    def _create_view(self):
        """Create the view widget for the current menu, parented to ``self.content``."""
        view_class = self.ui_state.view_class
        if view_class is not None:
            self.view = view_class(self.content)
        else:
            self.view = ActionScreen(self.current_menu, self.content)

    def set_view_class(self, view_class):
        """Swap the view in-place for animated transitions (no full screen rebuild).

        Deletes the current view widget and creates a new one from *view_class*.
        Also keeps ``ui_state.view_class`` in sync.
        """
        if self.view is not None:
            self.view.delete()
        self.ui_state.view_class = view_class
        self._create_view()

    def begin_view_transition(self, view_class):
        """Prepare old and new views for a temporary absolute-positioned slide.

        Returns ``(old_view, new_view, width, height)`` or ``None`` when a
        view cannot be created.  On failure, this method restores the existing
        view and normal content layout before returning.
        """
        if self.view is None:
            return None
        
        width, height = get_size(self.content)
        set_layout(self.content, lv.LAYOUT.NONE)

        old_view = self.view
        set_pos(old_view, 0, 0)
        set_size(old_view, width, height)
        self.view = None

        self.set_view_class(view_class)
        if self.view is None:
            self.view = old_view
            self._restore_view_layout()
            return None

        new_view = self.view
        set_pos(new_view, 0, 0)
        set_size(new_view, width, height)

        return old_view, new_view, width, height

    def finish_view_transition(self, old_view):
        """Delete the previous view and restore normal content layout."""
        if old_view is not None:
            old_view.delete()
        self._restore_view_layout()

    def _restore_view_layout(self):
        """Restore the normal flex-column ownership of the content viewport."""
        set_layout(self.content, lv.LAYOUT.FLEX)
        set_flex_flow(self.content, lv.FLEX_FLOW.COLUMN)
        self.content.update_layout()

    # ── Refresh helpers ──────────────────────────────────────────────────────

    def refresh(self):
        """Refresh all owned sub-widgets (view, context bar, battery)."""
        self.refresh_context_bar()
        self.refresh_battery()
        if self.view:
            self.view.refresh()        

    def refresh_battery(self):
        """Update battery widget from current device_state."""
        if self.battery:
            self.battery.update(self.device_state.battery_pct, self.device_state.is_charging)

    def refresh_context_bar(self):
        """Refresh context bar content (e.g. after seed/wallet rename)."""
        self._update_context_bar_size()
        if self.context_bar:
            self.context_bar.refresh()
