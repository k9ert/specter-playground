from .menu import GenericMenu


def DeviceMenu(on_navigate, state=None, *args, **kwargs):
    menu_items = [
        ("Manage Device", None),
        ("Manage Backup(s)", "manage_backups"),
        ("Manage Firmware", "manage_firmware"),
        ("Manage Security Features", "manage_security"),
        ("Change Network", "change_network"),
        ("Enable/Disable Interfaces", "interfaces"),
        ("Manage Sounds", "sounds")]

    if ((state and state.enabledSmartCard and state.hasSmartCard) or
        (state and state.enabledSD and state.hasSD)):
        menu_items.append(("Manage Storage", None))
        if (state and state.enabledSmartCard and state.hasSmartCard):
            menu_items.append(("Manage SmartCard", "smartcard"))
        if (state and state.enabledSD and state.hasSD):
            menu_items.append(("Manage SD Card", "sdcard")) 
    
    menu_items += [
        ("Dangerzone", None),
        ("Wipe Device", "wipe_device"),
        ("Navigate",None),
        ("Back", "back"),
    ]

    return GenericMenu("manage_device", "Manage Device/Storage", menu_items, 80, on_navigate, state, *args, **kwargs)
