"""Wallet model widget helpers — reusable LVGL building blocks for wallet display.
"""

import lvgl as lv
from .icon_widgets import make_icon
from .inputs import title_textarea
from .labels import make_label, menu_label, optimize_font_size
from .card_helpers import build_delete_slot
from ..symbol_lib import BTC_ICONS
from ..theming import apply_style, remove_style, get_style
from ..utils.ui_consts import BTC_ICON_WIDTH, SCREEN_WIDTH, CARD_H
from ..templates.specter_gui_base import SpecterGuiElement
from ..utils import set_size, set_align, style_as_flex_container

# Wallet-card slot names (ordered as they appear left-to-right in default layout)
WALLET_SLOTS = ("leading_icon", "type_icon", "name", "threshold", "account", "net", "delete")

# Fixed width budgets
_ICON_W    = BTC_ICON_WIDTH
_THRESH_W  = 42
_ACC_W     = 36
_NET_W     = 42

def wallet_signing_status_modifier(wallet, device_state):
    """Return MODIFIER.MUTED when not all required keys are loaded, None otherwise.

    Used to style the wallet type icon and any associated text (e.g. multisig
    threshold label) consistently everywhere wallets are displayed.
    """
    matched, required = device_state.signing_match_count(wallet)
    return None if (required > 0 and matched >= required) else get_style("MODIFIER.MUTED")


_NET_MAP = {"mainnet": "main", "testnet": "test", "signet": "sig", "regtest": "reg"}


def wallet_net_text(wallet):
    """Return the short network label for *wallet* (e.g. ``'test'``).
    """
    return _NET_MAP.get(wallet.net)


def wallet_account_text(wallet):
    """Return the account label string for *wallet* (e.g. ``'#2'``).
    """
    return "#" + str(wallet.account)


class MultisigKeyIcon(SpecterGuiElement):
    """Composite multisig type icon: two overlapping keys with independent colours.

    Rendered as two ``lv.image`` layers inside a transparent ``BTC_ICON_WIDTH``
    square container — the same approach as ``Battery``.

    Colour semantics
    ----------------
    lower/front key  - white when ≥ 1 related key is loaded, grey otherwise
                       (wallet is related to the loaded keys)
    upper/back  key  - white when ≥ quorum (wallet.threshold) keys loaded, grey otherwise
                       (device can fully sign without further keys)
    """

    def __init__(self, parent, wallet, device_state):
        super().__init__(parent)
        set_size(self, BTC_ICON_WIDTH, BTC_ICON_WIDTH)
        apply_style(self, "WIDGET.INFO_ITEM")
        # Upper/background key — rendered first, appears behind
        self.key_back = make_icon(self, BTC_ICONS.KEY_MULTI_BACK)
        set_align(self.key_back, lv.ALIGN.CENTER)
        apply_style(self.key_back, "WIDGET.INFO_ITEM")
        # Lower/foreground key — rendered second, appears in front
        self.key_front = make_icon(self, BTC_ICONS.KEY_MULTI_FRONT)
        set_align(self.key_front, lv.ALIGN.CENTER)
        apply_style(self.key_front, "WIDGET.INFO_ITEM")
        self.update(wallet, device_state)

    def update(self, wallet, device_state):
        """Restyle both key layers based on current signing readiness."""
        matched, _ = device_state.signing_match_count(wallet)
        threshold = getattr(wallet, 'threshold', 1) or 1
        
        if not matched >= threshold:
            apply_style(self.key_back, "MODIFIER.MUTED")
        else:
            remove_style(self.key_back, "MODIFIER.MUTED")

        if not matched >= 1:
            apply_style(self.key_front, "MODIFIER.MUTED")
        else:
            remove_style(self.key_front, "MODIFIER.MUTED")


def wallet_type_icon(parent, wallet, device_state):
    """Append a wallet type icon to *parent* with colour indicating signing readiness.

    Returns the widget (``lv.image`` for single-sig/non-standard,
    ``MultisigKeyIcon`` container for multisig).
    """
    ico = None
    mod = None
    if not wallet.is_standard():
        ico = make_icon(parent, BTC_ICONS.CONSOLE)
        mod = wallet_signing_status_modifier(wallet, device_state)
    elif wallet.isMultiSig:
        ico = MultisigKeyIcon(parent, wallet, device_state)
    else:
        ico = make_icon(parent, BTC_ICONS.KEY)
        mod = wallet_signing_status_modifier(wallet, device_state)
        
    apply_style(ico, "WIDGET.INFO_ITEM")
    if mod is not None:
        apply_style(ico, mod)
    return ico


class WalletCard(SpecterGuiElement):
    """Wallet card row widget — layout + optional callbacks for one wallet.

    Slot names control presence and left-to-right order of child widgets:

        ``"leading_icon"``  — icon passed via *leading_icon* arg
        ``"type_icon"``     — wallet type icon coloured by signing status
        ``"name"``          — wallet label; editable textarea if *on_name_click* provided
                              (never editable for the default wallet)
        ``"threshold"``     — M/N multisig label; only when wallet.isMultiSig
        ``"account"``       — account number label; only when wallet.account != 0
        ``"net"``           — network label; only when wallet is not mainnet
        ``"delete"``        — TRASH button; only when *on_delete* is provided

    Attributes:
        row        — the underlying ``lv.obj`` flex row
        text_edit  — the editable ``lv.textarea`` for the name slot, or ``None``
    """

    def __init__(self, parent, wallet, device_state, *,
                 height=None,
                 width=SCREEN_WIDTH,
                 slots=("leading_icon", "type_icon", "name", "threshold", "account", "net", "delete"),
                 leading_icon=None,
                 on_card_click=None,
                 on_name_click=None,
                 on_delete=None):

        super().__init__(parent)
        if height is None:
            height = lv.SIZE_CONTENT

        style_as_flex_container(self,
                                flow=lv.FLEX_FLOW.ROW,
                                main_align=lv.FLEX_ALIGN.START,
                                width=width, height=height, 
                                scrollable=False)
        # ── Input validation ──────────────────────────────────────────────────
        for s in slots:
            if s not in WALLET_SLOTS:
                print(f"WalletCard warning: unknown slot '{s}'")
        slots = tuple(s for s in slots if s in WALLET_SLOTS)
        if "name" not in slots:
            print("WalletCard warning: 'name' slot expected, adding to front.")
            slots = ("name",) + slots
        if "leading_icon" in slots and leading_icon is None:
            print("WalletCard warning: 'leading_icon' requires leading_icon= argument. dropping.")
            slots = tuple(s for s in slots if s != "leading_icon")
        if "delete" in slots and on_delete is None:
            print("WalletCard warning: 'delete' requires on_delete= callback. dropping.")
            slots = tuple(s for s in slots if s != "delete")

        # ── Derived flags ─────────────────────────────────────────────────────
        show_threshold = "threshold" in slots and wallet.isMultiSig and wallet.threshold is not None
        show_account   = "account" in slots and getattr(wallet, "account", 0) != 0
        show_net       = "net" in slots and wallet_net_text(wallet) not in (None, "main")
        show_delete    = "delete" in slots

        # ── Width budget ──────────────────────────────────────────────────────
        slot_widths = {
            "leading_icon": _ICON_W,
            "type_icon":    _ICON_W,
            "threshold":    _THRESH_W if show_threshold else 0,
            "account":      _ACC_W   if show_account   else 0,
            "net":          _NET_W   if show_net       else 0,
            "delete":       _ICON_W  if show_delete    else 0,
        }

        # ── Build row ─────────────────────────────────────────────────────────
        self.text_edit = None
        if on_card_click is not None:
            self.add_event_cb(on_card_click, lv.EVENT.CLICKED, None)

        for slot in slots:
            if slot == "leading_icon":
                self.leading_ico = make_icon(self, leading_icon)
                apply_style(self.leading_ico, ["WIDGET.INFO_ITEM"])

            elif slot == "type_icon":
                self.wallet_type_ico = wallet_type_icon(self, wallet, device_state)

            elif slot == "name":
                if on_name_click is not None and not wallet.is_default_wallet():
                    self.name_widget = title_textarea(self)
                    self.name_widget.set_text(wallet.label)
                    self.name_widget.add_event_cb(lambda e: on_name_click(self.name_widget), lv.EVENT.CLICKED, None)
                    self.text_edit = self.name_widget
                else:
                    self.name_widget = menu_label(self, wallet.label)
                
                self.name_widget.set_flex_grow(1)
                # when all slots are builtcthe actual width of the name widget
                # will be set and we can set its font optimally for the content
                def _on_name_resized(e):
                    optimize_font_size(self.name_widget)
                self.name_widget.add_event_cb(_on_name_resized, lv.EVENT.SIZE_CHANGED, None)

            elif slot == "threshold" and show_threshold:
                n = len(wallet.required_fingerprints)
                self.thresh_lbl = make_label(
                    self,
                    str(wallet.threshold) + "/" + str(n),
                )
                apply_style(self.thresh_lbl, ["WIDGET.INFO_ITEM", "TEXT.BODY", "TEXT.SMALL"])
                mod = wallet_signing_status_modifier(wallet, device_state)
                if mod is not None:
                    apply_style(self.thresh_lbl, "MODIFIER.MUTED")

            elif slot == "account" and show_account:
                self.acc_lbl = make_label(self, wallet_account_text(wallet))
                apply_style(self.acc_lbl, ["WIDGET.INFO_ITEM", "TEXT.SMALL"])

            elif slot == "net" and show_net:
                self.net_lbl = make_label(self, wallet_net_text(wallet))
                apply_style(self.net_lbl, ["WIDGET.INFO_ITEM", "TEXT.SMALL"])

            elif slot == "delete":
                self.del_btn = build_delete_slot(self, BTC_ICON_WIDTH, BTC_ICON_WIDTH, on_delete)
