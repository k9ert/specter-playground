import lvgl as lv
from ..basic import GenericMenu, MenuItem, BTC_ICONS, t
from ..seed_screens.add_seed_menu import make_add_seed_items


class MainMenu(GenericMenu):
    TITLE_KEY = "MAIN_MENU_TITLE"

    def get_menu_items(self):
        state = self.device_state
        has_seed = state and len(state.loaded_seeds) > 0

        if not has_seed:
            return self._items_no_seed(t, state)
        else:
            return self._items_with_seed(t, state)
        
    def _items_no_seed(self, t, state):
        """State: No Seed loaded yet — focus on key loading."""
        slots_available = 7
        slots_used = 2 + int(state.SmartCard_hasSeed()) + int(state.SD_hasSeed()) + int(state.Flash_hasSeed() + int(state.QR_enabled()))
        slots_remaining = slots_available - slots_used

        Seed_detected = (state.SmartCard_hasSeed() or state.SD_hasSeed() or state.Flash_hasSeed())

        # Size each row based on remaining slots / detected seeds.
        scaled = 1.0 + slots_remaining / slots_used if not Seed_detected else 1
        sizes = {
            "generate": scaled,
            "smartcard": 1.0 + slots_remaining,
            "qr": scaled,
            "keyboard": scaled,
            "sd": 1.0 + slots_remaining if not state.SmartCard_hasSeed() else 1,
            "flash": 1.0 + slots_remaining if not (state.SmartCard_hasSeed() or state.SD_hasSeed()) else 1,
        }
        return make_add_seed_items(state, sizes=sizes)

    def _items_with_seed(self, t, state):
        """State: Seed loaded — normal operating mode."""
        menu_items = []

        has_controlled_input = (state.QR_enabled() or state.SD_detected())
        
        has_seed_that_is_not_backed_up = not all (seed.is_backed_up for seed in state.loaded_seeds)
        has_wallet_that_was_never_synched = not all (wallet.has_been_synched for wallet in state.registered_wallets) or \
                                            not all (seed.has_been_synched for seed in state.loaded_seeds)

        highlighted = None
        if has_seed_that_is_not_backed_up:
            highlighted = "backup"
        elif has_wallet_that_was_never_synched:
            highlighted = "connect"
        elif has_controlled_input:
            if state.SD_detected():
                highlighted = "load_sd"
            elif state.QR_enabled():
                highlighted = "scan_qr"

        # ── Actions section ─────────────────────────────────────────────────
        if has_seed_that_is_not_backed_up:
            menu_items += [
                MenuItem(text=t("MAIN_MENU_BACKUP_SECTION")),
                MenuItem(BTC_ICONS.MNEMONIC, t("MAIN_MENU_BACKUP_SEED"), "backup_seed", height_scaling=1.3,
                         modifier="Highlight" if highlighted == "backup" else None,
                         help_key="HELP_BACKUP_SEED"),
            ]

        if has_controlled_input:
            menu_items.append(MenuItem(text=t("MAIN_MENU_PROCESS_INPUT")))
            if state.QR_enabled():
                menu_items.append(MenuItem(BTC_ICONS.QR_CODE, t("MAIN_MENU_SCAN_QR"), "scan_qr", height_scaling=1.3,
                                           modifier="Highlight" if highlighted == "scan_qr" else None,
                                           help_key="HELP_SCAN_QR"))
            if state.SD_detected():
                menu_items.append(MenuItem(BTC_ICONS.SD_CARD, t("MAIN_MENU_LOAD_FROM_SD"), "load_sd",
                                           modifier="Highlight" if highlighted == "load_sd" else None))

        # ── Explore section ─────────────────────────────────────────────────
        menu_items += [
            MenuItem(text=t("WALLET_MENU_EXPLORE")),
            MenuItem(BTC_ICONS.MENU, t("WALLET_MENU_VIEW_ADDRESSES"), "view_addresses"),
        ]

        # ── Connect Companion App (only if wallet not yet exported) ─────────
        if has_wallet_that_was_never_synched:
            menu_items += [
                MenuItem(text=t("MAIN_MENU_CONNECT_SECTION")),
                MenuItem(BTC_ICONS.LINK, t("MAIN_MENU_CONNECT_COMPANION"), "connect_sw_wallet", height_scaling=1.5,
                         modifier="Highlight" if highlighted == "connect" else None),
            ]

        return menu_items
    
    def refresh(self):
        super().refresh()
        self.rebuild_body()
