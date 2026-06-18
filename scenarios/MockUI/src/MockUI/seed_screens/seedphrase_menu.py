from ..basic import GenericMenu, BTC_ICONS, MenuItem
from ..basic.symbol_lib import BTC_ICONS
from ..basic.components.confirm_modals import confirm_delete_seed, make_delete_active_handler
from ..basic.widgets import MenuItem


class SeedPhraseMenu(GenericMenu):
    """Manage Seedphrase menu — includes passphrase, storage, and advanced options.

    menu_id: "manage_seedphrase"
    """
    TITLE_KEY = "MENU_MANAGE_SEED"

    def get_menu_items(self, t, state):
        # Sign message (only when signing is possible)
        has_controlled_input = (state.QR_enabled() or state.SD_detected())
        can_sign_msg = (
            len(state.registered_wallets) > 0
            and not all(wallet.isMultiSig for wallet in state.registered_wallets)
            and has_controlled_input
        )

        menu_items = []

        menu_items.append(MenuItem(BTC_ICONS.VISIBLE, t("SEEDPHRASE_MENU_SHOW"),
                                   target="show_seedphrase",
                                   modifier="Warning",
                                   is_submenu=True))

        pp_label = t("MENU_CHANGE_CLEAR_PASSPHRASE") if self.ui_state.active_seed.passphrase else t("MENU_SET_PASSPHRASE")
        menu_items.append(MenuItem(BTC_ICONS.PASSWORD, pp_label, "set_passphrase", is_submenu=True))

        menu_items += [
            MenuItem(text=t("SEEDPHRASE_MENU_BACKUP")),
            MenuItem(BTC_ICONS.RECEIVE, t("SEEDPHRASE_MENU_STORE_TO") + "...", "store_seedphrase", is_submenu=True),
        ]

        # Explore section
        menu_items += [
            MenuItem(text=t("SEEDPHRASE_MENU_EXPLORE")),
            MenuItem(BTC_ICONS.WALLET, t("SEEDPHRASE_MENU_RELATED_WALLETS"), "related_wallets_for_seed", is_submenu=True),
        ]

        menu_items.append(MenuItem(text=t("SEEDPHRASE_MENU_ADVANCED")))
        if can_sign_msg:
            menu_items.append(MenuItem(BTC_ICONS.SIGN, t("MAIN_MENU_SIGN_MESSAGE"), "sign_message"))        
        menu_items.append(MenuItem(BTC_ICONS.SHARED_WALLET, t("SEEDPHRASE_MENU_BIP85"), "derive_bip85"))

        return menu_items

    def post_init(self, t, state):
        # The ContextBar (shown automatically in SEED context) handles the
        # editable seed name and fingerprint display.  Here we only add the
        # delete button so the user can remove this seed from the device.
        self.add_title_delete_btn(make_delete_active_handler(
            self, t, confirm_delete_seed, "active_seed", "remove_seed"))
