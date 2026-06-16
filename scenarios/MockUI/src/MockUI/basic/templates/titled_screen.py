"""Base class for all views (menus, action screens, etc.) that have a title.

Provides a fixed-height title bar at the top (optionally containing a centred title
label) and a body area below that fills the remaining space.

Layout variants (absolute, no flex on root):

  Default (show_title=True):
    ┌─────────────────────────────────────────────────────────────┐
    │  title_bar  (TITLE_ROW_HEIGHT px), include title label      │
    ├─────────────────────────────────────────────────────────────┤
    │  body  (fills remaining height)                             │
    └─────────────────────────────────────────────────────────────┘

  show_title=False:
    ┌─────────────────────────────────────────────────────────────┐
    │  title_bar  (TITLE_ROW_HEIGHT px), no title label           │
    ├─────────────────────────────────────────────────────────────┤
    │  body  (fills remaining height)                             │
    └─────────────────────────────────────────────────────────────┘

"""

import lvgl as lv
from .specter_gui_base import SpecterGuiElement
from ..theming import apply_style
from ..utils import (
    TITLE_HEIGHT, CONTENT_H,
    style_as_flex_container, set_pos, set_align
)
from ..widgets import title_label, Btn, flex_row, screen_backdrop
from ..symbol_lib import BTC_ICONS

class TitledScreen(SpecterGuiElement):
    """Base class for all views that have a title.

    Attributes available to subclasses:
        self.title_bar    - lv.obj strip containing the title label,
                            or None when show_title=False
        self.title        - lv.label centred inside title_bar,
                            or None when show_title=False
        self.body         - lv.obj below the title bar; put content here

    Subclasses must guard before accessing self.title
    self.title might be None
    """

    def __init__(self, title, parent, *, show_title=True):
        super().__init__(parent)

        # Root: fill parent completely, no decoration.
        style_as_flex_container(self,
                                flow=lv.FLEX_FLOW.COLUMN, 
                                width=lv.pct(100), height=lv.pct(100),
                                main_align = lv.FLEX_ALIGN.START, 
                                scrollable=False)
        apply_style(self, "WIDGET.SCREEN")

        # ── 1. Title bar ──────────────────────────────────────────────────────
        self.title = None
        self.title_bar = flex_row(self, 
                                  width=lv.pct(100),
                                  height=TITLE_HEIGHT)
        if show_title:
            self.title = title_label(self.title_bar, title)

        # ── 2. Body ───────────────────────────────────────────────────────────
        content_h = CONTENT_H
        self.body = screen_backdrop(self, width=lv.pct(100), height=content_h - TITLE_HEIGHT)

    def refresh(self):
        """Refresh dynamic content (override in subclasses as needed)."""

    def _configure_scroll(self):
        """Enable vertical scrolling only when content overflows the visible body.

        Forces a layout pass first so child positions are accurate, then scans
        all children to find the actual content extent. This way post_init
        additions are automatically included and no manual height tracking is
        needed. Also zeroes pad_bottom to prevent the theme's default 13 px
        bottom padding from creating a phantom over-drag zone.
        """
        self.body.update_layout()
        content_h = 0
        for i in range(self.body.get_child_count()):
            child = self.body.get_child(i)
            bottom = child.get_y() + child.get_height()
            if bottom > content_h:
                content_h = bottom
        # Store so callers can read the real content height.
        self._items_content_h = content_h
        available_h = (self.body.get_height()
                       - self.body.get_style_pad_top(0)
                       - self.body.get_style_pad_bottom(0))
        if content_h > available_h:
            self.body.set_scroll_dir(lv.DIR.VER)
            self.body.set_scrollbar_mode(lv.SCROLLBAR_MODE.AUTO)
            self.body.remove_flag(lv.obj.FLAG.SCROLL_ELASTIC)
            self.body.remove_flag(lv.obj.FLAG.SCROLL_MOMENTUM)
            # Zero pad_bottom so LVGL's scroll_bottom formula
            # (last_child_bottom + pad_bottom - body_bottom) gives the exact
            # overflow. Then force a second layout pass so LVGL recalculates
            # scroll_bottom with the updated padding value.
            self.body.set_style_pad_bottom(0, 0)
            self.body.update_layout()
        else:
            self.body.set_scroll_dir(lv.DIR.NONE)
            self.body.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

    def add_title_delete_btn(self, on_click):
        """Add a right-aligned red TRASH button to the title bar.

        Args:
            on_click: Zero-argument callable invoked on CLICKED.

        Returns:
            The created ``Btn`` widget (stored as ``self.delete_btn``).
        """
        btn_size = TITLE_HEIGHT - 10
        self.delete_btn = Btn(self.title_bar,
                              icon=BTC_ICONS.TRASH,
                              size=(btn_size, btn_size),
                              background_style=["WIDGET.BUTTON", "BG.DANGER"],
                              )
        set_align(self.delete_btn, lv.ALIGN.RIGHT_MID)

        self.delete_btn.add_event_cb(on_click, lv.EVENT.CLICKED, None)
        return self.delete_btn
