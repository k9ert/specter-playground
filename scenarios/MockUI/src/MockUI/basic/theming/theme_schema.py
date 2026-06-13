"""theme_schema — palette schema constants for the Specter UI theming system.

These classes define the *keys* (integer indices) used to address color, font,
and style slots in compiled theme binaries.  They have no dependency on LVGL or
compiler infrastructure and can be imported freely by widget helpers.

Runtime consumers import from the package:
    from ..theming import SpecterColorPalette, SpecterFontPalette, SpecterStylePalette
"""


class SpecterColorPalette:
    """Minimum set of color slots a theme JSON must define."""
    PRIMARY    = 0
    SECONDARY  = 1
    TERTIARY   = 2
    QUATERNARY = 3
    NEUTRAL    = 4
    SUCCESS    = 5
    WARNING    = 6
    DANGER     = 7
    CANVAS     = 8
    INK        = 9


class SpecterFontPalette:
    """Minimum set of font slots a theme JSON must define."""
    TEXT  = 0
    TITLE = 1
    SMALL = 2


class SpecterStylePalette:
    """Integer style-token keys.  Pass to ``apply_style(obj, key)``."""

    class WIDGET:
        SCREEN                =  0
        SCREEN_TITLE          =  1
        OVERLAY               =  2
        NAVBAR                =  3
        NAVBAR_BUTTON         =  4
        MODAL_WINDOW          =  5
        BUTTON                =  6
        TEXT_EDIT             =  7
        INFO_ITEM             =  8
        HELP_ICON             =  9
        MENU_SECTION_HEADER   = 10
        MENU_BUTTON           = 11
        MENU_ICON             = 12
        MENU_BUTTON_LABEL     = 13
        MENU_SWITCH           = 14
        SUBMENU_INDICATOR     = 15
        DROPUP                = 16
        DROP_UP_ROW           = 17
        DROP_UP_ADDBTN        = 18
        CONTEXT_BAR           = 21
        KEYBOARD              = 22
        BATTERY               = 23
        PIN_BUTTON            = 24
        # reserved till 40

    class TEXT:
        DEFAULT = 40    # TEXT font
        TITLE   = 41    # TITLE font
        SMALL   = 42    # SMALL font
        BODY    = 43    # enables wrapping
        # reserved till 50

    class LAYOUT:
        BARE        = 50   # no padding/border/radius, transparent bg

    class APPEARANCE:
        VISIBLE     = 60   # full opacity for FG and BG
        TRANSPARENT = 61   # bg fully transparent
        INVISIBLE   = 62   # opacity = 0 for FG and BG
        SEE_THROUGH = 63   # FG and BG semi-transparent (~50% scrim)
        # reserved till 70

    class FG:
        DEFAULT   = 70
        SUCCESS   = 71
        WARNING   = 72
        DANGER    = 73
        HIGHLIGHT = 75   # accent, for emphasis
        LIGHT     = 76   # WHITEish — readable on dark fills
        DARK      = 77   # BLACKish — readable on light fills
        # reserved till 80

    class BG:
        DEFAULT   = 80   # SURFACE (normal background)
        SUCCESS   = 81
        WARNING   = 82
        DANGER    = 83
        # 84 reserved
        HIGHLIGHT = 85   # accent, for emphasis
        LIGHT     = 86   # WHITEish — readable with dark text/icons
        DARK      = 87   # BLACKish — readable with light text/icons
        # reserved till 90

    class BORDER:
        TOP    = 90
        BOTTOM = 91
        LEFT   = 92
        RIGHT  = 93
        # reserved till 100

    class CONTEXT:
        SEED     = 100
        WALLET   = 101
        MAIN     = 102
        SETTINGS = 103
        # reserved till 110

    class SLIDER:
        TRACK     = 110   # apply with lv.PART.MAIN
        INDICATOR = 111   # apply with lv.PART.INDICATOR
        KNOB      = 112   # apply with lv.PART.KNOB
        # reserved till 120

    class MODIFIER:
        MUTED = 120   # disabled/unusable widgets
