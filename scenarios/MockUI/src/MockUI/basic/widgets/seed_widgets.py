"""Seed model widget helpers — reusable LVGL building blocks for seed display.
"""

import lvgl as lv
from ..symbol_lib import BTC_ICONS
from ..ui_consts import WHITE_HEX, GREY_HEX, SMALL_TEXT_FONT, FINGERPRINT_LBL_WIDTH
from .icon_widgets import make_icon
from .labels import _make_label


def fingerprint_badge(parent, seed, digits=4):
    """Append a FINGERPRINT icon and the first *digits* hex chars of *seed*'s
    fingerprint to *parent*.

    Strips any leading ``0x`` prefix before truncating.

    Returns the fingerprint ``lv.label``.
    """
    make_icon(parent, BTC_ICONS.RELAY, WHITE_HEX)
    fp = seed.get_fingerprint()
    if fp[:2].lower() == "0x":
        fp = fp[2:]
    lbl = _make_label(parent, fp[:digits+1], width=FINGERPRINT_LBL_WIDTH, font=SMALL_TEXT_FONT)
    lbl.set_long_mode(lv.label.LONG_MODE.CLIP)
    return lbl


def passphrase_toggle(parent, seed, gui, stop_bubbling=False):
    """Append a PASSWORD toggle icon to *parent* for *seed*'s passphrase.

    Only creates the widget when ``seed.passphrase is not None``.  The icon is
    white when ``passphrase_active`` is True, grey when False.  Tapping
    toggles the flag and calls ``gui.refresh_ui()``.

    Args:
        stop_bubbling: When True the CLICKED event's ``stop_bubbling`` flag is
                       set

    Returns:
        The ``lv.image`` widget, or None when no passphrase is set.
    """
    if seed.passphrase is None:
        return None

    color = WHITE_HEX if seed.passphrase_active else GREY_HEX
    img = make_icon(parent, BTC_ICONS.PASSWORD, color)
    img.add_flag(lv.obj.FLAG.CLICKABLE)

    def _make_cb(s):
        def _cb(e):
            if e.get_code() != lv.EVENT.CLICKED:
                return
            if stop_bubbling:
                e.stop_bubbling = 1
            s.passphrase_active = not s.passphrase_active
            gui.refresh_ui()
        return _cb

    img.add_event_cb(_make_cb(seed), lv.EVENT.CLICKED, None)
    return img
