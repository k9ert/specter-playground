"""Shared confirmation modals for destructive actions."""

from ..widgets import slider_confirm_modal
from ..symbol_lib import BTC_ICONS

def confirm_delete_seed(t, label, on_confirm):
    """Show the 'Delete seed?' SliderConfirmModal.

    Args:
        t:          Translation callable (``gui.i18n.t``).
        label:      Seed display name (used in the modal text).
        on_confirm: Zero-argument callable invoked when the user confirms.
    """
    slider_confirm_modal(
        text=t("MODAL_DELETE_SEED_TEXT") % label,
        on_confirm=on_confirm,
        confirm_style="BG.DANGER",
        confirm_icon=BTC_ICONS.TRASH,
        on_reject=None,
        reject_style="BG.SUCCESS",
        reject_icon=BTC_ICONS.CARET_LEFT,
    )


def confirm_delete_wallet(t, label, on_confirm):
    """Show the 'Delete wallet?' SliderConfirmModal.

    Args:
        t:          Translation callable (``gui.i18n.t``).
        label:      Wallet display name (used in the modal text).
        on_confirm: Zero-argument callable invoked when the user confirms.
    """
    slider_confirm_modal(
        text=t("MODAL_DELETE_WALLET_TEXT") % label,
        on_confirm=on_confirm,
        confirm_style="BG.DANGER",
        confirm_icon=BTC_ICONS.TRASH,
        on_reject=None,
        reject_style="BG.SUCCESS",
        reject_icon=BTC_ICONS.CARET_LEFT,
    )


def make_delete_active_handler(menu, t, confirm_fn, attr, delete_method):
    """Build a title-bar trash callback for deleting the active entity.

    Confirms via *confirm_fn*, delegates deletion and UI cleanup to the
    corresponding ``SpecterGui`` helper, and returns to the main menu.

    Args:
        menu:          The GenericMenu instance owning the title-bar button.
        t:             Translation callable.
        confirm_fn:    Modal function ``confirm_delete_*(t, label, on_confirm)``.
        attr:          Name of the ui_state attribute holding the active entity.
        delete_method: Name of the ``SpecterGui`` deletion helper.
    """
    def _on_delete(e=None):
        entity = getattr(menu.ui_state, attr)

        def _do_delete():
            getattr(menu.gui, delete_method)(entity)
            # navigate_to("main") clears history, updates current_menu_id and
            # triggers the exit animation / refresh in one go.
            menu.on_navigate("main")

        confirm_fn(t, entity.label, _do_delete)

    return _on_delete
