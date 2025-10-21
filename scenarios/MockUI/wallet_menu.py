from .menu import GenericMenu


def WalletMenu(on_navigate, state=None, *args, **kwargs):

    menu_items = []

    menu_items.append(("Explore", None))
    menu_items.append(("View Addresses", "view_addresses"))
    if (state and not state.active_wallet is None and state.active_wallet.isMultiSig):
        menu_items.append(("View Signer", "view_signers"))

    menu_items.append(("Manage", None))
    if (state and not state.active_wallet is None and not state.active_wallet.isMultiSig):
        menu_items.append(("Manage Derivation Path", "derivation_path"))
        menu_items.append(("Manage Seedphrase", "seedphrase"))
        menu_items.append(("Enter/Set Passphrase", "passphrase"))
    elif (state and not state.active_wallet is None and state.active_wallet.isMultiSig):
        menu_items.append(("Manage Descriptor", "wallet_descriptor"))
    
    menu_items += [
        ("Rename Wallet", "rename_wallet"),
        ("Delete Wallet", "delete_wallet"),
        ("Connect/Export", None),
        ("Connect SW Wallet", "connect_sw_wallet"),
        ("Navigate",None),
        ("Back", "back")
    ]

    title = "Manage Wallet" + ("" if state is None or state.active_wallet is None else f": {state.active_wallet.name}")

    return GenericMenu("manage_wallet", title, menu_items, 80, on_navigate, state, *args, **kwargs)
