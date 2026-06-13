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
from ..theming import apply_style
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
                 callback=None):
        super().__init__(parent)
        self._btn = lv.button(self)

        if size is not None:
            w, h = size
            set_size(self._btn, w, h)

        apply_style(self._btn, ["WIDGET.BUTTON"])

        # If both icon and text: flex row so they sit side by side
        if icon is not None and text is not None:
            configure_flex(self._btn, flow=lv.FLEX_FLOW.ROW, main=lv.FLEX_ALIGN.CENTER)

        if icon is not None:
            self._ico = make_icon(self._btn, icon)
            if text is None:
                self._ico.center()
            apply_style(self._ico, ["WIDGET.BUTTON"])
        else:
            self._ico = None

        if text is not None:
            self._lbl = make_label(self._btn, text)
            self._lbl.set_text(text)
            if icon is None:
                self._lbl.center()
            apply_style(self._lbl, ["WIDGET.BUTTON"])
        else:
            self._lbl = None

        if callback is not None:
            self._btn.add_event_cb(callback, lv.EVENT.CLICKED, None)

    def update_icon(self, icon):
        if self._ico is None:
            apply_icon(self._ico, icon)

    def __getattr__(self, name):
        # Proxy all unknown attributes to the underlying lv.button.
        # Guard against recursion before _btn is initialised.
        if name == '_btn':
            raise AttributeError('_btn')
        return getattr(self._btn, name)
