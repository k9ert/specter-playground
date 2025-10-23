import lvgl as lv
from .menu import GenericMenu
from .ui_consts import BTN_WIDTH, BTN_HEIGHT, PAD_SIZE


class PassphraseMenu(GenericMenu):
    """Menu to enter/set the active wallet passphrase.

    menu_id: "set_passphrase"
    """

    def __init__(self, parent, *args, **kwargs):
        super().__init__("set_passphrase", "Set Passphrase", [], parent, *args, **kwargs)

        self.parent = parent
        self.state = parent.specter_state

        # Row for passphrase input
        pa_row = lv.obj(self.container)
        pa_row.set_width(lv.pct(100))
        pa_row.set_height(lv.pct(20))
        pa_row.set_layout(lv.LAYOUT.FLEX)
        pa_row.set_flex_flow(lv.FLEX_FLOW.ROW)
        pa_row.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        pa_row.set_style_border_width(0, 0)

        pa_lbl = lv.label(pa_row)
        pa_lbl.set_text("Passphrase:")
        pa_lbl.set_width(lv.pct(30))
        pa_lbl.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)

        # editable textarea
        self.pa_ta = lv.textarea(pa_row)
        # prefill with active passphrase (might be empty)
        val = ""
        if self.state.active_wallet.active_passphrase is not None:
            val = self.state.active_wallet.active_passphrase
        self.pa_ta.set_text(val)
        self.pa_ta.set_width(lv.pct(60))
        self.pa_ta.set_height(40)

        # make textarea clickable
        self.pa_ta.add_flag(lv.obj.FLAG.CLICKABLE)

        # on-screen keyboard (hidden until used)
        self._kb = lv.keyboard(self)
        self._kb.add_flag(lv.obj.FLAG.HIDDEN)
        self._kb.set_textarea(self.pa_ta)
        self.pa_ta.add_event_cb(self._open_keyboard, lv.EVENT.CLICKED, None)

        buttons_row = lv.obj(self.container)
        buttons_row.set_width(lv.pct(100))
        buttons_row.set_height(lv.pct(50))
        buttons_row.set_layout(lv.LAYOUT.FLEX)
        buttons_row.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        buttons_row.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        buttons_row.set_style_pad_all(PAD_SIZE, 0)
        buttons_row.set_style_border_width(0, 0)

        # Clear button
        self.clear_btn = lv.button(buttons_row)
        self.clear_btn.set_width(BTN_WIDTH)
        self.clear_btn.set_height(BTN_HEIGHT)
        self.clear_lbl = lv.label(self.clear_btn)
        self.clear_lbl.set_text("Clear")
        self.clear_lbl.center()
        self.clear_btn.add_event_cb(lambda e: self.pa_ta.set_text("") if e.get_code() == lv.EVENT.CLICKED else None, lv.EVENT.CLICKED, None)

        # Set button
        self.set_btn = lv.button(buttons_row)
        self.set_btn.set_width(BTN_WIDTH)
        self.set_btn.set_height(BTN_HEIGHT)
        self.set_lbl = lv.label(self.set_btn)
        self.set_lbl.set_text("Set")
        self.set_lbl.center()
        self.set_btn.add_event_cb(self._on_set, lv.EVENT.CLICKED, None)

    def _open_keyboard(self, e):
        if e.get_code() != lv.EVENT.CLICKED:
            return

        self._kb.set_textarea(self.pa_ta)
        self._kb.remove_flag(lv.obj.FLAG.HIDDEN)

    def _on_set(self, e):
        if e.get_code() != lv.EVENT.CLICKED:
            return
        # store into active wallet
        val = self.pa_ta.get_text()
        if val == "":
            self.state.active_wallet.active_passphrase = None
        else:
            self.state.active_wallet.active_passphrase = val
        # refresh status bar
        self.parent.status_bar.refresh(self.state)
        # leave menu and go back
        self.parent.show_menu(None)
