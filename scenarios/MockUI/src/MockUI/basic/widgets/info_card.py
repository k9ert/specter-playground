"""InfoCard -- shared base widget for information cards."""

import lvgl as lv

from .btn import Btn
from .inputs import make_textarea
from .labels import make_label, optimize_font_size
from ..symbol_lib import BTC_ICONS
from ..templates.specter_gui_base import SpecterGuiElement
from ..theming import apply_style, get_style
from ..utils import apply_click_feedback, set_scroll


class InfoCard(SpecterGuiElement):
    """Shared behavior for selectable information cards.

    Owners should call :meth:`optimize_name_font` once after the layout pass that
    resolves a non-editable name widget's bounds.
    """

    def __init__(self, parent, on_card_click=None):
        super().__init__(parent)
        apply_style(self, "CONTAINER.INFO_CARD")
        set_scroll(self, horizontal=False, vertical=False)

        self.text_edit = None
        if on_card_click is not None:
            apply_click_feedback(self)
            self.add_event_cb(on_card_click, lv.EVENT.CLICKED, None)

    def _add_name_slot(self, label, on_name_click=None):
        """Append a growing name label or editable name field."""
        if on_name_click is not None:
            self.name_widget = make_textarea(self)
            apply_style(self.name_widget, "TEXT.TITLE")
            self.name_widget.set_text(label)
            self.name_widget.add_event_cb(
                lambda event: on_name_click(self.name_widget),
                lv.EVENT.CLICKED,
                None)
            self.text_edit = self.name_widget
        else:
            self.name_widget = make_label(
                self,
                label,
                styles=[get_style("WIDGET.MENU_BUTTON", role="FG"),
                        "TEXT.TITLE", "TEXT.LEFT"])

        apply_style(self.name_widget, "LAYOUT.GROWS")

    def _add_delete_slot(self, on_delete):
        """Append a delete button that does not trigger the card click handler."""
        return Btn(
            self,
            icon=BTC_ICONS.TRASH,
            style="WIDGET.ICON_BUTTON",
            callback=on_delete,
            consume_click=True)

    def optimize_name_font(self):
        """Lock the settled name box and fit its text once.

        This is an owner-facing hook. Call only after the card's owner has
        completed the layout pass that resolves the name widget's bounds.
        """
        if self.text_edit is None:
            optimize_font_size(self.name_widget)