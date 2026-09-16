import MockUI.basic.widgets.labels as labels


class _Label:
    def __init__(self):
        self.calls = []

    def get_width(self):
        return 180

    def get_height(self):
        return 42

    def get_text(self):
        return "Long wallet name"

    def set_width(self, width):
        self.calls.append(("width", width))

    def set_height(self, height):
        self.calls.append(("height", height))

    def set_text(self, text):
        self.calls.append(("text", text))

    def set_style_text_font(self, font, part):
        self.calls.append(("font", font, part))


def test_optimize_font_size_locks_resolved_bounds_before_changing_text_or_font(
        monkeypatch):
    label = _Label()
    chosen_font = object()
    fitted = []

    def choose_font(text, width, height):
        fitted.append((text, width, height))
        return "TEXT", "Long\nwallet name"

    monkeypatch.setattr(labels, "best_fonttype_for_size", choose_font)
    monkeypatch.setattr(labels, "get_font", lambda key: (chosen_font, None))

    labels.optimize_font_size(label)

    assert fitted == [("Long wallet name", 180, 42)]
    assert label.calls == [
        ("width", 180),
        ("height", 42),
        ("text", "Long\nwallet name"),
        ("font", chosen_font, 0),
    ]