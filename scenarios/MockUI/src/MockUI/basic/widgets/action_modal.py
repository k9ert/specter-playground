import lvgl as lv
from .modal_overlay import modal_overlay
from .btn import Btn
from .containers import flex_row, flex_container
from .labels import body_label
from .icon_widgets import make_icon
from .menu_item import MenuItem
from .inputs import confirmation_slider
from ..theming import apply_style
from ..utils import (
    CONFIRMATION_SLIDER_HEIGHT,
    MODAL_WIDTH,
    MODAL_HEIGHT,
    BTN_HEIGHT,
)


def _action_modal(text):
    """Generic choice modal built on top of modal_overlay.
        Do not call directly. Use button_modal or slider_confirm_modal
    Args:
        text:    Main message displayed in the dialog.
    """
    modal = modal_overlay()

    dw = MODAL_WIDTH
    dh = MODAL_HEIGHT
    modal.dialog = flex_container(modal, 
                                  lv.FLEX_FLOW.COLUMN, 
                                  width=dw, height=dh, 
                                  main_align=lv.FLEX_ALIGN.CENTER)
    apply_style(modal.dialog, "WIDGET.MODAL_WINDOW")

    modal.dialog.body_text = body_label(modal.dialog, text)

    return modal

def button_modal(text, buttons=None):
    """Generic choice modal where the user options are given by buttons.

    Args:
        text:    Main message displayed in the dialog.
        buttons: List of ``MenuItem`` instances.  An empty list adds a
                 default "Close" button.
    """
    modal = _action_modal(text)
    if buttons is None or len(buttons) == 0:
        buttons = [MenuItem(text="Close")]

    modal.btn_row = flex_row(
        modal.dialog,
        width=lv.pct(100),
        height=lv.SIZE_CONTENT,
        main_align=lv.FLEX_ALIGN.SPACE_EVENLY,
    )

    modal.btn_row.buttons = []
    for item in buttons:
        icon = getattr(item, 'icon', None)
        label = getattr(item, 'text', None)
        callback = getattr(item, 'target', None)

        btn = Btn(
            modal.btn_row,
            icon=icon,
            text=label,
            size=(None, BTN_HEIGHT),
        )
        modal.btn_row.buttons.append(btn)

        def _handler(ev, cb=callback):
            modal.close()
            if callable(cb):
                cb()

        btn.add_event_cb(_handler, lv.EVENT.CLICKED, None)

    return modal

def slider_confirm_modal(text,
                         on_confirm=None, confirm_style=None, confirm_icon=None,
                         on_reject=None, reject_style=None, reject_icon=None
                        ):
    """Confirmation modal with a slider as user input.
       Slide to left is always cancelling, slide to right confirms.
    
    Usage::
        
        slider_confirm_modal(
            text="Delete wallet?\\nThis cannot be undone.",
            on_confirm=lambda: do_delete(),
            confirm_style="FG.DANGER",
        )
    
    Args:
        text:         Main message displayed in the dialog.
        on_confirm:   Zero-argument callable invoked when slider confirmation completes.
        on_reject:    Zero-argument callable invoked when slider is released without confirming (optional),
                      defaults to closing the modal without further action.
        confirm_style: Style to apply to the slider's indicator when confirming (optional).
        reject_style: Style to apply to the slider's indicator when rejecting (optional).
        confirm_icon:  Icon to show on the confirm (right) side of the slider (optional).
        reject_icon:   Icon to show on the reject (left) side of the slider (optional).
    """
    modal = _action_modal(text)

    def _on_user_decision(callback):
        modal.close()
        if callback is not None and callable(callback):
            callback()

    modal._slider = confirmation_slider(
        modal.dialog,
        max_value=300,
        on_max=lambda: _on_user_decision(on_confirm),
        max_style=confirm_style,
        min_value=-200,
        on_min=lambda: _on_user_decision(on_reject),
        min_style=reject_style,
    )
    if confirm_icon is not None:
        modal.confirm_icon = make_icon(modal._slider, confirm_icon)
        apply_style(modal.confirm_icon, "WIDGET.INFO_ITEM")
        apply_style(modal.confirm_icon, "APPEARENCE.TRANSPARENT")
        modal.confirm_icon.add_flag(lv.obj.FLAG.IGNORE_LAYOUT)
        modal.confirm_icon.align(lv.ALIGN.RIGHT_MID, CONFIRMATION_SLIDER_HEIGHT//3, 0)
    if reject_icon is not None:
        modal.reject_icon = make_icon(modal._slider, reject_icon)
        apply_style(modal.reject_icon, "WIDGET.INFO_ITEM")
        apply_style(modal.reject_icon, "APPEARENCE.TRANSPARENT")
        modal.reject_icon.add_flag(lv.obj.FLAG.IGNORE_LAYOUT)
        modal.reject_icon.align(lv.ALIGN.LEFT_MID, -CONFIRMATION_SLIDER_HEIGHT//3, 0)