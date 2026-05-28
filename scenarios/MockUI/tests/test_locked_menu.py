"""Unit tests for the locked menu's shuffle helper and DeviceState lock/unlock logic.

All tests run entirely in the host Python environment — no device or LVGL
runtime required.  The ``shuffle`` function lives in ``locked_menu`` which
imports ``rng`` (from ``src/rng.py``).  We add ``src/`` to ``sys.path``
before importing so that ``rng`` resolves without hardware.
"""
import os
import sys

import pytest

# Make src/rng.py available to the import chain of locked_menu.py
_SRC_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "src")
)
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

# Now we can safely import shuffle (locked_menu's top-level ``import rng``
# will resolve to src/rng.py which uses os.urandom on the host).
from MockUI.basic.utils.ui_utils import shuffle
from MockUI.stubs.device_state import DeviceState

# A non-trivial PIN used throughout the lock/unlock tests.
# Must not be None (which would bypass the PIN check in DeviceState.unlock).
_TEST_PIN = "42"

# Max attempts for randomness checks — probability of all producing natural
# order: (1/10!)^3 ≈ 10^-21 (scalar) and (1/4!)^3 ≈ 10^-8 (list).
_MAX_SHUFFLE_RETRIES = 3


# ---------------------------------------------------------------------------
# shuffle: scalar input
# ---------------------------------------------------------------------------


def test_shuffle_scalar_10_digits_covers_all():
    """shuffle(10) must be a permutation of 0..9 and must differ from natural
    order in at least one of _MAX_SHUFFLE_RETRIES attempts.

    Probability that all _MAX_SHUFFLE_RETRIES produce the identity permutation ≈ (1/10!)^_MAX_SHUFFLE_RETRIES
    """
    natural = list(range(10))
    results = [shuffle(10) for _ in range(_MAX_SHUFFLE_RETRIES)]
    for result in results:
        assert sorted(result) == natural, (
            f"not a permutation of range(10): {result}"
        )
    assert any(r != natural for r in results), (
        f"All {_MAX_SHUFFLE_RETRIES} shuffles returned natural order [0..9] — shuffle appears broken."
    )


# ---------------------------------------------------------------------------
# shuffle: list input
# ---------------------------------------------------------------------------

def test_shuffle_list_returns_permutation_of_items():
    """shuffle(list) shuffles in place, result is a permutation of original,
    and at least one of _MAX_SHUFFLE_RETRIES attempts must actually change the order.

    Probability that all _MAX_SHUFFLE_RETRIES leave 6 items unchanged ≈ (1/6!)^_MAX_SHUFFLE_RETRIES.
    """
    natural = ["a", "b", "c", "d", "e", "f"]
    changed = False
    for _ in range(_MAX_SHUFFLE_RETRIES):
        items = natural[:]
        shuffle(items)
        assert sorted(items) == sorted(natural), (
            f"shuffled items are not a permutation: {items}"
        )
        assert len(items) == len(natural)
        if items != natural:
            changed = True
    assert changed, (
        f"All {_MAX_SHUFFLE_RETRIES} list shuffles left the order unchanged — shuffle appears broken."
    )


def test_shuffle_list_indices_consistent():
    """items[i] after shuffle must equal snapshot[indices[i]] for all i."""
    items = list("0123456789")
    snapshot = items[:]
    indices = shuffle(items)
    reconstructed = [snapshot[i] for i in indices]
    assert reconstructed == items, (
        f"indices inconsistent with in-place shuffle.\n"
        f"  items after:   {items}\n"
        f"  reconstructed: {reconstructed}"
    )


def test_shuffle_list_mutates_in_place():
    """shuffle must modify the list in place (not return a new one)."""
    original = list("0123456789")
    same_ref = original
    shuffle(original)
    assert original is same_ref, "shuffle must operate on the same list object"


def test_shuffle_list_indices_are_permutation():
    """Returned indices must be a permutation of range(len(input))."""
    items = ["x", "y", "z"]
    indices = shuffle(items)
    assert sorted(indices) == list(range(len(items))), (
        f"indices are not a permutation of range({len(items)}): {indices}"
    )


# ---------------------------------------------------------------------------
# shuffle: wrong type
# ---------------------------------------------------------------------------

def test_shuffle_wrong_type_raises():
    """shuffle with a non-int, non-list argument must raise TypeError."""
    with pytest.raises(TypeError):
        shuffle(3.14)
    with pytest.raises(TypeError):
        shuffle("hello")
    with pytest.raises(TypeError):
        shuffle((1, 2, 3))


# ---------------------------------------------------------------------------
# shuffle: randomness
# ---------------------------------------------------------------------------

def test_shuffle_varies_with_different_calls():
    """Repeated calls must produce different results (RNG is live, not seeded).

    Probability of all 20 results being identical ≈ (1/10!)^19 ≈ 10^-133.
    Test failure would indicate a fundamentally broken RNG.
    """
    results = [tuple(shuffle(10)) for _ in range(20)]
    assert len(set(results)) > 1, (
        "All 20 shuffles produced the same permutation — RNG appears broken."
    )


# ---------------------------------------------------------------------------
# DeviceState: lock / unlock
# ---------------------------------------------------------------------------

def test_lock_sets_is_locked():
    state = DeviceState()
    assert not state.is_locked, "fresh state should not be locked"
    state.lock()
    assert state.is_locked, "state.lock() must set is_locked=True"


def test_unlock_correct_pin_returns_true_and_clears_lock(specter_state):
    specter_state.pin = _TEST_PIN
    specter_state.lock()
    assert specter_state.is_locked

    result = specter_state.unlock(_TEST_PIN)

    assert result is True, "unlock with correct PIN must return True"
    assert not specter_state.is_locked, "is_locked must be False after correct unlock"


def test_unlock_wrong_pin_returns_false_stays_locked(specter_state):
    specter_state.pin = _TEST_PIN
    specter_state.lock()
    assert specter_state.is_locked

    result = specter_state.unlock("wrong")

    assert result is False, "unlock with wrong PIN must return False"
    assert specter_state.is_locked, "is_locked must remain True after wrong unlock"
