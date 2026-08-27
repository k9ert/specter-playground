"""Input helpers — lv.textarea wrappers with Specter default styling."""

import lvgl as lv
from .btn import Btn
from ..symbol_lib import BTC_ICONS
from ..templates.specter_gui_base import SpecterGuiElement
from ..utils import (
    apply_click_feedback,
    set_size,
)
from ..theming import apply_style, remove_style

ACCEPTED_CHARS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/~ "
)

def make_textarea(parent, accepted_chars=ACCEPTED_CHARS):
    """Intended for editable names in the title bar."""
    ta = lv.textarea(parent)
    apply_style(ta, ["WIDGET.TEXT_EDIT"])
    apply_style(ta, "WIDGET.TEXT_EDIT_CURSOR", lv.PART.CURSOR | lv.STATE.FOCUSED)
    apply_click_feedback(ta)
    ta.set_one_line(True)
    ta.set_accepted_chars(accepted_chars)
    return ta

def make_password_textarea(parent, accepted_chars=ACCEPTED_CHARS):
    pw_ta_container = SpecterGuiElement(parent)
    apply_style(pw_ta_container, ["LAYOUT.FLEX_ROW", "LAYOUT.ALL_CENTERED", "LAYOUT.GROWS"])

    """Intended for password/passphrase entry."""
    pw_ta_container.ta = make_textarea(pw_ta_container, accepted_chars)
    apply_style(pw_ta_container.ta, "LAYOUT.GROWS")
    pw_ta_container.ta.set_password_bullet("*")

    def set_pw_mode(new_mode):
        pw_ta_container.ta.set_password_mode(new_mode)

        if new_mode:
            pw_ta_container.toggle_btn.update_icon(BTC_ICONS.VISIBLE)
        else:
            pw_ta_container.toggle_btn.update_icon(BTC_ICONS.HIDDEN)


    pw_ta_container.toggle_btn = Btn(pw_ta_container,
                     icon=BTC_ICONS.HIDDEN,
                     background_style="APPEARANCE.TRANSPARENT",
                     foreground_style="WIDGET.BUTTON_FG",
                     callback=lambda: set_pw_mode(not pw_ta_container.ta.get_password_mode())
                     )

    set_pw_mode(True)
    
    return pw_ta_container.ta


def make_switch(parent, init_value=False, setter_cb=None):
    switch = lv.switch(parent)
    apply_style(switch, "SWITCH.TRACK", lv.PART.MAIN)
    apply_style(switch, "SWITCH.KNOB", lv.PART.KNOB)
    apply_style(switch, "SWITCH.INDICATOR", lv.PART.INDICATOR)
    apply_style(switch, "BG.SUCCESS", lv.PART.INDICATOR | lv.STATE.CHECKED)
    apply_click_feedback(switch, lv.PART.KNOB)

    apply_style(switch, "MODIFIER.MUTED_BG", lv.PART.INDICATOR | lv.STATE.DISABLED)

    # Set initial state
    if init_value:
        switch.add_state(lv.STATE.CHECKED)
    else:
        switch.remove_state(lv.STATE.CHECKED)

    def _make_toggle_cb(setter_cb):
        def _cb(e):
            is_on = bool(e.get_target_obj().has_state(lv.STATE.CHECKED))
            if setter_cb is not None:
                setter_cb(is_on)
        return _cb
    switch.add_event_cb(_make_toggle_cb(setter_cb), lv.EVENT.VALUE_CHANGED, None)
    return switch

def confirmation_slider(parent,
                        on_max=None, max_value=100, max_style="BG.SUCCESS", 
                        on_min=None, min_value=-100, min_style="BG.DANGER"
                        ):
    """Bidirectional confirmation slider.
    
    User must drag the knob to confirm or reject an action.
    If released before reaching terminal position, it snaps back.
    Supports asymmetric ranges (e.g., easier to confirm than reject).
    
    Args:
        parent:         LVGL parent object.

        min_value:      Minimum slider value (left end), must be negative  (default:-100).
        max_value:      Maximum slider value (right end), must be positive (default: 100).
        
        on_min:         Zero-argument callable invoked when slider reaches min threshold.
        on_max:         Zero-argument callable invoked when slider reaches max threshold .
        
        min_style:      Style string for min direction (defaults to "BG.DANGER").
        max_style:      Style string for max direction (defaults to "BG.SUCCESS").
    The range is normalized so the larger absolute value becomes ±100. Start value is always at 0.
    
    returns the created slider

    Usage::
        slider = confirmation_slider(
            parent,
            on_max=lambda: print("Confirmed!"),
            on_min=lambda: print("Rejected!"),
        )
    """
    if min_value >= 0:
        print("Warning: min_value should be negative for a confirmation slider. Got:", min_value)
        min_value = -100
    if max_value <= 0:
        print("Warning: max_value should be positive for a confirmation slider. Got:", max_value)
        max_value = 100

    abs_max = max(abs(min_value), abs(max_value))
    min_value = int(min_value * 100 / abs_max)
    max_value = int(max_value * 100 / abs_max)

    # Create slider
    slider = lv.slider(parent)
    slider.set_range(min_value, max_value)
    slider.set_mode(lv.slider.MODE.SYMMETRICAL)
    
    apply_style(slider, "SLIDER.INDICATOR", lv.PART.INDICATOR)
    apply_style(slider, "SLIDER.TRACK", lv.PART.MAIN)
    apply_style(slider, "SLIDER.KNOB", lv.PART.KNOB)
    apply_click_feedback(slider, lv.PART.KNOB)
    
    # Start at 0
    slider.set_value(0, False)
    apply_style(slider, max_style, lv.PART.INDICATOR)

    # Mutable closure state (can't set arbitrary attrs on C extension objects)
    state = {"value": 0, "min_triggered": False, "max_triggered": False}

    # Knob is only draggable, not clickable (prevents accidental taps)
    slider.add_flag(lv.obj.FLAG.ADV_HITTEST)

    # --- Callbacks (close over slider and factory params) ---

    def _update_styling(value):
        new_style = max_style if value >= 0 else min_style
        old_style = min_style if value >= 0 else max_style
        remove_style(slider, old_style, lv.PART.INDICATOR)
        apply_style(slider, new_style, lv.PART.INDICATOR)

    def _on_value_changed(event):
        value = slider.get_value()
        if (state["value"] < 0 and value >= 0) or (state["value"] >= 0 and value < 0):
            _update_styling(value)
        state["value"] = value

        if value == min_value:
            state["min_triggered"] = True
            if on_min is not None:
                on_min()
        elif value > min_value:
            state["min_triggered"] = False

        if value == max_value:
            state["max_triggered"] = True
            if on_max is not None:
                on_max()
        elif value < max_value:
            state["max_triggered"] = False

    def _on_released(event):
        if not state["min_triggered"] and not state["max_triggered"]:
            slider.set_value(0, True)
            state["value"] = 0
            _update_styling(0)

    slider.add_event_cb(_on_value_changed, lv.EVENT.VALUE_CHANGED, None)
    slider.add_event_cb(_on_released, lv.EVENT.RELEASED, None)

    return slider
