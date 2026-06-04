import lvgl as lv
from .modal_overlay import ModalOverlay
from .btn import Btn
from .containers import dialog_card, flex_row
from .labels import body_label
from .menu_item import MenuItem
from ..widgets.icon_widgets import make_icon
from .inputs import confirmation_slider
from ..utils.ui_consts import (
    CONFIRMATION_SLIDER_HEIGHT,
    DEFAULT_MODAL_BG_OPA,
    MODAL_WIDTH_PCT,
    MODAL_HEIGHT_PCT,
    BTN_HEIGHT,
    RED_HEX,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    WHITE_HEX,
)


class _ActionModal:
    """Generic choice modal built on top of ModalOverlay.
        Do not instantiate directly. Use ButtonModal or SliderConfirmModal or other derived class.
    Args:
        text:    Main message displayed in the dialog.
        bg_opa:  Backdrop opacity (0-255).  Defaults to DEFAULT_MODAL_BG_OPA.
    """
    def __init__(self, text, bg_opa=None):
        if bg_opa is None:
            bg_opa = DEFAULT_MODAL_BG_OPA
        self._modal = ModalOverlay(bg_opa=bg_opa)

        self.dw = SCREEN_WIDTH * MODAL_WIDTH_PCT // 100
        self.dh = SCREEN_HEIGHT * MODAL_HEIGHT_PCT // 100
        self.dx = (SCREEN_WIDTH - self.dw) // 2
        self.dy = (SCREEN_HEIGHT - self.dh) // 2
        self.dialog = dialog_card(self._modal.overlay, self.dw, self.dh, self.dx, self.dy)

        body_label(self.dialog, text)
class ButtonModal(_ActionModal):
    """Generic choice modal where the user options are given by buttons.

    Args:
        text:    Main message displayed in the dialog.
        buttons: List of ``MenuItem`` instances.  An empty list adds a
                 default "Close" button.
        bg_opa:  Backdrop opacity (0-255).
    """
    def __init__(self, text, buttons=None, bg_opa=None):
        super().__init__(text, bg_opa)
        
        if buttons is None or len(buttons) == 0:
            buttons = [MenuItem(text="Close")]
    
        btn_row = flex_row(
            self.dialog,
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

class SliderConfirmModal(_ActionModal):
    """Confirmation modal with a slider as user input.
       Slide to left is always cancelling, slide to right confirms.
    
    Usage::
        
        SliderConfirmModal(
            text="Delete wallet?\\nThis cannot be undone.",
            on_confirm=lambda: do_delete(),
            slider_color=RED_HEX,
        )
    
    Args:
        text:         Main message displayed in the dialog.
        on_confirm:   Zero-argument callable invoked when slider confirmation completes.
        on_reject:    Zero-argument callable invoked when slider is released without confirming (optional).
        confirm_color:lv.color for the slider (optional).
        reject_color: lv.color for the slider when moving in the opposite direction (optional).
        confirm_icon:  Icon to show on the confirm (right) side of the slider (optional).
        reject_icon:   Icon to show on the reject (left) side of the slider (optional).
        bg_opa:       Backdrop opacity (0-255).
    """
    def __init__(self, text, 
                 on_confirm=None, confirm_color=None, confirm_icon=None,
                 on_reject=None, reject_color=None, reject_icon=None,
                 bg_opa=None):
        
        super().__init__(text, bg_opa)
        
        slider_container = flex_row(self.dialog)

        def _on_user_decision(callback):
            self._modal.close()
            if callback is not None and callable(callback):
                callback()

        self._slider = confirmation_slider(
            slider_container,
            max_value=300,
            on_max=lambda: _on_user_decision(on_confirm),
            max_color=confirm_color,
            min_value=-200,
            on_min=lambda: _on_user_decision(on_reject),
            min_color=reject_color,
        )
        if confirm_icon is not None:
            self.confirm_icon = make_icon(self._slider, confirm_icon, color=WHITE_HEX)
            self.confirm_icon.add_flag(lv.obj.FLAG.IGNORE_LAYOUT)
            self.confirm_icon.align(lv.ALIGN.RIGHT_MID, CONFIRMATION_SLIDER_HEIGHT//3, 0)
        if reject_icon is not None:
            self.reject_icon = make_icon(self._slider, reject_icon, color=WHITE_HEX)
            self.reject_icon.add_flag(lv.obj.FLAG.IGNORE_LAYOUT)
            self.reject_icon.align(lv.ALIGN.LEFT_MID, -CONFIRMATION_SLIDER_HEIGHT//3, 0)