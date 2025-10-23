from .menu import GenericMenu


def WalletMenu(parent, *args, **kwargs):
    on_navigate = getattr(parent, "on_navigate", None)
    state = getattr(parent, "specter_state", None)

    menu_items = []

    menu_items.append(("Explore", None))
    menu_items.append(("View Addresses", "view_addresses"))
    if (state and not state.active_wallet is None and state.active_wallet.isMultiSig):
        menu_items.append(("View Signers", "view_signers"))

    menu_items.append(("Manage", None))
    if (state and not state.active_wallet is None and not state.active_wallet.isMultiSig):
        menu_items.append(("Manage Derivation Path", "derivation_path"))
        menu_items.append(("Manage Seedphrase", "manage_seedphrase"))
        menu_items.append(("Enter/Set Passphrase", "set_passphrase"))
    elif (state and not state.active_wallet is None and state.active_wallet.isMultiSig):
        menu_items.append(("Manage Descriptor", "manage_wallet_descriptor"))
    menu_items.append(("Change Network (Mainnet/Testnet/...)", "change_network"))
    
    menu_items += [
        ("Rename Wallet", "rename_wallet"),
        ("Delete Wallet", "delete_wallet"),
        ("Connect/Export", None),
        ("Connect SW Wallet", "connect_sw_wallet"),
        ("Export Data", "export_wallet")
    ]

    title = "Manage Wallet" + ("" if state is None or state.active_wallet is None else f": {state.active_wallet.name}")

    return GenericMenu("manage_wallet", title, menu_items, parent, *args, **kwargs)
