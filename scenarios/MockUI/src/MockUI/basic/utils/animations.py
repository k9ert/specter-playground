"""Low-level LVGL animation helpers.

Each function prepares an lv.anim_t and returns it. The caller is responsible
for calling anim.start() — this ensures the ref is stored before the animation
(and its completion callback) can fire.

The exec callback (lambda) is kept alive by the anim_t binding internally, so
only the anim_t itself needs to be stored.

Animation duration is theme-driven.

Typical usage::

    def _on_done(anim): ...
    a = slide_y(obj, from_y=H, to_y=0, on_done_cb=_on_done)
    self._refs = [a]  # store ref first
    a.start()         # then start
"""

import lvgl as lv
from micropython import const

from ..theming import apply_style
from .ui_utils import set_pos, get_anim_duration

class GUIAnimations:
    horizontal_slide_in = const(1)
    horizontal_slide_out = const(2)
    horizontal_push_in = const(3)
    horizontal_push_out = const(4)
    vertical_slide_in = const(5)
    vertical_slide_out = const(6)

def _slide(obj, from_value, to_value, axis, anim_style, on_done_cb=None):
    """Prepare (but do NOT start) an x or y slide animation.

    Applies anim_style to obj, then reads its anim_duration from that style.
    Snaps obj to from_value immediately (avoids first-frame flicker).
    Returns anim — caller must store it, then call anim.start().
    on_done(anim) is called by LVGL when the animation completes.
    """
    apply_style(obj, anim_style)
    if axis == "x":
        set_pos(obj, x=from_value)
        cb = lambda anim, v: set_pos(obj, x=v)
    elif axis == "y":
        set_pos(obj, y=from_value)
        cb = lambda anim, v: set_pos(obj, y=v)
    a = lv.anim_t()
    a.init()
    a.set_custom_exec_cb(cb)
    a.set_values(from_value, to_value)
    a.set_duration(get_anim_duration(obj))
    if on_done_cb is not None:
        a.set_completed_cb(on_done_cb)
    return a

def slide_x(obj, from_x, to_x, on_done_cb=None):
    """Prepare (but do NOT start) an x slide. Returns anim."""
    return _slide(obj, from_x, to_x, axis="x", anim_style="ANIM.HORIZONTAL", on_done_cb=on_done_cb)

def slide_y(obj, from_y, to_y, on_done_cb=None):
    """Prepare (but do NOT start) a y slide. Returns anim."""
    return _slide(obj, from_y, to_y, axis="y", anim_style="ANIM.VERTICAL", on_done_cb=on_done_cb)