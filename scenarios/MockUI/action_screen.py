import lvgl as lv
from .ui_consts import BTN_HEIGHT, BTN_WIDTH


class ActionScreen(lv.obj):
    """Generic action screen for menu items"""
    def __init__(self, title, parent, *args, **kwargs):
        # parent is the NavigationController (not necessarily the LVGL parent)
        # attach to parent's `content` container when available so the status bar stays visible
        lv_parent = getattr(parent, "content", parent)
        super().__init__(lv_parent, *args, **kwargs)
        # discover navigation callback and shared state from parent
        self.on_navigate = getattr(parent, "on_navigate", None)

        # Fill parent
        self.set_width(lv.pct(100))
        self.set_height(lv.pct(100))

        # Title
        self.title = lv.label(self)
        self.title.set_text(title)
        self.title.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        # smaller title offset for a tighter layout
        self.title.align(lv.ALIGN.TOP_MID, 0, 18)

        # Message
        self.msg = lv.label(self)
        self.msg.set_text("Action: " + title)
        self.msg.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        # smaller gap between title and message
        self.msg.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 12)

        # Back button
        self.back_btn = lv.button(self)
        self.back_btn.set_width(BTN_WIDTH)
        self.back_btn.set_height(BTN_HEIGHT)
        back_lbl = lv.label(self.back_btn)
        back_lbl.set_text("Back")
        back_lbl.center()
        self.back_btn.align_to(self.msg, lv.ALIGN.OUT_BOTTOM_MID, 0, 40)
        self.back_btn.add_event_cb(self.on_back, lv.EVENT.CLICKED, None)

    def on_back(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            # navigate back to provided origin menu
            self.on_navigate(None)
