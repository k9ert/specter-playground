"""Image helpers — lv.image wrappers with Specter default styling."""

import lvgl as lv
from ..utils import BTC_ICON_WIDTH, set_size, set_scale

def apply_icon(img, icon):
    img.set_src(icon.get_image_dsc())

def make_icon(parent, icon, width=None, height=None):
    """Create an ``lv.image`` widget and apply *icon* to it.

    Args:
        parent: LVGL parent object.
        icon:   Icon factory (e.g. ``BTC_ICONS.RELAY``) or an ``Icon`` instance.
        width:  Targeted width in pixels.  Defaults to ``BTC_ICON_WIDTH``.
        height: Targeted height in pixels.  Defaults to ``BTC_ICON_WIDTH``.
        zoom:   Zoom factor for the icon.  Defaults to ``BTC_ICON_ZOOM``.

    Returns:
        The created ``lv.image`` widget.
    """
    """Apply *icon* bitmap and sizing to an existing ``lv.image`` widget."""
    if width is None and height is None:
        target_size = BTC_ICON_WIDTH
    elif height is None:
        target_size = width
    elif width is None:
        target_size = height
    elif width != height:
        print("WARNING: make_icon called with non-square dimensions; falling back to smaller square.")
        target_size = min(width, height)
    scale = target_size * 256 // icon.width

    img = lv.image(parent)
    apply_icon(img, icon)
    set_scale(img, scale)

    return img
