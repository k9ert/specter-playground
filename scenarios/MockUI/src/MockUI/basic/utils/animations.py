"""Low-level LVGL animation helpers.

Each function prepares an lv.anim_t and returns it. The caller is responsible
for calling anim.start() — this ensures the ref is stored before the animation
(and its completion callback) can fire.

The exec callback (lambda) is kept alive by the anim_t binding internally, so
only the anim_t itself needs to be stored.

Typical usage::

    def _on_done(anim): ...
    a = slide_y(obj, from_y=H, to_y=0, duration_ms=200, on_done=_on_done)
    self._refs = [a]  # store ref first
    a.start()         # then start
"""

import lvgl as lv
from .ui_consts import SCREEN_WIDTH, SCREEN_HEIGHT, CONTENT_PCT, ANIM_MS_HORIZONTAL, ANIM_MS_VERTICAL

_CONTENT_H = SCREEN_HEIGHT * CONTENT_PCT // 100

class GUIAnimations:
    horizontal_slide_in = 1
    horizontal_slide_out = 2
    horizontal_push_in = 3
    horizontal_push_out = 4
    vertical_slide_in = 5
    vertical_slide_out = 6

def _slide(obj, from_value, to_value, duration_ms, axis, on_done_cb=None):
    """Prepare (but do NOT start) an x or y slide animation.

    Snaps obj to from_value immediately (avoids first-frame flicker).
    Returns anim — caller must store it, then call anim.start().
    on_done(anim) is called by LVGL when the animation completes.
    """
    if axis == "x":
        obj.set_x(from_value)
        cb = lambda anim, v: obj.set_x(v)
    elif axis == "y":
        obj.set_y(from_value)
        cb = lambda anim, v: obj.set_y(v)
    a = lv.anim_t()
    a.init()
    a.set_custom_exec_cb(cb)
    a.set_values(from_value, to_value)
    a.set_duration(duration_ms)
    if on_done_cb is not None:
        a.set_completed_cb(on_done_cb)
    return a

def slide_x(obj, from_x, to_x, duration_ms, on_done_cb=None):
    """Prepare (but do NOT start) an x slide. Returns anim."""
    return _slide(obj, from_x, to_x, duration_ms, axis="x", on_done_cb=on_done_cb)

def slide_y(obj, from_y, to_y, duration_ms, on_done_cb=None):
    """Prepare (but do NOT start) a y slide. Returns anim."""
    return _slide(obj, from_y, to_y, duration_ms, axis="y", on_done_cb=on_done_cb)

def create_anims_for_transition(old_screen, new_screen, anim_type, on_done_cb=None, old_bar=None, new_bar=None):
    """Prepare (but do NOT start) and return anim(s) for a screen transition of the given type.

    old_bar / new_bar: optional context bar objects to animate in sync with
    the screen on vertical transitions (entering / leaving a context).
    """
    anims = []

    content_w_old = old_screen.get_width()
    content_w_new = new_screen.get_width()
    assert(content_w_old == content_w_new)  # caller must ensure this for horizontal animations
    assert(content_w_old == SCREEN_WIDTH)  # caller must ensure this for horizontal animations
    W = SCREEN_WIDTH

    if anim_type == GUIAnimations.horizontal_slide_in:
        anims.append(slide_x(new_screen, W, 0, ANIM_MS_HORIZONTAL, on_done_cb=on_done_cb))
    elif anim_type == GUIAnimations.horizontal_slide_out:
        new_screen.set_x(0)
        old_screen.move_foreground()  # old must be on top so its slide-out is visible
        anims.append(slide_x(old_screen, 0, W, ANIM_MS_HORIZONTAL, on_done_cb=on_done_cb))
    elif anim_type == GUIAnimations.horizontal_push_in:
        anims.append(slide_x(new_screen, W, 0, ANIM_MS_HORIZONTAL))
        anims.append(slide_x(old_screen, 0, -W, ANIM_MS_HORIZONTAL, on_done_cb=on_done_cb))
    elif anim_type == GUIAnimations.horizontal_push_out:
        anims.append(slide_x(new_screen, -W, 0, ANIM_MS_HORIZONTAL))
        anims.append(slide_x(old_screen, 0, W, ANIM_MS_HORIZONTAL, on_done_cb=on_done_cb))
    elif anim_type == GUIAnimations.vertical_slide_in:
        # Screen and bar form a unit of total height _CONTENT_H.  Both must travel
        # _CONTENT_H pixels so they stay visually glued together.
        # (content is offset by bar height when a bar is present, so the screen must
        # start at content y=_CONTENT_H even though its own height is smaller.)
        anims.append(slide_y(new_screen, _CONTENT_H, 0, ANIM_MS_VERTICAL, on_done_cb=on_done_cb))
        if new_bar:
            anims.append(slide_y(new_bar, _CONTENT_H, 0, ANIM_MS_VERTICAL))
    elif anim_type == GUIAnimations.vertical_slide_out:
        # Mirror of slide_in: both screen and bar exit downward by _CONTENT_H pixels.
        new_screen.set_y(0)
        old_screen.move_foreground()  # old must cover new while sliding away
        anims.append(slide_y(old_screen, 0, _CONTENT_H, ANIM_MS_VERTICAL, on_done_cb=on_done_cb))
        if old_bar:
            old_bar.move_foreground()
            anims.append(slide_y(old_bar, 0, _CONTENT_H, ANIM_MS_VERTICAL))
    return anims