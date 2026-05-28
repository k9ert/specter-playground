"""Container helpers — flex wrappers with Specter default styling.

All containers have border, padding, and radius zeroed by default.
"""

import lvgl as lv
from ..utils.ui_consts import DIALOG_RADIUS, BIG_PAD, WHITE_HEX, DROPUP_DIVIDER_OPA
from ..utils.ui_utils import configure_as_bare, configure_flex


def _flex_container(parent, flow, width, height, pad = 0, main_align = lv.FLEX_ALIGN.START, transparent_bg=True):
    cont = lv.obj(parent)
    cont.set_width(width if width is not None else lv.pct(100))
    cont.set_height(height if height is not None else lv.SIZE_CONTENT)
    cont.set_layout(lv.LAYOUT.FLEX)
    configure_flex(cont, flow=flow, main=main_align)
    cont.set_style_border_width(0, 0)
    cont.set_style_radius(0, 0)
    cont.set_style_pad_all(pad, 0)
    cont.set_style_pad_column(pad, 0)
    cont.set_style_pad_row(pad, 0)
    if transparent_bg:
        cont.set_style_bg_opa(lv.OPA.TRANSP, 0)
    return cont


def flex_col(parent, width=None, height=None, pad=0, main_align=lv.FLEX_ALIGN.START, transparent_bg=True):
    """lv.obj flex-column container."""
    return _flex_container(
        parent, lv.FLEX_FLOW.COLUMN,
        width, height, pad, main_align, transparent_bg
    )


def flex_row(parent, width=None, height=None, pad=0, main_align=lv.FLEX_ALIGN.SPACE_EVENLY, transparent_bg=True):
    """lv.obj flex-row container."""
    return _flex_container(
        parent, lv.FLEX_FLOW.ROW, 
        width, height, pad, main_align, transparent_bg
    )


def bare_strip(parent, height, y=0, transparent_bg=True):
    """Full-width, no-decoration horizontal strip at absolute y inside *parent*.

    Border, padding, and radius are all zeroed.  Positioned via TOP_MID align
    so it spans the full parent width regardless of parent padding.
    """
    strip = lv.obj(parent)
    configure_as_bare(strip, width=lv.pct(100), height=height, transparent_bg=transparent_bg)
    strip.align(lv.ALIGN.TOP_MID, 0, y)
    return strip


def card_row(parent, height, width, pad=BIG_PAD, border=True, transparent_bg=True):
    """Full-width horizontal flex row styled as an item card.

    Bottom divider line is drawn via border-bottom at low opacity.
    Pass ``border=False`` to suppress the divider (e.g. in the context bar).
    ``pad_column`` is explicitly zeroed so inter-item gaps in the flex layout
    don't cause horizontal overflow.

    Args:
        parent: LVGL parent object.
        height: Row height in pixels.
        width:  Row width in pixels.
        pad:    Left/right/top/bottom padding; defaults to ``BIG_PAD``.

    Returns:
        The created ``lv.obj`` flex-row widget.
    """
    row = flex_row(parent, width=width, height=height, pad=pad, main_align=lv.FLEX_ALIGN.START, transparent_bg=transparent_bg)
    row.set_style_pad_column(0, 0)
    if border:
        row.set_style_border_width(1, 0)
        row.set_style_border_side(lv.BORDER_SIDE.BOTTOM, 0)
        row.set_style_border_color(WHITE_HEX, 0)
        row.set_style_border_opa(DROPUP_DIVIDER_OPA, 0)
    row.set_scroll_dir(lv.DIR.NONE)
    row.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    return row


def dialog_card(overlay, w, h, x, y, pad=BIG_PAD):
    """Centred, rounded dialog card on a ModalOverlay.

    Standard Specter dialog box: radius=8, pad=12, FLEX COLUMN CENTER,
    scrollbar off.

    Args:
        overlay: The lv.obj from a ModalOverlay instance (modal.overlay).
        w, h:    Pixel width and height.
        x, y:    Absolute position (usually centred by the caller).
        pad:     Inner padding; defaults to BIG_PAD.
    """
    dialog = lv.obj(overlay)
    dialog.set_size(w, h)
    dialog.set_pos(x, y)
    dialog.set_style_radius(DIALOG_RADIUS, 0)
    dialog.set_style_border_width(0, 0)
    dialog.set_style_pad_all(pad, 0)
    dialog.set_scrollbar_mode(lv.SCROLLBAR_MODE.OFF)
    dialog.set_layout(lv.LAYOUT.FLEX)
    configure_flex(dialog, main=lv.FLEX_ALIGN.CENTER)
    return dialog
