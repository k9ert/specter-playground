from .menu import GenericMenu


def DeviceMenu(parent, *args, **kwargs):
    on_navigate = getattr(parent, "on_navigate", None)
    state = getattr(parent, "specter_state", None)

    menu_items = [("Manage Device", None)]

    if state and state.hasSD and state.enabledSD and state.detectedSD:
        menu_items.append(("Manage Backup(s)", "manage_backups"))

    menu_items += [
        ("Manage Firmware", "manage_firmware"),
        ("Manage Security Features", "manage_security"),
        ("Enable/Disable Interfaces", "interfaces"),
        ("Manage Sounds", "sounds")]

    menu_items += [
        ("Dangerzone", None),
        ("Wipe Device", "wipe_device")
    ]


    return GenericMenu("manage_device", "Manage Device/Storage", menu_items, parent, *args, **kwargs)
