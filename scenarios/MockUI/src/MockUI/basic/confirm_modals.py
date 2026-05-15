"""Shared confirmation modals for destructive actions."""

from .widgets.action_modal import ActionModal
from .symbol_lib import BTC_ICONS
from .ui_consts import RED_HEX


def _confirm_delete(t, title_text, on_confirm):
    ActionModal(
        text=title_text,
        buttons=[
            (None,            t("COMMON_CANCEL"), None,    None),
            (BTC_ICONS.TRASH, t("COMMON_DELETE"), RED_HEX, on_confirm),
        ],
    )


def confirm_delete_seed(t, label, on_confirm):
    """Show the 'Delete seed?' ActionModal.

    Args:
        t:          Translation callable (``gui.i18n.t``).
        label:      Seed display name (used in the modal text).
        on_confirm: Zero-argument callable invoked when the user confirms.
    """
    _confirm_delete(t, t("MODAL_DELETE_SEED_TEXT") % label, on_confirm)


def confirm_delete_wallet(t, label, on_confirm):
    """Show the 'Delete wallet?' ActionModal.

    Args:
        t:          Translation callable (``gui.i18n.t``).
        label:      Wallet display name (used in the modal text).
        on_confirm: Zero-argument callable invoked when the user confirms.
    """
    _confirm_delete(t, t("MODAL_DELETE_WALLET_TEXT") % label, on_confirm)
