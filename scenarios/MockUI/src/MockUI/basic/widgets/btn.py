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
from ..symbol_lib import Icon
from ..ui_consts import TEXT_FONT
from ..ui_utils import configure_flex, to_lv_color


class Btn:
    """Unified LVGL button wrapper with Specter default styling.

    Args:
        parent:   LVGL parent object.
        icon:     Icon instance (e.g. BTC_ICONS.TRASH), or None.
        text:     Label string, or None.
        color:    lv.color background override, or None (theme default).
        size:     (width, height) tuple; either element may be None = don't set.
        callback: Zero-argument callable, or an lv.EVENT handler with signature
                  ``fn(event)``.  Attached to lv.EVENT.CLICKED.
        font:     LVGL font for the text label; defaults to TEXT_FONT.
        fontcolor: LVGL color for the text label; defaults to theme default text color.
    """

    def __init__(self, parent, icon=None, text=None, color=None, size=None,
                 callback=None, font=TEXT_FONT, fontcolor=None):
        self._btn = lv.button(parent)

        if size is not None:
            w, h = size
            if w is not None:
                self._btn.set_width(w)
            if h is not None:
                self._btn.set_height(h)

        if color is not None:
            self._btn.set_style_bg_color(color, lv.PART.MAIN)

        # If both icon and text: flex row so they sit side by side
        if icon is not None and text is not None:
            self._btn.set_layout(lv.LAYOUT.FLEX)
            configure_flex(self._btn, flow=lv.FLEX_FLOW.ROW, main=lv.FLEX_ALIGN.CENTER)

        if icon is not None:
            self._ico_img = lv.image(self._btn)
            icon(to_lv_color(fontcolor))
            icon.apply_icon_to(self._ico_img)
            if text is None:
                self._ico_img.center()
        else:
            self._ico_img = None

        if text is not None:
            self.lbl = lv.label(self._btn)
            self.lbl.set_text(text)
            self.lbl.set_style_text_font(font, 0)
            if fontcolor is not None:
                self.lbl.set_style_text_color(to_lv_color(fontcolor), 0)
            if icon is None:
                self.lbl.center()
        else:
            self.lbl = None

        if callback is not None:
            self._btn.add_event_cb(callback, lv.EVENT.CLICKED, None)

    def update_icon(self, icon):
        if self._ico_img is not None:
            icon.apply_icon_to(self._ico_img)

    def make_background_transparent(self):
        """Remove button background, border and shadow.

        The button remains clickable and any icon/text content stays visible;
        only the button body itself becomes invisible.
        """
        self._btn.set_style_bg_opa(lv.OPA.TRANSP, 0)
        self._btn.set_style_shadow_width(0, 0)
        self._btn.set_style_border_width(0, 0)
        return self

    def set_visible(self, visible):
        """Show or hide this button in-place, preserving its layout slot.

        When hidden the icon becomes transparent and the button stops
        accepting touch events (acts as a placeholder spacer).
        """
        opa = lv.OPA.COVER if visible else lv.OPA.TRANSP
        if self._ico_img is not None:
            self._ico_img.set_style_opa(opa, 0)
        if self.lbl is not None:
            self.lbl.set_style_opa(opa, 0)
        if visible:
            self._btn.add_flag(lv.obj.FLAG.CLICKABLE)
        else:
            self._btn.remove_flag(lv.obj.FLAG.CLICKABLE)

    def __getattr__(self, name):
        # Proxy all unknown attributes to the underlying lv.button.
        # Guard against recursion before _btn is initialised.
        if name == '_btn':
            raise AttributeError('_btn')
        return getattr(self._btn, name)
