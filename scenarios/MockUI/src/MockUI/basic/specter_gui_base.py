"""specter_gui_base — GUI context access helpers.

Two classes are provided so each consumer picks the right base:

``SpecterGuiMixin``
    Pure-Python base.  Provides ``device_state``/``ui_state``/``i18n``/``t``/``on_navigate`` as
    properties resolved from ``self.gui``.  Use for controllers that are not
    LVGL widgets.

``SpecterGuiElement``
    ``lv.obj`` subclass with the same properties.  Use for concrete LVGL
    widgets (``TitledScreen``, ``NavigationBar``, …).

MicroPython does not support multiple inheritance, so the property set is
installed onto both classes via the ``_install_gui_properties`` helper rather
than being declared twice.
"""
import lvgl as lv


def _install_gui_properties(cls):
    """Install the shared ``self.gui``-derived properties on *cls*.

    Each entry maps an attribute name on *cls* to a single-argument function
    that, given the instance, returns the resolved value.  The properties are
    intentionally read-only (no setter) — consumers mutate the underlying
    ``self.gui`` / ``self.gui.ui_state`` objects directly.
    """
    accessors = {
        "device_state":     lambda self: self.gui.device_state,
        "ui_state":         lambda self: self.gui.ui_state,
        "current_menu":     lambda self: self.gui.ui_state.current_menu_id,
        "context":          lambda self: self.gui.ui_state.active_context,
        "active_seed":      lambda self: self.gui.ui_state.active_seed,
        "active_wallet":    lambda self: self.gui.ui_state.active_wallet,
        "i18n":             lambda self: self.gui.i18n,
        "t":                lambda self: self.gui.i18n.t,
        "on_navigate":      lambda self: self.gui.on_navigate,
        "keyboard_manager": lambda self: self.gui.keyboard_manager,
    }
    for name, fn in accessors.items():
        setattr(cls, name, property(fn))
    return cls


class SpecterGuiMixin:
    """Pure-Python base: properties resolved from ``self.gui``.

    Properties are installed by ``_install_gui_properties`` below.  Use this
    base for controllers that are not LVGL widgets.
    """

    def refresh(self):
        pass  # optional helper for non-LVGL controllers to trigger a UI refresh after changing state


_install_gui_properties(SpecterGuiMixin)


class SpecterGuiElement(lv.obj):
    """``lv.obj`` subclass: same ``self.gui``-derived properties as ``SpecterGuiMixin``.

    Properties are installed by ``_install_gui_properties`` below.  Use this
    base for concrete LVGL widgets (``TitledScreen``, ``NavigationBar``, …).
    MicroPython lacks multiple inheritance, so the property set is applied
    independently to both classes rather than inherited from a common base.
    """

    def refresh(self):
        pass  # optional helper for LVGL components to trigger a UI refresh after changing state


_install_gui_properties(SpecterGuiElement)
