import lvgl as lv
from ..basic import TitledScreen, BTN_WIDTH, BTN_HEIGHT, SMALL_PAD
from ..basic.keyboard_manager import Layout
from ..basic.widgets import flex_col, flex_row, form_label, form_textarea, Btn, ACCEPTED_CHARS
from ..basic.symbol_lib import BTC_ICONS

class PassphraseMenu(TitledScreen):
    """Form to enter/set the active seed's passphrase.

    menu_id: "set_passphrase"
    """

    def __init__(self, parent):
        super().__init__(parent.i18n.t("MENU_SET_PASSPHRASE"), parent)
        t = self.i18n.t

        self.body.set_layout(lv.LAYOUT.FLEX)
        self.body.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.body.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)

        # Row for passphrase input
        pa_row = flex_row(self.body, height=lv.pct(20), main_align=lv.FLEX_ALIGN.START)

        form_label(pa_row, t("PASSPHRASE_MENU_LABEL"))

        # editable textarea
        self.pa_ta = form_textarea(pa_row)
        val = ""
        if self.ui_state.active_seed and self.ui_state.active_seed.passphrase is not None:
            val = self.ui_state.active_seed.passphrase
        self.pa_ta.set_text(val)
        self.pa_ta.set_accepted_chars(ACCEPTED_CHARS)

        def _on_commit(value):
            if self.ui_state.active_seed:
                if not value:
                    self.ui_state.active_seed.passphrase = None
                else:
                    self.ui_state.active_seed.passphrase = value
                    self.ui_state.active_seed.passphrase_active = True
            self.gui.refresh_ui()
            self.on_navigate(None)

        keyboard_binder = lambda e: self.gui.keyboard_manager.bind(self.pa_ta, Layout.FULL, _on_commit, lambda text: text.strip())
        self.pa_ta.add_event_cb(keyboard_binder, lv.EVENT.CLICKED, None)

        buttons_row = flex_col(self.body, height=lv.pct(50), pad=SMALL_PAD)

        # Clear button
        self.clear_btn = Btn(
            buttons_row,
            icon=BTC_ICONS.CROSS,
            text=t("PASSPHRASE_MENU_CLEAR"),
            size=(lv.pct(BTN_WIDTH), BTN_HEIGHT),
            callback=self._on_clear,
        )

    def _on_clear(self, e):
        """Clear passphrase and update state."""
        if e.get_code() != lv.EVENT.CLICKED:
            return
        
        # Clear text area
        self.pa_ta.set_text("")
        # Clear passphrase in state
        if self.ui_state.active_seed:
            self.ui_state.active_seed.passphrase = None
        # Refresh UI
        self.gui.refresh_ui()

    def refresh(self):
        if not self.pa_ta.has_state(lv.STATE.FOCUSED):
            val = ""
            if self.ui_state.active_seed and self.ui_state.active_seed.passphrase is not None:
                val = self.ui_state.active_seed.passphrase
            self.pa_ta.set_text(val)