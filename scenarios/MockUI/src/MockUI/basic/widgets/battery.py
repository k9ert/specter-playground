import lvgl as lv
from .. import BLACK_HEX, GREEN_HEX, ORANGE_HEX, RED_HEX, WHITE_HEX, BTC_ICON_WIDTH, BTC_ICON_ZOOM
from ..symbol_lib import BTC_ICONS
from . import make_icon, set_visible
from ..specter_gui_base import configure_as_bare

class Battery(lv.obj):
    VALUE = None
    CHARGING = None
    LEVELS = [
        (95, BTC_ICONS.BATTERY_FULL_OUTLINE,  WHITE_HEX),
        (75, BTC_ICONS.BATTERY_4_OUTLINE,     GREEN_HEX),
        (50, BTC_ICONS.BATTERY_3_OUTLINE,     ORANGE_HEX),
        (25, BTC_ICONS.BATTERY_2_OUTLINE,     RED_HEX),
        (0,  BTC_ICONS.BATTERY_EMPTY_OUTLINE, RED_HEX),
    ]

    def __init__(self, parent, width=BTC_ICON_WIDTH, height=BTC_ICON_WIDTH):
        super().__init__(parent)
        configure_as_bare(self, width=width, height=height, transparent_bg=True)
        self.level_bg = make_icon(self, BTC_ICONS.BATTERY_EMPTY, WHITE_HEX)
        self.level_bg.align(lv.ALIGN.CENTER, 0, 0)
        self.level = make_icon(self, BTC_ICONS.BATTERY_FULL_OUTLINE, WHITE_HEX)
        self.level.align(lv.ALIGN.CENTER, 0, 0)
        self.level_ol = make_icon(self, BTC_ICONS.BATTERY_EMPTY_OUTLINE, WHITE_HEX)
        self.level_ol.align(lv.ALIGN.CENTER, 0, 0)        
        self.charge = make_icon(self, BTC_ICONS.LIGHTNING, WHITE_HEX, zoom=2*BTC_ICON_ZOOM//3)
        self.charge.align(lv.ALIGN.CENTER, 0, 0)
        self.update()

    def update(self):
        if self.VALUE is None:
            set_visible(self.level_bg, False)
            set_visible(self.level, False)
            set_visible(self.charge, False)
            return

        set_visible(self.level_bg, True)
        set_visible(self.level, True)

        for v, level_icon, level_color in self.LEVELS:
            if self.VALUE >= v:
        
                if self.CHARGING:
                    # when charging user has taken appropriate action -> do not highlight
                    # low battery levels too much anymore -> just set levels and 
                    # not background to level color. Make background invisible
                    set_visible(self.level_bg, False)
                    level_icon(level_color).apply_icon_to(self.level)
                else:
                    # Use colors as they usually encode urgency of user action better than
                    # plain level/value of battery fill
                    if level_color == WHITE_HEX:
                        # Full battery, no need to draw user attention to this icon.
                        # Hence use full neutral (=white) coloring
                        set_visible(self.level_bg, True)
                        BTC_ICONS.BATTERY_EMPTY(WHITE_HEX).apply_icon_to(self.level_bg)
                        set_visible(self.level, False)
                        #level_icon(level_color).apply_icon_to(self.level)
                    elif level_color == GREEN_HEX:
                        # Almost full battery, no need to draw user attention to this icon.
                        # Hence only color levels in green (and not whole background)
                        set_visible(self.level_bg, False)
                        level_icon(level_color).apply_icon_to(self.level)                        
                    else:
                        # Low battery, important to draw user attention -> color whole icon
                        # background with level color
                        set_visible(self.level_bg, True)
                        BTC_ICONS.BATTERY_EMPTY(level_color).apply_icon_to(self.level_bg)
                        level_icon(WHITE_HEX).apply_icon_to(self.level)

                #always draw outine in white to have clear border and better visibility on different backgrounds
                BTC_ICONS.BATTERY_EMPTY_OUTLINE(WHITE_HEX).apply_icon_to(self.level_ol)
                # Charging state is important to show user has taken appropriate action -> highlight with charging icon
                set_visible(self.charge, self.CHARGING)

                break
    
    def set_visible(self, visible):
        set_visible(self.level_bg, visible)
        set_visible(self.level, visible)
        set_visible(self.charge, visible)
        set_visible(self.level_ol, visible)