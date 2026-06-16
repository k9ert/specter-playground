import lvgl as lv
from ..basic import (
    TitledScreen, BTN_WIDTH, BTN_HEIGHT,
    Layout, ACCEPTED_CHARS,
    Btn,
    BTC_ICONS,
    flex_row, style_as_flex_container,
    form_label, password_textarea
)

class PassphraseMenu(TitledScreen):
    """Form to enter/set the active seed's passphrase.

    menu_id: "set_passphrase"
    """

    def __init__(self, parent):
        super().__init__(parent.i18n.t("MENU_SET_PASSPHRASE"), parent)
        t = self.i18n.t

        style_as_flex_container(self.body)

        # Row for passphrase input
        pa_row = flex_row(self.body)

        self.pa_lbl = form_label(pa_row, t("PASSPHRASE_MENU_LABEL"))

        # editable textarea
        self.pa_ta = password_textarea(pa_row)
        self.pa_ta.set_flex_grow(1)
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

        keyboard_binder = lambda e: self.gui.keyboard_manager.bind(self.pa_ta, 
                                                                   Layout.FULL, 
                                                                   _on_commit, 
                                                                   lambda text: text.strip()
                                                                   )
        self.pa_ta.add_event_cb(keyboard_binder, lv.EVENT.CLICKED, None)

        # Clear button
        self.clear_btn = Btn(self.body,
                             icon=BTC_ICONS.CROSS,
                             text=t("PASSPHRASE_MENU_CLEAR"),
                             size=(BTN_WIDTH, BTN_HEIGHT),
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