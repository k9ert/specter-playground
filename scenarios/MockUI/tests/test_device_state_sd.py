"""Tests for DeviceState SD detection + import (dummy SD import)."""
import json
import os

from MockUI.stubs.device_state import DeviceState


def _write(path, name, text):
    with open(os.path.join(path, name), "w") as f:
        f.write(text)


def _attach(tmp_path):
    state = DeviceState()
    state._hasSD = True
    state._enabledSD = True
    state.attach_sd_reader(str(tmp_path))
    return state


def test_detection_follows_files(tmp_path):
    state = _attach(tmp_path)
    # Empty card folder -> no card inserted.
    assert state.SD_detected() is False
    assert state.SD_hasSeed() is False

    _write(str(tmp_path), "notes.md", "# not importable")
    assert state.SD_detected() is True
    assert state.SD_hasSeed() is False

    _write(str(tmp_path), "seed.txt", "zoo " * 11 + "wrong")
    assert state.SD_hasSeed() is True

    # Removing the files flips detection back off (tests insert/remove UX).
    os.remove(os.path.join(str(tmp_path), "seed.txt"))
    assert state.SD_hasSeed() is False
    os.remove(os.path.join(str(tmp_path), "notes.md"))
    assert state.SD_detected() is False


def test_detection_requires_enabled(tmp_path):
    _write(str(tmp_path), "seed.txt", "zoo " * 11 + "wrong")
    state = _attach(tmp_path)
    state.set_SD_enabled(False)
    assert state.SD_detected() is False
    state.set_SD_enabled(True)
    assert state.SD_detected() is True


def test_import_from_sd_creates_objects(tmp_path):
    _write(str(tmp_path), "ghost.txt",
           "ghost ghost ghost ghost ghost ghost ghost ghost ghost ghost ghost machine")
    _write(str(tmp_path), "multi.json", json.dumps({
        "label": "Ghost Multisig",
        "descriptor": "wsh(sortedmulti(2,[8c24a510/48'/1'/0'/2']tpubA/0/*,"
                      "[74d682c3/48'/1'/0'/2']tpubB/0/*))#c",
    }))
    state = _attach(tmp_path)

    result = state.import_from_sd()
    assert result is not None
    assert result["seeds"] == 1
    assert result["wallets"] == 1
    assert result["skipped"] == []

    # Seed appears in loaded seeds; default wallet auto-created on add_seed.
    assert len(state.loaded_seeds) == 1
    assert any(w.is_default_wallet() for w in state.registered_wallets)

    # The imported multisig wallet is registered and marked synced (imported).
    multi = [w for w in state.registered_wallets if w.label == "Ghost Multisig"]
    assert len(multi) == 1
    assert multi[0].isMultiSig is True
    assert multi[0].threshold == 2
    assert multi[0].has_been_synched is True


def test_import_from_sd_no_reader():
    state = DeviceState()
    assert state.import_from_sd() is None
