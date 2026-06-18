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
    """Minimum set of font slots a theme JSON must define.
       The fonts need to be sorted in descending size.
    """
    TITLE = 0
    TEXT  = 1
    SMALL = 2


class SpecterStylePalette:
    """Integer style-token keys.  Pass to ``apply_style(obj, key)``."""

    class WIDGET:
        SCREEN_TITLE          =  1
        OVERLAY               =  2
        NAVBAR_BUTTON         =  3
        NAVBAR_BUTTON_FG      =  4
        BUTTON                =  5
        BUTTON_FG             =  6
        TEXT_EDIT             =  7
        INFO_ITEM             =  8
        HELP_ICON             =  9
        MENU_SECTION_HEADER   = 10
        MENU_BUTTON           = 11
        MENU_BUTTON_FG        = 12        
        MENU_ICON             = 13
        MENU_SWITCH           = 14
        SUBMENU_INDICATOR     = 15
        DROP_UP_ADDBTN        = 16
        DROP_UP_ADDBTN_FG     = 17
        KEYBOARD              = 18
        BATTERY               = 19
        PIN_BUTTON            = 20
        PIN_BUTTON_FG         = 21
        PIN_DISPLAY           = 22
        DELETE_BUTTON         = 23
        DELETE_BUTTON_FG      = 24
    
        # reserved till 40

    class TEXT:
        DEFAULT = 40    # TEXT font
        TITLE   = 41    # TITLE font
        SMALL   = 42    # SMALL font
        LEFT    = 43    # left-aligned text (default is centered)
        CENTER  = 44    # centered text
        RIGHT   = 45    # right-aligned text
        BODY    = 49    # enables wrapping
        # reserved till 50

    class LAYOUT:
        BARE        = 50   # no padding/border/radius, transparent bg
        BORDERLESS  = 51   # zero border width, keep other layout defaults
        GROWS       = 52   # flex grow: with standard weight 1
        FLEX_COL    = 53   # flex layout with column direction
        FLEX_ROW    = 54   # flex layout with row direction
        
        # reserved till 60

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

    class SWITCH:
        TRACK     = 120   # apply with lv.PART.MAIN
        INDICATOR = 121   # apply with lv.PART.INDICATOR
        KNOB      = 122   # apply with lv.PART.KNOB
        # reserved till 130

    class MODIFIER:
        MUTED = 130   # disabled/unusable widgets

    class CONTAINER:
        SCREEN              = 160
        NAVBAR              = 161
        MAIN_MENU           = 162
        MENU_CONTAINER      = 163
        MENU_ROW            = 164
        CONTEXT_BAR         = 165
        DROPUP              = 166
        DROP_UP_ROW         = 167
        INTERFACE_STATUS    = 168
        MODAL_WINDOW        = 169
        TITLE_BAR           = 169   
        #reserved until end (255)