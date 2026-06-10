"""Pytest configuration for MockUI tests."""
import json
import os
import shutil
from pathlib import Path

"""Pytest configuration for MockUI tests."""
import json
import os
import shutil
from pathlib import Path

import pytest

# Import state classes (micropython/lvgl already mocked by scenarios/conftest.py)
from MockUI.stubs.device_state import DeviceState
from MockUI.basic.ui_state import UIState
from MockUI.stubs.wallet import Wallet

# i18n imports
from MockUI.basic.i18n import I18nManager
from MockUI.basic.i18n.translation_keys import Keys
import MockUI.basic.i18n.lang_compiler as lang_compiler
from MockUI.basic.i18n.lang_compiler import LangCompiler as _LangCompiler

_c = _LangCompiler()

# ---------------------------------------------------------------------------
# Path to real language source files in the repo
# ---------------------------------------------------------------------------
_I18N_LANGUAGES_DIR = Path(__file__).parent.parent / "src" / "MockUI" / "basic" / "i18n" / "languages"
_EN_JSON = _I18N_LANGUAGES_DIR / "specter_ui_en.json"
_DE_JSON = _I18N_LANGUAGES_DIR / "specter_ui_de.json"


# ===== Existing fixtures (unchanged) =====

@pytest.fixture
def specter_state():
    """Fresh DeviceState instance."""
    return DeviceState()


@pytest.fixture
def ui_state():
    """Fresh UIState instance."""
    return UIState()


@pytest.fixture
def wallet():
    """Sample wallet."""
    return Wallet("Test Wallet", xpub="xpub123")


@pytest.fixture
def multisig_wallet():
    """Sample multisig wallet."""
    return Wallet("Multisig", isMultiSig=True, net="testnet")


# ===== i18n fixtures =====

@pytest.fixture
def key_to_index():
    """Key-to-index dict built from the Keys class (for test index lookups)."""
    return {k: getattr(Keys, k) for k in dir(Keys) if not k.startswith('_') and isinstance(getattr(Keys, k), int)}


@pytest.fixture
def en_json_source():
    """Path to the real English JSON in the repo (read-only)."""
    return _EN_JSON


@pytest.fixture
def de_json_source():
    """Path to the real German JSON in the repo (read-only)."""
    return _DE_JSON


@pytest.fixture
def en_json_data():
    """Parsed content of the real English JSON."""
    with open(_EN_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def de_json_data():
    """Parsed content of the real German JSON."""
    with open(_DE_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def i18n_flash_dir(tmp_path):
    """Temp directory mimicking /flash/i18n/ — empty on creation."""
    flash_dir = tmp_path / "flash" / "i18n"
    flash_dir.mkdir(parents=True)
    return flash_dir


@pytest.fixture
def en_json_path(tmp_path):
    """Copy of real English JSON in a temp directory."""
    dest = tmp_path / "specter_ui_en.json"
    shutil.copy(_EN_JSON, dest)
    return dest


@pytest.fixture
def de_json_path(tmp_path):
    """Copy of real German JSON in a temp directory."""
    dest = tmp_path / "specter_ui_de.json"
    shutil.copy(_DE_JSON, dest)
    return dest


@pytest.fixture
def en_binary_path(i18n_flash_dir, en_json_path):
    """Compiled lang_en.bin in the flash dir."""
    out = str(i18n_flash_dir / "lang_en.bin")
    result = _c.json_to_binary(str(en_json_path), Keys, out)
    assert result is not None, "Failed to compile English binary"
    return Path(out)


@pytest.fixture
def de_binary_path(i18n_flash_dir, de_json_path):
    """Compiled lang_de.bin in the flash dir."""
    out = str(i18n_flash_dir / "lang_de.bin")
    result = _c.json_to_binary(str(de_json_path), Keys, out)
    assert result is not None, "Failed to compile German binary"
    return Path(out)


@pytest.fixture
def incomplete_de_json_path(tmp_path, en_json_data):
    """German JSON with deliberately missing translations for fallback testing."""
    de_data = {
        "_metadata": {
            "language_code": "de",
            "language_name": "Deutsch (incomplete)",
        },
        "translations": {},
    }
    # Copy only half the keys
    all_keys = sorted(en_json_data["translations"].keys())
    for key in all_keys[: len(all_keys) // 2]:
        de_data["translations"][key] = f"DE:{key}"
    dest = tmp_path / "specter_ui_de.json"
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(de_data, f, indent=2, ensure_ascii=False)
    return dest


@pytest.fixture
def i18n_manager(i18n_flash_dir, en_binary_path):
    """
    Fully initialised I18nManager pointing at the temp flash dir
    with English pre-installed and selected.
    """
    # Write initial config so the manager finds it
    config_path = i18n_flash_dir / "language_config.json"
    with open(config_path, "w") as f:
        json.dump({"selected_file": "en"}, f)

    mgr = I18nManager()
    mgr.FLASH_DIR = str(i18n_flash_dir)
    mgr.FLASH_CONFIG_PATH = str(config_path)
    mgr._scan_available_files()
    mgr.set_language("en")
    return mgr
