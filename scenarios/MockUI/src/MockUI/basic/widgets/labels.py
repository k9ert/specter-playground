"""Label helpers — lv.label wrappers with Specter default styling."""

import lvgl as lv
from ..utils import set_size, get_size, best_fonttype_for_size
from ..theming import apply_style, get_font

# ── Font selection helpers ────────────────────────────────────────────────────

def optimize_font_size(label):
    w, h = get_size(label)
    font_key, display_text = best_fonttype_for_size(label.get_text(), w, h)
    font, err = get_font(font_key)
    label.set_text(display_text)
    label.set_style_text_font(font, 0)

def make_label(parent, text, width=lv.SIZE_CONTENT, styles = None):
    """Base label factory: create, size, font, align, colour."""
    lbl = lv.label(parent)
    lbl.set_text(text if text is not None else "")
    set_size(lbl, width, None)
    if styles is not None:
        apply_style(lbl, styles)
    return lbl

def body_label(parent, text, width=lv.pct(100)):
    lbl = make_label(parent, text, width=width, styles=["TEXT.DEFAULT", "TEXT.BODY", "TEXT.CENTER", "FG.DEFAULT"])
    lbl.set_long_mode(lv.label.LONG_MODE.WRAP)
    return lbl

def info_label(parent, text, width=None):
    return make_label(parent, text, width, ["TEXT.SMALL", "FG.DEFAULT"])

def form_label(parent, text, width=None):
    return make_label(parent, text, width, ["TEXT.DEFAULT", "FG.DEFAULT"])

def section_header(parent, text):
    return make_label(parent, text, lv.pct(100), ["WIDGET.MENU_SECTION_HEADER"]) 

def menu_label(parent, text, width=None):
    return make_label(parent, text, width, ["WIDGET.MENU_BUTTON_FG", "FG.DEFAULT", "TEXT.TITLE"])

def title_label(parent, text, width=None):
    return make_label(parent, text, width, ["WIDGET.SCREEN_TITLE"])
