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
from ..utils import set_scroll, get_pos, get_size, set_align
from ..widgets import make_label, Btn
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

    _SUBELEMENTS = [
        ("title_bar", SpecterGuiElement),
        ("body", SpecterGuiElement),
    ]

    def __init__(self, title, parent, *, show_title=True):
        self.show_title = show_title
        self.title = title
        super().__init__(parent)

    def setup_self(self):
        apply_style(self, "CONTAINER.TITLED_SCREEN")

    def post_init(self):
        apply_style(self.title_bar, "CONTAINER.TITLE_BAR")
        apply_style(self.body, "CONTAINER.CONTENT")
        # Force a layout pass so child pct() sizes (title_bar height) resolve
        # before the title label and body children are added.
        self.update_layout()
        if self.show_title:
            self.title = make_label(self.title_bar, self.title, "WIDGET.SCREEN_TITLE")

    def refresh(self):
        """Refresh dynamic content (override in subclasses as needed)."""

    def _configure_scroll(self):
        """Enable vertical scrolling only when content overflows the visible body.

        Forces a layout pass first so child positions are accurate, then scans
        all children to find the actual content extent. This way post_init
        additions are automatically included and no manual height tracking is
        needed.
        """
        self.body.update_layout()
        content_h = 0
        for i in range(self.body.get_child_count()):
            child = self.body.get_child(i)
            _, y = get_pos(child)
            _, h = get_size(child)
            bottom = y + h
            if bottom > content_h:
                content_h = bottom
        # Store so callers can read the real content height.
        self._items_content_h = content_h
        available_h = (self.body.get_height()
                       - self.body.get_style_pad_top(0)
                       - self.body.get_style_pad_bottom(0))
        if content_h > available_h:
            set_scroll(self.body, horizontal=False, vertical=True)
        else:
            set_scroll(self.body, horizontal=False, vertical=False)

    def add_title_delete_btn(self, on_click):
        """Add a right-aligned red TRASH button to the title bar.

        Args:
            on_click: Zero-argument callable invoked on CLICKED.

        Returns:
            The created ``Btn`` widget (stored as ``self.delete_btn``).
        """
        self.delete_btn = Btn(self.title_bar,
                              icon=BTC_ICONS.TRASH,
                              callback=on_click,
                              background_style="WIDGET.DELETE_BUTTON",
                              foreground_style="WIDGET.DELETE_BUTTON_FG"
                              )
        self.delete_btn.add_flag(lv.obj.FLAG.FLOATING)
        apply_style(self.delete_btn, "CONTAINER.DELETE_BUTTON")
        return self.delete_btn
