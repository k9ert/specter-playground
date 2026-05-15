"""ui_utils — low-level LVGL and colour utility functions.

These helpers have no GUI-state dependencies and can be imported by any module
without risk of circular imports.
"""
import lvgl as lv


# ---------------------------------------------------------------------------
# Widget helpers
# ---------------------------------------------------------------------------

def delete_all_children_of(widget):
    for i in reversed(range(widget.get_child_count())):
        widget.get_child(i).delete()


def set_background_visible(obj, visible):
    """Set background opacity to fully opaque or fully transparent."""
    obj.set_style_bg_opa(lv.OPA.COVER if visible else lv.OPA.TRANSP, 0)


def configure_as_bare(obj, width=None, height=None, transparent_bg=True):
    """Zero padding, border, and radius on an existing lv.obj (mutating)."""
    if width is not None:
        obj.set_width(width)
    if height is not None:
        obj.set_height(height)
    obj.set_style_pad_all(0, 0)
    obj.set_style_border_width(0, 0)
    obj.set_style_radius(0, 0)
    set_background_visible(obj, not transparent_bg)


# ---------------------------------------------------------------------------
# Colour helpers
# ---------------------------------------------------------------------------

def to_lv_color(color):
    """Return *color* as an ``lv.color_t``.

    Accepts either an ``lv.color_t`` object or a hex string
    (``"0xRRGGBB"`` or ``"#RRGGBB"``).
    """
    if isinstance(color, str):
        val = int(color[1:], 16) if color.startswith("#") else int(color, 16)
        return lv.color_hex(val)
    return color


def to_hex_str(color):
    """Return *color* as a ``"0xRRGGBB"`` hex string.

    Accepts either an ``lv.color_t`` object or a hex string
    (``"0xRRGGBB"`` or ``"#RRGGBB"``).
    """
    if isinstance(color, str):
        val = int(color[1:], 16) if color.startswith("#") else int(color, 16)
        return "0x{:06X}".format(val)
    c32 = lv.color_to32(color)
    return "0x{:02X}{:02X}{:02X}".format(c32.ch.red, c32.ch.green, c32.ch.blue)
