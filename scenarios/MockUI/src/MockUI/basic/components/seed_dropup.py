"""SeedDropUp — bottom-sheet overlay listing all loaded seeds."""

from ..widgets import MenuItem, SeedCard, button_modal
from ..ui_state import Context
from ..templates.dropup import DropUp
from ..theming import apply_style
from .confirm_modals import confirm_delete_seed


class SeedDropUp(DropUp):
    """Drop-up overlay listing all loaded seeds with passphrase + edit buttons."""

    def _get_items(self):
        return self.device_state.loaded_seeds

    def _add_button_label(self):
        return self.t("MENU_ADD_SEED")

    def _navigate_add(self):
        self.on_navigate("add_seed", target_seed=None)

    def _build_card(self, panel, seed, width):
        card = SeedCard(
            panel, seed,
            width=width,
            slots=("name", "backup_warning", "passphrase", "fingerprint", "delete"),
            on_card_click=self._make_on_row_click_cb(seed,
                                            Context.SEED,
                                            "active_seed",
                                            "set_active_seed",
                                            "manage_seedphrase",
                                            "target_seed"),
            on_backup_warning=lambda: self._on_backup_warning(seed),
            on_delete=lambda: self._on_delete_seed(seed),
        )
        apply_style(card, ["CONTAINER.DROP_UP_ROW", "CONTEXT.SEED"])
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

    def _do_delete_seed(self, seed):
        self.device_state.remove_seed(seed)
        if self.ui_state.active_seed is seed:
            self.ui_state.active_seed = None
        if not self.device_state.loaded_seeds:
            self.close()
            self.on_navigate("main")
        else:
            self.gui.refresh_ui()

    def _on_delete_seed(self, seed):
        confirm_delete_seed(self.t, seed.label, lambda: self._do_delete_seed(seed))
