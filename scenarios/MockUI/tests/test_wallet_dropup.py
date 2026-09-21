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


def test_wallet_groups_repeat_default_per_seed_without_copying_it(specter_state):
    first_seed = Seed("First", fingerprint="11111111")
    second_seed = Seed("Second", fingerprint="22222222")
    default = specter_state.add_seed(first_seed)
    specter_state.add_seed(second_seed)
    dropup = _WalletDropUp(specter_state)

    groups = dropup._get_raw_DropUpGroups()

    assert [group.heading for group in groups] == ["First", "Second"]
    assert [group.items[0] for group in groups] == [default, default]


def test_wallet_groups_label_a_lone_seed(specter_state):
    seed = Seed("Only seed", fingerprint="11111111")
    default = specter_state.add_seed(seed)
    groups = _WalletDropUp(specter_state)._get_raw_DropUpGroups()

    assert len(groups) == 1
    assert groups[0].heading == "Only seed"
    assert groups[0].items[0] is default


def test_wallet_groups_sort_standard_before_custom_within_a_seed(specter_state):
    seed = Seed("Seed", fingerprint="11111111")
    default = specter_state.add_seed(seed)
    custom = Wallet("Custom", descriptor="custom", is_custom=True,
                    required_fingerprints=[seed.get_fingerprint()])
    standard = Wallet("Standard", descriptor="standard",
                      required_fingerprints=[seed.get_fingerprint()])
    specter_state.register_wallet(custom)
    specter_state.register_wallet(standard)

    groups = _WalletDropUp(specter_state)._get_raw_DropUpGroups()

    assert groups[0].items == [
        default,
        standard,
        custom,
    ]


def test_wallet_groups_multisig_by_shared_signers(
        specter_state):
    seed = Seed("Seed", fingerprint="11111111")
    specter_state.add_seed(seed)
    first = Wallet(
        "Treasury", descriptor="wsh(sortedmulti(2,a,b,c))#00000001",
        isMultiSig=True, required_fingerprints=["11111111", "b", "c"],
        threshold=2)
    second = Wallet(
        "Treasury", descriptor="wsh(sortedmulti(2,a,b,c))#00000002",
        isMultiSig=True, required_fingerprints=["c", "11111111", "b"],
        threshold=2, account=1)
    specter_state.register_wallet(first)
    specter_state.register_wallet(second)
    dropup = _WalletDropUp(specter_state)

    seed_group, signer_group = dropup._get_raw_DropUpGroups()

    assert seed_group.heading == "Seed"
    assert signer_group.heading == "Seed, b, c"
    assert signer_group.items == [first, second]


def test_wallet_groups_keep_multisigs_with_different_thresholds_together(
        specter_state):
    seed = Seed("Seed", fingerprint="11111111")
    specter_state.add_seed(seed)
    first = Wallet(
        "Recovery", descriptor="one", isMultiSig=True,
        required_fingerprints=["11111111", "b", "c"], threshold=1)
    second = Wallet(
        "Treasury", descriptor="two", isMultiSig=True,
        required_fingerprints=["11111111", "b", "c"], threshold=2)
    specter_state.register_wallet(second)
    specter_state.register_wallet(first)

    signer_group = _WalletDropUp(specter_state)._get_raw_DropUpGroups()[1]

    assert signer_group.heading == "Seed, b, c"
    assert signer_group.items == [first, second]


def test_wallet_groups_omit_unassociated_singlesig_wallets(specter_state):
    seed = Seed("Seed", fingerprint="11111111")
    specter_state.add_seed(seed)
    imported = Wallet("Imported", descriptor="imported", is_custom=True,
                      required_fingerprints=["outside"])
    specter_state.register_wallet(imported)

    groups = _WalletDropUp(specter_state)._get_raw_DropUpGroups()

    assert len(groups) == 1
    assert groups[0].items == [specter_state.get_default_wallet()]
    assert imported not in groups[0].items


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