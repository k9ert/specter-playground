import lvgl as lv
from .ui_consts import BTN_HEIGHT, BTN_WIDTH, MENU_PCT, PAD_SIZE
from .symbol_lib import Icon, BTC_ICONS


class GenericMenu(lv.obj):
    """Reusable menu builder.

    title: string title shown at top
    menu_items: list of (icon, text, target_behavior, color) where:
        - icon: Icon object or lv.SYMBOL string
        - text: Display text for the menu item
        - target_behavior: None (creates label/spacer), string (menu_id to navigate to), or callable (custom callback)
        - color: Optional color for the button
    """

    def __init__(self, menu_id, title, menu_items, parent, *args, **kwargs):
        # parent is the NavigationController (not necessarily the LVGL parent)
        # attach to parent's `content` container when available so the status bar stays visible
        lv_parent = getattr(parent, "content", parent)
        super().__init__(lv_parent, *args, **kwargs)
        # discover navigation callback and shared state from parent
        self.on_navigate = parent.on_navigate
        # optional shared state object (SpecterState) is stored on parent
        self.state = parent.specter_state
        # identifier for this menu (used e.g. as a return target)
        self.menu_id = menu_id

        # Fill parent
        self.set_width(lv.pct(100))
        self.set_height(lv.pct(100))
        # Remove padding from base menu object to allow full-width content
        self.set_style_pad_all(0, 0)
        # Remove border
        self.set_style_border_width(0, 0)

        # If ui_state has history, show back button to the left of the title
        if parent.ui_state and parent.ui_state.history and len(parent.ui_state.history) > 0:
            self.back_btn = lv.button(self)
            self.back_btn.set_size(40, 28)
            self.back_ico = lv.image(self.back_btn)
            BTC_ICONS.CARET_LEFT.add_to_parent(self.back_ico)
            self.back_ico.center()
            # wire back to navigation callback: wrap handler in a lambda so the
            # LVGL binding's argument passing doesn't mismatch the method signature.
            self.back_btn.add_event_cb(lambda e: self.on_back(e), lv.EVENT.CLICKED, None)

        # Title
        self.title = lv.label(self)
        self.title.set_text(title)
        self.title.set_style_text_align(lv.TEXT_ALIGN.CENTER, 0)
        # reduce vertical space used by the title; center remains but offset horizontally
        self.title.align(lv.ALIGN.TOP_MID, 0, 6)

        # Container for buttons
        self.container = lv.obj(self)
        self.container.set_width(lv.pct(100))
        self.container.set_height(lv.pct(MENU_PCT))
        self.container.set_layout(lv.LAYOUT.FLEX)
        self.container.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.container.set_flex_align(lv.FLEX_ALIGN.START, lv.FLEX_ALIGN.CENTER, lv.FLEX_ALIGN.CENTER)
        self.container.set_style_pad_all(PAD_SIZE, 0)
        self.container.set_style_border_width(0, 0)
        # smaller gap between title and container
        self.container.align_to(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, PAD_SIZE)

        # Build items
        for icon, text, target_behavior, color in menu_items:
            if target_behavior is None:
                spacer = lv.label(self.container)
                spacer.set_recolor(True)
                spacer.set_text(text or "")
                spacer.set_width(lv.pct(BTN_WIDTH))
                spacer.set_style_text_align(lv.TEXT_ALIGN.LEFT, 0)
            else:
                btn = lv.button(self.container)
                btn.set_width(lv.pct(BTN_WIDTH))
                btn.set_height(BTN_HEIGHT)
                if color:
                    btn.set_style_bg_color(color, lv.PART.MAIN)
                
                if icon:
                    # Check if icon is an Icon (includes ColoredIcon subclass)
                    if isinstance(icon, Icon):
                        icon_img = lv.image(btn)
                        icon.add_to_parent(icon_img)
                        icon_img.align(lv.ALIGN.LEFT_MID, 8, 0)
                    else:
                        # Traditional string icon (lv.SYMBOL.*)
                        ico = lv.label(btn)
                        ico.set_recolor(True)
                        ico.set_text(icon or "")
                        ico.align(lv.ALIGN.LEFT_MID, 8, 0)
  
                # Add text label centered
                lbl = lv.label(btn)
                lbl.set_recolor(True)
                lbl.set_text(text)
                lbl.center()

                btn.add_event_cb(self.make_callback(target_behavior), lv.EVENT.CLICKED, None)

    def make_callback(self, target_behavior):
        """Create callback for button - handles both string menu_ids and custom callables."""
        # If it's already a callable, return it directly
        if callable(target_behavior):
            return target_behavior
        
        # Otherwise, it's a string menu_id - create navigation callback
        def callback(e):
            if e.get_code() == lv.EVENT.CLICKED:
                if not self.on_navigate:
                    return
                if target_behavior == "back":
                    self.on_navigate(None)
                else:
                    self.on_navigate(target_behavior)
        return callback

    def on_back(self, e):
        self.on_navigate(None)
