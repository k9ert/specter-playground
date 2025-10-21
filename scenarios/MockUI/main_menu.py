from .menu import GenericMenu


def MainMenu(parent, *args, **kwargs):
    # read state and navigation callback from the parent controller
    on_navigate = getattr(parent, "on_navigate", None)
    state = getattr(parent, "specter_state", None)

    menu_items = []

    #add "process inputs" label if any relevant input is available
    #relevant input possibilities are QR Scanner, SD Card, or (to sign messages) a registered wallet
    if (state and ((state.hasQR and state.enabledQR) or (state.hasSD and state.enabledSD) or len(state.registered_wallets) > 0)):
        menu_items.append(("Process input", None))
        if (state.hasQR and state.enabledQR):
            menu_items.append(("Scan QR", "scan_qr"))
        if (state.hasSD and state.enabledSD):
            menu_items.append(("Load File from SD", "load_sd"))
        if (state and len(state.registered_wallets) > 0):
            menu_items.append(("Sign Message", "sign_message"))

    menu_items.append(("Manage Specter", None))
    if (state and not state.active_wallet is None):
        menu_items.append(("Manage Wallet", "manage_wallet"))

    menu_items.append(("Manage Device/Storage", "manage_device"))
    menu_items.append(("Change/Add Wallet", "add_wallet"))  

    menu_items.append(("Quick links", None))
    menu_items.append(("Lock Device", "lock_device"))
    # power option depends on battery presence
    if (state and state.has_battery):
        menu_items.append(("Power Off", "power_down_device"))
    else:
        menu_items.append(("Reboot", "reboot_device"))
    
    return GenericMenu("main", "What do you want to do?", menu_items, 100, parent, *args, **kwargs)