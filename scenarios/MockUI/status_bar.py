import lvgl as lv


class StatusBar(lv.obj):
    """Simple status bar with a power button. Designed to be ~10% of the screen height."""
    def __init__(self, parent, height_pct=10, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.set_width(lv.pct(100))
        self.set_height(lv.pct(height_pct))
        self.set_layout(lv.LAYOUT.FLEX)
        self.set_flex_flow(lv.FLEX_FLOW.ROW)
        self.set_flex_align(lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        self.set_style_pad_all(6, 0)

        # Power button on the right
        self.power_btn = lv.button(self)
        self.power_btn.set_size(50, 25)
        self.power_lbl = lv.label(self.power_btn)
        #self.power_lbl.set_text("⏻")
        self.power_lbl.set_text("P")
        self.power_lbl.center()

        # expose a small callback slot that NavigationController can connect
        self.on_power = None
        self.power_btn.add_event_cb(self._on_power_cb, lv.EVENT.CLICKED, None)

    def _on_power_cb(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            if callable(self.on_power):
                self.on_power()
