"""ui_utils — low-level LVGL and colour utility functions.

These helpers have no GUI-state dependencies and can be imported by any module
without risk of circular imports.
"""
import lvgl as lv
import rng  # TODO: clarify if this should be encapsulated in a general HW/GUI interface


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


def configure_flex(obj,
                   flow=lv.FLEX_FLOW.COLUMN,
                   main=lv.FLEX_ALIGN.START,
                   cross=lv.FLEX_ALIGN.CENTER,
                   track=lv.FLEX_ALIGN.CENTER):
    """Apply a flex layout to *obj* with sensible defaults.

    Defaults match the typical titled-menu body: column flow with
    START / CENTER / CENTER alignment.
    """
    obj.set_flex_flow(flow)
    obj.set_flex_align(main, cross, track)


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


# ---------------------------------------------------------------------------
# Randomness helpers
# ---------------------------------------------------------------------------

def shuffle(items_or_count):
    """Shuffle items using the hardware RNG.

    If *items_or_count* is an ``int`` *n*, returns a list of *n* shuffled
    indices (a permutation of ``range(n)``).

    If *items_or_count* is a ``list``, shuffles it **in place** and returns
    the list of source indices (a permutation of ``range(len(list))``) so
    the caller can reconstruct the mapping if needed.  The caller is
    responsible for making a copy beforehand if the original order must be
    retained — this avoids a forced allocation on memory-constrained devices.
    """
    is_int = isinstance(items_or_count, int)
    is_list = isinstance(items_or_count, list)
    if is_int:
        n = items_or_count
    elif is_list:
        items = items_or_count  # mutate in place — caller copies beforehand if needed
        n = len(items)
    else:
        raise TypeError("shuffle expects int or list, got " + str(type(items_or_count)))

    idx_pool = list(range(n))
    result_idx = [0] * n
    rand_bytes = rng.get_random_bytes(n)

    for i in range(n):
        result_idx[i] = idx_pool.pop( rand_bytes[i] % len(idx_pool) )

    if is_list:
        items[:] = [items_or_count[i] for i in result_idx]

    return result_idx
