"""Image helpers — lv.image wrappers with Specter default styling."""

import lvgl as lv
from ..utils.ui_consts import BTC_ICON_WIDTH, BTC_ICON_ZOOM, WHITE_HEX


def make_icon(parent, icon, color=WHITE_HEX, width=BTC_ICON_WIDTH, zoom=BTC_ICON_ZOOM):
    """Create an ``lv.image`` widget and apply *icon* to it.

    Args:
        parent: LVGL parent object.
        icon:   Icon factory (e.g. ``BTC_ICONS.RELAY``) called with *color*,
                or a pre-resolved ``Icon`` instance passed directly.
        color:  Hex color string passed to the icon factory.  Defaults to
                ``WHITE_HEX`` (standard Specter icon colour).  Pass ``None``
                when *icon* is already a resolved ``Icon`` instance.
        width:  Widget width in pixels.  Defaults to ``BTC_ICON_WIDTH``.

    Returns:
        The created ``lv.image`` widget.
    """
    resolved = icon(color) if color is not None else icon
    img = lv.image(parent)
    img.set_width(width)
    resolved.apply_icon_to(img, zoom=zoom)
    return img

def set_visible(icon_widget, visible):
    """Set *icon_widget* visible or hidden by adjusting its opacity.

    Args:
        icon_widget: The ``lv.image`` widget containing the icon.
        visible:     Boolean visibility flag.
    """
    if visible:
        icon_widget.set_style_opa(lv.OPA.COVER, 0)
    else:
        icon_widget.set_style_opa(lv.OPA.TRANSP, 0)
