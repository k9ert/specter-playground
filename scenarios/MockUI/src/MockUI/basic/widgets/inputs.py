"""Input helpers — lv.textarea wrappers with Specter default styling."""

import lvgl as lv
from ..utils import (
    CONFIRMATION_SLIDER_HEIGHT,
    FORM_TA_HEIGHT,
    SWITCH_HEIGHT, SWITCH_WIDTH,
    set_size
)
from ..theming import apply_style

ACCEPTED_CHARS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/~ "
)


def title_textarea(parent, accepted_chars=ACCEPTED_CHARS):
    """Intended for editable names in the title bar."""
    ta = lv.textarea(parent)
    apply_style(ta, ["WIDGET.TEXT_EDIT", "TEXT.TITLE"])
    ta.set_one_line(True)
    ta.set_accepted_chars(accepted_chars)
    return ta

def form_textarea(parent, width=lv.pct(60)):
    ta = lv.textarea(parent)
    set_size(ta, width, FORM_TA_HEIGHT)
    apply_style(ta, ["WIDGET.TEXT_EDIT", "TEXT.DEFAULT"])
    ta.set_one_line(True)
    return ta

def password_textarea(parent, width=lv.pct(60)):
    ta = title_textarea(parent, width)
    ta.set_password_mode(True)
    return ta

def make_switch(parent, init_value=False, setter_cb=None):
    switch = lv.switch(parent)
    set_size(switch, SWITCH_HEIGHT, SWITCH_WIDTH)
    apply_style(switch, "SWITCH.TRACK", lv.PART.MAIN)
    apply_style(switch, "SWITCH.KNOB", lv.PART.KNOB)
    apply_style(switch, "SWITCH.INDICATOR", lv.PART.INDICATOR)
    apply_style(switch, "BG.SUCCESS", lv.PART.INDICATOR | lv.STATE.CHECKED)

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
                        width=lv.pct(100), height=CONFIRMATION_SLIDER_HEIGHT,
                        on_max=None, max_value=100, max_style="FG.SUCCESS", 
                        on_min=None, min_value=-100, min_style="FG.DANGER",
                        ):
    """Bidirectional confirmation slider.
    
    User must drag the knob to confirm or reject an action.
    If released before reaching terminal position, it snaps back.
    Supports asymmetric ranges (e.g., easier to confirm than reject).
    
    Args:
        parent:         LVGL parent object.
        optional:
        width:          Slider width in pixels or lv.pct(x) (defaults to 100% of parent).
        height:         Slider height in pixels (defaults to CONFIRMATION_SLIDER_HEIGHT).

        min_value:      Minimum slider value (left end), must be negative  (default:-100).
        max_value:      Maximum slider value (right end), must be positive (default: 100).
        
        on_min:         Zero-argument callable invoked when slider reaches min threshold.
        on_max:         Zero-argument callable invoked when slider reaches max threshold .
        
        min_style:      Style string for min direction (defaults to "FG.DANGER").
        max_style:      Style string for max direction (defaults to "FG.SUCCESS").
    
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
    slider.set_width(width)
    slider.set_height(height)
    slider.set_range(min_value, max_value)
    slider.set_mode(lv.slider.MODE.SYMMETRICAL)
    
    # Start at 0
    slider.set_value(0, False)

    # Mutable closure state (can't set arbitrary attrs on C extension objects)
    state = {"value": 0, "min_triggered": False, "max_triggered": False}
    
    apply_style(slider, "SLIDER.INDICATOR", lv.PART.INDICATOR)
    apply_style(slider, "SLIDER.TRACK", lv.PART.MAIN)
    apply_style(slider, "SLIDER.KNOB", lv.PART.KNOB)
    
    # Knob is only draggable, not clickable (prevents accidental taps)
    slider.add_flag(lv.obj.FLAG.ADV_HITTEST)

    # --- Callbacks (close over slider and factory params) ---

    def _update_styling(value):
        new_style = max_style if value >= 0 else min_style
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
