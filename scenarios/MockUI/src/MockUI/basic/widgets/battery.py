import lvgl as lv
from .icon_widgets import make_icon, apply_icon
from ..utils import BTC_ICON_WIDTH, set_size, set_align
from ..symbol_lib import BTC_ICONS
from ..theming import apply_style

ALL_STATES = (
    lv.STATE.USER_1 | lv.STATE.USER_2 | lv.STATE.USER_3 | lv.STATE.USER_4
)

level_states = {
    "full": lv.STATE.USER_1,
    "high": lv.STATE.USER_2,
    "mid":  lv.STATE.USER_3,
    "low":  lv.STATE.USER_4,
}
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
        apply_style(self.level_bg, "APPEARANCE.INVISIBLE", lv.STATE.DISABLED)
        apply_style(self.level_bg, "FG.DEFAULT", lv.STATE.USER_1)
        apply_style(self.level_bg, "FG.SUCCESS", lv.STATE.USER_2)
        apply_style(self.level_bg, "FG.WARNING", lv.STATE.USER_3)
        apply_style(self.level_bg, "FG.DANGER",  lv.STATE.USER_4)

        self.level = make_icon(self, BTC_ICONS.BATTERY_FULL_OUTLINE)
        set_align(self.level, lv.ALIGN.CENTER)
        apply_style(self.level, "WIDGET.BATTERY")
        apply_style(self.level, "APPEARANCE.INVISIBLE", lv.STATE.DISABLED)
        apply_style(self.level, "FG.DEFAULT", lv.STATE.USER_1)
        apply_style(self.level, "FG.SUCCESS", lv.STATE.USER_2)
        apply_style(self.level, "FG.WARNING", lv.STATE.USER_3)
        apply_style(self.level, "FG.DANGER",  lv.STATE.USER_4)

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
            self.level_bg.set_state(lv.STATE.DISABLED, True)
            self.level.set_state(lv.STATE.DISABLED, True)
            self.charge.set_state(lv.STATE.DISABLED, True)
            return

        self.level_bg.set_state(lv.STATE.DISABLED, False)
        self.level.set_state(lv.STATE.DISABLED, False)

        for v, level_icon, level in self.LEVELS:
            if self.value >= v:
        
                if self.charging:
                    # when charging user has taken appropriate action -> do not highlight
                    # low battery levels too much anymore -> just set levels and 
                    # not background to level color. Make background invisible
                    self.level_bg.set_state(lv.STATE.DISABLED, True)
                    apply_icon(self.level, level_icon)
                    self.level.set_state(ALL_STATES, False)
                    self.level.set_state(level_states[level], True)
                else:
                    if level == "full":
                        # Full battery, no need to draw user attention to this icon.
                        # Hence use full neutral coloring
                        apply_icon(self.level_bg, BTC_ICONS.BATTERY_EMPTY)
                        self.level_bg.set_state(ALL_STATES, False)
                        self.level_bg.set_state(level_states[level], True)
                        self.level.set_state(lv.STATE.DISABLED, True)
                    elif level == "high":
                        # Almost full battery, no need to draw user attention to this icon.
                        # Hence only color levels in green (and not whole background)
                        self.level_bg.set_state(lv.STATE.DISABLED, True)

                        apply_icon(self.level, level_icon)
                        self.level.set_state(ALL_STATES, False)
                        self.level.set_state(level_states[level], True)
                    else:
                        # Low battery, important to draw user attention -> color whole icon
                        # background with level color
                        apply_icon(self.level_bg, BTC_ICONS.BATTERY_EMPTY)
                        self.level_bg.set_state(ALL_STATES, False)
                        self.level_bg.set_state(level_states[level], True)

                        apply_icon(self.level, level_icon)
                        self.level.set_state(ALL_STATES, False)
                        self.level.set_state(level_states["full"], True)

                #always draw outline in white to have clear border and better visibility on different backgrounds
                apply_icon(self.level_ol, BTC_ICONS.BATTERY_EMPTY_OUTLINE)

                # Charging state is important to show user has taken appropriate action -> highlight with charging icon
                if self.charging:
                    self.charge.set_state(lv.STATE.DISABLED, False)
                else:
                    self.charge.set_state(lv.STATE.DISABLED, True)

                break