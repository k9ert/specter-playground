"""Guided tour for first-time users.

Provides a step-by-step introduction to the Specter hardware wallet UI,
highlighting key interface elements and explaining their purpose.
"""

from .ui_explainer import UIExplainer

# Static tour step definitions: (element_spec, i18n_key, position)
# element_spec is None, a dotted attribute-path string, or a (x, y, w, h) tuple.
# Resolved to runtime objects by GuidedTour.resolve_steps() before use.
INTRO_TOUR_STEPS = [
    (None,                          "TOUR_INTRO",       "center"),
    ("navigation_bar",              "TOUR_WALLET_BAR",  "above"),
    ((435, 143, 28, 28),            "TOUR_HELP_ICON",   "left"),
]


class GuidedTour:
    """Manages the startup guided tour.
    
    The tour highlights key UI elements and provides explanations for new users.
    It runs once on first startup and can be dismissed or completed.
    
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
        """Resolve a static step definition list into a runtime steps list.

        Each entry in static_steps is (element_spec, i18n_key, position) where
        element_spec is one of:
          - None                  -> no highlight (full-screen overlay)
          - (x, y, w, h) tuple   -> manual screen coordinates, passed through
          - "attr.path" string    -> resolved via getattr chain on nav

        Returns a list of (element, translated_text, position) tuples.
        """
        resolved = []
        for element_spec, key, position in static_steps:
            if element_spec is None:
                element = None
            elif isinstance(element_spec, tuple):
                if len(element_spec) != 4 or not all(isinstance(v, (int, float)) for v in element_spec):
                    raise ValueError(
                        "element_spec tuple must be (x, y, w, h) with 4 numeric values, got {!r}".format(element_spec)
                    )
                element = element_spec
            elif isinstance(element_spec, str):
                # Resolve dotted attribute path on nav (e.g. "device_bar.lock_btn")
                element = nav
                for part in element_spec.split("."):
                    element = getattr(element, part)
            else:
                raise TypeError(
                    "Invalid element_spec {!r}: expected None, tuple, or str".format(element_spec)
                )
            text = nav.i18n.t(key)
            resolved.append((element, text, position))
        return resolved
    
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
        element, text, position = self.steps[self.current_index]
        self.current_explainer = UIExplainer(self, element, text, position)
        self.current_explainer.show()
