import lvgl as lv
from ..helpers import Battery
from .ui_consts import BTC_ICON_WIDTH, GREEN_HEX, ORANGE_HEX, PAD_SIZE, RED_HEX, STATUS_BTN_HEIGHT, STATUS_BTN_WIDTH, TWO_LETTER_SYMBOL_WIDTH, THREE_LETTER_SYMBOL_WIDTH, GREEN, ORANGE, RED
from .symbol_lib import BTC_ICONS

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
        self.power_lbl.set_text(lv.SYMBOL.POWER)
        self.power_lbl.center()
        self.power_btn.add_event_cb(self.power_cb, lv.EVENT.CLICKED, None)

        # Lock button (small)
        self.lock_btn = lv.button(self)
        self.lock_btn.set_size(STATUS_BTN_WIDTH, STATUS_BTN_HEIGHT)
        self.lock_ico = lv.image(self.lock_btn)
        BTC_ICONS.UNLOCK.add_to_parent(self.lock_ico)
        self.lock_ico.center()
        self.lock_btn.add_event_cb(self.lock_cb, lv.EVENT.CLICKED, None)

        # Battery icon
        self.batt_icon = Battery(self)
        self.batt_icon.VALUE = parent.specter_state.battery_pct
        self.batt_icon.update()

        # Center area: wallet name + type + net + peripheral indicators
        self.wallet_name_lbl = lv.label(self)
        self.wallet_name_lbl.set_text("")
        # conservative fixed width for the wallet name
        self.wallet_name_lbl.set_width(60)

        self.wallet_type_img = lv.image(self)
        # small fixed width for the type indicator (e.g. 'MuSig'/'SiSig')
        self.wallet_type_img.set_width(BTC_ICON_WIDTH)

        # Passphrase indicator (shows 'PP' when the active wallet has a passphrase configured)
        self.pp_img = lv.image(self)
        self.pp_img.set_width(BTC_ICON_WIDTH)

        self.net_lbl = lv.label(self)
        self.net_lbl.set_text("")
        self.net_lbl.set_width(35)

        # peripheral indicators – give them stable small widths so changing text won't shift layout
        self.qr_img = lv.image(self)
        self.qr_img.set_width(BTC_ICON_WIDTH)

        self.usb_img = lv.image(self)
        self.usb_img.set_width(BTC_ICON_WIDTH)

        self.sd_img = lv.image(self)
        self.sd_img.set_width(BTC_ICON_WIDTH)

        self.smartcard_img = lv.image(self)
        self.smartcard_img.set_width(BTC_ICON_WIDTH)

        # Language indicator (clickable selector)
        self.lang_lbl = lv.label(self)
        self.lang_lbl.set_text("")
        self.lang_lbl.set_width(THREE_LETTER_SYMBOL_WIDTH)
        self.lang_lbl.add_flag(lv.obj.FLAG.CLICKABLE)
        self.lang_lbl.add_event_cb(self.lang_clicked, lv.EVENT.CLICKED, None)
        
        # Language dropdown (created on demand)
        self.lang_dropdown = None

        # Apply a smaller font to all labels in the status bar
        self.font = lv.font_montserrat_12
        labels = [
            self.wallet_name_lbl,
            self.net_lbl,
            self.lang_lbl,
            self.qr_img,
            self.power_lbl,
        ]
        for ico in labels:
            ico.set_style_text_font(self.font, 0)

        # Make some icons clickable to navigate quickly
        # Clicking wallet-related icons opens the wallet management menu
        wallet_icons = [
            self.wallet_name_lbl,
            self.wallet_type_img,
            self.pp_img,
            self.net_lbl,
        ]

        for ico in wallet_icons:
            #make clickable
            ico.add_flag(lv.obj.FLAG.CLICKABLE)
            if ico == self.wallet_name_lbl:
                ico.add_event_cb(self.wallet_name_ico_clicked, lv.EVENT.CLICKED, None)
            else:
                ico.add_event_cb(self.wallet_config_ico_clicked, lv.EVENT.CLICKED, None)

        # Clicking peripheral indicators opens the interfaces menu
        peripheral_icons = [
            self.qr_img,
            self.usb_img,
            self.sd_img,
            self.smartcard_img,
        ]
        for ico in peripheral_icons:
            ico.add_flag(lv.obj.FLAG.CLICKABLE)
            ico.add_event_cb(self.peripheral_ico_clicked, lv.EVENT.CLICKED, None)

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
                # unlocking should be handled by the locked screen's PIN flow
                return
            else:
                # lock the device and force NavigationController to show the locked screen
                self.parent.specter_state.lock()
                # show_menu will detect is_locked and show the locked screen
                self.parent.show_menu(None)

    def wallet_name_ico_clicked(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            if self.parent.specter_state.active_wallet is None:
                if self.parent.ui_state.current_menu_id != "add_wallet":
                    self.parent.show_menu("add_wallet")
            else:
                if self.parent.ui_state.current_menu_id != "change_wallet":
                    self.parent.show_menu("change_wallet")

    def wallet_config_ico_clicked(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            if self.parent.specter_state.active_wallet is None:
                if self.parent.ui_state.current_menu_id != "add_wallet":
                    self.parent.show_menu("add_wallet")
            else:
                if self.parent.ui_state.current_menu_id != "manage_wallet":
                    self.parent.show_menu("manage_wallet")

    def peripheral_ico_clicked(self, e):
        if e.get_code() == lv.EVENT.CLICKED:
            if self.parent.ui_state.current_menu_id != "interfaces":
                self.parent.show_menu("interfaces")
    
    def lang_clicked(self, e):
        """Navigate to language selection menu when language label is clicked."""
        if e.get_code() == lv.EVENT.CLICKED:
            if self.parent.ui_state.current_menu_id != "select_language":
                self.parent.show_menu("select_language")

    def refresh(self, state):
        """Update visual elements from a SpecterState-like object."""
        # determine locked state once
        locked = state.is_locked

        # battery (shared between locked/unlocked)
        self.batt_icon.CHARGING = state.is_charging
        if state.has_battery:
            perc = state.battery_pct
            self.batt_icon.VALUE = perc
            self.batt_icon.update()
        else:
            self.batt_icon.VALUE = 100
            self.batt_icon.update()

        # language is always shown even when locked
        # Get current language from i18n manager (always available via NavigationController)
        lang_code = self.parent.i18n.get_language()
        if not lang_code:
            lang_code = "??"
        self.lang_lbl.set_text(self._truncate(lang_code.upper(), 3))

        # Now set elements that differ between locked/unlocked
        if locked:
            BTC_ICONS.LOCK.add_to_parent(self.lock_ico)
            # hide everything else which should not be visible when locked
            self.wallet_name_lbl.set_text("")
            self.wallet_type_img.set_src(None)
            self.pp_img.set_src(None)
            self.net_lbl.set_text("")
            self.qr_img.set_src(None)
            self.usb_img.set_src(None)
            self.sd_img.set_src(None)
            self.smartcard_img.set_src(None)
        else:
            BTC_ICONS.UNLOCK.add_to_parent(self.lock_ico)
            # wallet name and type separated into two labels (unlocked only)
            if state.active_wallet is not None:
                w = state.active_wallet
                name = getattr(w, "name", "") or ""
                self.wallet_name_lbl.set_text(self._truncate(name, 8))
                ico = BTC_ICONS.TWO_KEYS if w.isMultiSig else BTC_ICONS.KEY
                ico.add_to_parent(self.wallet_type_img)
                # show PP indicator if wallet reports a passphrase configured
                if w.active_passphrase is not None:
                    BTC_ICONS.PASSWORD.add_to_parent(self.pp_img)
                else:
                    self.pp_img.set_src(None)
                # net
                self.net_lbl.set_text(self._truncate(w.net or "", 4))
            else:
                self.wallet_name_lbl.set_text("")
                self.wallet_type_img.set_src(None)
                self.pp_img.set_src(None)
                self.net_lbl.set_text("")


            # peripherals
            # if feature is physically not present (hasXY = False: show nothing)
            # if feature is present and only can be enabled (USB+QR): show lower case when disabled and upper case when enabled
            # if feature is present and can be enabled and detected (SD + SmartCard): show lower case when enabled and upper case when also detected
            if state.hasQR:
                if state.enabledQR:
                    BTC_ICONS.QR_CODE(GREEN_HEX).add_to_parent(self.qr_img)
                else:
                    BTC_ICONS.QR_CODE(ORANGE_HEX).add_to_parent(self.qr_img)
            else:
                self.qr_img.set_src(None)

            if state.hasUSB:
                if state.enabledUSB:
                    BTC_ICONS.USB(GREEN_HEX).add_to_parent(self.usb_img)
                else:
                    BTC_ICONS.USB(ORANGE_HEX).add_to_parent(self.usb_img)
            else:
                self.usb_img.set_src(None)

            if state.hasSD:
                if state.enabledSD:
                    if state.detectedSD:
                        BTC_ICONS.SD_CARD(GREEN_HEX).add_to_parent(self.sd_img)
                    else:
                        BTC_ICONS.SD_CARD(ORANGE_HEX).add_to_parent(self.sd_img)
                else:
                    BTC_ICONS.SD_CARD(RED_HEX).add_to_parent(self.sd_img)
            else:
                self.sd_img.set_src(None)

            if state.hasSmartCard:
                if state.enabledSmartCard:
                    if state.detectedSmartCard:
                        BTC_ICONS.SMARTCARD(GREEN_HEX).add_to_parent(self.smartcard_img)
                    else:
                        BTC_ICONS.SMARTCARD(ORANGE_HEX).add_to_parent(self.smartcard_img)
                else:
                    BTC_ICONS.SMARTCARD(RED_HEX).add_to_parent(self.smartcard_img)
            else:
                self.smartcard_img.set_src(None)

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
