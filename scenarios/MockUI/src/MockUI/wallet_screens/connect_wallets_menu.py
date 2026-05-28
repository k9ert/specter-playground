from ..basic import GenericMenu
from ..basic.widgets import MenuItem
import lvgl as lv

class ConnectWalletsMenu(GenericMenu):
    """Menu to connect or export to software wallets.

    Selecting any companion app marks the active wallet as exported,
    since the descriptor is being shared with that app.
    """

    TITLE_KEY = "MENU_CONNECT_SW_WALLET"

    def get_menu_items(self, t, state):
        return [
            MenuItem(text=t("CONNECT_WALLETS_SPARROW"),    target=self._mark_exported_and_navigate("connect_sparrow")),
            MenuItem(text=t("CONNECT_WALLETS_NUNCHUCK"),   target=self._mark_exported_and_navigate("connect_nunchuck")),
            MenuItem(text=t("CONNECT_WALLETS_BLUEWALLET"), target=self._mark_exported_and_navigate("connect_bluewallet")),
            MenuItem(text=t("CONNECT_WALLETS_OTHER"),      target=self._mark_exported_and_navigate("connect_other")),
        ]

    def _mark_exported_and_navigate(self, target):
        """Return a callback that sets has_been_exported then navigates."""
        def _cb(e):
            if e.get_code() != lv.EVENT.CLICKED:
                return
            self.ui_state.active_wallet.has_been_exported = True
            self.on_navigate(None)
        return _cb