import lvgl as lv
from ..basic import GenericMenu, BTN_WIDTH, BTN_HEIGHT, PAD_SIZE


class PassphraseMenu(GenericMenu):
    """Menu to enter/set the active wallet passphrase.

    menu_id: "set_passphrase"
    """

    def __init__(self, parent, *args, **kwargs):
        # Get translation function from i18n manager (always available via NavigationController)
        t = parent.i18n.t
        
        super().__init__("set_passphrase", t("MENU_SET_PASSPHRASE"), [], parent, *args, **kwargs)

        self.parent = parent
        self.state = parent.specter_state
        
        # Track keyboard state and original value
        self.keyboard = None
        self.original_passphrase = ""

        # Row for passphrase input
        pa_row = lv.obj(self.container)
        pa_row.set_width(lv.pct(100))
        pa_row.set_height(lv.pct(20))
        pa_row.set_layout(lv.LAYOUT.FLEX)
        pa_row.set_flex_flow(lv.FLEX_FLOW.ROW)
        pa_row.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        pa_row.set_style_border_width(0, 0)

        pa_lbl = lv.label(pa_row)
        pa_lbl.set_text(t("PASSPHRASE_MENU_LABEL"))
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
        self.pa_ta.set_accepted_chars("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/~ ")  # No newlines

        # make textarea clickable
        self.pa_ta.add_flag(lv.obj.FLAG.CLICKABLE)
        self.pa_ta.add_event_cb(self._open_keyboard, lv.EVENT.CLICKED, None)
        
        # Add defocus handler
        self.pa_ta.add_event_cb(self._on_defocus, lv.EVENT.DEFOCUSED, None)

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
        self.clear_btn.set_width(lv.pct(BTN_WIDTH))
        self.clear_btn.set_height(BTN_HEIGHT)
        self.clear_lbl = lv.label(self.clear_btn)
        self.clear_lbl.set_text(lv.SYMBOL.CLOSE + " " + t("PASSPHRASE_MENU_CLEAR"))
        self.clear_lbl.center()
        self.clear_btn.add_event_cb(self._on_clear, lv.EVENT.CLICKED, None)

    def _on_clear(self, e):
        """Clear passphrase and update state."""
        if e.get_code() != lv.EVENT.CLICKED:
            return
        
        # Clear text area
        self.pa_ta.set_text("")
        # Clear passphrase in state
        self.state.active_wallet.active_passphrase = None
        # Refresh status bar
        self.parent.status_bar.refresh(self.state)

    def _open_keyboard(self, e):
        """Show keyboard for editing passphrase."""
        if e.get_code() != lv.EVENT.CLICKED:
            return

        # If keyboard already exists, delete it first
        if self.keyboard:
            self.keyboard.delete()
            self.keyboard = None

        # Store original passphrase for cancel/defocus
        self.original_passphrase = self.pa_ta.get_text()

        # Create keyboard
        self.keyboard = lv.keyboard(self)
        self.keyboard.set_textarea(self.pa_ta)
        
        # Keep focus on text area
        self.pa_ta.add_state(lv.STATE.FOCUSED)
        
        # Add event handler for when OK button is pressed
        def on_keyboard_ready(e):
            if e.get_code() == lv.EVENT.READY:
                # Update passphrase in state
                val = self.pa_ta.get_text()
                if val == "":
                    self.state.active_wallet.active_passphrase = None
                else:
                    self.state.active_wallet.active_passphrase = val
                # Refresh status bar
                self.parent.status_bar.refresh(self.state)
                # Remove focus from text area
                self.pa_ta.remove_state(lv.STATE.FOCUSED)
                # Delete keyboard
                if self.keyboard:
                    self.keyboard.delete()
                    self.keyboard = None
        
        # Add event handler for when Cancel button is pressed
        def on_keyboard_cancel(e):
            if e.get_code() == lv.EVENT.CANCEL:
                # Restore original passphrase
                self.pa_ta.set_text(self.original_passphrase)
                # Remove focus from text area
                self.pa_ta.remove_state(lv.STATE.FOCUSED)
                # Delete keyboard
                if self.keyboard:
                    self.keyboard.delete()
                    self.keyboard = None
        
        self.keyboard.add_event_cb(on_keyboard_ready, lv.EVENT.READY, None)
        self.keyboard.add_event_cb(on_keyboard_cancel, lv.EVENT.CANCEL, None)

    def _on_defocus(self, e):
        """Handle text area losing focus - close keyboard and discard changes."""
        if e.get_code() != lv.EVENT.DEFOCUSED:
            return
        
        # If keyboard is open, close it and discard changes
        if self.keyboard:
            # Restore original passphrase
            self.pa_ta.set_text(self.original_passphrase)
            # Delete keyboard
            self.keyboard.delete()
            self.keyboard = None
