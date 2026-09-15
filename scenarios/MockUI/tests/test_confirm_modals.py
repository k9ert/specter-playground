from types import SimpleNamespace

from MockUI.basic.components.confirm_modals import make_delete_active_handler


def test_delete_active_handler_uses_the_gui_deletion_helper():
    seed = SimpleNamespace(label="Seed")
    calls = []

    class Gui:
        def delete_seed(self, item):
            calls.append(("delete_seed", item))

    class Menu:
        gui = Gui()
        ui_state = SimpleNamespace(active_seed=seed)

        def on_navigate(self, target):
            calls.append(("navigate", target))

    def confirm(t, label, on_confirm):
        calls.append(("confirm", label))
        on_confirm()

    handler = make_delete_active_handler(
        Menu(), None, confirm, "active_seed", "delete_seed")
    handler()

    assert calls == [
        ("confirm", "Seed"),
        ("delete_seed", seed),
        ("navigate", "main"),
    ]