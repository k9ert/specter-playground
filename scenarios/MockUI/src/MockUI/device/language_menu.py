import lvgl as lv
from ..basic import GenericMenu


class LanguageMenu(GenericMenu):
    def __init__(self, parent):
        # Get available languages from i18n manager
        self.parent = parent
        available_langs = parent.i18n.get_available_languages()
        current_lang = parent.i18n.get_language()
        
        # Get translation function from i18n manager
        t = parent.i18n.t

        # Build menu items with custom callbacks for language selection
        menu_items = []
        
        for lang_code in available_langs:
            label = parent.i18n.get_language_name(lang_code)
            # Add checkmark for currently selected language
            if lang_code == current_lang:
                symbol = lv.SYMBOL.OK
            else:
                symbol = None

            # Pass a callback function instead of a string
            menu_items.append((symbol, label, lambda e, lc=lang_code: self._on_language_selected(e, lc), None))
        
        # Add "Load new language" option (uses default string navigation)
        menu_items.append((lv.SYMBOL.DOWNLOAD, t("MENU_LOAD_NEW_LANGUAGE"), "load_language", None))
        
        # Call GenericMenu constructor
        super().__init__(
            "select_language",
            parent.i18n.t("MENU_LANGUAGE"),
            menu_items,
            parent
        )
    
    def _on_language_selected(self, e, lang_code):
        """Handle language selection: change language and go back."""
        if e.get_code() == lv.EVENT.CLICKED:
            self.parent.change_language(lang_code)
            self.parent.on_navigate(None)
