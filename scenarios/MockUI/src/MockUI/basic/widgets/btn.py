"""Btn — unified button widget for the Specter MockUI.

A single class that handles all button variants:
  - icon-only:        Btn(parent, icon=BTC_ICONS.CARET_LEFT, size=(60, 50), callback=cb)
  - text-only:        Btn(parent, text="Cancel", size=(lv.pct(100), 75), callback=cb)
  - icon + text:      Btn(parent, icon=BTC_ICONS.TRASH, text="Delete", color=RED_HEX, callback=cb)
  - make_transparent: Btn(parent, size=(60, 50)).make_transparent()
  - placeholder:      Btn(parent, size=(60, 50)).placeholder()

Size parameter is a (width, height) tuple; either element may be None to skip setting it.

Proxy: all lv.button methods are accessible directly on Btn instances (e.g. btn.align(...)).
"""

import lvgl as lv
from .icon_widgets import apply_icon, make_icon
from .labels import make_label
from ..templates.specter_gui_base import SpecterGuiElement
from ..theming import apply_style, get_style, style_has_property
from ..utils.ui_utils import apply_click_feedback, set_size


class Btn(SpecterGuiElement):
    """Unified button wrapper with Specter specific styling/tweaks.

    Styling: the base ``style`` token themes the button background/border/
    geometry, its ``FG`` role (``WIDGET.BUTTON`` with ``roles.FG`` in the
    theme) themes the icon + label.  A missing role is skipped.

    Args:
        parent:   LVGL parent object.
        icon:     Icon instance (e.g. BTC_ICONS.TRASH), or None.
        text:     Label string, or None.
        size:     (width, height) tuple; either element may be None = don't set.
        callback: Zero-argument callable invoked when the button is clicked.
        consume_click: Stop the click event from bubbling to a parent widget.
        style:    Base style token (default "WIDGET.BUTTON").  ``None`` = unstyled.
    """

    def __init__(self, parent, icon=None, text=None, size=None,
                 callback=None, consume_click=False,
                 style="WIDGET.BUTTON"):
        super().__init__(parent)
        self._btn = lv.button(self)

        w, h = (None, None) if size is None else size

        # bubble CLICKED up to Btn so external add_event_cb works
        self._btn.add_flag(lv.obj.FLAG.EVENT_BUBBLE)


        if icon is not None:
            self._ico = make_icon(self._btn, icon)
        else:
            self._ico = None

        if text is not None:
            self._lbl = make_label(self._btn, text)
        else:
            self._lbl = None

        wrapper_style = get_style(style, role="WRAPPER") if style is not None else None
        if style is not None:
            apply_style(self._btn, style)
            if self._ico is not None:
                apply_style(self._ico, style, role="FG")
            if self._lbl is not None:
                apply_style(self._lbl, style, role="FG")
            if wrapper_style is not None:
                apply_style(self, wrapper_style)
        apply_click_feedback(self._btn)

        resolved_w = self._btn.get_style_width(lv.PART.MAIN)
        resolved_h = self._btn.get_style_height(lv.PART.MAIN)
        wrapper_has_width = style_has_property(wrapper_style, lv.STYLE.WIDTH)
        wrapper_has_height = style_has_property(wrapper_style, lv.STYLE.HEIGHT)

        if w is None:
            if not wrapper_has_width and resolved_w != lv.SIZE_CONTENT:
                set_size(self, width=resolved_w)
                set_size(self._btn, width=lv.pct(100))
            elif not wrapper_has_width:
                set_size(self, width=lv.SIZE_CONTENT)
        elif w == lv.SIZE_CONTENT:
            set_size(self, width=lv.SIZE_CONTENT)
            set_size(self._btn, width=lv.SIZE_CONTENT)
        else:
            set_size(self, width=w)
            set_size(self._btn, width=lv.pct(100))

        if h is None:
            if not wrapper_has_height and resolved_h != lv.SIZE_CONTENT:
                set_size(self, height=resolved_h)
                set_size(self._btn, height=lv.pct(100))
            elif not wrapper_has_height:
                set_size(self, height=lv.SIZE_CONTENT)
        elif h == lv.SIZE_CONTENT:
            set_size(self, height=lv.SIZE_CONTENT)
            set_size(self._btn, height=lv.SIZE_CONTENT)
        else:
            set_size(self, height=h)
            set_size(self._btn, height=lv.pct(100))

        if callback is not None:
            def _on_clicked(event):
                if consume_click:
                    event.stop_bubbling = 1
                callback()

            self._btn.add_event_cb(_on_clicked, lv.EVENT.CLICKED, None)

    def update_icon(self, icon):
        if self._ico is not None:
            apply_icon(self._ico, icon)

    def set_disabled(self, disabled):
        self.set_state(lv.STATE.DISABLED, disabled)
        self._btn.set_state(lv.STATE.DISABLED, disabled)
