"""Shared card-row scaffolding helpers.

Provides helpers for the leading-icon, name, and delete slots that are
identical between seed and wallet card rows, plus the row-container factory.
"""
import lvgl as lv
from .icon_widgets import make_icon
from .labels import make_label
from .inputs import title_textarea
from .btn import Btn
from ..symbol_lib import BTC_ICONS
from ..utils import BIG_PAD, best_fonttype_for_size
from ..theming import get_font, apply_style


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

def build_name_slot(row, text, name_w, height, on_name_click, editable=True):
    """Append the name slot to a card row.

    Renders an editable textarea when *editable* is True and *on_name_click*
    is provided; otherwise renders a static clipped label.

    Args:
        row:           The card row ``lv.obj``.
        text:          Display string.
        name_w:        Width budget for this slot in pixels.
        height:        Row height (used for font selection).
        on_name_click: Callback ``cb(textarea)`` invoked on CLICKED, or None.
        editable:      Whether this slot may be editable (e.g. False for the
                       default wallet whose name is fixed).

    Returns:
        The ``lv.textarea`` widget, or None when rendered as a static label.
    """
    font_key, display_text = best_fonttype_for_size(text, name_w, height)
    font = get_font(font_key)
    if editable and on_name_click is not None:
        text_edit = title_textarea(row)
        text_edit.set_width(name_w)
        text_edit.set_style_text_font(font, 0)
        text_edit.set_text(display_text)

        text_edit.add_event_cb(lambda e: on_name_click(text_edit), lv.EVENT.CLICKED, None)
        return (text_edit, True)
    else:
        lbl = make_label(row, display_text, width=name_w)
        apply_style(lbl, ["TEXT.TITLE", "TEXT.BODY"])
        lbl.set_style_text_font(font, 0)
        return (lbl, False)


def build_delete_slot(row, icon_w, height, on_delete):
    """Append a TRASH delete button to a card row.

    The button suppresses event bubbling on click before invoking *on_delete*.

    Args:
        row:       The card row ``lv.obj``.
        icon_w:    Width (and height) of the delete button in pixels.
        height:    Row height in pixels.
        on_delete: Zero-argument callable.
    """
    def _del_cb(e):
        e.stop_bubbling = 1
        on_delete()
    btn = Btn(row, icon=BTC_ICONS.TRASH, size=(icon_w, height), callback=_del_cb)
    apply_style(btn, ["WIDGET.INFO_ITEM"])
    return btn
