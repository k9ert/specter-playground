import lvgl as lv
from ..basic import (
    TitledScreen, BTC_ICONS,
    PIN_BTN_WIDTH, PIN_BTN_HEIGHT, SCREEN_WIDTH,
    shuffle,
    Btn,  flex_row, body_label, title_label, style_as_flex_container,
    apply_style
)

class LockedMenu(TitledScreen):
    """Simple lock screen that accepts a numeric PIN to unlock the device."""

    def __init__(self, parent):
        super().__init__(parent.i18n.t("LOCKED_MENU_TITLE"), parent)

        self.pin_buf = ""
        style_as_flex_container(self.body, flow=lv.FLEX_FLOW.COLUMN,
                                main_align = lv.FLEX_ALIGN.CENTER,
                                scrollable=False
                                )

        # Firmware version – shown as a subtitle directly under the title bar,
        # inside the TITLE_PADDING gap so it doesn't push body content down.
        self.fw_ver = body_label(self, self.t("LOCKED_MENU_FW_VERSION") + str(self.device_state.fw_version))
        self.fw_ver.align_to(self.title_bar, lv.ALIGN.OUT_BOTTOM_MID, 0, 1)

        # Instruction label
        self.instr = title_label(self.body, self.t("LOCKED_MENU_ENTER_PIN"), width=int(4*SCREEN_WIDTH/5))

        # masked PIN display
        self.mask_lbl = body_label(self.body, "", width=int(4*SCREEN_WIDTH/5))

        # keypad layout (3x4): digits in randomised order, Del, and OK
        chars = list("0123456789")
        shuffle(chars)  # shuffles in place

        keys = [
            [chars[0], chars[1], chars[2]],
            [chars[3], chars[4], chars[5]],
            [chars[6], chars[7], chars[8]],
            ["Del",    chars[9],    "OK"],
        ]

        for row in keys:
            row_cont = flex_row(
                self.body,
                width=lv.pct(100),
                height=lv.SIZE_CONTENT,
                main_align=lv.FLEX_ALIGN.CENTER,
            )
            for k in row:
                if k == "Del":
                    b = Btn(
                        row_cont,
                        icon=BTC_ICONS.CLEAR_CHARACTER,
                        size=(PIN_BTN_WIDTH, PIN_BTN_HEIGHT),
                        callback=lambda e: self._on_del(e),
                    )
                elif k == "OK":
                    b = Btn(
                        row_cont,
                        icon=BTC_ICONS.CHECK,
                        size=(PIN_BTN_WIDTH, PIN_BTN_HEIGHT),
                        callback=lambda e: self._on_ok(e),
                    )
                else:
                    b = Btn(
                        row_cont,
                        text=k,
                        size=(PIN_BTN_WIDTH, PIN_BTN_HEIGHT),
                        callback=lambda e, d=k: self._on_digit(e, d),
                    )
                apply_style(b, "WIDGET.PIN_BUTTON")

    def _update_mask(self):
        self.mask_lbl.set_text("*" * len(self.pin_buf))

    def _on_digit(self, e, d):
        if e.get_code() != lv.EVENT.CLICKED:
            return
        # append up to 8 digits
        if len(self.pin_buf) >= 8: #TODO: replace by call to HW/backend for max pin length
            return
        self.pin_buf += d
        self._update_mask()

    def _on_del(self, e):
        if e.get_code() != lv.EVENT.CLICKED:
            return
        if not self.pin_buf:
            return
        self.pin_buf = self.pin_buf[:-1]
        self._update_mask()

    def _on_ok(self, e):
        if e.get_code() != lv.EVENT.CLICKED:
            return
        pin = self.pin_buf
        # attempt unlock; DeviceState.unlock will check PIN
        unlocked = self.device_state.unlock(pin)
        if unlocked:
            # reset UI history and show main menu
            self.gui.ui_state.clear_history()
            self.on_navigate("main")
        else:
            # clear buffer and indicate failure (simple UX)
            self.pin_buf = ""
            self._update_mask()
