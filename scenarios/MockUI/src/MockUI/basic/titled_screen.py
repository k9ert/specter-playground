"""Base class for all views (menus, action screens, etc.) that have a title.

Provides an optional fixed-height title bar at the top (containing a centred title
label) and a body area below that fills the remaining space.

Layout variants (absolute, no flex on root):

  Default (show_title=True):
    ┌────────────────────────────────────────┐
    │  title_bar  (TITLE_ROW_HEIGHT px)      │
    ├────────────────────────────────────────┤
    │  (TITLE_PADDING gap)                   │
    ├────────────────────────────────────────┤
    │  body  (fills remaining height)        │
    └────────────────────────────────────────┘

  show_title=False:
    ┌────────────────────────────────────────┐
    │  (transparent spacer TITLE_ROW_HEIGHT) │
    ├────────────────────────────────────────┤
    │  body  (fills remaining height)        │
    └────────────────────────────────────────┘

"""

import lvgl as lv
from .ui_consts import (
    TITLE_ROW_HEIGHT, TITLE_PADDING, SCREEN_HEIGHT, CONTENT_PCT,
    TITLE_FONT,
)
from .widgets.labels import body_label
from .widgets.containers import bare_strip
from .specter_gui_base import SpecterGuiElement, configure_as_bare


class TitledScreen(SpecterGuiElement):
    """Base class for all views that have a title.

    Attributes available to subclasses:
        self.gui          - the SpecterGui that owns this screen
        self.device_state - gui.device_state shorthand
        self.ui_state     - gui.ui_state shorthand
        self.i18n         - gui.i18n shorthand
        self.on_navigate  - navigation callback from gui.on_navigate
        self.title_bar    - lv.obj strip containing the title label,
                            or None when show_title=False
        self.title        - lv.label centred inside title_bar,
                            or None when show_title=False
        self.body         - lv.obj below the title bar; put content here

    Subclasses must guard before accessing self.title / self.title_bar
    self.title and self.title_bar might be None
    """

    def __init__(self, title, parent, *, show_title=True):
        # If parent is the GUI itself, anchor to its content area so we don't
        # cover the navigation bar at the bottom.
        lv_parent = getattr(parent, "content", parent)
        super().__init__(lv_parent)

        # Convenience shortcut — must be set before any property access.
        self.gui = parent

        # Root: fill parent completely, no decoration.
        configure_as_bare(self, width=lv.pct(100), height=lv.pct(100))
        self.set_scroll_dir(lv.DIR.NONE)

        y_body = 0  # accumulated y-offset for the body widget

        # ── 1. Title bar ──────────────────────────────────────────────────────
        self.title_bar = None
        self.title = None
        if show_title:
            self.title_bar = bare_strip(self, TITLE_ROW_HEIGHT, 0)
            self.title = body_label(self.title_bar, title, font=TITLE_FONT)
            self.title.align(lv.ALIGN.CENTER, 0, 0)
            y_body = TITLE_ROW_HEIGHT + TITLE_PADDING
        else:
            # No title strip — place an invisible spacer so the battery widget
            # (floating above content at y=0) doesn't overlap body content.
            self.spacer = bare_strip(self, TITLE_ROW_HEIGHT, 0)
            self.spacer.set_style_bg_opa(lv.OPA.TRANSP, 0)
            y_body = TITLE_ROW_HEIGHT

        # ── 2. Body ───────────────────────────────────────────────────────────
        content_h = SCREEN_HEIGHT * CONTENT_PCT // 100
        self.body = bare_strip(self, content_h - y_body, y_body)
        # Disable scrolling on body; subclasses can re-enable via set_scroll_dir.
        self.body.set_scroll_dir(lv.DIR.NONE)

    def refresh(self):
        """Refresh dynamic content (override in subclasses as needed)."""

    def on_back(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            self.on_navigate(None)
