import lvgl as lv
from .menu import GenericMenu


class LockedMenu(GenericMenu):
    """Simple lock screen that accepts a numeric PIN to unlock the device."""

    def __init__(self, parent, *args, **kwargs):
        # parent is the NavigationController
        super().__init__("locked", "Device Locked", [], parent, *args, **kwargs)

        self.parent = parent
        self.pin_buf = ""

        # center the content in this menu's container
        self.container.set_flex_align(
            lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER
        )

        # Instruction label
        instr = lv.label(self.container)
        instr.set_text("Enter PIN to unlock:")
        instr.set_width(200)
        instr.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)

        # masked PIN display
        self.mask_lbl = lv.label(self.container)
        self.mask_lbl.set_text("")
        self.mask_lbl.set_width(200)
        self.mask_lbl.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)

        # keypad layout (3x4): 1..9, Del, 0, OK
        keys = [
            ["1", "2", "3"],
            ["4", "5", "6"],
            ["7", "8", "9"],
            ["Del", "0", "OK"],
        ]

        for row in keys:
            row_cont = lv.obj(self.container)
            # make the row container slightly taller than the buttons so they fit
            row_cont.set_layout(lv.LAYOUT.FLEX)
            row_cont.set_flex_flow(lv.FLEX_FLOW.ROW)
            row_cont.set_width(lv.pct(100))
            row_cont.set_height(48)
            # center buttons in the row and remove visible backgrounds/borders
            row_cont.set_flex_align(
                lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER
            )
            row_cont.set_style_border_width(0, 0)
            row_cont.set_style_pad_all(0, 0)

            for k in row:
                b = lv.button(row_cont)
                b.set_width(60)
                b.set_height(36)
                lb = lv.label(b)
                lb.set_text(k)
                lb.center()
                if k == "Del":
                    b.add_event_cb(lambda e: self._on_del(e), lv.EVENT.CLICKED, None)
                elif k == "OK":
                    b.add_event_cb(lambda e: self._on_ok(e), lv.EVENT.CLICKED, None)
                else:
                    # capture digit in default arg
                    b.add_event_cb(lambda e, d=k: self._on_digit(e, d), lv.EVENT.CLICKED, None)

    def _update_mask(self):
        self.mask_lbl.set_text("*" * len(self.pin_buf))

    def _on_digit(self, e, d):
        if e.get_code() != lv.EVENT.CLICKED:
            return
        # append up to 8 digits
        if len(self.pin_buf) >= 8:
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
        # attempt unlock; SpecterState.unlock will check PIN
        unlocked = self.parent.specter_state.unlock(pin)
        if unlocked:
            # reset UI history and show main menu
            self.parent.ui_state.clear_history()
            # Ensure state updated
            self.parent.specter_state.is_locked = False
            # load main menu fresh
            self.parent.ui_state.current_menu_id = "main"
            # delete current and create main menu
            if self.parent.current_screen:
                self.parent.current_screen.delete()
            self.parent.current_screen = None
            self.parent.show_menu(None)
        else:
            # clear buffer and indicate failure (simple UX)
            self.pin_buf = ""
            self._update_mask()
