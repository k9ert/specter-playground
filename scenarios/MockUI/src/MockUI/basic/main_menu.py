import lvgl as lv
from .menu import GenericMenu
from .symbol_lib import BTC_ICONS
from .ui_consts import GREEN_HEX, RED_HEX, WHITE_HEX, ORANGE_HEX
from .widgets import MenuItem


class MainMenu(GenericMenu):
    TITLE_KEY = "MAIN_MENU_TITLE"

    def get_menu_items(self, t, state):
        has_seed = state and len(state.loaded_seeds) > 0

        if not has_seed:
            return self._items_no_seed(t, state)
        else:
            return self._items_with_seed(t, state)
        
    def _items_no_seed(self, t, state):
        """State: No Seed loaded yet — focus on key loading."""
        menu_items = []
        slots_available = 7
        slots_used = 2 + int(state.SmartCard_hasSeed()) + int(state.SD_hasSeed()) + int(state.Flash_hasSeed() + int(state.QR_enabled()))
        slots_remaining = slots_available - slots_used

        Seed_detected = (state.SmartCard_hasSeed() or state.SD_hasSeed() or state.Flash_hasSeed())

        menu_items.append(MenuItem(text=t("ADD_SEED_GENERATE_SECTION")))

        # Generate New Key
        gen_size = 1.0+slots_remaining/slots_used if not Seed_detected else 1
        menu_items.append(MenuItem(BTC_ICONS.DICE, t("ADD_SEED_GENERATE_SEED"), "generate_seedphrase", size=gen_size, is_submenu=True))

        menu_items.append(MenuItem(text=t("ADD_SEED_IMPORT_SECTION")))

        # SmartCard (highlighted exclusively when detected with key)
        if state.SmartCard_hasSeed():
            sc_size = 1.0 + slots_remaining
            menu_items.append(MenuItem(BTC_ICONS.SMARTCARD, t("HARDWARE_SMARTCARD"), "import_from_smartcard", size=sc_size))

        # Scan QR
        qr_size = 1.0+slots_remaining/slots_used if not Seed_detected else 1
        if state.QR_enabled():
            menu_items.append(MenuItem(BTC_ICONS.QR_CODE, t("HARDWARE_QR_CODE"), "import_from_qr", size=qr_size))

        # Keyboard
        kb_size = 1.0+slots_remaining/slots_used if not Seed_detected else 1
        menu_items.append(MenuItem(BTC_ICONS.KEYBOARD, t("COMMON_KEYBOARD"), "import_from_keyboard", size=kb_size))

        # SD Card (only if key data detected)
        if state.SD_hasSeed():
            sd_size = 1.0 + slots_remaining if not state.SmartCard_hasSeed() else 1
            menu_items.append(MenuItem(BTC_ICONS.SD_CARD, t("HARDWARE_SD_CARD"), "import_from_sd", size=sd_size))

        # Flash (only if key data in flash)
        if state.Flash_hasSeed():
            flash_size = 1.0 + slots_remaining if not (state.SmartCard_hasSeed() or state.SD_hasSeed()) else 1
            menu_items.append(MenuItem(BTC_ICONS.FILE, t("HARDWARE_INTERNAL_FLASH"), "import_from_flash", size=flash_size))

        return menu_items

    def _items_with_seed(self, t, state):
        """State: Seed loaded — normal operating mode."""
        menu_items = []

        has_controlled_input = (state.QR_enabled() or state.SD_detected())
        
        has_seed_that_is_not_backed_up = not all (seed.is_backed_up for seed in state.loaded_seeds)
        has_wallet_that_was_never_synched = not all (wallet.has_been_synched for wallet in state.registered_wallets) or \
                                            not all (seed.has_been_synched for seed in state.loaded_seeds)

        # ── Actions section ─────────────────────────────────────────────────
        if has_seed_that_is_not_backed_up:
            menu_items += [
                MenuItem(text=t("MAIN_MENU_BACKUP_SECTION")),
                MenuItem(BTC_ICONS.MNEMONIC, t("MAIN_MENU_BACKUP_SEED"), "backup_seed", size=1.5, color=ORANGE_HEX, help_key="HELP_BACKUP_SEED"),
            ]


        if has_controlled_input:
            menu_items.append(MenuItem(text=t("MAIN_MENU_PROCESS_INPUT")))
            if state.QR_enabled():
                menu_items.append(MenuItem(BTC_ICONS.QR_CODE, t("MAIN_MENU_SCAN_QR"), "scan_qr", size=1.5, help_key="HELP_SCAN_QR"))
            if state.SD_detected():
                menu_items.append(MenuItem(BTC_ICONS.SD_CARD, t("MAIN_MENU_LOAD_FROM_SD"), "load_sd"))

        # ── Explore section ─────────────────────────────────────────────────
        menu_items += [
            MenuItem(text=t("WALLET_MENU_EXPLORE")),
            MenuItem(BTC_ICONS.MENU, t("WALLET_MENU_VIEW_ADDRESSES"), "view_addresses"),
        ]

        # ── Connect Companion App (only if wallet not yet exported) ─────────
        if has_wallet_that_was_never_synched:
            menu_items += [
                MenuItem(text=t("MAIN_MENU_CONNECT_SECTION")),
                MenuItem(BTC_ICONS.LINK, t("MAIN_MENU_CONNECT_COMPANION"), "connect_sw_wallet", size=1.5),
            ]

        return menu_items
    
    def refresh(self):
        super().refresh()
        self.rebuild_body()
