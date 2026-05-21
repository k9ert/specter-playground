"""AppScreen — composite container that holds context_bar, battery and content.

One AppScreen is always active in SpecterGui.  It owns:

  - context_bar  (optional ContextBar, top 60 px, SEED/WALLET contexts only)
  - battery      (optional Battery, top-right corner, overlaps context_bar row)
  - content      (flex-col, fills remaining height below context_bar)
"""

import lvgl as lv

from .ui_consts import (
    SCREEN_WIDTH, SCREEN_HEIGHT, CONTENT_PCT, TITLE_ROW_HEIGHT, BATTERY_WIDTH,
)
from .specter_gui_base import SpecterGuiElement
from .ui_utils import configure_as_bare
from .widgets.containers import flex_col
from .widgets.battery import Battery
from .context_bar import ContextBar
from ..stubs.ui_state import Context

_CONTENT_H = SCREEN_HEIGHT * CONTENT_PCT // 100
CONTEXT_BAR_WIDTH = SCREEN_WIDTH - BATTERY_WIDTH


class AppScreen(SpecterGuiElement):
    """Self-contained screen unit: content + optional context_bar + battery."""

    def __init__(self, gui):
        super().__init__(gui)   # LVGL parent = SpecterGui
        self.gui = gui

        configure_as_bare(self, width=SCREEN_WIDTH, height=_CONTENT_H, transparent_bg=False)
        self.set_pos(0, 0)
        self.set_layout(lv.LAYOUT.NONE)
        self.set_scroll_dir(lv.DIR.NONE)

        ctx = gui.ui_state.active_context
        needs_bar = (
            (ctx == Context.SEED and gui.ui_state.active_seed is not None)
            or (ctx == Context.WALLET and gui.ui_state.active_wallet is not None)
        )

        content_y = TITLE_ROW_HEIGHT if needs_bar else 0
        content_h = _CONTENT_H - content_y

        # ── 1. Content (painted first = behind everything) ────────────────────
        self.content = flex_col(self, width=lv.pct(100), height=content_h)
        self.content.set_pos(0, content_y)
        self.content.set_scroll_dir(lv.DIR.NONE)

        # ── 2. Context bar (painted over content top area) ────────────────────
        if needs_bar:
            self.context_bar = ContextBar(self, width=CONTEXT_BAR_WIDTH, height=TITLE_ROW_HEIGHT)
        else:
            self.context_bar = None

        # ── 3. Battery (painted last = always on top) ─────────────────────────
        if gui.device_state.has_battery:
            self.battery = Battery(self, width=BATTERY_WIDTH, height=TITLE_ROW_HEIGHT)
            self.battery.align(lv.ALIGN.TOP_RIGHT, 0, 0)
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
