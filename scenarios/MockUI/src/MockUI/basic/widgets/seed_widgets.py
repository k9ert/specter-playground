"""Seed model widget helpers — reusable LVGL building blocks for seed display.
"""

import lvgl as lv
from .icon_widgets import make_icon
from .containers import flex_row
from .labels import make_label
from .card_helpers import build_name_slot, build_delete_slot, compute_name_width
from ..templates.specter_gui_base import SpecterGuiElement
from ..symbol_lib import BTC_ICONS
from ..theming import apply_style
from ..utils import BTC_ICON_WIDTH, SCREEN_WIDTH, CARD_H, FINGERPRINT_LBL_WIDTH, style_as_flex_container

SEED_SLOTS = ("leading_icon", "name", "backup_warning", "passphrase", "fingerprint", "delete")

# Width contributions of fixed slots (pixels)
_ICON_W = BTC_ICON_WIDTH          # any single icon slot
_FINGERPRINT_W   = _ICON_W + FINGERPRINT_LBL_WIDTH   # relay icon + 4-char label

def fingerprint_badge(parent, seed, digits=4):
    """Append a FINGERPRINT icon and the first *digits* hex chars of *seed*'s
    fingerprint to *parent*.

    Strips any leading ``0x`` prefix before truncating.

    Returns the fingerprint ``lv.label``.
    """
    badge = flex_row(parent)
    badge._ico = make_icon(badge, BTC_ICONS.FINGERPRINT)
    apply_style(badge._ico, ["WIDGET.INFO_ITEM"])

    fp = seed.get_fingerprint()
    if fp[:2].lower() == "0x":
        fp = fp[2:]
    badge._lbl = make_label(badge, fp[:digits+1], width=FINGERPRINT_LBL_WIDTH)
    apply_style(badge._lbl, ["WIDGET.INFO_ITEM", "TEXT.BODY"])
    return badge

def passphrase_toggle(parent, seed):
    """Append a PASSWORD toggle icon to *parent* for *seed*'s passphrase.

    Only creates the widget when ``seed.passphrase is not None``.  The icon is
    styled as INFO_ITEM when ``passphrase_active`` is True, MUTED when False.  
    Tapping toggles the flag and calls ``gui.refresh_ui()``.

    Returns:
        The ``lv.image`` widget, or None when no passphrase is set.
    """
    if seed.passphrase is None:
        return None

    img = make_icon(parent, BTC_ICONS.PASSWORD)
    img.add_flag(lv.obj.FLAG.CLICKABLE)
    apply_style(img, "WIDGET.INFO_ITEM")
    apply_style(img, "MUTED", lv.STATE.DISABLED)
    img.set_state(lv.STATE.DISABLED, not seed.passphrase_active)

    def _cb(e):
        e.stop_bubbling = 1
        seed.passphrase_active = not seed.passphrase_active
        img.set_state(lv.STATE.DISABLED, not seed.passphrase_active)
        parent.gui.refresh_ui()

    img.add_event_cb(_cb, lv.EVENT.CLICKED, None)
    return img

class SeedCard(SpecterGuiElement):
    """Seed card row widget — layout + optional callbacks for one seed.

    Slot names control presence and left-to-right order of child widgets:

        ``"leading_icon"``   — icon passed via *leading_icon* arg
        ``"name"``           — seed label; editable textarea if *on_name_click* provided
        ``"backup_warning"`` — ALERT_CIRCLE icon; only when seed is not backed up
        ``"passphrase"``     — PASSWORD toggle; only when seed has a passphrase set
        ``"fingerprint"``    — FINGERPRINT icon + first 4 hex chars of fingerprint
        ``"delete"``         — TRASH button; only when *on_delete* is provided

    Attributes:
        row        — the underlying ``lv.obj`` flex row
        text_edit  — the editable ``lv.textarea`` for the name slot, or ``None``
    """

    def __init__(self, parent, seed, *,
                 height=None,
                 width=SCREEN_WIDTH,
                 slots=("leading_icon", "name", "backup_warning", "passphrase", "fingerprint", "delete"),
                 leading_icon=None,
                 on_card_click=None,
                 on_name_click=None,
                 on_delete=None,
                 on_backup_warning=None):
        super().__init__(parent)
        if height is None:
            height = CARD_H

        style_as_flex_container(self, width=width, height=height, scrollable=False)

        # ── Input validation ──────────────────────────────────────────────────
        for s in slots:
            if s not in SEED_SLOTS:
                print(f"SeedCard warning: unknown slot '{s}'")
        slots = tuple(s for s in slots if s in SEED_SLOTS)
        if "name" not in slots:
            print("SeedCard warning: 'name' slot expected, adding to front.")
            slots = ("name",) + slots
        if "leading_icon" in slots and leading_icon is None:
            print("SeedCard warning: 'leading_icon' requires leading_icon= argument. dropping.")
            slots = tuple(s for s in slots if s != "leading_icon")
        if "delete" in slots and on_delete is None:
            print("SeedCard warning: 'delete' requires on_delete= callback. dropping.")
            slots = tuple(s for s in slots if s != "delete")
        if "backup_warning" in slots and on_backup_warning is None:
            print("SeedCard warning: 'backup_warning' requires on_backup_warning= callback. dropping.")
            slots = tuple(s for s in slots if s != "backup_warning")

        # ── Derived flags ─────────────────────────────────────────────────────
        show_backup_warning = "backup_warning" in slots and not seed.is_backed_up
        show_passphrase     = "passphrase" in slots and seed.passphrase is not None
        show_delete         = "delete" in slots

        # ── Width budget ──────────────────────────────────────────────────────
        slot_widths = {
            "leading_icon":   _ICON_W,
            "backup_warning": _ICON_W if show_backup_warning else 0,
            "passphrase":     _ICON_W if show_passphrase else 0,
            "fingerprint":    _FINGERPRINT_W,
            "delete":         _ICON_W if show_delete else 0,
        }
        name_w = compute_name_width(width, slots, slot_widths)

        # ── Build row ─────────────────────────────────────────────────────────

        self.text_edit = None
        if on_card_click is not None:
            self.add_event_cb(on_card_click, lv.EVENT.CLICKED, None)

        for slot in slots:
            if slot == "leading_icon":
                self.leading_ico = make_icon(self, leading_icon)
                apply_style(self.leading_ico, ["WIDGET.INFO_ITEM"])

            elif slot == "name":
                self.name_widget, is_edit = build_name_slot(self, seed.label, name_w, height, on_name_click)
                if is_edit:
                    self.text_edit = self.name_widget

            elif slot == "backup_warning":
                if show_backup_warning:
                    self.warn_img = make_icon(self, BTC_ICONS.ALERT_CIRCLE)
                    apply_style(self.warn_img, ["WIDGET.INFO_ITEM", "FG.WARNING"])
                    self.warn_img.add_flag(lv.obj.FLAG.CLICKABLE)
                    def _warn_cb(e):
                        e.stop_bubbling = 1
                        on_backup_warning()
                    self.warn_img.add_event_cb(_warn_cb, lv.EVENT.CLICKED, None)

            elif slot == "passphrase":
                if show_passphrase:
                    self.passphrase_widget = passphrase_toggle(self, seed)

            elif slot == "fingerprint":
                self.fp_badge = fingerprint_badge(self, seed, digits=4)

            elif slot == "delete":
                self.del_btn = build_delete_slot(self, _ICON_W, height, on_delete)
