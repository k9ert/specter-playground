"""Runtime-friendly UI state helper for the MockUI.

Keeps track of the UI-specific state in a small, mutable object so the
navigation controller and menus can be kept stateless and simple.

Designed to avoid typing and external deps so it runs in the MicroPython
simulator environment.
"""


class UIState:
    """Small helper to track UI-level state.

    Attributes are intentionally public and mutable for simplicity in the
    mock environment.
    """

    def __init__(self):
        # current visible menu id (string)
        self.current_menu_id = "main"

        # stack of previous menu ids (LIFO)
        self.history = []

        # modal currently open (string name) or None
        self.modal = None

    # Navigation helpers
    def push_menu(self, menu_id):
        """Navigate to a new menu and push the old one on the history stack."""
        if self.current_menu_id is not None:
            self.history.append(self.current_menu_id)
        self.current_menu_id = menu_id

    def pop_menu(self):
        """Pop the last menu from history and make it current (or go to 'main')."""
        if self.history:
            self.current_menu_id = self.history.pop()
        else:
            self.current_menu_id = "main"

    def clear_history(self):
        self.history.clear()
    # Modal helpers
    def open_modal(self, name):
        self.modal = name

    def close_modal(self):
        self.modal = None

    def is_modal_open(self):
        return self.modal is not None
