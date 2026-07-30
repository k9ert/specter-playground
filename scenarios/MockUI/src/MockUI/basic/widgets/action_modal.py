import lvgl as lv
from .modal_overlay import SpecterGuiElement, modal_overlay
from .btn import Btn
from .labels import body_label, make_label
from .icon_widgets import make_icon
from .menu_item import MenuItem
from .inputs import confirmation_slider
from ..theming import apply_style
from ..utils import set_align


def _action_modal(text, title=None, parent=None):
    """Generic modal built on top of modal_overlay: optional title and body text.
        Do not call directly. Use button_modal or slider_confirm_modal.

    Args:
        text:       Main message displayed in the dialog.
        title:      Optional title text shown above the body (styled WIDGET.SCREEN_TITLE).
        body_style: Optional style (string or list) applied to the body label, in
                    addition to body_label()'s own default styling.
        parent:     Existing overlay/container to build the dialog box into. When
                    None (default), a new screen-centered modal_overlay() is created
                    and returned. When provided, the dialog box is attached to
                    `parent` instead and `parent` is returned unchanged — this lets
                    the caller own backdrop and positioning.
    """
    if parent is None:
        overlay = modal_overlay()
        apply_style(overlay, ["LAYOUT.FLEX_COL", "LAYOUT.ALL_CENTERED"])
    else:
        overlay = parent

    overlay.modal_window = SpecterGuiElement(overlay)
    apply_style(overlay.modal_window, "CONTAINER.MODAL_WINDOW")

    if title is not None:
        overlay.modal_window.title_lbl = make_label(overlay.modal_window, title)
        apply_style(overlay.modal_window.title_lbl, "WIDGET.SCREEN_TITLE")

    overlay.modal_window.body_text = body_label(overlay.modal_window, text, "WIDGET.MODAL_BODY")

    return [overlay, overlay.modal_window]


def _handle_button_click(overlay, auto_close, callback):
    if auto_close:
        overlay.delete()
    if callable(callback):
        callback()

def button_modal(text, title=None, buttons=None, auto_close=True, parent=None):
    """Generic choice modal where the user options are given by buttons.

    Args:
        text:       Main message displayed in the dialog.
        title:      Optional title text shown above the body.
        buttons:    List of ``MenuItem`` instances.  An empty list adds a
                    default "Close" button.
        auto_close: When True (default), clicking any button closes the modal
                    before invoking its callback. Set False when the caller owns
                    the modal's lifecycle instead (e.g. a guided tour explainer).
        parent:     Existing overlay/container to build the dialog box into,
                    instead of creating a new screen-centered modal_overlay().
                    Lets a caller own the backdrop and positioning (e.g. a
                    spotlight/coach-mark overlay with its own dim strips).
    """
    if buttons is None or len(buttons) == 0:
        buttons = [MenuItem(text="Close")]

    overlay, modal_window = _action_modal(text, title=title, parent=parent)

    modal_window.btn_row = SpecterGuiElement(modal_window)
    apply_style(modal_window.btn_row, "CONTAINER.MODAL_BUTTON_ROW")

    modal_window.btn_row.buttons = []
    for item in buttons:
        icon = getattr(item, 'icon', None)
        label = getattr(item, 'text', None)
        callback = getattr(item, 'target', None)
        visible = getattr(item, 'visible', True)

        btn = Btn(
            modal_window.btn_row,
            icon=icon,
            text=label,
            callback=lambda cb=callback: _handle_button_click(overlay, auto_close, cb),
        )

        if item.modifier == "Danger":
            btn.apply_style(background_style="BG.DANGER")
        elif item.modifier == "Warning":
            btn.apply_style(background_style="BG.WARNING")
        elif item.modifier == "Highlight":
            btn.apply_style(background_style="BG.HIGHLIGHT")

        if not visible:
            apply_style(btn, "APPEARANCE.INVISIBLE")

        modal_window.btn_row.buttons.append(btn)

    return overlay

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
    overlay, modal_window = _action_modal(text)

    def _on_user_decision(callback):
        overlay.delete()
        if callback is not None and callable(callback):
            callback()

    modal_window._slider = confirmation_slider(
        modal_window,
        max_value=300,
        on_max=lambda: _on_user_decision(on_confirm),
        max_style=confirm_style,
        min_value=-200,
        on_min=lambda: _on_user_decision(on_reject),
        min_style=reject_style
    )
    if confirm_icon is not None:
        modal_window.confirm_icon = make_icon(modal_window._slider, confirm_icon)
        apply_style(modal_window.confirm_icon, "WIDGET.INFO_ITEM")
        apply_style(modal_window.confirm_icon, "APPEARANCE.TRANSPARENT")
        set_align(modal_window.confirm_icon, lv.ALIGN.RIGHT_MID)
    
    if reject_icon is not None:
        modal_window.reject_icon = make_icon(modal_window._slider, reject_icon)
        apply_style(modal_window.reject_icon, "WIDGET.INFO_ITEM")
        apply_style(modal_window.reject_icon, "APPEARANCE.TRANSPARENT")
        set_align(modal_window.reject_icon, lv.ALIGN.LEFT_MID)