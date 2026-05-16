"""Seed model widget helpers — reusable LVGL building blocks for seed display.
"""

import lvgl as lv
from ..symbol_lib import BTC_ICONS
from ..ui_consts import (
    WHITE_HEX, GREY_HEX, ORANGE_HEX, SMALL_TEXT_FONT, FINGERPRINT_LBL_WIDTH,
    BTC_ICON_WIDTH, BIG_PAD, STATUS_BTN_HEIGHT, SCREEN_WIDTH, CARD_H,
)
from .icon_widgets import make_icon
from .labels import make_label, best_font_for_size
from .card_helpers import build_card_row, build_leading_icon_slot, build_name_slot, build_delete_slot

# Width contributions of fixed slots (pixels)
_ICON_W = BTC_ICON_WIDTH          # any single icon slot
_FP_W   = _ICON_W + FINGERPRINT_LBL_WIDTH   # relay icon + 4-char label

SEED_SLOTS = ("leading_icon", "name", "backup_warning", "passphrase", "fingerprint", "delete")


def fingerprint_badge(parent, seed, digits=4):
    """Append a FINGERPRINT icon and the first *digits* hex chars of *seed*'s
    fingerprint to *parent*.

    Strips any leading ``0x`` prefix before truncating.

    Returns the fingerprint ``lv.label``.
    """
    make_icon(parent, BTC_ICONS.FINGERPRINT, WHITE_HEX)
    fp = seed.get_fingerprint()
    if fp[:2].lower() == "0x":
        fp = fp[2:]
    lbl = make_label(parent, fp[:digits+1], width=FINGERPRINT_LBL_WIDTH, font=SMALL_TEXT_FONT)
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


def build_seed_card(
    parent,
    seed,
    *,
    height=None,
    width=SCREEN_WIDTH,
    slots=("leading_icon", "name", "backup_warning", "passphrase", "fingerprint", "delete"),
    leading_icon=None,
    on_card_click=None,
    on_name_click=None,
    on_delete=None,
    on_backup_warning=None,
    gui=None,
    border=True,
    event_bubble=False,
):
    """Build a horizontal seed card row inside *parent*.

    Slot names control both presence and order of child widgets:

        ``"leading_icon"``   — icon passed via *leading_icon* arg (e.g. BTC_ICONS.KEY_OUTLINE)
        ``"name"``           — seed label; editable textarea if *on_name_click* is provided,
                               otherwise a static clipped label
        ``"backup_warning"`` — ALERT_CIRCLE icon (orange), only rendered when seed is not backed up
        ``"passphrase"``     — PASSWORD toggle icon; only rendered when seed has a passphrase set.
                               Requires *gui* argument.
        ``"fingerprint"``    — FINGERPRINT icon + first 4 hex chars of seed fingerprint
        ``"delete"``         — TRASH icon button; only rendered when *on_delete* is provided

    Args:
        parent:            LVGL parent object.
        seed:              Seed model object.
        height:            Row height in pixels; defaults to ``CARD_H``.
        width:             Row width in pixels; defaults to ``SCREEN_WIDTH``.
        slots:             Iterable of slot name strings controlling presence and
                           left-to-right order of child widgets.
        leading_icon:      Icon factory (e.g. ``BTC_ICONS.KEY_OUTLINE``) for the
                           ``"leading_icon"`` slot.  Required when ``"leading_icon"``
                           is in *slots*.
        on_card_click:     ``cb(event)`` attached to the row; fires on ``CLICKED``.
        on_name_click:     ``cb(textarea)`` called when the name widget is clicked.
                           When provided, the name is rendered as an editable textarea;
                           otherwise it is a static label.
        on_delete:         ``cb()`` called when the delete button is pressed (after
                           ``stop_bubbling``).  Required when ``"delete"`` is in *slots*.
        on_backup_warning: ``cb()`` called when the backup-warning icon is pressed.
                           When ``None`` and ``"backup_warning"`` is in *slots*, the slot
                           is still rendered but with no click handler.
        gui:               SpecterGui instance.  Required when ``"passphrase"`` is in
                           *slots* and the seed has a passphrase set.

    Returns:
        The editable ``lv.textarea`` widget for the name slot, or ``None`` when
        the name is rendered as a static label.
    """
    if height is None:
        height = CARD_H

    # ── Input validation ─────────────────────────────────────────────────────
    slots = tuple(slots)
    unknown = [s for s in slots if s not in SEED_SLOTS]
    assert not unknown, "Unknown seed card slots: " + str(unknown)
    assert "name" in slots, "'name' slot is mandatory"
    if "leading_icon" in slots:
        assert leading_icon is not None, "'leading_icon' slot requires leading_icon= argument"
    if "delete" in slots:
        assert on_delete is not None, "'delete' slot requires on_delete= callback"
    if "passphrase" in slots and seed.passphrase is not None:
        assert gui is not None, "'passphrase' slot requires gui= argument when seed has a passphrase"

    # ── Width budget for the name slot ───────────────────────────────────────
    fixed_w = 2 * BIG_PAD   # row left+right padding
    for slot in slots:
        if slot == "leading_icon":
            fixed_w += _ICON_W
        elif slot == "backup_warning" and not seed.is_backed_up:
            fixed_w += _ICON_W
        elif slot == "passphrase" and seed.passphrase is not None:
            fixed_w += _ICON_W
        elif slot == "fingerprint":
            fixed_w += _FP_W
        elif slot == "delete" and on_delete is not None:
            fixed_w += _ICON_W
    name_w = max(10, width - fixed_w)

    # ── Build row ────────────────────────────────────────────────────────────
    row = build_card_row(parent, height=height, width=width, border=border, on_card_click=on_card_click)
    ta = None

    for slot in slots:
        if slot == "leading_icon":
            build_leading_icon_slot(row, leading_icon)

        elif slot == "name":
            ta = build_name_slot(row, seed.label, name_w, height, on_name_click)

        elif slot == "backup_warning":
            if not seed.is_backed_up:
                warn_img = make_icon(row, BTC_ICONS.ALERT_CIRCLE, ORANGE_HEX)
                if on_backup_warning is not None:
                    warn_img.add_flag(lv.obj.FLAG.CLICKABLE)
                    def _warn_cb(e):
                        if e.get_code() == lv.EVENT.CLICKED:
                            e.stop_bubbling = 1
                            on_backup_warning()
                    warn_img.add_event_cb(_warn_cb, lv.EVENT.CLICKED, None)

        elif slot == "passphrase":
            passphrase_toggle(row, seed, gui, stop_bubbling=True)

        elif slot == "fingerprint":
            fingerprint_badge(row, seed, digits=4)

        elif slot == "delete":
            build_delete_slot(row, _ICON_W, height, on_delete)

    if event_bubble:
        row.add_flag(lv.obj.FLAG.EVENT_BUBBLE)
    return ta
