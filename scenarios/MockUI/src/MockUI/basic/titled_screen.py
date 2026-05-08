"""Base class for all views (menus, action screens, etc.) that have a title.

Provides a fixed-height title bar at the top (containing a centred title
label), an optional context bar for SEED/WALLET screens, and a body area
below that fills the remaining space.  Battery placement is handled here;
subclasses no longer need to create the Battery widget themselves.

Layout variants (absolute, no flex on root):

  Default (no context, show_title=True):
    ┌────────────────────────────────────────┐
    │  title_bar  (TITLE_ROW_HEIGHT px)   [B]│
    ├────────────────────────────────────────┤
    │  (TITLE_PADDING gap)                   │
    ├────────────────────────────────────────┤
    │  body  (fills remaining height)        │
    └────────────────────────────────────────┘

  SEED / WALLET context, show_title=True:
    ┌────────────────────────────────────────┐
    │  _context_bar  (TITLE_ROW_HEIGHT px)[B]│  ← seed/wallet info
    ├────────────────────────────────────────┤
    │  title_bar     (TITLE_ROW_HEIGHT px)   │  ← screen-specific title
    ├────────────────────────────────────────┤
    │  (TITLE_PADDING gap)                   │
    ├────────────────────────────────────────┤
    │  body  (fills remaining height)        │
    └────────────────────────────────────────┘

  SEED / WALLET context, show_title=False:
    ┌────────────────────────────────────────┐
    │  _context_bar  (TITLE_ROW_HEIGHT px)[B]│
    ├────────────────────────────────────────┤
    │  body  (fills remaining height)        │
    └────────────────────────────────────────┘

  No context, show_title=False:
    ┌────────────────────────────────────────┐
    │  (transparent spacer TITLE_ROW_HEIGHT) │  ← [B] floats here
    ├────────────────────────────────────────┤
    │  body  (fills remaining height)        │
    └────────────────────────────────────────┘

[B] = battery, always a direct child of TitledScreen, top-right aligned
      (only when show_battery=True and device_state.has_battery).
"""

import lvgl as lv
from .ui_consts import (
    TITLE_ROW_HEIGHT, TITLE_PADDING, SCREEN_HEIGHT, CONTENT_PCT,
    TITLE_FONT, BATTERY_OFFSET_X,
)
from .widgets.labels import body_label
from .widgets.containers import bare_strip
from .specter_gui_base import SpecterGuiElement, configure_as_bare
from .context_bar import ContextBar
from ..stubs.ui_state import Context
from ..stubs.battery import Battery

# Vertical offset so the battery is centred within the top TITLE_ROW_HEIGHT strip.
# Battery height is 20 px (set in Battery.__init__).
_BATT_Y = (TITLE_ROW_HEIGHT - 20) // 2


class TitledScreen(SpecterGuiElement):
    """Base class for all views that have a title.

    Attributes available to subclasses:
        self.gui          - the SpecterGui that owns this screen
        self.show_title   - True when a title bar was created
        self.device_state - gui.device_state shorthand
        self.ui_state     - gui.ui_state shorthand
        self.i18n         - gui.i18n shorthand
        self.on_navigate  - navigation callback from gui.on_navigate
        self.title_bar    - lv.obj strip containing the title label,
                            or None when show_title=False
        self.title        - lv.label centred inside title_bar,
                            or None when show_title=False
        self.body         - lv.obj below all header strips; put content here
        self._context_bar - ContextBar instance, or None when not applicable

    Subclasses must guard before accessing self.title / self.title_bar:
        if self.show_title:
            self.title.set_text(...)
    """

    def __init__(self, title, parent, *, show_title=True):
        # If parent is the GUI itself, anchor to its content area so we don't
        # cover the navigation bar at the bottom.
        lv_parent = getattr(parent, "content", parent)
        super().__init__(lv_parent)

        # Convenience shortcut — must be set before any property access.
        self.gui = parent
        self.show_title = show_title

        # Root: fill parent completely, no decoration.
        configure_as_bare(self, width=lv.pct(100), height=lv.pct(100))
        self.set_scroll_dir(lv.DIR.NONE)

        # ── Determine layout ──────────────────────────────────────────────────
        ui_state = self.ui_state
        ctx = self.context
        has_context_bar = (
            (ctx == Context.SEED and ui_state.active_seed is not None)
            or (ctx == Context.WALLET and ui_state.active_wallet is not None)
        )

        y_body = 0  # accumulated y-offset for the body widget

        # ── 1. Context bar (SEED / WALLET context only) ───────────────────────
        self.context_bar = None
        if has_context_bar:
            self.context_bar = ContextBar(self)
            y_body = TITLE_ROW_HEIGHT

        # ── 2. Title bar ──────────────────────────────────────────────────────
        self.title_bar = None
        self.title = None
        if show_title:
            self.title_bar = bare_strip(self, TITLE_ROW_HEIGHT, y_body)
            self.title = body_label(self.title_bar, title, font=TITLE_FONT)
            self.title.align(lv.ALIGN.CENTER, 0, 0)
            y_body += TITLE_ROW_HEIGHT + TITLE_PADDING
        elif not has_context_bar:
            # No header strip at all — place an invisible spacer so the battery
            # widget has a reserved row and body content starts below it.
            self.spacer = bare_strip(self, TITLE_ROW_HEIGHT, 0)
            self.spacer.set_style_bg_opa(lv.OPA.TRANSP, 0)
            y_body = TITLE_ROW_HEIGHT

        # ── 3. Battery — always a direct child of self ────────────────────────
        if self.device_state.has_battery:
            self.batt = Battery(self)
            self.batt.VALUE = self.device_state.battery_pct
            self.batt.update()
            self.batt.align(lv.ALIGN.TOP_RIGHT, BATTERY_OFFSET_X, _BATT_Y)

        # ── 4. Body ───────────────────────────────────────────────────────────
        content_h = SCREEN_HEIGHT * CONTENT_PCT // 100
        self.body = bare_strip(self, content_h - y_body, y_body)
        # Disable scrolling on body; subclasses can re-enable via set_scroll_dir.
        self.body.set_scroll_dir(lv.DIR.NONE)

    def refresh(self):
        """Refresh dynamic content: battery level (in-place, no rebuild)."""
        if hasattr(self, "batt"):
            self.batt.VALUE = self.device_state.battery_pct
            self.batt.update()
        if self.context_bar:
            self.context_bar.refresh()

    def on_back(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            self.on_navigate(None)
