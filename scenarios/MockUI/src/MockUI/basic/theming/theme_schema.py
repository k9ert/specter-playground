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
        TEXT_EDIT_CURSOR      =  8        
        INFO_ITEM             =  9
        HELP_ICON             = 10
        MENU_SECTION_HEADER   = 11
        MENU_BUTTON           = 12
        MENU_BUTTON_FG        = 13        
        MENU_ICON             = 14
        MENU_LABEL            = 15
        MENU_SWITCH           = 16
        SUBMENU_INDICATOR     = 17
        DROP_UP_ADDBTN        = 18
        DROP_UP_ADDBTN_FG     = 19
        KEYBOARD              = 20
        PIN_BUTTON            = 21
        PIN_BUTTON_FG         = 22
        PIN_DISPLAY           = 23
        DELETE_BUTTON         = 24
        DELETE_BUTTON_FG      = 25
        MODAL_BODY            = 26
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
        BARE          = 50   # no padding/border/radius, transparent bg
        BORDERLESS    = 51   # zero border width, keep other layout defaults
        GROWS         = 52   # flex grow: with standard weight 1
        PARENT_WIDTH  = 53   # width = 100% of parent
        PARENT_HEIGHT = 54   # height = 100% of parent
        FLEX_COL      = 55   # flex layout with column direction
        FLEX_ROW      = 56   # flex layout with row direction
        FULL_SIZE     = 57   # fill parent to 100%
        ALL_CENTERED  = 58   # flex layout, all axes centered
        START         = 59   # flex layout, main axes start-aligned, others centered
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
        MUTED    = 130   # disabled/unusable widgets
        MUTED_BG = 131   # disabled/unusable widgets

    class ANIM:
        HORIZONTAL = 140   # anim_duration for horizontal slide/push transitions
        VERTICAL   = 141   # anim_duration for vertical slide transitions
        # reserved till 160

    class CONTAINER:
        SCREEN              = 160
        NAVBAR              = 161
        DROPUP              = 162
        DROP_UP_ROW         = 163    
        APP_SCREEN          = 164
        BATTERY             = 165
        CONTEXT_BAR         = 166
        INFO_CARD           = 167
        CONTENT             = 168
        TITLED_SCREEN       = 169
        TITLE_BAR           = 170
        MENU_CONTAINER      = 171
        MENU_ROW            = 172
        MENU_BUTTON_RHS     = 173
        MAIN_MENU           = 174
        INTERFACE_STATUS    = 175
        PIN_SCREEN          = 176
        PIN_BUTTON_ROW      = 177
        MODAL_WINDOW        = 178        
        MODAL_BUTTON_ROW    = 179
        FINGERPRINT_BADGE   = 180
        DELETE_BUTTON       = 181
        #reserved until end (255)