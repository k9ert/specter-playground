"""Btn — unified button widget for the Specter MockUI.

A single class that handles all button variants:
  - icon-only:        Btn(parent, icon=BTC_ICONS.CARET_LEFT, size=(60, 50), callback=cb)
  - text-only:        Btn(parent, text="Cancel", size=(lv.pct(100), BTN_HEIGHT), callback=cb)
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
from ..theming import apply_style as t_apply_style
from ..utils.ui_utils import configure_flex, set_size


class Btn(SpecterGuiElement):
    """Unified button wrapper with Specter specific styling/tweaks.

    Args:
        parent:   LVGL parent object.
        icon:     Icon instance (e.g. BTC_ICONS.TRASH), or None.
        text:     Label string, or None.
        size:     (width, height) tuple; either element may be None = don't set.
        callback: Zero-argument callable, or an lv.EVENT handler with signature
                  ``fn(event)``.  Attached to lv.EVENT.CLICKED.
    """

    def __init__(self, parent, icon=None, text=None, size=None,
                 callback=None, background_style="WIDGET.BUTTON", foreground_style="WIDGET.BUTTON_FG"):
        super().__init__(parent)
        set_size(self, lv.SIZE_CONTENT, lv.SIZE_CONTENT)  # container auto-sizes to content by default
        self._btn = lv.button(self)
        self._btn.add_flag(lv.obj.FLAG.EVENT_BUBBLE)  # bubble CLICKED up to Btn so external add_event_cb works

        if size is not None:
            w, h = size
            set_size(self._btn, w, h)

        # If both icon and text: flex row so they sit side by side
        if icon is not None and text is not None:
            configure_flex(self._btn, flow=lv.FLEX_FLOW.ROW, main=lv.FLEX_ALIGN.CENTER)

        if icon is not None:
            self._ico = make_icon(self._btn, icon)
            if text is None:
                self._ico.center()
        else:
            self._ico = None

        if text is not None:
            self._lbl = make_label(self._btn, text)
            self._lbl.set_text(text)
            if icon is None:
                self._lbl.center()
        else:
            self._lbl = None

        if background_style is not None or foreground_style is not None:
            self.apply_style(background_style, foreground_style)

        if callback is not None:
            self._btn.add_event_cb(callback, lv.EVENT.CLICKED, None)


    def apply_style(self, background_style=None, foreground_style=None):
        if background_style is not None:
            t_apply_style(self._btn, background_style)
        if foreground_style is not None:
            if self._ico is not None:
                t_apply_style(self._ico, foreground_style)
            if self._lbl is not None:
                t_apply_style(self._lbl, foreground_style)

    def update_icon(self, icon):
        if self._ico is None:
            apply_icon(self._ico, icon)

    def __getattr__(self, name):
        # Proxy all unknown attributes to the underlying lv.button.
        # Guard against recursion before _btn is initialised.
        if name == '_btn':
            raise AttributeError('_btn')
        return getattr(self._btn, name)
