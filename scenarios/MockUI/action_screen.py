import lvgl as lv
from .ui_consts import BTN_HEIGHT, BTN_WIDTH


class ActionScreen(lv.obj):
    """Generic action screen for menu items"""
    def __init__(self, title, on_navigate, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_navigate = on_navigate

        # Fill parent
        self.set_width(lv.pct(100))
        self.set_height(lv.pct(100))

        # Title
        self.title = lv.label(self)
        self.title.set_text(title)
        self.title.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.title.align(lv.ALIGN.TOP_MID, 0, 50)

        # Message
        self.msg = lv.label(self)
        self.msg.set_text("Action: " + title)
        self.msg.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.msg.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 30)

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
