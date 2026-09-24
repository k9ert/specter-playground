"""Tests for the dummy SD card reader stub (stubs/sd_loader.py)."""
import json
import os

from MockUI.stubs.sd_loader import (
    SDCardReader,
    parse_descriptor,
    parse_seed_file,
    parse_wallet_file,
    bip39_fingerprint,
    _HAS_EMBIT,
)


# ---------------------------------------------------------------------------
# parse_descriptor
# ---------------------------------------------------------------------------

def test_parse_descriptor_singlesig_mainnet():
    desc = "wpkh([8c24a510/84'/0'/0']xpub6BosfCnifzQJJX.../0/*)#abcd1234"
    info = parse_descriptor(desc)
    assert info["fingerprints"] == ["8c24a510"]
    assert info["is_multisig"] is False
    assert info["threshold"] is None
    assert info["net"] == "mainnet"


def test_parse_descriptor_multisig_testnet():
    desc = ("wsh(sortedmulti(2,[8c24a510/48'/1'/0'/2']tpubAAA/0/*,"
            "[deadbeef/48'/1'/0'/2']tpubBBB/0/*))#xyz")
    info = parse_descriptor(desc)
    assert info["fingerprints"] == ["8c24a510", "deadbeef"]
    assert info["is_multisig"] is True
    assert info["threshold"] == 2
    assert info["net"] == "testnet"


def test_parse_descriptor_empty():
    info = parse_descriptor("")
    assert info["fingerprints"] == []
    assert info["is_multisig"] is False
    assert info["net"] == "mainnet"


# ---------------------------------------------------------------------------
# parse_wallet_file / parse_seed_file
# ---------------------------------------------------------------------------

def test_parse_wallet_file_valid():
    text = json.dumps({
        "label": "Ghost Multisig",
        "descriptor": "wsh(sortedmulti(2,[8c24a510/48'/1'/0'/2']tpubA/0/*,"
                      "[74d682c3/48'/1'/0'/2']tpubB/0/*))#c",
    })
    wallet = parse_wallet_file(text)
    assert wallet is not None
    assert wallet.label == "Ghost Multisig"
    assert wallet.isMultiSig is True
    assert wallet.threshold == 2
    assert wallet.net == "testnet"
    assert set(wallet.get_signers()) == {"74d682c3", "8c24a510"}
    assert wallet.has_been_synched is True


def test_parse_wallet_file_not_a_wallet():
    assert parse_wallet_file(json.dumps({"foo": "bar"})) is None
    assert parse_wallet_file("not json at all") is None


def test_parse_seed_file_valid():
    text = "ghost ghost ghost ghost ghost ghost ghost ghost ghost ghost ghost machine\n"
    seed = parse_seed_file(text, "01-ghost-PUBLIC-TEST-SEED.txt")
    assert seed is not None
    assert "ghost" in seed.label.lower()
    # deterministic placeholder fingerprint (embit not importable under CPython)
    assert seed.fingerprint == bip39_fingerprint("ghost ghost ghost ghost ghost ghost "
                                                 "ghost ghost ghost ghost ghost machine")
    assert len(seed.fingerprint) == 8


def test_parse_seed_file_rejects_short():
    assert parse_seed_file("too short", "x.txt") is None


# ---------------------------------------------------------------------------
# SDCardReader filesystem behaviour (uses tmp dir as the mounted SD card)
# ---------------------------------------------------------------------------

def _write(path, name, text):
    with open(os.path.join(path, name), "w") as f:
        f.write(text)


def test_reader_presence_and_scan(tmp_path):
    sd = str(tmp_path)
    reader = SDCardReader(sd)
    assert reader.is_present() is False
    assert reader.has_importable_files() is False

    _write(sd, "wallet.json", json.dumps({"label": "W", "descriptor": "wpkh([8c24a510/84'/0'/0']xpubX/0/*)"}))
    _write(sd, "seed.txt", "zoo " * 11 + "wrong")
    _write(sd, "notes.md", "# ignore me")

    scan = reader.scan()
    assert scan["present"] is True
    assert scan["wallets"] == ["wallet.json"]
    assert scan["seeds"] == ["seed.txt"]
    assert scan["other"] == ["notes.md"]
    assert reader.has_importable_files() is True


def test_reader_missing_dir():
    reader = SDCardReader("/nonexistent-sd-path-xyz")
    assert reader.is_present() is False
    assert reader.has_importable_files() is False
    seeds, wallets, skipped = reader.load_all()
    assert seeds == [] and wallets == [] and skipped == []


def test_reader_load_all(tmp_path):
    sd = str(tmp_path)
    _write(sd, "w.json", json.dumps({"label": "Hot", "descriptor": "wpkh([b07b0001/84'/0'/0']xpubY/0/*)"}))
    _write(sd, "s.txt", "ghost " * 11 + "machine")
    _write(sd, "bad.json", "{not json")
    reader = SDCardReader(sd)

    seeds, wallets, skipped = reader.load_all()
    assert len(seeds) == 1
    assert len(wallets) == 1
    assert skipped == ["bad.json"]
    assert wallets[0].label == "Hot"
    assert seeds[0].fingerprint == bip39_fingerprint("ghost " * 11 + "machine")
