"""Shared card-row scaffolding helpers.

Provides shared card-row slot helpers used by seed and wallet rows.
"""
from .btn import Btn
from ..symbol_lib import BTC_ICONS


def build_delete_slot(row, on_delete):
    """Append a TRASH delete button to a card row.

    The button suppresses event bubbling on click before invoking *on_delete*.

    Args:
        row:       The card row ``lv.obj``.
        on_delete: Zero-argument callable.
    """
    btn = Btn(row, 
              icon=BTC_ICONS.TRASH, 
              background_style="APPEARANCE.TRANSPARENT",
              foreground_style="WIDGET.BUTTON_FG",
              callback=on_delete,
              consume_click=True)
    return btn
