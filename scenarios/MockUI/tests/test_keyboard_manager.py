"""Unit tests for KeyboardManager lifecycle and event handling.

These tests run entirely in the host Python environment using lightweight
mock objects — no device or LVGL runtime required.
"""
import pytest
import lvgl as lv

# ── Extend the shared lvgl mock with constants needed by KeyboardManager ──
# The base mock in scenarios/conftest.py only has CLICKED; add the rest here.

lv.EVENT.READY     = 100
lv.EVENT.CANCEL    = 101
lv.EVENT.DEFOCUSED = 102
lv.EVENT.DELETE    = 103


class _FLAG:
    HIDDEN    = 10
    CLICKABLE = 11


class _STATE:
    FOCUSED = 20


class _PART:
    ITEMS = 30


class _MODE:
    TEXT_LOWER = 0
    TEXT_UPPER = 1
    SPECIAL    = 2


lv.obj.FLAG  = _FLAG
lv.STATE     = _STATE
lv.PART      = _PART

# Symbol chars needed when building keyboard layout maps
lv.SYMBOL.BACKSPACE = "BS"
lv.SYMBOL.LEFT      = "<"
lv.SYMBOL.RIGHT     = ">"
lv.SYMBOL.OK        = "OK"

lv.font_montserrat_22 = "font22"


# ── Minimal mock objects ──

class MockKeyboard:
    """Tracks calls made by KeyboardManager without doing real LVGL work."""
    FLAG = _FLAG
    MODE = _MODE

    def __init__(self, *args, **kwargs):
        self._flags     = {_FLAG.HIDDEN}
        self._event_cbs = []
        self._textarea  = None

    def add_flag(self, flag):              self._flags.add(flag)
    def remove_flag(self, flag):           self._flags.discard(flag)
    def is_hidden(self):                   return _FLAG.HIDDEN in self._flags
    def add_event_cb(self, cb, ev, ud):    self._event_cbs.append((cb, ev))
    def set_style_text_font(self, *a):     pass
    def set_textarea(self, ta):            self._textarea = ta
    def set_map(self, *a):                 pass
    def move_foreground(self):             pass


class _EventDsc:
    """Descriptor returned by add_event_cb, consumed by remove_event_dsc."""
    def __init__(self, cb, ev):
        self.cb = cb
        self.ev = ev


class MockTextarea:
    def __init__(self, text="initial"):
        self._text        = text
        self._event_cbs   = []   # list of _EventDsc objects
        self._states      = set()
        self.set_text_calls = []

    def get_text(self):               return self._text
    def set_text(self, t):
        self.set_text_calls.append(t)
        self._text = t
    def add_state(self, s):           self._states.add(s)
    def add_event_cb(self, cb, ev, ud):
        dsc = _EventDsc(cb, ev)
        self._event_cbs.append(dsc)
        return dsc
    def remove_event_dsc(self, dsc):
        if dsc in self._event_cbs:
            self._event_cbs.remove(dsc)
            return True
        return False
    def add_flag(self, *a):           pass


class MockNav:
    pass


class MockEvent:
    def __init__(self, code):     self._code = code
    def get_code(self):           return self._code


# ── Fixtures ──

@pytest.fixture()
def nav():
    return MockNav()


@pytest.fixture()
def manager(nav):
    original_kb = lv.keyboard
    lv.keyboard = MockKeyboard
    from MockUI.basic.utils.keyboard_manager import KeyboardManager
    km = KeyboardManager(nav)
    yield km
    lv.keyboard = original_kb


@pytest.fixture()
def ta():
    return MockTextarea("initial")


@pytest.fixture()
def ta2():
    return MockTextarea("other_initial")


# ── Tests ──

def test_bind_creates_and_shows_keyboard(manager, ta):
    manager.bind(ta, 1)  # Layout.FULL = 1
    assert manager.keyboard is not None
    assert not manager.keyboard.is_hidden()
    assert manager.keyboard._textarea is ta


def test_bind_sets_textarea_reference(manager, ta):
    manager.bind(ta, 1)
    assert manager.textarea is ta


def test_bind_same_textarea_twice_is_noop(manager, ta):
    manager.bind(ta, 1)
    cb_count = len(ta._event_cbs)
    manager.bind(ta, 1)
    assert len(ta._event_cbs) == cb_count, "Second bind to same textarea must not register more callbacks"


def test_commit_calls_on_commit_with_text(manager, ta):
    committed = []
    manager.bind(ta, 1, on_commit=lambda t: committed.append(t))
    ta.set_text("hello")
    manager._commit(MockEvent(lv.EVENT.READY))
    assert committed == ["hello"]


def test_commit_applies_sanitizer_before_callback(manager, ta):
    committed = []
    manager.bind(ta, 1, on_commit=lambda t: committed.append(t), sanitize=str.strip)
    ta.set_text("  hello  ")
    manager._commit(MockEvent(lv.EVENT.READY))
    assert committed == ["hello"]
    assert ta.get_text() == "hello"


def test_commit_works_without_on_commit(manager, ta):
    """Commit with no callback should still update textarea and unbind cleanly."""
    manager.bind(ta, 1, sanitize=str.strip)
    ta.set_text("  hello  ")
    manager._commit(MockEvent(lv.EVENT.READY))
    assert ta.get_text() == "hello"
    assert manager.textarea is None


def test_commit_unbinds(manager, ta):
    manager.bind(ta, 1)
    manager._commit(MockEvent(lv.EVENT.READY))
    assert manager.textarea is None
    assert manager.keyboard.is_hidden()
    assert manager.keyboard._textarea is None


def test_cancel_restores_original_text(manager, ta):
    manager.bind(ta, 1)        # snapshots "initial"
    ta.set_text("modified")
    manager._cancel(MockEvent(lv.EVENT.CANCEL))
    assert ta.set_text_calls[-1] == "initial"


def test_cancel_calls_on_cancel(manager, ta):
    cancelled = []
    manager.bind(ta, 1, on_cancel=lambda: cancelled.append(True))
    manager._cancel(MockEvent(lv.EVENT.CANCEL))
    assert cancelled == [True]


def test_cancel_unbinds(manager, ta):
    manager.bind(ta, 1)
    manager._cancel(MockEvent(lv.EVENT.CANCEL))
    assert manager.textarea is None
    assert manager.keyboard.is_hidden()


def test_cancel_on_delete_does_not_restore_text(manager, ta):
    """When the textarea is being destroyed, set_text must not be called on it."""
    manager.bind(ta, 1)
    ta.set_text("modified")
    calls_before = len(ta.set_text_calls)
    manager._cancel(MockEvent(lv.EVENT.DELETE))
    assert len(ta.set_text_calls) == calls_before, "set_text must not be called during DELETE"


def test_cancel_on_delete_does_not_call_on_cancel(manager, ta):
    """When the textarea is being destroyed, on_cancel must not be called.

    Documented contract: neither text restore nor on_cancel are triggered
    during lv.EVENT.DELETE because the object is being destroyed by LVGL.
    """
    cancelled = []
    manager.bind(ta, 1, on_cancel=lambda: cancelled.append(True))
    manager._cancel(MockEvent(lv.EVENT.DELETE))
    assert cancelled == [], "on_cancel must not be called during DELETE"


def test_cancel_on_delete_unbinds(manager, ta):
    manager.bind(ta, 1)
    manager._cancel(MockEvent(lv.EVENT.DELETE))
    assert manager.textarea is None
    assert manager.keyboard.is_hidden()


def test_rebind_different_textarea_replaces_old(manager, ta, ta2):
    manager.bind(ta, 1)
    manager.bind(ta2, 1)
    assert manager.textarea is ta2
    # All callbacks should have been removed from the old textarea
    assert ta._event_cbs == [], "Old textarea callbacks must be cleaned up on rebind"


def test_rebind_different_textarea_does_not_call_on_cancel(manager, ta, ta2):
    cancelled = []
    manager.bind(ta, 1, on_cancel=lambda: cancelled.append(True))
    manager.bind(ta2, 1)
    assert cancelled == [], "on_cancel must be suppressed when replacing a binding"


def test_rebind_different_textarea_restores_old_text(manager, ta, ta2):
    """Replacing a binding should still restore the original text of the old textarea."""
    ta.set_text("modified")
    manager.bind(ta, 1)         # snapshots "modified" as original
    ta.set_text("changed again")
    manager.bind(ta2, 1)        # replaces; should restore ta to "modified"
    assert ta.get_text() == "modified"


def test_direct_cancel_call_with_none_event(manager, ta):
    """_cancel(None) is used internally during rebind; must not raise."""
    manager.bind(ta, 1)
    manager._cancel(None)       # called as plain Python, not from LVGL
    assert manager.textarea is None


def test_no_crash_when_cancel_called_without_binding(manager):
    """Calling _cancel with no active binding is a safe no-op."""
    manager._cancel(MockEvent(lv.EVENT.CANCEL))  # must not raise


def test_no_crash_when_commit_called_without_binding(manager):
    """Calling _commit with no active binding is a safe no-op."""
    manager._commit(MockEvent(lv.EVENT.READY))   # must not raise
