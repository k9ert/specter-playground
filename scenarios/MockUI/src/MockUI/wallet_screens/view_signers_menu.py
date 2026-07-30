from ..basic import GenericMenu,  BTC_ICONS, MenuItem, t
from ..stubs import Seed

class ViewSignersMenu(GenericMenu):
    """Form to view the active seed's signers.

    menu_id: "view_signers"
    """

    TITLE_KEY = "WALLET_MENU_VIEW_SIGNERS"

    def get_menu_items(self):
        state = self.device_state
        """Show list of signers for the active seed."""
        s4w = state.seeds_for_wallet(self.ui_state.active_wallet)
        loaded_fp4w = []
        if s4w:
            loaded_fp4w = Seed.get_fingerprints(s4w)

        if self.ui_state.active_wallet.is_default_wallet():
            fp_list = loaded_fp4w
        else:
            fp_list = self.ui_state.active_wallet.required_fingerprints

        menu_items = []
        for fp in fp_list:
            signer_name = fp[2:]  # do not show "0x" hex prefix in fingerprint
            icon = BTC_ICONS.KEY_OUTLINE
            target = lambda: None

            if s4w and fp in loaded_fp4w:
                matched_seed = s4w[loaded_fp4w.index(fp)]
                signer_name += " (" + matched_seed.label + ")"
                icon = BTC_ICONS.KEY

                target = lambda seed=matched_seed: self.on_navigate(
                    "manage_seedphrase", target_seed=seed
                )

            menu_items.append(MenuItem(icon, signer_name, target=target))
        return menu_items

    def refresh(self):
        self.rebuild_body()
