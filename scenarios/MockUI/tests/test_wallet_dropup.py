from MockUI.basic.components.wallet_dropup import WalletDropUp
from MockUI.basic.specter_gui import SpecterGui
from MockUI.basic.ui_state import Context
from MockUI.stubs.seed import Seed
from MockUI.stubs.wallet import Wallet, wallet_sort_key


class _WalletDropUp(WalletDropUp):
    def __init__(self, device_state):
        super().__init__()
        self._test_device_state = device_state

    @property
    def device_state(self):
        return self._test_device_state

    @property
    def t(self):
        return lambda key: {
            "ADD_SWITCH_WALLET_MENU_OTHER_WALLETS": "Other wallets",
            "COMMON_MULTISIG": "MultiSig",
        }.get(key, key)


class _Descriptor:
    def __init__(self, value):
        self._value = value

    def __str__(self):
        return self._value


def test_wallet_tree_key_uses_descriptor_across_rename_and_reconstruction():
    dropup = WalletDropUp()
    wallet = Wallet("Same label", descriptor=_Descriptor("wpkh([first]xpub...)"))
    other_wallet = Wallet("Same label", descriptor=_Descriptor("wpkh([other]xpub...)"))
    restored_wallet = Wallet("Restored", descriptor=_Descriptor("wpkh([first]xpub...)"))

    key = dropup._get_item_key(wallet)
    assert key == "wpkh([first]xpub...)"
    assert key != dropup._get_item_key(other_wallet)

    wallet.label = "Renamed"
    assert key == dropup._get_item_key(wallet)
    assert key == dropup._get_item_key(restored_wallet)


def test_wallet_sort_key_orders_by_signers_threshold_policy_and_account():
    default = Wallet("Default", descriptor="default")
    standard = Wallet("Standard", descriptor="wpkh(standard)#00000002",
                      required_fingerprints=["a"])
    custom = Wallet("Custom", descriptor="wsh(custom)#00000003",
                    required_fingerprints=["a"], is_custom=True)
    multisig_standard = Wallet(
        "Multisig", descriptor="wsh(sortedmulti(2,a,b,c))#00000004",
        isMultiSig=True, required_fingerprints=["c", "a", "b"], threshold=2)
    multisig_custom = Wallet(
        "Custom multisig", descriptor="wsh(and_v(...))#00000005",
        isMultiSig=True, required_fingerprints=["a", "b", "c"], threshold=2,
        is_custom=True)
    second_account = Wallet(
        "Multisig", descriptor="wsh(sortedmulti(2,a,b,c))#00000006",
        isMultiSig=True, required_fingerprints=["a", "b", "c"], threshold=2,
        account=1)

    ordered = sorted(
        [multisig_custom, custom, second_account, standard,
         default, multisig_standard],
        key=wallet_sort_key,
    )

    assert ordered == [
        default,
        standard,
        custom,
        multisig_standard,
        second_account,
        multisig_custom,
    ]
    assert multisig_standard.get_signers() == ("a", "b", "c")


def test_device_state_returns_the_shared_default_wallet(specter_state):
    default = specter_state.get_default_wallet()

    assert specter_state.add_seed(Seed("First", fingerprint="11111111")) is default
    reused_default = specter_state.add_seed(Seed("Second", fingerprint="22222222"))

    assert specter_state.get_default_wallet() is default
    assert reused_default is default


def test_delete_wallet_clears_active_selection_and_expansion_state(
        specter_state, ui_state):
    wallet = Wallet("Wallet", descriptor=_Descriptor("wpkh([wallet]xpub...)"))
    specter_state.register_wallet(wallet)
    key = WalletDropUp()._get_item_key(wallet)

    gui = SpecterGui.__new__(SpecterGui)
    gui.device_state = specter_state
    gui.ui_state = ui_state
    gui.ui_state.active_wallet = wallet
    gui.ui_state.is_item_expanded[(Context.WALLET, key)] = True
    gui.app_screen = None
    gui.navigation_bar = None

    SpecterGui.delete_wallet(gui, wallet)

    assert wallet not in gui.device_state.registered_wallets
    assert gui.ui_state.active_wallet is None
    assert (Context.WALLET, key) not in gui.ui_state.is_item_expanded


def test_wallet_tree_parent_uses_the_longest_derivation_prefix(specter_state):
    signers = ["c01da001", "b07b0001"]
    account = Wallet("Account", derivation_path="m/84'/0'/0'",
                     required_fingerprints=signers)
    change = Wallet("Change", derivation_path="m/84'/0'/0'/1'",
                    required_fingerprints=list(reversed(signers)))
    nested = Wallet("Nested", derivation_path="m/84'/0'/0'/1'/2'",
                    required_fingerprints=signers)
    unrelated = Wallet("Unrelated", derivation_path="m/49'/0'/0'",
                       required_fingerprints=signers)
    extra_signer = Wallet("Extra signer", derivation_path="m/84'/0'/0'/1'/3'",
                          required_fingerprints=signers + ["deadbeef"])

    for wallet in (account, change, nested, unrelated, extra_signer):
        specter_state.register_wallet(wallet)
    dropup = _WalletDropUp(specter_state)

    assert dropup._get_item_parent(account) is None
    assert dropup._get_item_parent(change) is account
    assert dropup._get_item_parent(nested) is change
    assert dropup._get_item_parent(unrelated) is None
    assert dropup._get_item_parent(extra_signer) is None