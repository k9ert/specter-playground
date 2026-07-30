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

def make_label(parent, text, styles = None):
    """Base label factory: create, size, font, align, colour."""
    lbl = lv.label(parent)
    lbl.set_text(text if text is not None else "")
    if styles is not None:
        apply_style(lbl, styles)
    return lbl

def body_label(parent, text, styles = None):
    lbl = make_label(parent, text, styles)

    # Post-process to make sure textwrapping actually works
    # (a max. width for the label is needed, otherwise it
    #  will just expand to fit the text)
    w = lbl.get_style_width(lv.PART.MAIN)
    if w == lv.SIZE_CONTENT:
        set_size(lbl, width=lv.pct(100))
        
    lbl.set_long_mode(lv.label.LONG_MODE.WRAP)
    return lbl
