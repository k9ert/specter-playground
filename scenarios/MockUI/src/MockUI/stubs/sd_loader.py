"""Dummy SD card reader stub for the MockUI.

TODO: DUMMY CODE — this is a *placeholder* for the real SD card integration.
It reads files from the SD folder and turns them into MockUI :class:`Seed`
and :class:`Wallet` stubs so the UI can be exercised with realistic data.

It understands the same file formats the browser simulator
(try.clavastack.com) and the real specter-diy SD export use:

* Wallet files   ``*.json`` — ``{"label": ..., "descriptor": ..., ...}``
* Seed files     ``*.txt``   — a plain BIP39 mnemonic (public test seeds only!)

Design notes
------------
* **No autoload.**  Nothing is imported at boot; :meth:`SDCardReader.load_all`
  is only run when the user explicitly presses "Load from SD-Card".
* **Optional embit.**  embit is frozen into the simulator firmware but is NOT
  importable under CPython (it needs the secp256k1 C bindings).  All imports
  are therefore guarded: when embit is available (in the simulator) we compute
  *real* BIP39 master fingerprints; otherwise (unit tests) we fall back to a
  deterministic placeholder fingerprint so behaviour stays reproducible.
* **Dependency-free descriptor parsing.**  Threshold, signer fingerprints and
  network are extracted from the descriptor string with plain string parsing so
  the same code path works in the simulator and in the CPython test suite.

This module never talks to hardware; the caller supplies the SD directory path
(already mounted into the VFS by the entry point, e.g. ``/sd``).
"""

import json
import os

# embit is frozen into the unix-simulator firmware but unavailable under
# CPython (unit tests).  Guard the import and degrade gracefully.
try:
    from embit import bip39, bip32
    _HAS_EMBIT = True
except ImportError:  # pragma: no cover - exercised under CPython tests
    bip39 = None
    bip32 = None
    _HAS_EMBIT = False

from .seed import Seed
from .wallet import Wallet

# File extensions this reader understands.
WALLET_EXTENSIONS = (".json",)
SEED_EXTENSIONS = (".txt",)


def bip39_fingerprint(mnemonic):
    """Return the BIP39 master fingerprint (hex) for *mnemonic*.

    Uses embit when it is available (in the simulator) to produce the *real*
    fingerprint.  Falls back to a deterministic 32-bit placeholder derived
    from the mnemonic so unit tests (no embit) get stable, distinct values.
    """
    mnemonic = (mnemonic or "").strip()
    if _HAS_EMBIT and bip39.mnemonic_is_valid(mnemonic):
        seed_bytes = bip39.mnemonic_to_seed(mnemonic)
        return bip32.HDKey.from_seed(seed_bytes).my_fingerprint.hex()
    return _placeholder_fingerprint(mnemonic)


def _placeholder_fingerprint(mnemonic):
    """Deterministic 8-hex-char placeholder fingerprint (no embit).

    A tiny FNV-1a-style hash keeps values stable across runs without pulling in
    hashlib (which is only partially available in the mocked test env).
    """
    h = 2166136261
    for ch in mnemonic:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    return "%08x" % h


def _seed_label_from_filename(filename):
    """Derive a friendly label from a seed file name."""
    base = filename.rsplit("/", 1)[-1]
    for ext in SEED_EXTENSIONS:
        if base.endswith(ext):
            base = base[: -len(ext)]
    # Tidy up clavastack-style names like "01-ghost-PUBLIC-TEST-SEED".
    base = base.replace("_", " ").replace("-", " ").strip()
    return base or "Imported seed"


def parse_wallet_file(text, fallback_label="Imported wallet"):
    """Parse a wallet JSON export into a :class:`Wallet`.

    Accepts the specter-diy / clavastack shape::

        {"label": "...", "descriptor": "wsh(sortedmulti(2,...))#chk", ...}

    Returns ``None`` when the file does not look like a wallet export.
    """
    try:
        obj = json.loads(text)
    except ValueError:
        return None
    if not isinstance(obj, dict) or "descriptor" not in obj:
        return None

    descriptor = obj.get("descriptor") or ""
    label = obj.get("label") or fallback_label
    info = parse_descriptor(descriptor)

    return Wallet(
        label=label,
        descriptor=descriptor,
        isMultiSig=info["is_multisig"],
        net=info["net"],
        required_fingerprints=info["fingerprints"],
        threshold=info["threshold"],
        has_been_synched=True,  # came from a companion export
    )


def parse_seed_file(text, filename):
    """Parse a plain-mnemonic ``.txt`` file into a :class:`Seed`.

    Returns ``None`` when the content does not look like a BIP39 mnemonic.
    """
    mnemonic = " ".join((text or "").split())
    words = mnemonic.split()
    # BIP39 mnemonics are 12/15/18/21/24 words; be lenient but sane.
    if not (12 <= len(words) <= 24):
        return None
    return Seed(label=_seed_label_from_filename(filename),
                fingerprint=bip39_fingerprint(mnemonic))


def parse_descriptor(descriptor):
    """Extract mock-relevant fields from an output descriptor string.

    Returns a dict with keys ``fingerprints`` (list of hex strings),
    ``threshold`` (int or None), ``is_multisig`` (bool) and ``net``.

    This is a small, dependency-free string parser — deliberately NOT a full
    descriptor implementation (TODO: DUMMY CODE, replace with embit.Descriptor
    when a C-free parse path is available).
    """
    fingerprints = []
    threshold = None
    is_multisig = False
    net = "mainnet"

    if not descriptor:
        return {"fingerprints": fingerprints, "threshold": threshold,
                "is_multisig": is_multisig, "net": net}

    desc = descriptor.strip()

    # Signer fingerprints appear as [<fingerprint>/<path>]key.
    body = desc
    while "[" in body:
        start = body.find("[")
        end = body.find("]", start)
        if end == -1:
            break
        origin = body[start + 1:end]
        fp = origin.split("/", 1)[0].strip()
        if fp and all(c in "0123456789abcdefABCDEF" for c in fp):
            fingerprints.append(fp.lower())
        body = body[end + 1:]

    # Multisig threshold: sortedmulti(<m>, ...) or multi(<m>, ...).
    lowered = desc.lower()
    for marker in ("sortedmulti(", "multi("):
        idx = lowered.find(marker)
        if idx != -1:
            is_multisig = True
            rest = lowered[idx + len(marker):]
            num = ""
            for ch in rest:
                if ch.isdigit():
                    num += ch
                else:
                    break
            if num:
                threshold = int(num)
            break

    # Network from the extended-key prefix.
    if any(tok in desc for tok in ("tpub", "vpub", "upub")):
        net = "testnet"
    elif any(tok in desc for tok in ("xpub", "zpub", "ypub")):
        net = "mainnet"

    return {"fingerprints": fingerprints, "threshold": threshold,
            "is_multisig": is_multisig, "net": net}


class SDCardReader:
    """Dummy SD card reader.

    TODO: DUMMY CODE — stands in for the real SD stack.  It only needs a
    mounted directory path; presence is defined as "the directory exists and
    contains at least one recognisable wallet/seed file".
    """

    def __init__(self, path="/sd"):
        self.path = path

    # ── Directory inspection ─────────────────────────────────────────
    def _list_files(self):
        """Return sorted file names in the SD root (empty if unavailable)."""
        try:
            names = os.listdir(self.path)
        except OSError:
            return []
        # Keep regular files only; ignore sub-directories and hidden files.
        return sorted(n for n in names if not n.startswith("."))

    def _read_text(self, name):
        try:
            with open(self._full(name), "r") as stream:
                return stream.read()
        except (OSError, UnicodeError):
            return None

    def _full(self, name):
        return self.path.rstrip("/") + "/" + name

    def _classify(self, name):
        lower = name.lower()
        if lower.endswith(WALLET_EXTENSIONS):
            return "wallet"
        if lower.endswith(SEED_EXTENSIONS):
            return "seed"
        return None

    # ── Public API ───────────────────────────────────────────────────
    def is_present(self):
        """True when the SD directory contains at least one visible entry.

        An empty directory counts as no card, like an empty card slot.
        """
        return bool(self._list_files())

    def has_importable_files(self):
        """True when at least one wallet/seed file is on the card."""
        return any(self._classify(n) for n in self._list_files())

    def scan(self):
        """Return a summary dict of what is on the card (no side effects)."""
        files = self._list_files()
        return {
            "present": self.is_present(),
            "files": files,
            "wallets": [n for n in files if self._classify(n) == "wallet"],
            "seeds": [n for n in files if self._classify(n) == "seed"],
            "other": [n for n in files if self._classify(n) is None],
        }

    def load_all(self):
        """Parse every wallet/seed file on the card.

        Returns ``(seeds, wallets, skipped)`` — newly created stub objects plus
        a list of file names that were recognised but failed to parse.
        """
        seeds = []
        wallets = []
        skipped = []
        for name in self._list_files():
            kind = self._classify(name)
            if kind is None:
                continue
            text = self._read_text(name)
            if text is None:
                skipped.append(name)
                continue
            if kind == "wallet":
                wallet = parse_wallet_file(text, fallback_label=name)
                if wallet is None:
                    skipped.append(name)
                else:
                    wallets.append(wallet)
            else:  # seed
                seed = parse_seed_file(text, name)
                if seed is None:
                    skipped.append(name)
                else:
                    seeds.append(seed)
        return seeds, wallets, skipped


# ── UI glue (TODO: DUMMY CODE) ──────────────────────────────────────────
def make_load_sd_handler(menu):
    """Return the click handler for the "Load from SD-Card" menu item.

    Kept here (not in main_menu.py) so the whole dummy feature is removed in
    one sweep: delete this module plus the marked one-line hooks in
    main_menu.py, mockui_fw/main.py and stubs/device_state.py.
    """
    from ..basic.widgets import button_modal

    def _on_load_from_sd():
        result = menu.device_state.import_from_sd()
        if result is None:
            button_modal(text=menu.t("BACKUPS_MENU_NO_SD_DETECTED"),
                         title=menu.t("MAIN_MENU_LOAD_FROM_SD"))
            return
        lines = [menu.t("MAIN_MENU_LOADED_FROM_SD").format(
            seeds=result["seeds"], wallets=result["wallets"])]
        if result["skipped"]:
            lines.append(menu.t("MAIN_MENU_SD_SKIPPED").format(
                files=", ".join(result["skipped"])))
        button_modal(text="\n".join(lines), title=menu.t("MAIN_MENU_LOAD_FROM_SD"))
        menu.gui.refresh_ui()

    return _on_load_from_sd
