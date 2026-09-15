from MockUI.stubs.wallet import Wallet
from MockUI.wallet_screens.create_custom_wallet_menu import CreateCustomWalletMenu


def test_multisig_descriptors_include_all_fingerprints_and_nonce():
    fingerprints = ["deadbeef", "cafebabe"]

    standard = CreateCustomWalletMenu._build_descriptor(
        fingerprints, 2, True, False, "testnet", 7, "1234abcd")
    custom = CreateCustomWalletMenu._build_descriptor(
        fingerprints, 2, True, True, "testnet", 7, "1234abcd")

    assert standard.startswith("wsh(sortedmulti(2,")
    assert custom.startswith("wsh(and_v(v:thresh(2,")
    for fingerprint in fingerprints:
        assert fingerprint in standard
        assert fingerprint in custom
    assert "xpub...1234abcd" in standard
    assert "xpub...1234abcd" in custom
    assert "/48h/1h/7h/2h]" in standard
    assert "after(840000)" in custom


def test_descriptor_nonce_distinguishes_otherwise_identical_wallets():
    arguments = (["deadbeef"], 1, False, True, "mainnet", 0)

    first = CreateCustomWalletMenu._build_descriptor(*arguments, "00000001")
    second = CreateCustomWalletMenu._build_descriptor(*arguments, "00000002")

    assert first != second


def test_custom_classification_does_not_depend_on_descriptor_text():
    standard = Wallet("Standard", descriptor="fancy script")
    custom = Wallet("Custom", descriptor="wsh(and_v(v:pk(key),after(840000)))",
                    is_custom=True)

    assert standard.is_standard() is True
    assert custom.is_standard() is False