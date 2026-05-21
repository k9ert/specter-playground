"""Shared card-row scaffolding helpers.

Provides helpers for the leading-icon, name, and delete slots that are
identical between seed and wallet card rows, plus the row-container factory.
"""

import lvgl as lv
from .containers import card_row
from .icon_widgets import make_icon
from .labels import make_label, best_font_for_size
from .inputs import title_textarea
from .btn import Btn
from ..symbol_lib import BTC_ICONS
from ..ui_consts import WHITE_HEX, BIG_PAD


def compute_name_width(width, slots, slot_costs, min_width=10):
    """Compute the width budget for a card row's name slot.

    The card layout reserves a fixed left/right padding plus a per-slot
    width contribution for each non-name slot.  Callers provide
    ``slot_costs`` as a mapping of slot name → pixel width contributed
    by that slot (zero or missing entries are skipped).

    Args:
        width:      Total row width.
        slots:      Iterable of slot names present on the row.
        slot_costs: ``{slot: pixel_width}`` mapping for non-name slots.
        min_width:  Lower bound on the returned width.

    Returns:
        Pixel width to allocate to the name slot.
    """
    fixed_w = 2 * BIG_PAD + sum(slot_costs.get(slot, 0) for slot in slots)
    return max(min_width, width - fixed_w)


def build_card_row(parent, height, width, border, on_card_click):
    """Create a card row container and optionally attach a click handler.

    Args:
        parent:        LVGL parent object.
        height:        Row height in pixels.
        width:         Row width in pixels.
        border:        Whether to show the card border.
        on_card_click: ``cb(event)`` attached to the row on ``CLICKED``, or None.

    Returns:
        The created ``lv.obj`` row.
    """
    row = card_row(parent, height=height, width=width, border=border)
    if on_card_click is not None:
        row.add_event_cb(on_card_click, lv.EVENT.CLICKED, None)
    return row


def build_leading_icon_slot(row, leading_icon):
    """Append a leading icon to a card row.

    Args:
        row:          The card row ``lv.obj``.
        leading_icon: Icon constant (e.g. ``BTC_ICONS.KEY_OUTLINE``).
    """
    make_icon(row, leading_icon, WHITE_HEX)


def build_name_slot(row, label, name_w, height, on_name_click, editable=True):
    """Append the name slot to a card row.

    Renders an editable textarea when *editable* is True and *on_name_click*
    is provided; otherwise renders a static clipped label.

    Args:
        row:           The card row ``lv.obj``.
        label:         Display string.
        name_w:        Width budget for this slot in pixels.
        height:        Row height (used for font selection).
        on_name_click: Callback ``cb(textarea)`` invoked on CLICKED, or None.
        editable:      Whether this slot may be editable (e.g. False for the
                       default wallet whose name is fixed).

    Returns:
        The ``lv.textarea`` widget, or None when rendered as a static label.
    """
    name_font, display_text = best_font_for_size(label, name_w, height)
    if editable and on_name_click is not None:
        ta = title_textarea(row)
        ta.set_width(name_w)
        ta.set_style_text_font(name_font, 0)
        ta.set_text(display_text)

        def _make_name_cb(t):
            def _cb(e):
                if e.get_code() == lv.EVENT.CLICKED:
                    on_name_click(t)
            return _cb

        ta.add_event_cb(_make_name_cb(ta), lv.EVENT.CLICKED, None)
        return ta
    else:
        lbl = make_label(row, display_text, width=name_w, font=name_font)
        lbl.set_long_mode(lv.label.LONG_MODE.CLIP)
        return None


def build_delete_slot(row, icon_w, height, on_delete):
    """Append a TRASH delete button to a card row if *on_delete* is provided.

    The button suppresses event bubbling on click before invoking *on_delete*.

    Args:
        row:       The card row ``lv.obj``.
        icon_w:    Width (and height) of the delete button in pixels.
        height:    Row height in pixels.
        on_delete: Zero-argument callable, or None (no button rendered).
    """
    if on_delete is not None:
        def _del_cb(event=None):
            if event is not None:
                event.stop_bubbling = 1
            on_delete()
        del_btn = Btn(row, icon=BTC_ICONS.TRASH, size=(icon_w, height), callback=_del_cb)
        del_btn.make_background_transparent()
