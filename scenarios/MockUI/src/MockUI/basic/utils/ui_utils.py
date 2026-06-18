"""ui_utils — low-level LVGL and colour utility functions.

These helpers have no GUI-state dependencies and can be imported by any module
without risk of circular imports.
"""
import lvgl as lv
import rng  # TODO: clarify if this should be encapsulated in a general HW/GUI interface

from .ui_consts import SCREEN_WIDTH, CONTENT_H
from ..theming import apply_style, get_font, get_palette_entries, SpecterFontPalette

# ---------------------------------------------------------------------------
# Widget helpers
# ---------------------------------------------------------------------------

def delete_all_children_of(widget):
    for i in reversed(range(widget.get_child_count())):
        widget.get_child(i).delete()

def set_size(obj, width=None, height=None):
    if width is not None:
        obj.set_width(width)
    if height is not None:
        obj.set_height(height)

def get_size(obj):
    return obj.get_width(), obj.get_height()

def set_pos(obj, x=None, y=None):
    if x is not None:
        obj.set_x(x)
    if y is not None:
        obj.set_y(y)

def get_pos(obj):
    return obj.get_x(), obj.get_y()

def set_scale(obj, scale):
    obj.set_scale(scale)

def set_align(obj, align):
    obj.set_align(align)

def set_scroll(obj, horizontal=True, vertical=True):
    if horizontal and vertical:
        obj.set_scroll_dir(lv.DIR.ALL)
        obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.AUTO)
    elif horizontal:
        obj.set_scroll_dir(lv.DIR.HOR)
        obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.AUTO)
    elif vertical:
        obj.set_scroll_dir(lv.DIR.VER)
        obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.AUTO)
    else:
        obj.set_scroll_dir(lv.DIR.NONE)
        obj.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)

def set_propagate_events(obj, propagate):
    if propagate:
        obj.add_flag(lv.obj.FLAG.EVENT_BUBBLE)
    else:
        obj.remove_flag(lv.obj.FLAG.EVENT_BUBBLE)

def text_width(text, font):
    """Calculate width of *text* in *font*, including kerning."""
    n = len(text)
    total = 0
    for i in range(n):
        next_cp = ord(text[i + 1]) if i + 1 < n else 0
        total += font.get_glyph_width(ord(text[i]), next_cp)
    return total

def best_fonttype_for_size(text, max_w, max_h):
    """Return *(font_type, display_text)* fitting *text* within max_w x max_h px.

    Tries each font in font palette for a single-line fit.
    Falls back to a balanced two-line word split at smallest font when
    the available height allows two lines.  Always returns a valid pair.
    """
    # Fetch all palette fonts and filter out any that failed to load
    all_font_keys = get_palette_entries(SpecterFontPalette).values()
    loaded_fonts = []
    for font_key in all_font_keys:
        font, err = get_font(font_key)
        if font is not None:
            loaded_fonts.append((font_key, font))

    # Sort largest-first by actual line height (theme-driven, not by index)
    loaded_fonts.sort(key=lambda item: item[1].get_line_height(), reverse=True)

    for font_key, font in loaded_fonts:
        if font.get_line_height() <= max_h and text_width(text, font) <= max_w:
            return font_key, text

    font_key = SpecterFontPalette.SMALL
    f_small, err = get_font(font_key)
    if f_small is not None:
        if f_small.get_line_height() * 2 <= max_h:
            words = text.split()
            best_split = None
            best_balance = None
            for i in range(1, len(words)):
                left = " ".join(words[:i])
                right = " ".join(words[i:])
                lw = text_width(left, f_small)
                rw = text_width(right, f_small)
                if lw <= max_w and rw <= max_w:
                    balance = max(lw, rw)
                    if best_balance is None or balance < best_balance:
                        best_split = left + "\n" + right
                        best_balance = balance
            if best_split is not None:
                return font_key, best_split

    return font_key, text

def style_as_screen_backdrop(obj, width=SCREEN_WIDTH, height=CONTENT_H, x=None, y=None):
    obj.set_layout(lv.LAYOUT.NONE)
    set_pos(obj, x=x, y=y)
    set_size(obj, width=width, height=height)
    set_scroll(obj, horizontal=False, vertical=False)
    apply_style(obj, "CONTAINER.SCREEN")

def style_as_flex_container(obj, flow=lv.FLEX_FLOW.COLUMN, 
                   width=lv.SIZE_CONTENT, height=lv.SIZE_CONTENT, 
                   main_align = lv.FLEX_ALIGN.START, cross_align = lv.FLEX_ALIGN.CENTER, track_align = lv.FLEX_ALIGN.CENTER, 
                   scrollable=True):
    set_size(obj, width, height)
    configure_flex(obj, flow=flow, main=main_align, cross=cross_align, track=track_align)
    apply_style(obj, "LAYOUT.BARE")
    if not scrollable:
        set_scroll(obj, horizontal=False, vertical=False)

def configure_flex(obj,
                   flow=lv.FLEX_FLOW.COLUMN,
                   main=lv.FLEX_ALIGN.START,
                   cross=lv.FLEX_ALIGN.CENTER,
                   track=lv.FLEX_ALIGN.CENTER):
    #TODO: CHECK IF needed outside of style_as_flex_container, if not: inline
    """Apply a flex layout to *obj* with sensible defaults.

    Defaults match the typical titled-menu body: column flow with
    START / CENTER / CENTER alignment.
    """
    obj.set_layout(lv.LAYOUT.FLEX)
    obj.set_flex_flow(flow)
    obj.set_flex_align(main, cross, track)

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
