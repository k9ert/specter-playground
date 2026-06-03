"""Input helpers — lv.textarea wrappers with Specter default styling."""

import lvgl as lv
from ..utils.ui_consts import (
    TITLE_ROW_HEIGHT,
    TITLE_TA_WIDTH,
    WHITE_HEX,
    TITLE_FONT,
    TEXT_FONT,
    RED_HEX,
    GREEN_HEX,
    CONFIRMATION_SLIDER_HEIGHT,
)
from ..utils.ui_utils import to_lv_color

ACCEPTED_CHARS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    "0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/~ "
)


def title_textarea(parent, accepted_chars=ACCEPTED_CHARS):
    """Editable title-bar text area (TITLE_FONT, centred, 2px white border).

    Intended for editable names in the title bar.
    """
    ta = lv.textarea(parent)
    ta.set_width(TITLE_TA_WIDTH)
    ta.set_height(TITLE_ROW_HEIGHT)
    ta.set_style_text_font(TITLE_FONT, 0)
    ta.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
    ta.set_style_border_width(1, lv.PART.MAIN)
    ta.set_style_border_color(WHITE_HEX, lv.PART.MAIN)
    ta.set_one_line(True)
    ta.set_accepted_chars(accepted_chars)
    return ta


def form_textarea(parent, width=lv.pct(60), font=TEXT_FONT):
    """Compact form input field (TEXT_FONT, height=50, 60% width by default).
    """
    ta = lv.textarea(parent)
    ta.set_width(width)
    ta.set_height(50)
    ta.set_style_text_font(font, 0)
    ta.set_style_border_width(1, lv.PART.MAIN)
    ta.set_style_border_color(WHITE_HEX, lv.PART.MAIN)
    return ta


def confirmation_slider(parent,
                        width=lv.pct(100), height=CONFIRMATION_SLIDER_HEIGHT,
                        on_max=None, max_value=100, max_color=GREEN_HEX, 
                        on_min=None, min_value=-100, min_color=RED_HEX,
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
        
        min_color:      Color for min direction (defaults to RED_HEX).
        max_color:      Color for max direction (defaults to GREEN_HEX).
    
    The range is normalized so the larger absolute value becomes ±100. Start value is always at 0.
    
    returns the created slider

    Usage::
        slider = confirmation_slider(
            parent,
            on_max=lambda: print("Confirmed!"),
            on_min=lambda: print("Rejected!"),
        )
    """
    if min_value >= 0 or max_value <= 0:
        raise ValueError("min_value must be negative and max_value must be positive.")

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

    # Calculate sizes for styling
    knob_radius = height // 2
    
    # Main part (the track/background)+
    slider.set_style_bg_opa(lv.OPA._30, lv.PART.MAIN)
    slider.set_style_pad_left(knob_radius, lv.PART.MAIN)
    slider.set_style_pad_right(knob_radius, lv.PART.MAIN)
    
    # Indicator part (the filled portion)
    slider.set_style_bg_color(to_lv_color(max_color), lv.PART.INDICATOR)
    slider.set_style_bg_opa(lv.OPA._70, lv.PART.INDICATOR)
    
    # Knob part (the draggable handle)
    slider.set_style_bg_color(to_lv_color(WHITE_HEX), lv.PART.KNOB)
    slider.set_style_bg_opa(lv.OPA.COVER, lv.PART.KNOB)
    slider.set_style_pad_all(0, lv.PART.KNOB)
    
    # Knob is only draggable, not clickable (prevents accidental taps)
    slider.add_flag(lv.obj.FLAG.ADV_HITTEST)

    # --- Callbacks (close over slider and factory params) ---

    def _update_colors(value):
        color = max_color if value >= 0 else min_color
        slider.set_style_bg_color(to_lv_color(color), lv.PART.INDICATOR)
        slider.set_style_bg_opa(lv.OPA._70, lv.PART.INDICATOR)

    def _on_value_changed(event):
        value = slider.get_value()
        if (state["value"] < 0 and value >= 0) or (state["value"] >= 0 and value < 0):
            _update_colors(value)
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
            _update_colors(0)

    slider.add_event_cb(_on_value_changed, lv.EVENT.VALUE_CHANGED, None)
    slider.add_event_cb(_on_released, lv.EVENT.RELEASED, None)

    return slider
