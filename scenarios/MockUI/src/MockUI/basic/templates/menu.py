import lvgl as lv
from .titled_screen import TitledScreen
from ..utils import (
    BTN_HEIGHT, BTN_WIDTH,
    SWITCH_HEIGHT,
    CONTENT_H, TITLE_HEIGHT,
    delete_all_children_of, style_as_flex_container,
    set_size, set_pos, set_scroll, set_align,
    AUTO_GROW_MENU_BUTTONS
)
from ..symbol_lib import Icon, BTC_ICONS
from ..theming import apply_style
from ..widgets import (
    button_modal, 
    Btn, 
    body_label, menu_label, section_header, 
    flex_row,
    make_icon, make_switch
)


class GenericMenu(TitledScreen):
    """Reusable menu builder — template method pattern.

    Subclasses override the three hooks:
        get_title(t, state)      -> str          title shown at the top
        get_menu_items(t, state) -> list         list of MenuItems; will be used to create the actual menu
        pre_init(t, state)       -> None         called before menu items are built (optional)
        post_init(t, state)      -> None         called after all LVGL widgets are built (optional)
    """

    def __init__(self, parent):
        # TitledScreen sets self.gui, self.device_state, self.ui_state, self.i18n, self.on_navigate, self.body, etc.
        super().__init__("", parent)

        if self.title:
            title = self.get_title(self.t, self.device_state)
            self.title.set_text(title)

        self.fill_body()

    def refresh(self):
        # Delegate to TitledScreen (updates battery, context bar, etc.)
        super().refresh()

    def fill_body(self):
        style_as_flex_container(self.body, width=lv.pct(100), height=CONTENT_H-TITLE_HEIGHT, scrollable=True)
        menu_items = self.get_menu_items(self.t, self.device_state)
        self.pre_init(self.t, self.device_state)
        self._build_menu_items(menu_items)
        self.post_init(self.t, self.device_state)
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
        row = flex_row(self.body, width=lv.pct(100), main_align=lv.FLEX_ALIGN.START)
        apply_style(row, "WIDGET.MENU_SECTION_HEADER")

        if item.icon and isinstance(item.icon, Icon):
            row.ico = make_icon(row, item.icon)
            apply_style(row.ico, "WIDGET.MENU_ICON")

            if item.modifier == "Danger":
                apply_style(row.ico, "FG.DANGER")
            elif item.modifier == "Warning":
                apply_style(row.ico, "FG.WARNING")
            elif item.modifier == "Highlight":
                apply_style(row.ico, "FG.HIGHLIGHT")

        row.lbl = section_header(row, item.text)
        row.lbl.set_flex_grow(1)
        if item.modifier == "Danger":
            apply_style(row.lbl, "FG.DANGER")
        elif item.modifier == "Warning":
            apply_style(row.lbl, "FG.WARNING")
        elif item.modifier == "Highlight":
            apply_style(row.lbl, "FG.HIGHLIGHT")

        return row

    def _build_toggle_select_row(self, item):
        """Switch row: icon + label + optional help + lv.switch wired to get/set_value."""
        row = flex_row(self.body, width=lv.pct(100), height=SWITCH_HEIGHT, main_align=lv.FLEX_ALIGN.START)
        apply_style(row, "WIDGET.MENU_SWITCH")
        if item.icon and isinstance(item.icon, Icon):
            row.ico = make_icon(row, item.icon)
            apply_style(row.ico, "WIDGET.MENU_ICON")
        row.lbl = menu_label(row, item.text, width=None)
        row.lbl.set_flex_grow(1)
        if item.help_key:
            row.h_btn = self._add_help_btn(row, item.text, item.help_key)
        
        current_value = item.get_value() if callable(item.get_value) else item.get_value
        def setter_cb(is_on):
            if callable(item.set_value):
                item.set_value(is_on)
            else:
                item.set_value = is_on
            self.gui.refresh_ui()

        row.switch = make_switch(row, init_value=current_value, setter_cb=setter_cb)

        return row

    def _build_button_row(self, item):
        """Full menu button: icon + text + right-side suffixes/help/caret."""
        # Normalize size: default to 1, ensure minimum of 1
        size = item.height_scaling if item.height_scaling and item.height_scaling >= 1 else 1

        btn = Btn(self.body,
                  text=item.text,
                  size=(BTN_WIDTH, int(BTN_HEIGHT*size)),
                  background_style="WIDGET.MENU_BUTTON",
                  foreground_style="WIDGET.MENU_BUTTON_FG",
                )
        if AUTO_GROW_MENU_BUTTONS:
            btn.set_flex_grow(int(size*10))

        if item.modifier == "Danger":
            btn.apply_style(background_style="BG.DANGER")
        elif item.modifier == "Warning":
            btn.apply_style(background_style="BG.WARNING")
        elif item.modifier == "Highlight":
            btn.apply_style(background_style="BG.HIGHLIGHT")

        if item.icon:
            btn.ico = make_icon(btn, item.icon)
            apply_style(btn.ico, "WIDGET.MENU_ICON")

        # Right-side container: [suffixes...] [help?] [caret — always reserved]
        btn.right_cont = flex_row(
            btn,
            width=lv.SIZE_CONTENT,
            height=lv.pct(100),
            main_align=lv.FLEX_ALIGN.START,
        )
        btn.right_cont.remove_flag(lv.obj.FLAG.CLICKABLE)
        btn.right_cont.suf = []
        for suf in (item.suffix or []):
            if suf.icon is not None:
                ico = make_icon(btn.right_cont, suf.icon)
                apply_style(ico, "WIDGET.INFO_ITEM")
                btn.right_cont.suf.append(ico)
            if suf.text is not None:
                lbl = body_label(btn.right_cont, suf.text, width=lv.SIZE_CONTENT)
                apply_style(lbl, ["WIDGET.INFO_ITEM", "TEXT.SMALL"])
                btn.right_cont.suf.append(lbl)

        if item.help_key:
            btn.right_cont.h_btn = self._add_help_btn(btn.right_cont, item.text, item.help_key)

        if item.is_submenu:
            btn.right_cont.sub_men_ind = make_icon(btn.right_cont, BTC_ICONS.CARET_RIGHT)
            apply_style(btn.right_cont.sub_men_ind, "WIDGET.SUBMENU_INDICATOR")        

        set_align(btn.right_cont, lv.ALIGN.RIGHT_MID)

        btn_click_cb = None
        if callable(item.target):
            # If it's already a callable, use it directly
            btn_click_cb = item.target
        else:
            # Otherwise, it's a string menu_id - create navigation callback
            btn_click_cb = lambda e, target=item.target: self.on_navigate(target)

        btn.add_event_cb(btn_click_cb, lv.EVENT.CLICKED, None)
        return btn
    
    def _add_help_btn(self, parent, item_text, help_key):
        h_btn = Btn(parent, 
                    icon=BTC_ICONS.QUESTION_CIRCLE,
                    background_style="APPEARANCE.TRANSPARENT",
                    foreground_style="WIDGET.HELP_ICON",
                )
        help_text = item_text + "\n" + self.t(help_key)
        def _on_help_click(e):
            e.stop_bubbling = 1
            button_modal(text=help_text)
        h_btn.add_event_cb(_on_help_click, lv.EVENT.CLICKED, None)
        return h_btn
        
    # --- template-method hooks -------------------------------------------

    TITLE_KEY = None  # set in subclass to avoid overriding get_title

    def get_title(self, t, state):
        """Return the menu title string. Override in subclasses, or just set TITLE_KEY."""
        return t(self.TITLE_KEY) if self.TITLE_KEY else ""

    def get_menu_items(self, t, state):
        """Return the list of MenuItems."""
        return []

    def pre_init(self, t, state):
        """Called before menu items are built. Override to insert widgets above the item list."""
        pass

    def post_init(self, t, state):
        """Called after all LVGL widgets are built. Override for post-construction work."""
        pass
