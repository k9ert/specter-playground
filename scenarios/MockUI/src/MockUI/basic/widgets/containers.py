"""Container helpers — flex wrappers with Specter default styling.

All containers have border, padding, and radius zeroed by default.
"""

import lvgl as lv
from ..templates.specter_gui_base import SpecterGuiElement
from ..utils import (
    style_as_flex_container, style_as_screen_backdrop
)

#create an oject and apply flex container styling to it
def flex_container(parent, flow=lv.FLEX_FLOW.COLUMN, 
                   width=lv.SIZE_CONTENT, height=lv.SIZE_CONTENT, 
                   main_align = lv.FLEX_ALIGN.START, cross_align = lv.FLEX_ALIGN.CENTER, track_align = lv.FLEX_ALIGN.CENTER, 
                   scrollable=True):
    cont = SpecterGuiElement(parent)
    style_as_flex_container(cont,
                            flow=flow,
                            width=width,
                            height=height,
                            main_align=main_align,
                            cross_align=cross_align,
                            track_align=track_align,
                            scrollable=scrollable)
    return cont

#shortcut for common container types
def flex_col(parent, width=lv.SIZE_CONTENT, height=lv.SIZE_CONTENT, main_align=lv.FLEX_ALIGN.START):
    """lv.obj flex-column container."""
    return flex_container(
        parent, lv.FLEX_FLOW.COLUMN,
        width, height, main_align
    )

#shortcut for common container types
def flex_row(parent, width=lv.SIZE_CONTENT, height=lv.SIZE_CONTENT, main_align=lv.FLEX_ALIGN.SPACE_EVENLY):
    """lv.obj flex-row container."""
    return flex_container(
        parent, lv.FLEX_FLOW.ROW, 
        width, height, main_align
    )

def screen_backdrop(parent, width, height):
    scr = SpecterGuiElement(parent)
    style_as_screen_backdrop(scr, width=width, height=height)
    return scr