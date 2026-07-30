from ..basic import GenericMenu, BTC_ICONS, MenuItem, t

def make_add_seed_items(state, sizes=None):
    """Build the full 'Add Seed' menu block.

    Returns the Generate section header + 'Generate Seedphrase' row + Import
    section header + the conditional SmartCard / QR / Keyboard / SD / Flash
    import-source rows. Used by `AddSeedMenu.get_menu_items` and
    `MainMenu._items_no_seed`.

    ``sizes`` is an optional dict mapping import-source name to size multiplier
    (keys: ``smartcard``, ``qr``, ``keyboard``, ``sd``, ``flash``); missing keys
    default to 1.
    """
    sizes = sizes or {}

    highlighted = None
    if state.SmartCard_hasSeed():
        highlighted = "smartcard"
    elif state.SD_hasSeed():
        highlighted = "sd"
    elif state.Flash_hasSeed():
        highlighted = "flash"
    elif state.QR_enabled():
        highlighted = "qr"

    items = [
        MenuItem(text=t("ADD_SEED_GENERATE_SECTION")),
        MenuItem(BTC_ICONS.DICE, t("ADD_SEED_GENERATE_SEED"), "generate_seedphrase",
                 height_scaling=sizes.get("generate", 1),
                 modifier="Highlight" if highlighted == "generate" else None,
                 help_key="HELP_GENERATE_SEED",
                 is_submenu=True),
        MenuItem(text=t("ADD_SEED_IMPORT_SECTION")),
    ]
    if state.SmartCard_hasSeed():
        items.append(MenuItem(BTC_ICONS.SMARTCARD, t("HARDWARE_SMARTCARD"),
                              "import_from_smartcard", height_scaling=sizes.get("smartcard", 1),
                              modifier="Highlight" if highlighted == "smartcard" else None))
    if state.QR_enabled():
        items.append(MenuItem(BTC_ICONS.QR_CODE, t("HARDWARE_QR_CODE"),
                              "import_from_qr", height_scaling=sizes.get("qr", 1),
                              modifier="Highlight" if highlighted == "qr" else None))
    items.append(MenuItem(BTC_ICONS.KEYBOARD, t("COMMON_KEYBOARD"),
                          "import_from_keyboard", height_scaling=sizes.get("keyboard", 1),
                          modifier="Highlight" if highlighted == "keyboard" else None))
    if state.SD_hasSeed():
        items.append(MenuItem(BTC_ICONS.SD_CARD, t("HARDWARE_SD_CARD"),
                              "import_from_sd", height_scaling=sizes.get("sd", 1),
                              modifier="Highlight" if highlighted == "sd" else None))
    if state.Flash_hasSeed():
        items.append(MenuItem(BTC_ICONS.FILE, t("HARDWARE_INTERNAL_FLASH"),
                              "import_from_flash", height_scaling=sizes.get("flash", 1),
                              modifier="Highlight" if highlighted == "flash" else None))
    return items


class AddSeedMenu(GenericMenu):
    """Menu to create or import a MasterKey (seedphrase).

    menu_id: "add_seed"
    """

    TITLE_KEY = "MENU_ADD_SEED"

    def get_menu_items(self):
        return make_add_seed_items(self.device_state)
