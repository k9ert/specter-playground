"""SeedDropUp — bottom-sheet overlay showing the seed hierarchy."""

from ..widgets import MenuItem, SeedCard, button_modal
from ..ui_state import Context
from ..templates.dropup import DropUp
from ..theming import apply_style
from .confirm_modals import confirm_delete_seed


class SeedDropUp(DropUp):
    """Drop-up overlay rendering the collapsible seed hierarchy."""

    EXPANSION_CONTEXT = Context.SEED

    def _get_selectable_items(self):
        return self.device_state.get_sorted_loaded_seeds()

    def _delete_from_gui(self, seed):
        self.gui.delete_seed(seed)

    def _get_item_children(self, seed):
        # Mock discovery until real BIP85 derivation records exist.
        return seed.known_bip85_derivations(self.device_state.loaded_seeds)

    def _get_item_key(self, seed):
        return seed.get_fingerprint()

    def _add_button_label(self):
        return self.t("MENU_ADD_SEED")

    def _navigate_add(self):
        self.on_navigate("add_seed", target_seed=None)

    def _build_card(self, row, seed):
        card = SeedCard(
            row, seed,
            slots=("name", "backup_warning", "passphrase", "fingerprint", "delete"),
            on_card_click=self._make_on_row_click_cb(seed,
                                            Context.SEED,
                                            "active_seed",
                                            "set_active_seed",
                                            "manage_seedphrase",
                                            "target_seed"),
            on_backup_warning=lambda: self._on_backup_warning(seed),
            on_delete=lambda: confirm_delete_seed(
                self.t, seed.label, lambda: self._delete_item(seed)),
        )
        apply_style(card, "CONTEXT.SEED")
        return card

    def _on_backup_warning(self, seed):
        def _mark_backed_up():
            seed.is_backed_up = True
            self.gui.refresh_ui()
            
        button_modal(
            text=self.t("MODAL_BACKUP_WARNING_TEXT"),
            buttons=[
                MenuItem(icon=None, text=self.t("MODAL_BACKUP_CONFIRMED_BTN"), target=_mark_backed_up),
                MenuItem(text=self.t("COMMON_OK")),
            ],
        )

