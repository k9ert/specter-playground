from ..basic import RED_HEX, WHITE_HEX, GenericMenu, TITLE_ROW_HEIGHT, SMALL_PAD
from ..basic.symbol_lib import BTC_ICONS
from ..basic.widgets.action_modal import ActionModal
from ..basic.confirm_modals import confirm_delete_wallet
from ..basic.widgets import Btn, MenuItem
from ..basic.ui_consts import BTN_HEIGHT, BTN_WIDTH
import lvgl as lv


class WalletMenu(GenericMenu):
    """Menu for managing an active wallet with editable name."""

    TITLE_KEY = "MENU_MANAGE_WALLET"

    def get_menu_items(self, t, state):
        menu_items = []

        menu_items.append(MenuItem(text=t("WALLET_MENU_EXPLORE")))
        menu_items.append(MenuItem(BTC_ICONS.MENU, t("WALLET_MENU_VIEW_ADDRESSES"), "view_addresses"))
        if (self.ui_state.active_wallet and self.ui_state.active_wallet.isMultiSig):
            menu_items.append(MenuItem(BTC_ICONS.ADDRESS_BOOK, t("WALLET_MENU_VIEW_SIGNERS"), "view_signers", is_submenu=True))

        menu_items.append(MenuItem(text=t("WALLET_MENU_MANAGE")))
        menu_items.append(MenuItem(BTC_ICONS.CONSOLE, t("WALLET_MENU_MANAGE_DESCRIPTOR"), "manage_wallet_descriptor"))
        menu_items.append(MenuItem(BTC_ICONS.BITCOIN, t("WALLET_MENU_CHANGE_NETWORK"), "change_network"))

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
            textarea_height = TITLE_ROW_HEIGHT - 10
            self.delete_btn = Btn(
                self.title_bar,
                icon=BTC_ICONS.TRASH,
                color=RED_HEX,
                size=(textarea_height, textarea_height),
            )
            self.delete_btn.align(lv.ALIGN.RIGHT_MID, -SMALL_PAD, 0)

            def _on_delete(e):
                if e.get_code() != lv.EVENT.CLICKED:
                    return
                wallet = self.ui_state.active_wallet

                def _do_delete():
                    self.device_state.remove_wallet(wallet)
                    self.ui_state.active_wallet = None
                    self.gui.ui_state.clear_history()
                    self.gui.ui_state.current_menu_id = "main"
                    self.gui.refresh_ui()
                    self.on_navigate(None)

                confirm_delete_wallet(t, wallet.label, _do_delete)

            self.delete_btn.add_event_cb(_on_delete, lv.EVENT.CLICKED, None)

        # Account row (shown for both default and custom wallets)
        self._add_account_row(t, state)

    def _add_account_row(self, t, state):
        """Add read-only Account label row. Account is fixed at wallet creation time."""
        wallet = self.ui_state.active_wallet
        if wallet is None:
            return

        row = lv.obj(self.body)
        row.set_width(lv.pct(BTN_WIDTH))
        row.set_height(BTN_HEIGHT)
        row.set_layout(lv.LAYOUT.FLEX)
        row.set_flex_flow(lv.FLEX_FLOW.ROW)
        row.set_flex_align(lv.FLEX_ALIGN.SPACE_BETWEEN, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        row.set_style_pad_hor(16, 0)
        row.set_style_radius(8, 0)
        row.set_style_border_width(0, 0)

        desc_lbl = lv.label(row)
        desc_lbl.set_text(t("WALLET_MENU_SELECT_ACCOUNT"))
        desc_lbl.set_style_text_font(lv.font_montserrat_22, 0)

        val_lbl = lv.label(row)
        val_lbl.set_style_text_font(lv.font_montserrat_22, 0)
        val_lbl.set_text(str(wallet.account))

        row.move_to_index(1)
