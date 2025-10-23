from .menu import GenericMenu


def SecurityMenu(parent, *args, **kwargs):
    state = getattr(parent, "specter_state", None)

    menu_items = [
        ("Change PIN", "change_pin"),
        ("Run Self-Test", "self_test"),
        ("Set allowed PIN retries", "set_allowed_pin_retries"),
        ("Set exceeded PIN retries action", "set_exceeded_pin_action"),
        ("Set duress PIN", "set_duress_pin"),
        ("Set duress PIN action", "set_duress_pin_action"),
    ]

    return GenericMenu("manage_security", "Manage Security Features", menu_items, parent, *args, **kwargs)
