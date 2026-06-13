import lvgl as lv
from .icon_widgets import make_icon, apply_icon
from ..utils import BTC_ICON_WIDTH, set_size, set_align
from ..symbol_lib import BTC_ICONS
from ..theming import apply_style

ALL_STATES = (
    lv.STATE.USER_1 | lv.STATE.USER_2 | lv.STATE.USER_3 | lv.STATE.USER_4 | lv.STATE.DISABLED
)

level_states = {
    "full": lv.STATE.USER_1,
    "high": lv.STATE.USER_2,
    "mid":  lv.STATE.USER_3,
    "low":  lv.STATE.USER_4,
    "off":  lv.STATE.DISABLED,
}

def set_level(obj, level):
        obj.set_state(ALL_STATES, False)
        obj.set_state(level_states[level], True)

class Battery(lv.obj):
    LEVELS = [
        (95, BTC_ICONS.BATTERY_FULL_OUTLINE,   "full"),
        (75, BTC_ICONS.BATTERY_4_OUTLINE,      "high"),
        (55, BTC_ICONS.BATTERY_3_OUTLINE,      "high"),
        (35, BTC_ICONS.BATTERY_2_OUTLINE,      "mid"),
        (18, BTC_ICONS.BATTERY_EMPTY_OUTLINE,  "low"),
    ]

    def __init__(self, parent, width=BTC_ICON_WIDTH, height=BTC_ICON_WIDTH):
        super().__init__(parent)
        set_size(self, width=width, height=height)
        self.value = None      # battery percentage (0-100) or None to hide
        self.charging = None   # bool or None

        self.level_bg = make_icon(self, BTC_ICONS.BATTERY_EMPTY)
        set_align(self.level_bg, lv.ALIGN.CENTER)
        apply_style(self.level_bg, "WIDGET.BATTERY")
        apply_style(self.level_bg, "FG.DEFAULT", lv.STATE.USER_1)
        apply_style(self.level_bg, "FG.SUCCESS", lv.STATE.USER_2)
        apply_style(self.level_bg, "FG.WARNING", lv.STATE.USER_3)
        apply_style(self.level_bg, "FG.DANGER",  lv.STATE.USER_4)
        apply_style(self.level_bg, "APPEARANCE.INVISIBLE", lv.STATE.DISABLED)        

        self.level = make_icon(self, BTC_ICONS.BATTERY_FULL_OUTLINE)
        set_align(self.level, lv.ALIGN.CENTER)
        apply_style(self.level, "WIDGET.BATTERY")
        apply_style(self.level, "FG.DEFAULT", lv.STATE.USER_1)
        apply_style(self.level, "FG.SUCCESS", lv.STATE.USER_2)
        apply_style(self.level, "FG.WARNING", lv.STATE.USER_3)
        apply_style(self.level, "FG.DANGER",  lv.STATE.USER_4)
        apply_style(self.level, "APPEARANCE.INVISIBLE", lv.STATE.DISABLED)

        self.level_ol = make_icon(self, BTC_ICONS.BATTERY_EMPTY_OUTLINE)
        set_align(self.level_ol, lv.ALIGN.CENTER)
        apply_style(self.level_ol, ["WIDGET.BATTERY", "FG.DEFAULT"])

        self.charge = make_icon(self, BTC_ICONS.LIGHTNING, width=int(2*BTC_ICON_WIDTH//3))
        set_align(self.charge, lv.ALIGN.CENTER)
        apply_style(self.charge, ["WIDGET.BATTERY", "FG.DEFAULT"])
        apply_style(self.charge, "APPEARANCE.INVISIBLE", lv.STATE.DISABLED)

        self.update()

    def update(self, value=None, charging=None):
        """Refresh the widget. If *value*/*charging* are provided, update state first."""
        if value is not None:
            self.value = value
        if charging is not None:
            self.charging = charging
        if self.value is None:
            set_level(self.level_bg, "off")
            set_level(self.level, "off")
            set_level(self.charge, "off")
            return

        for v, level_icon, level in self.LEVELS:
            if self.value >= v:
        
                if self.charging:
                    # when charging user has taken appropriate action -> do not highlight
                    # low battery levels too much anymore -> just set levels and 
                    # not background to level color. Make background invisible
                    set_level(self.level_bg, "off")
                    apply_icon(self.level, level_icon)
                    set_level(self.level, level)
                else:
                    if level == "full":
                        # Full battery, no need to draw user attention to this icon.
                        # Hence use full neutral coloring
                        apply_icon(self.level_bg, BTC_ICONS.BATTERY_EMPTY)
                        set_level(self.level_bg, level)

                        set_level(self.level, "off")
                    elif level == "high":
                        # Almost full battery, no need to draw user attention to this icon.
                        # Hence only color levels in green (and not whole background)
                        set_level(self.level_bg, "off")

                        apply_icon(self.level, level_icon)
                        set_level(self.level, level)
                    else:
                        # Low battery, important to draw user attention -> color whole icon
                        # background with level color
                        apply_icon(self.level_bg, BTC_ICONS.BATTERY_EMPTY)
                        set_level(self.level_bg, level)

                        apply_icon(self.level, level_icon)
                        set_level(self.level, "full")

                #always draw outline in white to have clear border and better visibility on different backgrounds
                apply_icon(self.level_ol, BTC_ICONS.BATTERY_EMPTY_OUTLINE)

                # Charging state is important to show user has taken appropriate action -> highlight with charging icon
                if self.charging:
                    set_level(self.charge, "full")
                else:
                    set_level(self.charge, "off")

                break