import lvgl as lv
from .ui_consts import BTN_HEIGHT, BTN_WIDTH, MENU_PCT, PAD_SIZE


class InterfacesMenu(lv.obj):
    """Menu to enable/disable hardware interfaces.

    menu_id: "interfaces"
    """

    def __init__(self, parent, *args, **kwargs):
        # parent is the NavigationController (not necessarily the lv parent)
        lv_parent = getattr(parent, "content", parent)
        super().__init__(lv_parent, *args, **kwargs)

        self.on_navigate = getattr(parent, "on_navigate", None)
        self.state = getattr(parent, "specter_state", None)
        self.parent = parent
        self.menu_id = "interfaces"

        # layout
        self.set_width(lv.pct(100))
        self.set_height(lv.pct(100))

        # If ui_state has history, show back button to the left of the title
        if parent.ui_state and parent.ui_state.history and len(parent.ui_state.history) > 0:
            self.back_btn = lv.button(self)
            self.back_btn.set_size(40, 28)
            self.back_lbl = lv.label(self.back_btn)
            self.back_lbl.set_text("<")
            self.back_lbl.center()
            # wire back to navigation callback: wrap handler in a lambda so the
            # LVGL binding's argument passing doesn't mismatch the method signature.
            self.back_btn.add_event_cb(lambda e: self.on_back(e), lv.EVENT.CLICKED, None)
        # Title
        self.title = lv.label(self)
        self.title.set_text("Enable/Disable Interfaces")
        self.title.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        self.title.align(lv.ALIGN.TOP_MID, 0, 6)

        # Container for rows
        self.container = lv.obj(self)
        self.container.set_width(lv.pct(100))
        self.container.set_height(lv.pct(MENU_PCT))
        self.container.set_layout(lv.LAYOUT.FLEX)
        self.container.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.container.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        self.container.set_style_pad_all(PAD_SIZE, 0)
        self.container.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, PAD_SIZE)

        # Build interface rows: list of tuples (label_text, state_attr)
        rows = [
            ("QR Scanner", "enabledQR"),
            ("USB", "enabledUSB"),
            ("SD Card", "enabledSD"),
            ("SmartCard", "enabledSmartCard"),
        ]

        for text, state_attr in rows:
            row = lv.obj(self.container)
            row.set_width(lv.pct(100))
            row.set_height(BTN_HEIGHT)
            row.set_layout(lv.LAYOUT.FLEX)
            row.set_flex_flow(lv.FLEX_FLOW.ROW)
            row.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)

            # Left label
            lbl = lv.label(row)
            lbl.set_text(text)
            lbl.set_width(lv.pct(70))
            lbl.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)

            # Right toggle button
            sw = lv.switch(row)
            sw.set_size(60, 30)

            # Set initial state from specter_state (if present)
            enabled = False
            if self.state and hasattr(self.state, state_attr):
                enabled = bool(getattr(self.state, state_attr))
            if enabled:
                #sw.on(lv.ANIM.OFF)
                sw.add_state(lv.STATE.CHECKED)
            else:
                sw.remove_state(lv.STATE.CHECKED)

            # Event handler: single handler function and a lambda that binds
            # the current state_attr into its default argument so each switch
            # receives the correct attribute (avoids late-binding loop issue).
            def _handler(e, attr):
                sw_obj = e.get_target_obj()
                is_on = bool(sw_obj.has_state(lv.STATE.CHECKED))

                # update specter_state stored on this menu instance and in NavigationController
                setattr(self.state, attr, is_on)
                setattr(self.parent.specter_state, attr, is_on)

                # refresh status bar
                self.parent.status_bar.refresh(self.parent.specter_state)


            sw.add_event_cb(lambda e, a=state_attr: _handler(e, a), lv.EVENT.VALUE_CHANGED, None)

    def on_back(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            self.on_navigate(None)
