"""specter_gui_base — GUI context access helpers.

Two classes are provided so each consumer picks the right base:

``SpecterGuiMixin``
    Pure-Python base.  Provides ``device_state``/``ui_state``/``i18n``/``t``/``on_navigate`` as
    properties resolved from ``self.gui``.  Use for controllers that are not
    LVGL widgets.

``SpecterGuiElement``
    ``lv.obj`` subclass with the same properties.  Use for concrete LVGL
    widgets (``TitledScreen``, ``NavigationBar``, …).

MicroPython does not support multiple inheritance, so both classes define the
same properties independently.
"""
import lvgl as lv


def delete_all_children_of(widget):
    for i in reversed(range(widget.get_child_count())):
        widget.get_child(i).delete()


def configure_as_bare(obj, width=None, height=None):
    """Zero padding, border, and radius on an existing lv.obj (mutating).
    """
    if width is not None:
        obj.set_width(width)
    if height is not None:
        obj.set_height(height)
    obj.set_style_pad_all(0, 0)
    obj.set_style_border_width(0, 0)
    obj.set_style_radius(0, 0)


class SpecterGuiMixin:
    """Pure-Python base: ``device_state``, ``ui_state``, ``i18n``, ``t``, ``on_navigate`` from ``self.gui``."""

    @property
    def device_state(self):
        return self.gui.device_state

    @property
    def ui_state(self):
        return self.gui.ui_state
    
    @property
    def current_menu(self):
        return self.gui.ui_state.current_menu_id

    @property
    def context(self):
        return self.gui.ui_state.active_context
    
    @property
    def active_seed(self):
        return self.gui.ui_state.active_seed
    
    @property
    def active_wallet(self):
        return self.gui.ui_state.active_wallet

    @property
    def i18n(self):
        return self.gui.i18n

    @property
    def t(self):
        return self.gui.i18n.t

    @property
    def on_navigate(self):
        return self.gui.on_navigate

    def refresh(self):
        pass  # optional helper for non-LVGL controllers to trigger a UI refresh after changing state

class SpecterGuiElement(lv.obj):
    """``lv.obj`` subclass: ``device_state``, ``ui_state``, ``i18n``, ``t``, ``on_navigate`` from ``self.gui``."""

    @property
    def device_state(self):
        return self.gui.device_state

    @property
    def ui_state(self):
        return self.gui.ui_state
    
    @property
    def current_menu(self):
        return self.gui.ui_state.current_menu_id

    @property
    def context(self):
        return self.gui.ui_state.active_context
    
    @property
    def active_seed(self):
        return self.gui.ui_state.active_seed
    
    @property
    def active_wallet(self):
        return self.gui.ui_state.active_wallet

    @property
    def i18n(self):
        return self.gui.i18n

    @property
    def t(self):
        return self.gui.i18n.t

    @property
    def on_navigate(self):
        return self.gui.on_navigate
    
    def refresh(self):
        pass  # optional helper for LVGL components to trigger a UI refresh after changing state
