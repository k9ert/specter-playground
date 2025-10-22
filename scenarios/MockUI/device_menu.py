from .menu import GenericMenu


def DeviceMenu(parent, *args, **kwargs):
    on_navigate = getattr(parent, "on_navigate", None)
    state = getattr(parent, "specter_state", None)

    menu_items = [
        ("Manage Device", None),
        ("Manage Backup(s)", "manage_backups"),
        ("Manage Firmware", "manage_firmware"),
        ("Manage Security Features", "manage_security"),
        ("Change Network (Mainnet/Testnet/...)", "change_network"),
        ("Enable/Disable Interfaces", "interfaces"),
        ("Manage Sounds", "sounds")]

    if ((state and state.hasSmartCard and state.enabledSmartCard and state.detectedSmartCard) or
        (state and state.hasSD and state.enabledSD and state.detectedSD)):
        menu_items.append(("Manage Storage", None))
        if (state and state.hasSmartCard and state.enabledSmartCard and state.detectedSmartCard):
            menu_items.append(("Manage SmartCard", "smartcard"))
        if (state and state.hasSD and state.enabledSD and state.detectedSD):
            menu_items.append(("Manage SD Card", "sdcard"))

    menu_items += [
        ("Dangerzone", None),
        ("Wipe Device", "wipe_device")
    ]


    return GenericMenu("manage_device", "Manage Device/Storage", menu_items, parent, *args, **kwargs)
