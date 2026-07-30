from ..basic import GenericMenu, MenuItem, t


class ConnectWalletsMenu(GenericMenu):
    """Menu to connect or export to software wallets.

    Selecting any companion app marks the active wallet as exported,
    since the descriptor is being shared with that app.
    """

    TITLE_KEY = "MENU_CONNECT_SW_WALLET"

    def get_menu_items(self):
        return [
            MenuItem(text=t("CONNECT_WALLETS_SPARROW"),    target=self._mark_synched_and_navigate("connect_sparrow")),
            MenuItem(text=t("CONNECT_WALLETS_NUNCHUCK"),   target=self._mark_synched_and_navigate("connect_nunchuck")),
            MenuItem(text=t("CONNECT_WALLETS_BLUEWALLET"), target=self._mark_synched_and_navigate("connect_bluewallet")),
            MenuItem(text=t("CONNECT_WALLETS_OTHER"),      target=self._mark_synched_and_navigate("connect_other")),
        ]

    def post_init(self):
        super().post_init()

        # Ensure an active_wallet is selected.
        if self.ui_state.active_wallet is None or self.ui_state.active_wallet.has_been_synched:
            #TODO: IMPLEMENT PROPER WALLET SELECTION MODAL [generic]
            #HERE JUST DUMMY TO CYCLE THROUGH ALL UNSYNCHED WALLETS AND PICK THE FIRST ONE
            for i in reversed(range(len(self.device_state.registered_wallets))):
                if not self.device_state.registered_wallets[i].has_been_synched or i == 0:
                    self.ui_state.active_wallet = self.device_state.registered_wallets[i]
                    break

    def _mark_synched_and_navigate(self, target):
        """Return a callback that sets has_been_synched then navigates."""
        def _cb():
            #TODO: IMPLEMENT ACTUAL WALLET SYNCHING LOGIC [generic]
            self.ui_state.active_wallet.has_been_synched = True
            if self.ui_state.active_wallet.is_default_wallet():
                for seed in self.device_state.loaded_seeds:
                    seed.has_been_synched = True
            self.on_navigate(None)
        return _cb