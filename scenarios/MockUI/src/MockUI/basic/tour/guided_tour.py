"""Guided tour for first-time users.

Provides a step-by-step introduction to the Specter hardware wallet UI,
highlighting key interface elements and explaining their purpose.
"""

from .ui_explainer import UIExplainer
from ..utils.generic_utils import resolve_obj

# Static tour step definitions: (element_spec, i18n_key, position)
# element_spec is None or a dotted attribute-path string.
#       None: create tour text window in center of screen (no highlight)
#       str: resolve at runtime to a UI element (e.g. "navigation_bar")
#            name has to be relative to gui
# Resolved to runtime objects by GuidedTour.resolve_steps() before use.
INTRO_TOUR_STEPS = [
    (None,                                                  "TOUR_INTRO",          "center"),
    ("navigation_bar",                                      "TOUR_WALLET_BAR",     "above"),
    ("app_screen.view.body.rows[1].right_cont.h_btn",       "TOUR_HELP_ICON",      "left"),
]


class GuidedTour:
    """Manages the startup guided tour.
    
    The tour highlights key UI elements and provides explanations for new users.
    It runs once on first startup or when retriggered and can be dismissed or completed.
    
    Acts as the central controller - UIExplainer delegates navigation back here.
    
    Usage:
        steps = GuidedTour.resolve_steps(SpecterGui.INTRO_TOUR_STEPS, nav)
        tour = GuidedTour(nav, steps)
        tour.start()
    """
    
    def __init__(self, nav_controller, steps):
        """Initialize the tour with a SpecterGui and resolved steps.

        Args:
            nav_controller: The SpecterGui instance (must be fully constructed)
            steps: List of (element, text, position) tuples already resolved at runtime.
        """
        self.nav = nav_controller
        self.steps = steps
        self.current_index = 0
        self.current_explainer = None
    
    def start(self):
        """Show the first step of the tour."""
        self.current_index = 0
        self._show_current()

    @staticmethod
    def resolve_steps(static_steps, nav):
        """Pre-process a static step definition list.

        Translates i18n keys eagerly (text is stable). 
        Element specs that are strings are kept as-is and resolved lazily at 
        show-time via ``_resolve_element``, because screen-dependent paths (e.g.
        ``app_screen.view.body.rows[1]``) are only valid while that screen is active.

        Returns a list of (element_spec, translated_text, position) tuples.
        """
        resolved = []
        for element_spec, key, position in static_steps:
            if element_spec is not None and not isinstance(element_spec, str):
                raise TypeError(
                    "Invalid element_spec {!r}: expected None, tuple, or str".format(element_spec)
                )
            text = nav.i18n.t(key)
            resolved.append((element_spec, text, position))
        return resolved

    def _resolve_element(self, element_spec):
        """Resolve a single element_spec to a runtime object (called at show-time)."""
        if element_spec is None:
            return None
        # string path — resolve against nav now (current screen is live)
        element = resolve_obj(element_spec, self.nav)
        if element is None:
            #if element cannot be resolved, log a warning and return None 
            # (tour step will show centered without highlight)
            print(f"Could not resolve element_spec '{element_spec}'")
        return element
    
    def is_first(self):
        """Return True if currently on the first step."""
        return self.current_index == 0
    
    def is_last(self):
        """Return True if currently on the last step."""
        return self.current_index >= len(self.steps) - 1
    
    def prev(self):
        """Navigate to the previous step."""
        if not self.is_first():
            self.current_explainer.hide()
            self.current_index -= 1
            self._show_current()
    
    def next(self):
        """Navigate to the next step."""
        if not self.is_last():
            self.current_explainer.hide()
            self.current_index += 1
            self._show_current()
    
    def skip(self):
        """End the tour (skip or complete)."""
        self.current_explainer.hide()
        self.current_explainer = None
        self.nav.ui_state.set_tour_completed()
    
    def _show_current(self):
        """Show the current step."""
        element_spec, text, position = self.steps[self.current_index]
        element = self._resolve_element(element_spec)
        self.current_explainer = UIExplainer(self, element, text, position)
        self.current_explainer.show()
