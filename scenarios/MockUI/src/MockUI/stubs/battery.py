import lvgl as lv
from ..basic import GREEN_HEX, ORANGE_HEX, RED_HEX
from ..basic.widgets import set_label_color
from ..basic.specter_gui_base import configure_as_bare

class Battery(lv.obj):
    VALUE = None
    CHARGING = None
    LEVELS = [
        (95, lv.SYMBOL.BATTERY_FULL,  GREEN_HEX),
        (75, lv.SYMBOL.BATTERY_3,     GREEN_HEX),
        (50, lv.SYMBOL.BATTERY_2,     ORANGE_HEX),
        (25, lv.SYMBOL.BATTERY_1,     RED_HEX),
        (0,  lv.SYMBOL.BATTERY_EMPTY, RED_HEX),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        configure_as_bare(self)
        self.level = lv.label(self)
        self.icon = lv.label(self)
        self.charge = lv.label(self)
        self.set_size(30,20)
        # self.bar = lv.bar(self)
        self.update()

    def update(self):
        if self.VALUE is None:
            self.icon.set_text("")
            self.level.set_text("")
            self.charge.set_text("")
            return
        for v, icon, color in self.LEVELS:
            if self.VALUE >= v:
                if self.CHARGING:
                    self.level.set_text(icon)
                    set_label_color(self.level, GREEN_HEX)
                else:
                    self.level.set_text(icon)
                    set_label_color(self.level, color)
                break
        self.icon.set_text(lv.SYMBOL.BATTERY_EMPTY)
        self.icon.align(lv.ALIGN.CENTER, 0, 0)
        self.level.align(lv.ALIGN.CENTER, 0, 0)
        if self.CHARGING:
            self.charge.set_text(lv.SYMBOL.CHARGE)
            self.charge.align(lv.ALIGN.CENTER, -5, 0)
        else:
            self.charge.set_text("")
