"""font_manager.py — descriptor-based font resolver for the Specter MockUI.

A *font descriptor* is a ``"family:size"`` string (e.g. ``"montserrat:22"``) or a
``(family, size)`` tuple.  :class:`FontManager` resolves a descriptor to a
concrete ``lv.font`` object:

1. **Cache** — keyed by ``(resolved_family, size)``; each font is created once.
2. **Builtin first** — ``lv.font_montserrat_<size>`` when available.
3. **`.bin` file** — loaded as *data* via ``lv.binfont_create_from_buffer`` from
   the font directory (``/flash/fonts`` on device or the bundled dir in the
   simulator).  This is the same trust model the i18n framework uses: fonts are
   data, never executed code.
4. **Nearest fallback** — the closest already-resolvable size.

Language-aware families
------------------------
Some languages need extended glyphs (e.g. German umlauts).  The active language
selects a *family variant*: ``set_language("de")`` makes the logical family
``"montserrat"`` resolve to the umlaut-enabled ``montserrat_<size>_de.bin`` set.
Themes therefore stay language-agnostic — they ask for ``"montserrat:22"`` and
get the right variant for the active language automatically.

This module folds in the former ``font_loader_de`` (German umlaut loader): the
``montserrat`` family with language ``"de"`` loads exactly those ``.bin`` files.
"""

import lvgl as lv

# Montserrat sizes shipped as builtins in this MicroPython/LVGL build.
_BUILTIN_MONTSERRAT = (8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28)
# Roboto Mono sizes compiled into the udisplay_f469 usermod.
_BUILTIN_ROBOTO_MONO = (12, 16, 22, 28)
# Unscii sizes compiled as LVGL builtins.
_BUILTIN_UNSCII = (8, 16)


class FontManager:
    """Resolves + caches fonts by descriptor; language-aware family variants."""

    def __init__(self):
        self._cache = {}        # (family, size) -> lv.font
        self._language = "en"
        # Directory holding *.bin fonts (the de umlaut set lives next to this file).
        self._font_dir = __file__.rsplit("/", 1)[0] if "/" in __file__ else "."

    # ── language / family resolution ──────────────────────────────────────
    def set_language(self, lang):
        """Select the active language; affects which family variant is used."""
        self._language = lang or "en"

    def _resolve_family(self, family):
        """Map a logical *family* to a language-specific variant when needed."""
        if family == "montserrat" and self._language == "de":
            return "montserrat_de"
        return family

    # ── public API ────────────────────────────────────────────────────────
    def get_font(self, descriptor):
        """Return the ``lv.font`` for *descriptor* (``"family:size"`` or tuple)."""
        family, size = self._parse(descriptor)
        family = self._resolve_family(family)
        key = (family, size)
        if key in self._cache:
            return self._cache[key]
        font = self._load(family, size)
        if font is None:
            font = self._fallback(family, size)
        self._cache[key] = font
        return font

    # ── internals ─────────────────────────────────────────────────────────
    @staticmethod
    def _parse(descriptor):
        if isinstance(descriptor, (tuple, list)):
            return descriptor[0], int(descriptor[1])
        family, _, size = descriptor.partition(":")
        return family, int(size)

    def _load(self, family, size):
        """Try builtin, then a ``.bin`` file; return None if neither works."""
        # Builtin Montserrat (only the plain, language-neutral family).
        if family == "montserrat" and size in _BUILTIN_MONTSERRAT:
            font = getattr(lv, "font_montserrat_%d" % size, None)
            if font is not None:
                return font
        # Builtin Roboto Mono (compiled into udisplay_f469 usermod).
        if family == "roboto_mono" and size in _BUILTIN_ROBOTO_MONO:
            font = getattr(lv, "font_roboto_mono_%d" % size, None)
            if font is not None:
                return font
        # Builtin Unscii.
        if family == "unscii" and size in _BUILTIN_UNSCII:
            font = getattr(lv, "font_unscii_%d" % size, None)
            if font is not None:
                return font
        # .bin file: <family>_<size>.bin (e.g. montserrat_de -> montserrat_<size>_de.bin)
        path = self._bin_path(family, size)
        try:
            with open(path, "rb") as f:
                data = f.read()
            return lv.binfont_create_from_buffer(data, len(data))
        except Exception:
            return None

    def _bin_path(self, family, size):
        # The German umlaut set is named montserrat_<size>_de.bin.
        if family == "montserrat_de":
            return "%s/montserrat_%d_de.bin" % (self._font_dir, size)
        return "%s/%s_%d.bin" % (self._font_dir, family, size)

    def _fallback(self, family, size):
        """Resolve the nearest available size for *family* (never returns None)."""
        # Pick the builtin set matching the requested family, fall back to montserrat.
        if family == "roboto_mono":
            candidates = [("roboto_mono", s, "font_roboto_mono_%d" % s) for s in _BUILTIN_ROBOTO_MONO]
        elif family == "unscii":
            candidates = [("unscii", s, "font_unscii_%d" % s) for s in _BUILTIN_UNSCII]
        else:
            candidates = [("montserrat", s, "font_montserrat_%d" % s) for s in _BUILTIN_MONTSERRAT]

        best = None
        for _, s, attr in candidates:
            font = getattr(lv, attr, None)
            if font is None:
                continue
            if best is None or abs(s - size) < abs(best[0] - size):
                best = (s, font)
        if best is not None:
            return best[1]
        # Last resort: LVGL's default font.
        return lv.font_montserrat_16


# Global singleton shared by the theme framework and (future) i18n font hooks.
font_manager = FontManager()
