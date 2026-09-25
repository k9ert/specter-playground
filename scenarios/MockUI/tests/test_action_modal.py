from types import SimpleNamespace

import pytest

import MockUI.basic.templates.specter_gui_base as specter_gui_base
import MockUI.basic.widgets.action_modal as action_modal_module


@pytest.mark.parametrize("buttons", [None, []])
def test_button_modal_default_button_uses_translated_close_label(
        monkeypatch, buttons):
    labels = []

    class _Element:
        def __init__(self, parent):
            self.parent = parent

    class _Button:
        def __init__(self, *args, **kwargs):
            labels.append(kwargs["text"])

    translations = {"MODAL_CLOSE_BTN": "Schließen"}
    gui = SimpleNamespace(i18n=SimpleNamespace(t=translations.__getitem__))
    monkeypatch.setattr(specter_gui_base, "_gui_instance", gui)
    monkeypatch.setattr(
        action_modal_module, "_action_modal",
        lambda text, title=None, parent=None: [object(), _Element(None)])
    monkeypatch.setattr(action_modal_module, "SpecterGuiElement", _Element)
    monkeypatch.setattr(action_modal_module, "Btn", _Button)
    monkeypatch.setattr(action_modal_module, "apply_style", lambda *args: None)

    action_modal_module.button_modal("Body", buttons=buttons)

    assert labels == ["Schließen"]
