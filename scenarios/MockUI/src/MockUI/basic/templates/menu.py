import lvgl as lv
from .titled_screen import TitledScreen
from .specter_gui_base import SpecterGuiElement, t
from ..utils import delete_all_children_of, set_size, AUTO_GROW_MENU_BUTTONS
from ..symbol_lib import Icon, BTC_ICONS
from ..theming import apply_style
from ..widgets import (
    button_modal, 
    Btn, 
    make_label, make_icon, make_switch
)


class GenericMenu(TitledScreen):
    """Reusable menu builder — template method pattern.

    Subclasses override the three hooks:
        get_title(self)          -> str          title shown at the top
        get_menu_items(self)     -> list         list of MenuItems; will be used to create the actual menu
        pre_itemlist(self)       -> None         optional hook to insert widgets above the menu items
        post_itemlist(self)      -> None         optional hook to insert widgets below the menu items
    """

    # --- template-method hooks /START-------------------------------------------
    TITLE_KEY = None  # set in subclass to avoid overriding get_title. Use KEY for i18n.t

    def get_title(self):
        """Return the menu title string. Override in subclasses, or just set TITLE_KEY."""
        return t(self.TITLE_KEY) if self.TITLE_KEY else ""

    def get_menu_items(self):
        """Return the list of MenuItems."""
        return []

    def pre_itemlist(self):
        """Called before menu items are built. Override to insert widgets above the item list."""
        pass

    def post_itemlist(self):
        """Called after all LVGL widgets are built. Override for post-construction work."""
        pass
    # --- template-method hooks /END---------------------------------------------

    def __init__(self, parent):
        # Hand no title to TitledScreen just yet (i18n not ready to resolve the title key yet)
        # Title will be resolved later in setup_self
        super().__init__("", parent)

    def setup_self(self):
        super().setup_self()  # applies CONTAINER.TITLED_SCREEN
        if self.show_title:
            self.title = self.get_title()

    def post_init(self):
        #super will make title label with stored title
        super().post_init()
        apply_style(self.body, "CONTAINER.MENU_CONTAINER")
        #now create all the menu items
        self.fill_body()

    def refresh(self):
        # Delegate to TitledScreen (updates battery, context bar, etc.)
        super().refresh()

    def fill_body(self):
        menu_items = self.get_menu_items()
        self.pre_itemlist()
        self._build_menu_items(menu_items)
        self.post_itemlist()
        # make sure to enable scrolling when necessary
        self._configure_scroll()

    def rebuild_body(self):
        delete_all_children_of(self.body)
        self.fill_body()

    def _build_menu_items(self, menu_items):
        self.body.rows=[];

        """Dispatch each MenuItem to the appropriate row builder."""
        for item in menu_items:
            if item.target is None and (item.get_value is None or item.set_value is None):
                row = self._build_section_title_row(item)
            elif item.get_value is not None and item.set_value is not None:
                row = self._build_toggle_select_row(item)
            else:
                row = self._build_button_row(item)
            self.body.rows.append(row)

    def _build_section_title_row(self, item):
        """Section header row: optional icon + bold/coloured heading label."""
        row = SpecterGuiElement(self.body)
        apply_style(row, "CONTAINER.MENU_ROW")

        if item.icon and isinstance(item.icon, Icon):
            row.ico = make_icon(row, item.icon)
            apply_style(row.ico, "WIDGET.MENU_ICON")

            if item.modifier == "Danger":
                apply_style(row.ico, "FG.DANGER")
            elif item.modifier == "Warning":
                apply_style(row.ico, "FG.WARNING")
            elif item.modifier == "Highlight":
                apply_style(row.ico, "FG.HIGHLIGHT")

        row.lbl = make_label(row, item.text)
        apply_style(row.lbl, "WIDGET.MENU_SECTION_HEADER")
        if item.modifier == "Danger":
            apply_style(row.lbl, "FG.DANGER")
        elif item.modifier == "Warning":
            apply_style(row.lbl, "FG.WARNING")
        elif item.modifier == "Highlight":
            apply_style(row.lbl, "FG.HIGHLIGHT")

        return row

    def _build_toggle_select_row(self, item):
        """Switch row: icon + label + optional help + lv.switch wired to get/set_value."""
        row = SpecterGuiElement(self.body)
        apply_style(row, "CONTAINER.MENU_ROW")

        if item.icon and isinstance(item.icon, Icon):
            row.ico = make_icon(row, item.icon)
            apply_style(row.ico, "WIDGET.MENU_ICON")
        row.lbl = make_label(row, item.text)
        apply_style(row.lbl, ["WIDGET.MENU_BUTTON_FG", "LAYOUT.GROWS"])
        if item.help_key:
            row.h_btn = self._add_help_btn(row, item.text, item.help_key)
        
        current_value = item.get_value() if callable(item.get_value) else item.get_value
        def setter_cb(is_on):
            if callable(item.set_value):
                item.set_value(is_on)
            self.gui.refresh_ui()

        row.switch = make_switch(row, init_value=current_value, setter_cb=setter_cb)
        apply_style(row.switch, "WIDGET.MENU_SWITCH")
        return row

    def _build_button_row(self, item):
        """Full menu button: icon + text + right-side suffixes/help/caret."""
        # Normalize size: default to 1, ensure minimum of 1
        size = item.height_scaling if item.height_scaling and item.height_scaling >= 1 else 1

        if callable(item.target):
            # If it's already a callable, use it directly
            btn_click_cb = item.target
        else:
            # Otherwise, it's a string menu_id - create navigation callback
            btn_click_cb = lambda target=item.target: self.on_navigate(target)

        btn = Btn(self.body,
                  callback=btn_click_cb,
                  background_style="WIDGET.MENU_BUTTON")
                
        if AUTO_GROW_MENU_BUTTONS:
            btn.set_flex_grow(int(size*10))
            set_size(btn._btn, height=lv.pct(100))

        if item.modifier == "Danger":
            btn.apply_style(background_style="BG.DANGER")
        elif item.modifier == "Warning":
            btn.apply_style(background_style="BG.WARNING")
        elif item.modifier == "Highlight":
            btn.apply_style(background_style="BG.HIGHLIGHT")

        # Build children in visual left-to-right order
        if item.icon:
            btn.ico = make_icon(btn._btn, item.icon)
            apply_style(btn.ico, "WIDGET.MENU_ICON")

        btn.lbl = make_label(btn._btn, item.text)
        apply_style(btn.lbl, "WIDGET.MENU_LABEL")

        # Right-side container: [suffixes...] [help?]
        btn.right_cont = SpecterGuiElement(btn._btn)
        apply_style(btn.right_cont, "CONTAINER.MENU_BUTTON_RHS")
        btn.right_cont.remove_flag(lv.obj.FLAG.CLICKABLE)
        
        btn.right_cont.suf = []
        for suf in (item.suffix or []):
            if suf.icon is not None:
                ico = make_icon(btn.right_cont, suf.icon)
                apply_style(ico, "WIDGET.INFO_ITEM")
                btn.right_cont.suf.append(ico)
            if suf.text is not None:
                lbl = make_label(btn.right_cont, suf.text)
                apply_style(lbl, "WIDGET.INFO_ITEM")
                btn.right_cont.suf.append(lbl)

        if item.help_key:
            btn.right_cont.h_btn = self._add_help_btn(btn.right_cont, item.text, item.help_key)

        #Submenu indicator (caret) to indicate this button leads to a submenu
        #always added, only visible if is_submenu is True [to make menu appearence homogeneous]
        btn.sub_men_ind = make_icon(btn._btn, BTC_ICONS.CARET_RIGHT)
        apply_style(btn.sub_men_ind, "WIDGET.SUBMENU_INDICATOR")
        if not item.is_submenu:
            apply_style(btn.sub_men_ind, "APPEARANCE.INVISIBLE")

        return btn
    
    def _add_help_btn(self, parent, item_text, help_key):

        help_text = item_text + "\n\n" + self.t(help_key)

        h_btn = Btn(parent, 
                    icon=BTC_ICONS.QUESTION_CIRCLE,
                    callback=lambda: button_modal(text=help_text),
                    consume_click=True,
                    background_style="APPEARANCE.TRANSPARENT",
                    foreground_style="WIDGET.HELP_ICON",
                )
        return h_btn
