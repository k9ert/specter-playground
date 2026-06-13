import lvgl as lv
from ..templates.specter_gui_base import SpecterGuiElement
from ..theming import apply_style
from ..utils.ui_consts import SCREEN_WIDTH, SCREEN_HEIGHT
from ..utils.ui_utils import set_size, set_pos, set_scroll


def modal_overlay(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, x=0, y=0):
    disp = lv.display_get_default()
    overlay = SpecterGuiElement(disp.get_layer_top())
    
    if x > SCREEN_WIDTH:
         print("WARNING: ModalOverlay x position exceeds screen width; clipping is applied.")
         x = min(x, SCREEN_WIDTH)
    if y > SCREEN_HEIGHT:
         print("WARNING: ModalOverlay y position exceeds screen height; clipping is applied.")
         y = min(y, SCREEN_HEIGHT)
    if x+width > SCREEN_WIDTH:
         print("WARNING: ModalOverlay dimensions exceed screen size; clipping is applied.")
         width = min(width, SCREEN_WIDTH - x)
    if y+height > SCREEN_HEIGHT:
         print("WARNING: ModalOverlay dimensions exceed screen size; clipping is applied.")
         height = min(height, SCREEN_HEIGHT - y)

    set_size(overlay, width, height)
    set_pos(overlay, x, y)
    set_scroll(overlay, horizontal=False, vertical=False)
    apply_style(overlay, "WIDGETS.OVERLAY")
    return overlay