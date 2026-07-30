import lvgl as lv
from ..basic import (
    SpecterGuiElement,
    GenericMenu,
    MenuItem,
    Layout, ACCEPTED_CHARS,
    Btn,
    BTC_ICONS,
    apply_style,
    remove_style,
    make_password_textarea,
    t
)

class PassphraseMenu(GenericMenu):
    """Form to enter/set the active seed's passphrase.

    menu_id: "MENU_SET_PASSPHRASE"
    """

    TITLE_KEY = "MENU_SET_PASSPHRASE"

    def setup_self(self):
        super().setup_self()
        self._displayed_seed = self.active_seed
        self.passphrase_value = self.active_seed.passphrase or ""

    def pre_itemlist(self):
        self.pa_ta_row = SpecterGuiElement(self.body)
        apply_style(self.pa_ta_row, "CONTAINER.MENU_ROW")
        # editable textarea
        self.pa_ta = make_password_textarea(self.pa_ta_row)
        apply_style(self.pa_ta, "TEXT.TITLE")
        self.pa_ta.set_text(self.passphrase_value)
        self.pa_ta.set_accepted_chars(ACCEPTED_CHARS)

        keyboard_binder = lambda e: self.keyboard_manager.bind(textarea=self.pa_ta,
                                                               layout_id=Layout.FULL,
                                                               on_commit=self._set_passphrase_value,
                                                               on_cancel=self._set_passphrase_value,
                                                               sanitize=lambda text: text.strip(),
                                                               restore_on_defocussed=False,
                                                              )
        self.pa_ta.add_event_cb(keyboard_binder, lv.EVENT.CLICKED, None)

    def _has_passphrase(self):
        return bool(self.passphrase_value)

    def _set_passphrase_value(self, text=None):
        if text is None:
            text = self.pa_ta.get_text()
        had_passphrase = self._has_passphrase()
        self.passphrase_value = text.strip()
        self.pa_ta.set_text(self.passphrase_value)
        has_passphrase = self._has_passphrase()
        if not has_passphrase:
            self._set_pp_enabled(False)
        else:
            self._set_pp_enabled(True)
            if not had_passphrase:
                self._set_pp_active(True)

    def _set_pp_enabled(self, enabled):
        if enabled:
            remove_style(self.passphrase_enabled_ico, "MODIFIER.MUTED")
            remove_style(self.passphrase_enabled_lbl, "MODIFIER.MUTED")
            self.passphrase_enabled_switch.remove_state(lv.STATE.DISABLED)
        else:
            apply_style(self.passphrase_enabled_ico, "MODIFIER.MUTED")
            apply_style(self.passphrase_enabled_lbl, "MODIFIER.MUTED")
            self.passphrase_enabled_switch.add_state(lv.STATE.DISABLED)
            self._set_pp_active(False)

    def _set_pp_active(self, active):
        if active:
            self.passphrase_enabled_switch.add_state(lv.STATE.CHECKED)
        else:
            self.passphrase_enabled_switch.remove_state(lv.STATE.CHECKED)

    def get_menu_items(self):
        items = []
        items.append(MenuItem(
            BTC_ICONS.PASSWORD, t("PASSPHRASE_MENU_ENABLE_DISABLE"),
            get_value=(self._has_passphrase() and self.active_seed.passphrase_active),
            set_value=self._set_pp_active,
        ))
        return items

    def post_itemlist(self):
        self.passphrase_enabled_switch = self.body.rows[0].switch
        self.passphrase_enabled_ico = self.body.rows[0].ico
        self.passphrase_enabled_lbl = self.body.rows[0].lbl

        self._set_passphrase_value(self.passphrase_value)

        self.button_row = SpecterGuiElement(self.body)
        apply_style(self.button_row, "CONTAINER.MODAL_BUTTON_ROW")
        # Accept button
        self.accept_btn = Btn(self.button_row,
                              icon=BTC_ICONS.CHECK,
                              text=t("COMMON_OK"),
                              callback=self._on_accept,
                              background_style= "WIDGET.BUTTON",
                              foreground_style= "WIDGET.BUTTON_FG"
                             )
        # Clear button
        self.clear_btn = Btn(self.button_row,
                             icon=BTC_ICONS.TRASH,
                             text=t("PASSPHRASE_MENU_CLEAR"),
                             callback=self._on_clear,
                             background_style= "WIDGET.BUTTON",
                             foreground_style= "WIDGET.BUTTON_FG"
                            )
        # Cancel button
        self.cancel_btn = Btn(self.button_row,
                              icon=BTC_ICONS.CROSS,
                              text=t("COMMON_CANCEL"),
                              callback=self._on_cancel,
                              background_style= "WIDGET.BUTTON",
                              foreground_style= "WIDGET.BUTTON_FG"
                             )

    def _on_clear(self):
        self._set_passphrase_value("")

    def _on_accept(self):
        self._set_passphrase_value(self.pa_ta.get_text())
        # Commit passphrase and its requested activation state.
        self.ui_state.active_seed.passphrase = self.passphrase_value
        self.ui_state.active_seed.passphrase_active = bool(self._has_passphrase() and self.passphrase_enabled_switch.has_state(lv.STATE.CHECKED))

        self.gui.refresh_ui()
        self.on_navigate(None)

    def _on_cancel(self):
        # Navigate back
        self.on_navigate(None)

    def refresh(self):
        super().refresh()

        if self.active_seed != self._displayed_seed:
            self._displayed_seed = self.active_seed
            self.passphrase_value = self.active_seed.passphrase or ""
            self._set_passphrase_value(self.passphrase_value)
            if self._has_passphrase() and self.active_seed.passphrase_active:
                self._set_pp_active(True)