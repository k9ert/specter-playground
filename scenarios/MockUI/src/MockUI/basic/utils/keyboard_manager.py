import lvgl as lv
from .keyboard_layouts import _full_layout, _alnum_layout
from ..theming import apply_style
class Layout:
    ALNUM = 0
    FULL = 1


class KeyboardManager:
    """Shared on-screen keyboard controller for MockUI screens."""

    def __init__(self, gui):
        self.gui = gui

        self.keyboard = None
        self._reset_internals()
        self.textarea = None
        self.defocus_cb = None
        self.delete_cb = None

    def bind(self, textarea, layout_id, on_commit=None, sanitize=None, on_cancel=None):
        """Activate the on-screen keyboard for a textarea.

        Call this from the textarea's CLICKED event callback. The manager then
        owns keyboard open/close handling until the user commits or cancels.

        Invariant: only one binding is active at a time. If another textarea is
        already bound, it is silently cancelled and replaced by the new one.
        The binding is automatically cleared when the textarea emits
        ``lv.EVENT.DELETE``.

        Args:
            textarea: The target ``lv.textarea`` to edit with the on-screen
                keyboard. Must be an LVGL object that emits ``lv.EVENT.DELETE`` on destruction.
            layout_id: Keyboard layout identifier (``Layout.ALNUM`` or
                ``Layout.FULL``).
            on_commit: Optional callback ``fn(new_text: str)`` invoked after the
                user confirms with keyboard OK.
            sanitize: Optional callback ``fn(text: str) -> str`` applied on
                READY before ``on_commit``.
            on_cancel: Optional callback ``fn()`` invoked when input is
                canceled/aborted. Original text is restored to the textarea
                before the call. Neither the text restore nor this callback
                are triggered when the textarea fires ``lv.EVENT.DELETE``
                (the object is being destroyed by LVGL; operating on it
                or calling navigation logic at that point would be unsafe).
        """
        self._ensure_keyboard()

        if self.textarea is not None:
            if self.textarea == textarea:
                # Already bound to this textarea, ignore
                return
            else:
                # Bound to a different textarea, cancel this previous binding before proceeding
                # This will also unbind
                # Suppress calling the handed over cancel callback because we're immediately 
                # rebinding to a new textarea, and don't want to trigger any intermediate 
                # cancel logic in the old screen. The original text gets restored as usual
                self._cancel(None, call_cb=False)
        
        self._apply_layout(layout_id)

        self._set_internals(on_commit=on_commit, on_cancel=on_cancel, sanitize=sanitize, original_text=textarea.get_text())

        textarea.add_state(lv.STATE.FOCUSED)
        self.defocus_cb = textarea.add_event_cb(self._cancel, lv.EVENT.DEFOCUSED, None)
        self.delete_cb = textarea.add_event_cb(self._cancel, lv.EVENT.DELETE, None)

        self.keyboard.remove_flag(lv.obj.FLAG.HIDDEN)
        self.keyboard.set_textarea(textarea)
        self.keyboard.move_foreground()  # must render above everything else

        #Do this last to mark binding is complete
        self.textarea = textarea

    def _unbind(self, textarea_is_deleting=False):
        if self.textarea is None:
            return
        
        if not textarea_is_deleting:
            if self.defocus_cb:
                self.textarea.remove_event_dsc(self.defocus_cb)
                self.defocus_cb = None
            if self.delete_cb:
                self.textarea.remove_event_dsc(self.delete_cb)
                self.delete_cb = None

        self._reset_internals()

        self.keyboard.add_flag(lv.obj.FLAG.HIDDEN)
        self.keyboard.set_textarea(None)

        #Do this last to mark binding is cleared
        self.textarea = None

    def _reset_internals(self):
        self.on_commit = None
        self.on_cancel = None
        self.sanitize = None
        self._original_text = None

    def _set_internals(self, on_commit=None, on_cancel=None, sanitize=None, original_text=None):
        self.on_commit = on_commit
        self.on_cancel = on_cancel
        self.sanitize = sanitize
        self._original_text = original_text

    def _ensure_keyboard(self):
        if self.keyboard:
            return

        self.keyboard = lv.keyboard(self.gui)
        self.keyboard.add_flag(lv.obj.FLAG.HIDDEN)
        apply_style(self.keyboard, "WIDGET.KEYBOARD", lv.PART.ITEMS)
        apply_style(self.keyboard, "WIDGET.KEYBOARD", lv.PART.MAIN)
        self.keyboard.add_event_cb(self._commit, lv.EVENT.READY, None)
        self.keyboard.add_event_cb(self._cancel, lv.EVENT.CANCEL, None)

    def _apply_layout(self, layout_id):
        builder = _alnum_layout if layout_id == Layout.ALNUM else _full_layout
        map_lower, map_upper, map_special, ctrl_text, ctrl_special = builder()

        self.keyboard.set_map(lv.keyboard.MODE.TEXT_LOWER, map_lower, ctrl_text)
        self.keyboard.set_map(lv.keyboard.MODE.TEXT_UPPER, map_upper, ctrl_text)
        self.keyboard.set_map(lv.keyboard.MODE.SPECIAL, map_special, ctrl_special)

    def _cancel(self, e, call_cb=True):
        if self.textarea is None:
            return
        
        #first remove keyboard and callbacks, then call cancel callback (if any) to avoid potential reentrancy issues
        cancel_cb = None

        is_deleting = (e is not None and e.get_code() == lv.EVENT.DELETE)

        if not is_deleting:
            # reset to initial value/text
            self.textarea.set_text(self._original_text)    
            cancel_cb = self.on_cancel
        
        self._unbind(is_deleting)

        if cancel_cb and call_cb:
            cancel_cb()

    def _commit(self, e):
        if self.textarea is None:
            return
        
        #first remove keyboard and callbacks, then call sanitizer/commit callback (if any) to avoid potential reentrancy issues
        sanitizer_cb = self.sanitize
        commit_cb = self.on_commit
        textarea = self.textarea
        new_text = textarea.get_text()
        
        self._unbind()

        if sanitizer_cb:
            new_text = sanitizer_cb(new_text)
        textarea.set_text(new_text)

        if commit_cb:
            commit_cb(new_text)
