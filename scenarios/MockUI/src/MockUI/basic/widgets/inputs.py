"""Input helpers — lv.textarea wrappers with Specter default styling."""

import lvgl as lv
from ..ui_consts import TITLE_ROW_HEIGHT, TITLE_TA_WIDTH, WHITE_HEX, TITLE_FONT, TEXT_FONT

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
