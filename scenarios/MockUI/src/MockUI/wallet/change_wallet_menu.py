import lvgl as lv
from ..basic import GenericMenu, BTN_HEIGHT, BTN_WIDTH
from ..basic.symbol_lib import BTC_ICONS


class ChangeWalletMenu(GenericMenu):
    """Menu listing registered wallets and allowing switching the active wallet.

    Buttons:
    - one button per wallet in parent.specter_state.registered_wallets (label = wallet.name)
    - an "Add Wallet" button that navigates to the add_wallet menu

    Selecting an existing wallet sets parent.specter_state.active_wallet to that wallet
    and then navigates back (behaves like pressing back).
    """

    def __init__(self, parent, *args, **kwargs):
        # Build menu items directly to avoid GenericMenu attaching its own callbacks
        self.parent = parent
        wallets = getattr(parent.specter_state, "registered_wallets", [])

        # Get translation function from i18n manager (always available via NavigationController)
        t = parent.i18n.t

        # Initialize base GenericMenu with no auto-built items
        super().__init__("change_wallet", t("MAIN_MENU_CHANGE_ADD_WALLET"), [], parent, *args, **kwargs)

        # Helper to set active wallet and navigate back
        def _make_select_callback(wallet):
            def cb(e):
                # only act on actual clicked events
                if e.get_code() == lv.EVENT.CLICKED:
                    parent.specter_state.active_wallet = wallet
                    self.on_navigate(None)  # navigate back
            return cb

        # Create a button for each registered wallet
        for w in wallets:
            btn = lv.button(self.container)
            btn.set_width(lv.pct(BTN_WIDTH))
            btn.set_height(BTN_HEIGHT)
            lbl = lv.label(btn)
            lbl.set_text(w.name)
            lbl.center()
            btn.add_event_cb(_make_select_callback(w), lv.EVENT.CLICKED, None)

        # spacer
        spacer = lv.label(self.container)
        spacer.set_text("")

        # Add Wallet button navigates to add_wallet
        add_btn = lv.button(self.container)
        add_btn.set_width(lv.pct(BTN_WIDTH))
        add_btn.set_height(BTN_HEIGHT)
        
        # Icon on the left
        add_ico = lv.image(add_btn)
        BTC_ICONS.PLUS.add_to_parent(add_ico)
        add_ico.align(lv.ALIGN.LEFT_MID, 8, 0)
        
        # Text centered
        add_lbl = lv.label(add_btn)
        add_lbl.set_text(t("MENU_ADD_WALLET"))
        add_lbl.center()
        
        add_btn.add_event_cb(lambda e: self.on_navigate("add_wallet") if e.get_code() == lv.EVENT.CLICKED else None, lv.EVENT.CLICKED, None)
