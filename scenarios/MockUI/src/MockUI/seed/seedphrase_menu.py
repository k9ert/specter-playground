from ..basic import ORANGE_HEX, RED_HEX, WHITE_HEX, GenericMenu, TITLE_ROW_HEIGHT, SMALL_PAD
from ..basic.symbol_lib import BTC_ICONS
from ..basic.widgets.action_modal import ActionModal
from ..basic.confirm_modals import confirm_delete_seed
from ..basic.widgets import Btn, MenuItem
import lvgl as lv

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

        menu_items.append(MenuItem(BTC_ICONS.VISIBLE, t("SEEDPHRASE_MENU_SHOW"), "show_seedphrase", color=ORANGE_HEX))

        pp_label = t("MENU_CHANGE_CLEAR_PASSPHRASE") if self.ui_state.active_seed.passphrase else t("MENU_SET_PASSPHRASE")
        menu_items.append(MenuItem(BTC_ICONS.PASSWORD, pp_label, "set_passphrase", is_submenu=True))

        menu_items.append(MenuItem(text=t("SEEDPHRASE_MENU_BACKUP")))
        menu_items.append(MenuItem(lv.SYMBOL.DOWNLOAD, t("SEEDPHRASE_MENU_STORE_TO") + "...", "store_seedphrase", is_submenu=True))

        # Explore section
        menu_items.append(MenuItem(text=t("SEEDPHRASE_MENU_EXPLORE")))
        menu_items.append(MenuItem(BTC_ICONS.WALLET, t("SEEDPHRASE_MENU_RELATED_WALLETS"), "related_wallets_for_seed", is_submenu=True))

        menu_items.append(MenuItem(text=t("SEEDPHRASE_MENU_ADVANCED")))
        if can_sign_msg:
            menu_items.append(MenuItem(BTC_ICONS.SIGN, t("MAIN_MENU_SIGN_MESSAGE"), "sign_message"))        
        menu_items.append(MenuItem(BTC_ICONS.SHARED_WALLET, t("SEEDPHRASE_MENU_BIP85"), "derive_bip85"))

        return menu_items

    def post_init(self, t, state):
        # The ContextBar (shown automatically in SEED context) handles the
        # editable seed name and fingerprint display.  Here we only add the
        # delete button so the user can remove this seed from the device.
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
            seed = self.ui_state.active_seed

            def _do_delete():
                self.device_state.remove_seed(seed)
                self.ui_state.active_seed = None
                self.gui.ui_state.clear_history()
                self.gui.ui_state.current_menu_id = "main"
                self.gui.refresh_ui()
                self.on_navigate(None)

            confirm_delete_seed(t, seed.label, _do_delete)

        self.delete_btn.add_event_cb(_on_delete, lv.EVENT.CLICKED, None)
