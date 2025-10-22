from .menu import GenericMenu


def SeedPhraseMenu(parent, *args, **kwargs):
    on_navigate = getattr(parent, "on_navigate", None)
    state = getattr(parent, "specter_state", None)

    menu_items = []

    # Show the seedphrase (requires confirmation in a real device)
    menu_items.append(("Show Seedphrase", "show_seedphrase"))

    # Store Seedphrase group (label)
    menu_items.append(("Store Seedphrase", None))
    if state and state.hasSmartCard and state.enabledSmartCard and state.detectedSmartCard:
        menu_items.append(("to SmartCard", "store_to_smartcard"))
    if state and state.hasSD and state.enabledSD and state.detectedSD:
        menu_items.append(("to SD Card", "store_to_sd"))
    menu_items.append(("to internal Flash", "store_to_flash"))

    # Clear Seedphrase group (label)
    menu_items.append(("Clear Seedphrase", None))
    if state and state.hasSmartCard and state.enabledSmartCard and state.detectedSmartCard:
        menu_items.append(("from SmartCard", "clear_from_smartcard"))
    if state and state.hasSD and state.enabledSD and state.detectedSD:
        menu_items.append(("from SD Card", "clear_from_sd"))
    menu_items.append(("from internal Flash", "clear_from_flash"))
    menu_items.append(("all attached storage", "clear_all_storage"))

    # Derive new via BIP-85
    menu_items.append(("Avanced Features", None))
    menu_items.append(("Derive new via BIP-85", "derive_bip85"))

    return GenericMenu("manage_seedphrase", "Manage Seedphrase", menu_items, parent, *args, **kwargs)
