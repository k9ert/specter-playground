from ..basic import GenericMenu
from ..basic.symbol_lib import BTC_ICONS
from ..basic.widgets import MenuItem
from ..stubs import Seed
import lvgl as lv

class ViewSignersScreen(GenericMenu):
    """Form to view the active seed's signers.

    menu_id: "view_signers"
    """

    TITLE_KEY = "WALLET_MENU_VIEW_SIGNERS"

    def get_menu_items(self, t, state):
        """Show list of signers for the active seed."""
        s4w = state.seeds_for_wallet(self.ui_state.active_wallet)
        loaded_fp4w = Seed.get_fingerprints(s4w) if s4w else []

        if self.ui_state.active_wallet.is_default_wallet():
            fp_list = loaded_fp4w
        else:
            fp_list = self.ui_state.active_wallet.required_fingerprints

        menu_items = []
        for fp in fp_list:
            signer_name = fp[2:]  # do not show "0x" hex prefix in fingerprint
            icon = BTC_ICONS.KEY_OUTLINE
            target = lambda e: None

            if s4w and fp in loaded_fp4w:
                matched_seed = s4w[loaded_fp4w.index(fp)]
                signer_name += " (" + matched_seed.label + ")"
                icon = BTC_ICONS.KEY

                def _make_seed_cb(seed):
                    def _cb(e):
                        if e.get_code() != lv.EVENT.CLICKED:
                            return
                        self.on_navigate("manage_seedphrase", target_seed=seed)
                    return _cb

                target = _make_seed_cb(matched_seed)

            menu_items.append(MenuItem(icon, signer_name, target=target))
        return menu_items

    def refresh(self):
        self.rebuild_body()
