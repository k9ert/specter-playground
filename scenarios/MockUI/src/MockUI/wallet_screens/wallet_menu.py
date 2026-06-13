from ..basic import (
    GenericMenu, BTC_ICONS, MenuItem,
    confirm_delete_wallet, make_delete_active_handler
)


class WalletMenu(GenericMenu):
    """Menu for managing an active wallet with editable name."""

    TITLE_KEY = "MENU_MANAGE_WALLET"

    def get_menu_items(self, t, state):
        menu_items = []

        menu_items += [
            MenuItem(text=t("WALLET_MENU_EXPLORE")),
            MenuItem(BTC_ICONS.MENU, t("WALLET_MENU_VIEW_ADDRESSES"), "view_addresses"),
            MenuItem(BTC_ICONS.ADDRESS_BOOK, t("WALLET_MENU_VIEW_SIGNERS"), "view_signers", is_submenu=True),
        ]

        menu_items += [
            MenuItem(text=t("WALLET_MENU_MANAGE")),
            MenuItem(BTC_ICONS.CONSOLE, t("WALLET_MENU_MANAGE_DESCRIPTOR"), "manage_wallet_descriptor"),
            MenuItem(BTC_ICONS.BITCOIN, t("WALLET_MENU_CHANGE_NETWORK"), "change_network"),
        ]

        menu_items += [
            MenuItem(text=t("WALLET_MENU_CONNECT_EXPORT")),
            MenuItem(BTC_ICONS.LINK, t("MENU_CONNECT_SW_WALLET"), "connect_sw_wallet"),
            MenuItem(BTC_ICONS.EXPORT, t("WALLET_MENU_EXPORT_DATA"), "export_wallet"),
        ]

        return menu_items

    def post_init(self, t, state):
        # The ContextBar (shown automatically in WALLET context) handles the
        # editable wallet name and type icon.  Here we only add the delete
        # button (custom wallets) and the account row.

        is_default = self.ui_state.active_wallet.is_default_wallet()

        if not is_default:
            # Custom wallet: trash button in title bar, right-aligned
            self.add_title_delete_btn(make_delete_active_handler(
                self, t, confirm_delete_wallet, "active_wallet", "remove_wallet"))
