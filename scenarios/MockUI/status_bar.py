import lvgl as lv
from .ui_consts import PAD_SIZE, STATUS_BTN_HEIGHT, STATUS_BTN_WIDTH, TWO_LETTER_SYMBOLD_WIDTH, THREE_LETTER_SYMBOLD_WIDTH


class StatusBar(lv.obj):
    """Simple status bar with a power button. Designed to be ~10% of the screen height."""

    def __init__(self, parent, height_pct=10, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent  # for callback access

        self.set_width(lv.pct(100))
        self.set_height(lv.pct(height_pct))

        self.set_layout(lv.LAYOUT.FLEX)
        self.set_flex_flow(lv.FLEX_FLOW.ROW)
        self.set_flex_align(
            lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER
        )
        self.set_style_pad_all(0, 0)

        # Power button
        self.power_btn = lv.button(self)
        self.power_btn.set_size(STATUS_BTN_WIDTH, STATUS_BTN_HEIGHT)
        self.power_lbl = lv.label(self.power_btn)
        self.power_lbl.set_text("PWR")
        self.power_lbl.center()
        self.power_btn.add_event_cb(self.power_cb, lv.EVENT.CLICKED, None)

        # Lock button (small)
        self.lock_btn = lv.button(self)
        self.lock_btn.set_size(STATUS_BTN_WIDTH, STATUS_BTN_HEIGHT)
        self.lock_lbl = lv.label(self.lock_btn)
        self.lock_lbl.set_text("LOCK")
        self.lock_lbl.center()
        self.lock_btn.add_event_cb(self.lock_cb, lv.EVENT.CLICKED, None)

        # Left side: battery icon (anchored to extreme left)
        self.batt_lbl = lv.label(self)
        self.batt_lbl.set_text("")
        self.batt_lbl.set_width(45)

        # Center area: wallet name + type + net + peripheral indicators
        self.wallet_name_lbl = lv.label(self)
        self.wallet_name_lbl.set_text("")
        # conservative fixed width for the wallet name
        self.wallet_name_lbl.set_width(60)

        self.wallet_type_lbl = lv.label(self)
        self.wallet_type_lbl.set_text("")
        # small fixed width for the type indicator (e.g. 'MuSig'/'SiSig')
        self.wallet_type_lbl.set_width(30)

        # Passphrase indicator (shows 'PP' when the active wallet has a passphrase configured)
        self.pp_lbl = lv.label(self)
        self.pp_lbl.set_text("")
        self.pp_lbl.set_width(TWO_LETTER_SYMBOLD_WIDTH)

        self.net_lbl = lv.label(self)
        self.net_lbl.set_text("")
        self.net_lbl.set_width(35)

        # peripheral indicators – give them stable small widths so changing text won't shift layout
        self.qr_lbl = lv.label(self)
        self.qr_lbl.set_text("")
        self.qr_lbl.set_width(TWO_LETTER_SYMBOLD_WIDTH)

        self.usb_lbl = lv.label(self)
        self.usb_lbl.set_text("")
        self.usb_lbl.set_width(THREE_LETTER_SYMBOLD_WIDTH)

        self.sd_lbl = lv.label(self)
        self.sd_lbl.set_text("")
        self.sd_lbl.set_width(TWO_LETTER_SYMBOLD_WIDTH)

        self.smartcard_lbl = lv.label(self)
        self.smartcard_lbl.set_text("")
        self.smartcard_lbl.set_width(TWO_LETTER_SYMBOLD_WIDTH)

        # spacer to push the following content to the right
        self._spacer = lv.obj(self)
        # expand horizontally but avoid increasing the bar height
        self._spacer.set_flex_grow(1)
        # ensure no padding/border is added that could grow vertically
        self._spacer.set_style_pad_all(0, 0)
        self._spacer.set_style_border_width(0, 0)
        # if available, keep height minimal so it won't be taller than the bar
        self._spacer.set_height(0)


        # Language indicator (TODO: make a selector)
        self.lang_lbl = lv.label(self)
        self.lang_lbl.set_text("")
        self.lang_lbl.set_width(THREE_LETTER_SYMBOLD_WIDTH)        

        # Apply a smaller font to all labels in the status bar
        self.font = lv.font_montserrat_12
        labels = [
            self.batt_lbl,
            self.wallet_name_lbl,
            self.wallet_type_lbl,
            self.pp_lbl,
            self.net_lbl,
            self.lang_lbl,
            self.qr_lbl,
            self.usb_lbl,
            self.sd_lbl,
            self.smartcard_lbl,
            self.lock_lbl,
            self.power_lbl,
        ]
        for lbl in labels:
            lbl.set_style_text_font(self.font, 0)

    def power_cb(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            if self.parent.specter_state.battery_pct is None:
                self.parent.specter_state.battery_pct = 50
                self.refresh(self.parent.specter_state)
            else:
                self.parent.specter_state.battery_pct = None
                self.refresh(self.parent.specter_state)

    def lock_cb(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            if self.parent.specter_state.is_locked:
                self.parent.specter_state.unlock()
            else:
                self.parent.specter_state.lock()

    def refresh(self, state):
        """Update visual elements from a SpecterState-like object."""
        # battery
        if state.has_battery:
            # show simple percent if available
            perc = state.battery_pct
            if perc is not None:
                # show as 'B:34%'
                self.batt_lbl.set_text("B:%d%%" % int(perc))
            else:
                self.batt_lbl.set_text("B:")

        # wallet name and type separated into two labels
        if state.active_wallet is not None:
            w = state.active_wallet
            name = getattr(w, "name", "") or ""
            typ = "MuSig" if w.isMultiSig else "SiSig"
            self.wallet_name_lbl.set_text(self._truncate(name, 8))
            self.wallet_type_lbl.set_text(self._truncate(typ, 5))
            # show PP indicator if wallet reports a passphrase configured
            if state.active_passphrase is not None:
                self.pp_lbl.set_text("PP")
            else:
                self.pp_lbl.set_text("")
        else:
            self.wallet_name_lbl.set_text("")
            self.wallet_type_lbl.set_text("")
            self.pp_lbl.set_text("")

        # net
        self.net_lbl.set_text(self._truncate(state.net or "", 4))

        # language
        self.lang_lbl.set_text(self._truncate(state.language or "", 3))

        # peripherals
        # if feature is physically not present (hasXY = False: show nothing)
        # if feature is present and only can be enabled (USB+QR): show lower case when disabled and upper case when enabled
        # if feature is present and can be enabled and detected (SD + SmartCard): show lower case when enabled and upper case when also detected
        if state.hasQR:
            if state.enabledQR:
                self.qr_lbl.set_text("QR")
            else:
                self.qr_lbl.set_text("qr")
        else:
            self.qr_lbl.set_text("")

        if state.hasUSB:
            if state.enabledUSB:
                self.usb_lbl.set_text("USB")
            else:
                self.usb_lbl.set_text("usb")
        else:
            self.usb_lbl.set_text("")

        if state.hasSD and state.enabledSD:
            if state.detectedSD:
                self.sd_lbl.set_text("SD")
            else:
                self.sd_lbl.set_text("sd")
        else:
            self.sd_lbl.set_text("")

        if state.hasSmartCard and state.enabledSmartCard:
            if state.detectedSmartCard:
                self.smartcard_lbl.set_text("SC")
            else:
                self.smartcard_lbl.set_text("sc")  
        else:
            self.smartcard_lbl.set_text("") 

    # end refresh

    def _truncate(self, text, max_chars):
        """Return text truncated to max_chars. Append '...' when truncated.

        This is intentionally simple and avoids any LVGL-specific API calls so
        it works across MicroPython LVGL bindings without guarded checks.
        """
        if not text:
            return ""
        s = str(text)
        if len(s) <= max_chars:
            return s
        if max_chars <= 3:
            return s[:3]
        return s[: max_chars]