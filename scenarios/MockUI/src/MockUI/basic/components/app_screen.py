"""AppScreen — composite container that holds context_bar, battery and content.

One AppScreen is always active in SpecterGui.  It owns:

  - context_bar  (optional ContextBar, top 7.5%, SEED/WALLET contexts only)
  - battery      (optional Battery, top-right corner, overlaps context_bar row)
  - content      (flex-col, fills remaining height below context_bar)
"""

import lvgl as lv

from .context_bar import ContextBar
from ..utils import (
    SCREEN_WIDTH, CONTENT_H, TITLE_HEIGHT, BATTERY_WIDTH,
    set_pos, set_scroll, set_align,
    style_as_screen_backdrop,
)
from ..templates.specter_gui_base import SpecterGuiElement
from ..widgets import flex_col, Battery
from ..ui_state import Context


class AppScreen(SpecterGuiElement):
    """Self-contained screen unit: content + optional context_bar + battery."""

    def __init__(self, gui):
        super().__init__(gui)
        style_as_screen_backdrop(self, width=SCREEN_WIDTH, height=CONTENT_H, x=0, y=0)

        ctx = gui.ui_state.active_context
        needs_bar = (
            (ctx == Context.SEED and gui.ui_state.active_seed is not None)
            or (ctx == Context.WALLET and gui.ui_state.active_wallet is not None)
        )

        content_y = TITLE_HEIGHT if needs_bar else 0
        content_h = CONTENT_H - content_y
        context_bar_width = SCREEN_WIDTH - BATTERY_WIDTH

        # ── 1. Content (painted first = behind everything) ────────────────────
        self.content = flex_col(self, width=lv.pct(100), height=content_h)
        set_pos(self.content, x=0, y=content_y)
        set_scroll(self.content, horizontal=False, vertical=False)

        # ── 2. Context bar (painted over content top area) ────────────────────
        if needs_bar:
            self.context_bar = ContextBar(self, width=context_bar_width, height=TITLE_HEIGHT)
        else:
            self.context_bar = None

        # ── 3. Battery (painted last = always on top) ─────────────────────────
        if gui.device_state.has_battery:
            self.battery = Battery(self, width=BATTERY_WIDTH, height=TITLE_HEIGHT)
            set_align(self.battery, lv.ALIGN.TOP_RIGHT)
            set_pos(self.battery, x=0, y=0)
            self.battery.update(gui.device_state.battery_pct, gui.device_state.is_charging)
        else:
            self.battery = None

        # Set by SpecterGui after _build_view; updated on each view swap.
        self.view = None

    def refresh(self):
        """Refresh all owned sub-widgets (view, context bar, battery)."""
        if self.view:
            self.view.refresh()
        self.refresh_context_bar()
        self.refresh_battery()

    def refresh_battery(self):
        """Update battery widget from current device_state."""
        if self.battery:
            self.battery.update(self.gui.device_state.battery_pct, self.gui.device_state.is_charging)

    def refresh_context_bar(self):
        """Refresh context bar content (e.g. after seed/wallet rename)."""
        if self.context_bar:
            self.context_bar.refresh()
