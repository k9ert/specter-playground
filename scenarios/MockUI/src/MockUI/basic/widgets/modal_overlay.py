import lvgl as lv
from ..templates.specter_gui_base import SpecterGuiElement
from ..theming import apply_style
from ..utils.ui_utils import set_size, set_pos, set_scroll


def modal_overlay(width=None, height=None, x=0, y=0):
    disp = lv.display_get_default()
    overlay = SpecterGuiElement(disp.get_layer_top())
    max_x = overlay.gui.get_width()
    max_y = overlay.gui.get_height()

    if width is None:
        width = max_x
    if height is None:
        height = max_y
    
    if x > max_x:
         print("WARNING: ModalOverlay x position exceeds screen width; clipping is applied.")
         x = min(x, max_x)
    if y > max_y:
         print("WARNING: ModalOverlay y position exceeds screen height; clipping is applied.")
         y = min(y, max_y)
    if x+width > max_x:
         print("WARNING: ModalOverlay dimensions exceed screen size; clipping is applied.")
         width = min(width, max_x - x)
    if y+height > max_y:
         print("WARNING: ModalOverlay dimensions exceed screen size; clipping is applied.")
         height = min(height, max_y - y)

    set_size(overlay, width, height)
    set_pos(overlay, x, y)
    set_scroll(overlay, horizontal=False, vertical=False)
    apply_style(overlay, "WIDGET.OVERLAY")
    return overlay