"""Runtime-friendly UI state helper for the MockUI.

Keeps track of the UI-specific state in a small, mutable object so the
navigation controller and menus can be kept stateless and simple.
"""

import json
from micropython import const
from ..basic.animations import GUIAnimations
from ..basic.ui_consts import MAX_HISTORY_DEPTH

CONFIG_FILE = "/flash/ui_state_config.json"

_MENU_CTX_MAIN       = const(0)
_MENU_CTX_DEVICE     = const(1)
_MENU_CTX_ADD_SEED   = const(2)
_MENU_CTX_SEED       = const(3)
_MENU_CTX_ADD_WALLET = const(4)
_MENU_CTX_WALLET     = const(5)

# Fast O(1) lookup: menu_id → Context constant
_MENU_CONTEXT = {
    "main":              _MENU_CTX_MAIN,
    "manage_settings":   _MENU_CTX_DEVICE,
    "add_seed":          _MENU_CTX_ADD_SEED,
    "manage_seedphrase": _MENU_CTX_SEED,
    "add_wallet":        _MENU_CTX_ADD_WALLET,
    "manage_wallet":     _MENU_CTX_WALLET,
}

class Context:
    MAIN   = _MENU_CTX_MAIN
    DEVICE = _MENU_CTX_DEVICE
    ADD_SEED = _MENU_CTX_ADD_SEED
    SEED   = _MENU_CTX_SEED
    ADD_WALLET = _MENU_CTX_ADD_WALLET
    WALLET = _MENU_CTX_WALLET

class UIState:
    class Snapshot:
        def __init__(self, menu_id, context=None, seed=None, wallet=None, out_anim=None):
            self.menu_id = menu_id
            self.context = context
            self.seed = seed
            self.wallet = wallet
            self.anim = out_anim

    def _set_to_main(self):
        self.current_menu_id = "main"
        self.active_context = Context.MAIN
        self.active_seed = None
        self.active_wallet = None

    def __init__(self):
        # stack of previous Snapshots (LIFO)
        self.history = []

        self._set_to_main()
        self.are_animations_enabled = True

        # Tour state - loaded from config file
        self._run_tour_on_startup = self._load_tour_state()

    # Active selection helpers
    def set_active_seed(self, seed):
        self.active_seed = seed

    def set_active_wallet(self, wallet):
        self.active_wallet = wallet

    # Navigation helpers
    def push_menu(self, menu_id):
        #Infer context switches and animations and store in history for backward navigation
        if menu_id == self.current_menu_id:
            return None # already on this menu — refresh only, don't grow history
        
        if len(self.history) >= MAX_HISTORY_DEPTH:
            self.history.pop(0)  # drop oldest before appending to stay within cap

        from_ctx = self.active_context
        to_ctx = _MENU_CONTEXT.get(menu_id, from_ctx)  # default to current context if unknown menu_id
        out_anim = self.forward_transition_type(from_ctx, to_ctx)

        self.history.append(UIState.Snapshot(
            self.current_menu_id,
            context=from_ctx,
            seed=self.active_seed,
            wallet=self.active_wallet,
            out_anim=out_anim
        ))
        self.active_context = to_ctx
        self.current_menu_id = menu_id
        return out_anim

    def pop_menu(self):
        if self.history:
            snap = self.history.pop()
            self.current_menu_id = snap.menu_id
            self.active_context = snap.context
            self.active_seed = snap.seed
            self.active_wallet = snap.wallet
            in_anim = self.backward_transition_type(snap.anim)
            return in_anim
        
        # e.g. if pressing "back" often after history got truncated by MAX_HISTORY_DEPTH
        self._set_to_main()
        return None

    def forward_transition_type(self, from_ctx, to_ctx):
        # Forward navigation — animation type determined by destination
        if from_ctx == to_ctx:
            return GUIAnimations.horizontal_slide_in
        if to_ctx == Context.DEVICE:
            return GUIAnimations.horizontal_push_in
        if to_ctx in (Context.ADD_SEED, Context.SEED, Context.ADD_WALLET, Context.WALLET):
            return GUIAnimations.vertical_slide_in
        return None  # fallback: unknown → just appear, no animation


    def backward_transition_type(self, forward_transition_type):
        # Backward navigation — reverse of forward animation
        if forward_transition_type == GUIAnimations.horizontal_slide_in:
            return GUIAnimations.horizontal_slide_out
        if forward_transition_type == GUIAnimations.horizontal_push_in:
            return GUIAnimations.horizontal_push_out
        if forward_transition_type == GUIAnimations.vertical_slide_in:
            return GUIAnimations.vertical_slide_out
        return None  # fallback: just disappear, no animation


    def clear_history(self):
        if len(self.history) > 0 and self.current_menu_id != "main":
            anim = self.backward_transition_type(self.forward_transition_type(Context.MAIN, self.active_context))
        else:
            anim = None
        self.history.clear()
        self._set_to_main()
        return anim

    @property
    def is_run_tour_on_startup(self):
        """Whether the guided tour should run on startup."""
        return self._run_tour_on_startup
    
    def set_tour_completed(self):
        """Mark the tour as completed and persist the state."""
        self._run_tour_on_startup = False
        self._save_tour_state()
    
    def reset_tour_completed(self):
        """Reset tour state to run again on next startup (for testing)."""
        self._run_tour_on_startup = True
        self._save_tour_state()
    
    def _load_tour_state(self):
        """Load tour completion state from config file."""
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                return not config.get("tour_completed", False)
        except OSError:
            # File doesn't exist - first run, show tour
            return True
    
    def _save_tour_state(self):
        """Save tour completion state to config file."""
        config = {"tour_completed": not self._run_tour_on_startup}
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)