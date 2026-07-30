import lvgl as lv
from ..basic import (
    TitledScreen, BTC_ICONS, SpecterGuiElement,
    shuffle,
    Btn,
    apply_style,
    make_label,
    set_scroll,
)

class LockedMenu(TitledScreen):
    """Simple lock screen that accepts a numeric PIN to unlock the device."""

    def __init__(self, parent):
        super().__init__(parent.t("LOCKED_MENU_TITLE"), parent)

        self.pin_buf = ""
        apply_style(self.body, "CONTAINER.PIN_SCREEN")

        # Firmware version – shown as a subtitle directly under the title bar
        self.fw_ver = make_label(self.body, self.t("LOCKED_MENU_FW_VERSION") + str(self.device_state.fw_version))
        apply_style(self.fw_ver, "WIDGET.INFO_ITEM")

        # Instruction label
        self.instr = make_label(self.body, self.t("LOCKED_MENU_ENTER_PIN"))
        apply_style(self.instr, "WIDGET.SCREEN_TITLE")

        # masked PIN display
        self.mask_lbl = make_label(self.body, "")
        apply_style(self.mask_lbl, "WIDGET.PIN_DISPLAY")

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
            row_cont = SpecterGuiElement(self.body)
            apply_style(row_cont, "CONTAINER.PIN_BUTTON_ROW")
            set_scroll(row_cont, vertical=False, horizontal=False)
            
            for k in row:
                if k == "Del":
                    b = Btn(
                        row_cont,
                        icon=BTC_ICONS.CLEAR_CHARACTER,
                        background_style="WIDGET.PIN_BUTTON",
                        foreground_style="WIDGET.PIN_BUTTON_FG",
                        callback=self._on_del,
                    )
                elif k == "OK":
                    b = Btn(
                        row_cont,
                        icon=BTC_ICONS.CHECK,
                        background_style="WIDGET.PIN_BUTTON",
                        foreground_style="WIDGET.PIN_BUTTON_FG",
                        callback=self._on_ok,
                    )
                else:
                    b = Btn(
                        row_cont,
                        text=k,
                        background_style="WIDGET.PIN_BUTTON",
                        foreground_style="WIDGET.PIN_BUTTON_FG",
                        callback=lambda d=k: self._on_digit(d),
                    )

    def _update_mask(self):
        self.mask_lbl.set_text("*" * len(self.pin_buf))

    def _on_digit(self, d):
        # append up to 8 digits
        if len(self.pin_buf) >= 8: #TODO: replace by call to HW/backend for max pin length
            return
        self.pin_buf += d
        self._update_mask()

    def _on_del(self):
        if not self.pin_buf:
            return
        self.pin_buf = self.pin_buf[:-1]
        self._update_mask()

    def _on_ok(self):
        pin = self.pin_buf
        # attempt unlock; DeviceState.unlock will check PIN
        unlocked = self.device_state.unlock(pin)
        if unlocked:
            # reset UI history and show main menu
            self.ui_state.clear_history()
            self.on_navigate("main")
        else:
            # clear buffer and indicate failure (simple UX)
            self.pin_buf = ""
            self._update_mask()
