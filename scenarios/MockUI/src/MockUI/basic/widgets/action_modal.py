"""ActionModal — generic choice/confirmation modal.

Displays a text message and a row of buttons. Any button press closes the
modal; if the button has a callable attached it is invoked afterwards.

Usage::

    ActionModal(
        text="Delete wallet?\\nThis cannot be undone.",
        buttons=[
            MenuItem(text="Cancel"),
            MenuItem(BTC_ICONS.TRASH, "Delete", color=RED_HEX, target=lambda: do_delete()),
        ],
    )

Each entry in *buttons* must be a ``MenuItem`` (or any object with ``.icon``,
``.text``, ``.color``, ``.target`` attributes).

If ``buttons`` is empty a single "Close" button is added automatically.
"""

import lvgl as lv
from .modal_overlay import ModalOverlay
from .btn import Btn
from .containers import dialog_card, flex_row
from .labels import body_label
from .menu_item import MenuItem
from ..utils.ui_consts import DEFAULT_MODAL_BG_OPA, MODAL_WIDTH_PCT, MODAL_HEIGHT_PCT, BTN_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT


class ActionModal:
    """Generic choice modal built on top of ModalOverlay.

    Args:
        text:    Main message displayed in the dialog.
        buttons: List of ``MenuItem`` instances.  An empty list adds a
                 default "Close" button.
        bg_opa:  Backdrop opacity (0-255).  Defaults to DEFAULT_MODAL_BG_OPA.
    """

    def __init__(self, text, buttons=None, bg_opa=DEFAULT_MODAL_BG_OPA):
        if buttons is None or len(buttons) == 0:
            buttons = [MenuItem(text="Close")]

        self._modal = ModalOverlay(bg_opa=bg_opa)

        dw = SCREEN_WIDTH * MODAL_WIDTH_PCT // 100
        dh = SCREEN_HEIGHT * MODAL_HEIGHT_PCT // 100
        dx = (SCREEN_WIDTH - dw) // 2
        dy = (SCREEN_HEIGHT - dh) // 2
        dialog = dialog_card(self._modal.overlay, dw, dh, dx, dy)

        body_label(dialog, text)

        btn_row = flex_row(
            dialog,
            width=lv.pct(100),
            height=lv.SIZE_CONTENT,
            main_align=lv.FLEX_ALIGN.SPACE_EVENLY,
        )

        for item in buttons:
            icon = getattr(item, 'icon', None)
            label = getattr(item, 'text', None)
            color = getattr(item, 'color', None)
            callback = getattr(item, 'target', None)

            btn = Btn(
                btn_row,
                icon=icon,
                text=label,
                color=color,
                size=(None, BTN_HEIGHT),
            )

            def _make_handler(modal, cb):
                def _handler(ev):
                    if ev.get_code() == lv.EVENT.CLICKED:
                        modal.close()
                        if cb is not None and callable(cb):
                            cb()
                return _handler

            btn.add_event_cb(_make_handler(self._modal, callback), lv.EVENT.CLICKED, None)
