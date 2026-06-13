"""Label helpers — lv.label wrappers with Specter default styling."""

import lvgl as lv
from ..utils import set_size, set_align
from ..theming import apply_style

# ── Font selection helpers ────────────────────────────────────────────────────

def make_label(parent, text, width=lv.SIZE_CONTENT, styles = None):
    """Base label factory: create, size, font, align, colour."""
    lbl = lv.label(parent)
    lbl.set_text(text if text is not None else "")
    set_size(lbl, width, None)
    if styles is not None:
        apply_style(lbl, styles)
    return lbl

def body_label(parent, text, width=None):
    return make_label(parent, text, width, ["TEXT.DEFAULT", "TEXT.BODY", "FG.DEFAULT"])

def info_label(parent, text, width=None):
    return make_label(parent, text, width, ["TEXT.SMALL", "FG.DEFAULT"])

def form_label(parent, text, width=None):
    return make_label(parent, text, width, ["TEXT.DEFAULT", "FG.DEFAULT"])

def section_header(parent, text):
    return make_label(parent, text, lv.pct(100), ["WIDGET.MENU_SECTION_HEADER"]) 

def menu_label(parent, text, width=None):
    return make_label(parent, text, width, ["WIDGET.MENU_LABEL", "FG.DEFAULT"])

def title_label(parent, text, width=None):
    lbl = make_label(parent, text, width, ["WIDGET.SCREEN_TITLE"])
    set_align(lbl, lv.ALIGN.CENTER)
    return lbl
