"""Wallet model widget helpers — reusable LVGL building blocks for wallet display.
"""

import lvgl as lv
from ..symbol_lib import BTC_ICONS
from ..ui_consts import (
    WHITE_HEX, GREY_HEX, BTC_ICON_WIDTH, BIG_PAD, SCREEN_WIDTH,
    STATUS_BTN_HEIGHT, SMALL_TEXT_FONT,
)
from .icon_widgets import make_icon

# Wallet-card slot names (ordered as they appear left-to-right in default layout)
WALLET_SLOTS = ("leading_icon", "type_icon", "name", "threshold", "account", "net", "delete")

# Fixed width budgets
_ICON_W    = BTC_ICON_WIDTH
_THRESH_W  = 40
_ACC_W     = 36
_NET_W     = 42

# Default card height (matches dropup.py _CARD_H)
_CARD_H = STATUS_BTN_HEIGHT + 2 * BIG_PAD + 2


def wallet_signing_color(wallet, device_state):
    """Return WHITE_HEX when all required keys are loaded, GREY_HEX otherwise.

    Used to colour the wallet type icon and any associated text (e.g. multisig
    threshold label) consistently everywhere wallets are displayed.
    """
    matched, required = device_state.signing_match_count(wallet)
    return WHITE_HEX if (required > 0 and matched >= required) else GREY_HEX


_NET_MAP = {"mainnet": "main", "testnet": "test", "signet": "sig", "regtest": "reg"}


def wallet_net_text(wallet):
    """Return the short network label for *wallet* (e.g. ``'test'``).
    """
    return _NET_MAP.get(wallet.net)


def wallet_account_text(wallet):
    """Return the account label string for *wallet* (e.g. ``'#2'``).
    """
    return "#" + str(wallet.account)


def add_wallet_type_icon(parent, wallet, device_state):
    """Append a wallet type icon to *parent* with colour indicating signing readiness.

    Returns the ``lv.image`` widget.
    """
    if not wallet.is_standard():
        icon = BTC_ICONS.CONSOLE
    elif wallet.isMultiSig:
        icon = BTC_ICONS.TWO_KEYS
    else:
        icon = BTC_ICONS.KEY
    color = wallet_signing_color(wallet, device_state)
    return make_icon(parent, icon, color)


def build_wallet_card(
    parent,
    wallet,
    device_state,
    *,
    height=None,
    width=SCREEN_WIDTH,
    slots=("leading_icon", "type_icon", "name", "threshold", "account", "net", "delete"),
    leading_icon=None,
    on_card_click=None,
    on_name_click=None,
    on_delete=None,
    gui=None,
    border=True,
    event_bubble=False,
):
    """Build a horizontal wallet card row inside *parent*.

    Slot names control both presence and order of child widgets:

        ``"leading_icon"``  — icon passed via *leading_icon* arg (e.g. BTC_ICONS.WALLET_OUTLINE)
        ``"type_icon"``     — wallet type icon (key / two-keys / console) coloured by signing status
        ``"name"``          — wallet label; editable textarea if *on_name_click* is provided,
                              otherwise a static clipped label.  For the default wallet,
                              always rendered as static even when *on_name_click* is set.
        ``"threshold"``     — M/N multisig label; only rendered when wallet.isMultiSig
        ``"account"``       — account number label; only rendered when wallet.account != 0
        ``"net"``           — network label; only rendered when wallet is not mainnet
        ``"delete"``        — TRASH icon button; only rendered when *on_delete* is provided

    Args:
        parent:         LVGL parent object.
        wallet:         Wallet model object.
        device_state:   DeviceState instance (needed for signing-colour calculation).
        height:         Row height in pixels; defaults to ``_CARD_H``.
        width:          Row width in pixels; defaults to ``SCREEN_WIDTH``.
        slots:          Iterable of slot name strings controlling presence and
                        left-to-right order of child widgets.
        leading_icon:   Icon factory for the ``"leading_icon"`` slot.
                        Required when ``"leading_icon"`` is in *slots*.
        on_card_click:  ``cb(event)`` attached to the row; fires on ``CLICKED``.
        on_name_click:  ``cb(textarea)`` called when the name widget is clicked.
                        When provided (and wallet is not the default wallet), the name
                        is rendered as an editable textarea; otherwise a static label.
        on_delete:      ``cb()`` called when the delete button is pressed (after
                        ``stop_bubbling``).  Required when ``"delete"`` is in *slots*.
        gui:            Unused; reserved for future use (accepted to keep call-site
                        signatures symmetric with build_seed_card).

    Returns:
        The created row ``lv.obj``.
    """
    from .labels import _make_label, best_font_for_size
    from .containers import card_row

    if height is None:
        height = _CARD_H

    # ── Input validation ─────────────────────────────────────────────────────
    slots = tuple(slots)
    unknown = [s for s in slots if s not in WALLET_SLOTS]
    assert not unknown, "Unknown wallet card slots: " + str(unknown)
    assert "name" in slots, "'name' slot is mandatory"
    if "leading_icon" in slots:
        assert leading_icon is not None, "'leading_icon' slot requires leading_icon= argument"
    if "delete" in slots:
        assert on_delete is not None, "'delete' slot requires on_delete= callback"

    # ── Derived flags ─────────────────────────────────────────────────────────
    show_threshold = "threshold" in slots and wallet.isMultiSig and wallet.threshold is not None
    show_account   = "account" in slots and getattr(wallet, "account", 0) != 0
    show_net       = "net" in slots and wallet_net_text(wallet) not in (None, "main")
    show_delete    = "delete" in slots and on_delete is not None

    # ── Width budget for the name slot ────────────────────────────────────────
    fixed_w = 2 * BIG_PAD
    for slot in slots:
        if slot == "leading_icon":
            fixed_w += _ICON_W
        elif slot == "type_icon":
            fixed_w += _ICON_W
        elif slot == "threshold" and show_threshold:
            fixed_w += _THRESH_W
        elif slot == "account" and show_account:
            fixed_w += _ACC_W
        elif slot == "net" and show_net:
            fixed_w += _NET_W
        elif slot == "delete" and show_delete:
            fixed_w += _ICON_W
    name_w = max(10, width - fixed_w)

    # ── Build row ─────────────────────────────────────────────────────────────
    row = card_row(parent, height=height, width=width, border=border)
    if on_card_click is not None:
        row.add_event_cb(on_card_click, lv.EVENT.CLICKED, None)

    for slot in slots:
        if slot == "leading_icon":
            make_icon(row, leading_icon, WHITE_HEX)

        elif slot == "type_icon":
            add_wallet_type_icon(row, wallet, device_state)

        elif slot == "name":
            name_font, display_text = best_font_for_size(wallet.label, name_w, height)
            editable = on_name_click is not None and not wallet.is_default_wallet()
            if editable:
                from .inputs import title_textarea
                parent.ta = title_textarea(row)
                parent.ta.set_width(name_w)
                parent.ta.set_style_text_font(name_font, 0)
                parent.ta.set_text(display_text)
                def _make_name_cb(t):
                    def _cb(e):
                        if e.get_code() == lv.EVENT.CLICKED:
                            on_name_click(t)
                    return _cb
                parent.ta.add_event_cb(_make_name_cb(parent.ta), lv.EVENT.CLICKED, None)
            else:
                lbl = _make_label(row, display_text, width=name_w, font=name_font)
                lbl.set_long_mode(lv.label.LONG_MODE.CLIP)

        elif slot == "threshold" and show_threshold:
            n = len(wallet.required_fingerprints)
            thresh_lbl = _make_label(
                row,
                str(wallet.threshold) + "/" + str(n),
                width=_THRESH_W,
                font=SMALL_TEXT_FONT,
            )
            thresh_lbl.set_long_mode(lv.label.LONG_MODE.CLIP)

        elif slot == "account" and show_account:
            acc_lbl = _make_label(row, wallet_account_text(wallet), width=_ACC_W, font=SMALL_TEXT_FONT)
            acc_lbl.set_long_mode(lv.label.LONG_MODE.CLIP)

        elif slot == "net" and show_net:
            net_lbl = _make_label(row, wallet_net_text(wallet), width=_NET_W, font=SMALL_TEXT_FONT)
            net_lbl.set_long_mode(lv.label.LONG_MODE.CLIP)

        elif slot == "delete" and show_delete:
            from .btn import Btn
            def _del_cb(event=None):
                if event is not None:
                    event.stop_bubbling = 1
                on_delete()
            del_btn = Btn(row, icon=BTC_ICONS.TRASH, size=(_ICON_W, height), callback=_del_cb)
            del_btn.make_background_transparent()

    if event_bubble:
        row.add_flag(lv.obj.FLAG.EVENT_BUBBLE)
    return row
