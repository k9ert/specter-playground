"""Label helpers — lv.label wrappers with Specter default styling."""

import lvgl as lv
from ..ui_consts import BTN_WIDTH, TEXT_FONT
from ..ui_utils import to_lv_color

# ── Font selection helpers ────────────────────────────────────────────────────

_NAME_FONTS = [
    lv.font_montserrat_28,
    lv.font_montserrat_22,
    lv.font_montserrat_16,
]


def text_width(text, font):
    """Advance width of *text* in *font*, including kerning."""
    n = len(text)
    total = 0
    for i in range(n):
        next_cp = ord(text[i + 1]) if i + 1 < n else 0
        total += font.get_glyph_width(ord(text[i]), next_cp)
    return total


def best_font_for_size(text, max_w, max_h):
    """Return *(font, display_text)* fitting *text* within max_w × max_h px.

    Tries each font in ``_NAME_FONTS`` (largest first) for a single-line fit.
    Falls back to a balanced two-line word split at font_montserrat_16 when
    the available height allows two lines.  Always returns a valid pair.
    """
    for font in _NAME_FONTS:
        if font.get_line_height() <= max_h and text_width(text, font) <= max_w:
            return font, text

    f16 = lv.font_montserrat_16
    if f16.get_line_height() * 2 <= max_h:
        words = text.split()
        best_split = None
        best_balance = None
        for i in range(1, len(words)):
            left = " ".join(words[:i])
            right = " ".join(words[i:])
            lw = text_width(left, f16)
            rw = text_width(right, f16)
            if lw <= max_w and rw <= max_w:
                balance = max(lw, rw)
                if best_balance is None or balance < best_balance:
                    best_split = left + "\n" + right
                    best_balance = balance
        if best_split is not None:
            return f16, best_split

    return lv.font_montserrat_16, text



def set_label_color(lbl, color):
    """Set text colour of an lv.label and enable recolor markup."""
    lbl.set_style_text_color(to_lv_color(color), 0)
    lbl.set_recolor(True)


def make_label(parent, text, width=None, align=None, font=None, recolor=False, color=None):
    """Base label factory: create, size, font, align, colour."""
    lbl = lv.label(parent)
    lbl.set_text(text if text is not None else "")
    lbl.set_width(width if width is not None else lv.pct(100))
    lbl.set_style_text_font(font if font is not None else TEXT_FONT, 0)
    lbl.set_style_text_align(align if align is not None else lv.TEXT_ALIGN.LEFT, 0)
    if color is not None:
        set_label_color(lbl, color)
    elif recolor:
        lbl.set_recolor(True)
    return lbl


def body_label(parent, text, width=lv.pct(100), align=lv.TEXT_ALIGN.CENTER, font=None, recolor=False, color=None):
    """Wrapping body/message label (CENTER, WRAP).
    """
    lbl = make_label(parent, text, width, align, font, recolor, color)
    lbl.set_long_mode(lv.label.LONG_MODE.WRAP)
    return lbl


def section_header(parent, text, recolor=False, color=None):
    """Section divider label for GenericMenu (LEFT-aligned)."""
    return make_label(parent, text, lv.pct(BTN_WIDTH), lv.TEXT_ALIGN.LEFT, None, recolor, color)


def form_label(parent, text, width=lv.pct(30), font=None, recolor=False, color=None):
    """Short left-aligned form field label (30% width by default)."""
    return make_label(parent, text, width, lv.TEXT_ALIGN.LEFT, font, recolor, color)
