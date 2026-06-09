#!/usr/bin/env python3
"""
Style Palette Compiler for Specter UI Theming System

Converts JSON style palette sections in theme JSON files to efficient binary
format for flash storage and reconstructs lv.style_t objects at runtime.

Binary format for the styles section:
  [HEADER 44 bytes]  b"STYL" | version u32le | key_count u32le | name (32)
  [STYLE INDEX]      key_count x 4-byte absolute file offsets (0xFFFFFFFF = absent)
  [STYLE ENTRIES]    for each: op_count u8, then op_count x 3-byte ops
  [LIT DICT header]  b"DICT" | lit_count u16le |
  [LIT INDEX]        lit_count x 2-byte offsets from start of DICT block
  [LIT_ENTRIES]      for each: key (null-terminated UTF-8), value (null-terminated UTF-8)

Each 3-byte op:  prop_id u8 | val_type u8 | index u8

val_type constants:
  0x01 COLOR_PAL  — index into SpecterColorPalette
  0x02 FONT_PAL   — index into SpecterFontPalette
  0x03 STYLE_PAL  — SPECTER_STYLES int value (STYLE_INHERIT op only, prop_id 0xFF)
  0x04 LIT        — index into LIT dict

PROP_ID ranges (device side uses range checks, not a dict):
  0x01-0x0B  COLOR attrs
  0x10       FONT attr (text_font)
  0x20-0x2E  OPA attrs
  0x30-0x58  INT attrs
  0x60-0x69  ENUM attrs
  0x70-0x74  BOOL attrs
  0xFF       STYLE_INHERIT (special)
"""

import struct

if '.' in __name__:
    from .theme_section_compiler import ThemeSectionCompiler
    from ..templates.settings_file_compiler import (
        MAGIC_SIZE, VERSION_SIZE, KEY_COUNT_SIZE, NAME_FIELD_SIZE, HEADER_SIZE, OFFSET_SIZE,
        read_cstring, collect_int_constants
    )
    from .color_palette_compiler import (
        SpecterColorPalette, to_lv_color, shade
    )
    from .font_palette_compiler import SpecterFontPalette
else:
    import sys as _sys, pathlib as _pathlib
    _sys.path.insert(0, str(_pathlib.Path(__file__).parent.parent))
    _sys.path.insert(0, str(_pathlib.Path(__file__).parent))
    from theme_section_compiler import ThemeSectionCompiler
    from templates.settings_file_compiler import (
        MAGIC_SIZE, VERSION_SIZE, KEY_COUNT_SIZE, NAME_FIELD_SIZE, HEADER_SIZE, OFFSET_SIZE,
        read_cstring, collect_int_constants
    )
    from color_palette_compiler import (
        SpecterColorPalette, to_lv_color, shade
    )
    from font_palette_compiler import SpecterFontPalette

try:
    import lvgl as lv
except ImportError:
    lv = None

# ─────────────────────────────────────────────────────────────────────────────
# SPECTER_STYLES — stable integer style-token keys
# ─────────────────────────────────────────────────────────────────────────────

class SPECTER_STYLES:    

    class TEXT:
        DEFAULT = 0    # FONT_TEXT + ON_SURFACE colour
        TITLE   = 1    # FONT_TITLE + ON_SURFACE colour
        SMALL   = 2    # FONT_SMALL + ON_SURFACE colour
        # 3-9 reserved

    class WIDGET:
        BUTTON      = 10
        BUTTON_FLAT = 11   # modifier: strip bg/shadow/border
        TEXT_INPUT  = 12
        PANEL       = 13   # plain container, no decoration
        CARD        = 14   # rounded + padded container
        NAVBAR      = 15
        SCREEN      = 16
        OVERLAY     = 17   # modal dimming layer
        # 18-19 reserved

    class LAYOUT:
        BARE        = 20   # no padding/border/radius, transparent bg
        TRANSPARENT = 21   # bg fully transparent
        INVISIBLE   = 22   # full widget opacity = 0
        SEE_THROUGH = 23   # bg semi-transparent (~70% scrim)
        # 24-29 reserved

    class FG:
        DEFAULT   = 30   # ON_SURFACE (normal text/icon colour)
        SUCCESS   = 31
        WARNING   = 32
        DANGER    = 33
        # 34 reserved (was MUTED — use [FG.DEFAULT, MODIFIER.MUTED] instead)
        HIGHLIGHT = 35   # accent/primary colour, for emphasis
        LIGHT     = 36   # pure white — readable on dark fills
        DARK      = 37   # pure black — readable on light fills
        # 38-39 reserved

    class BG:
        DEFAULT   = 40   # SURFACE (normal background)
        SUCCESS   = 41
        WARNING   = 42
        DANGER    = 43
        # 44 reserved (was MUTED)
        HIGHLIGHT = 45   # accent/primary fill
        LIGHT     = 46   # pure white background
        DARK      = 47   # pure black background
        # 48-49 reserved

    class BORDER:
        TOP    = 50
        BOTTOM = 51
        LEFT   = 52
        RIGHT  = 53
        # 54-59 reserved

    class CONTEXT:
        SEED     = 60
        WALLET   = 61
        MAIN     = 62
        SETTINGS = 63
        # 64-69 reserved

    class SLIDER:
        TRACK     = 70   # apply with lv.PART.MAIN
        INDICATOR = 71   # apply with lv.PART.INDICATOR
        KNOB      = 72   # apply with lv.PART.KNOB
        # 73-79 reserved

    class MODIFIER:
        MUTED = 80   # disabled/unusable widgets



# ─────────────────────────────────────────────────────────────────────────────
# val_type constants
# ─────────────────────────────────────────────────────────────────────────────

VAL_COLOR_PAL = 0x01
VAL_FONT_PAL  = 0x02
VAL_STYLE_PAL = 0x03
VAL_LIT       = 0x04

PROP_STYLE_INHERIT = 0xFF

# ─────────────────────────────────────────────────────────────────────────────
# PROP_ID tables — tuples live in code flash when frozen; no heap for the
# structure itself (only for temporaries during a call).
# ─────────────────────────────────────────────────────────────────────────────

_COLOR_BASE = 0x01
_COLOR_ATTRS = (
    "bg_color",          # 0x01
    "bg_grad_color",     # 0x02
    "text_color",        # 0x03
    "border_color",      # 0x04
    "shadow_color",      # 0x05
    "outline_color",     # 0x06
    "arc_color",         # 0x07
    "line_color",        # 0x08
    "image_recolor",     # 0x09
    "bg_image_recolor",  # 0x0A
    "recolor",           # 0x0B
)

_FONT_BASE = 0x10
# text_font is the only FONT attr; handled directly by range check.

_OPA_BASE = 0x20
_OPA_ATTRS = (
    "bg_opa",                # 0x20
    "bg_grad_opa",           # 0x21
    "bg_main_opa",           # 0x22
    "border_opa",            # 0x23
    "text_opa",              # 0x24
    "shadow_opa",            # 0x25
    "outline_opa",           # 0x26
    "arc_opa",               # 0x27
    "line_opa",              # 0x28
    "image_opa",             # 0x29
    "bg_image_opa",          # 0x2A
    "bg_image_recolor_opa",  # 0x2B
    "opa",                   # 0x2C
    "opa_layered",           # 0x2D
    "color_filter_opa",      # 0x2E
)

_INT_BASE = 0x30
_INT_ATTRS = (
    "border_width",      # 0x30
    "radius",            # 0x31
    "pad_all",           # 0x32
    "pad_top",           # 0x33
    "pad_bottom",        # 0x34
    "pad_left",          # 0x35
    "pad_right",         # 0x36
    "pad_hor",           # 0x37
    "pad_ver",           # 0x38
    "pad_row",           # 0x39
    "pad_column",        # 0x3A
    "pad_gap",           # 0x3B
    "shadow_width",      # 0x3C
    "shadow_spread",     # 0x3D
    "shadow_offset_x",   # 0x3E
    "shadow_offset_y",   # 0x3F
    "outline_width",     # 0x40
    "outline_pad",       # 0x41
    "arc_width",         # 0x42
    "line_width",        # 0x43
    "line_dash_width",   # 0x44
    "line_dash_gap",     # 0x45
    "text_letter_space", # 0x46
    "text_line_space",   # 0x47
    "width",             # 0x48
    "height",            # 0x49
    "min_width",         # 0x4A
    "max_width",         # 0x4B
    "min_height",        # 0x4C
    "max_height",        # 0x4D
    "transform_rotation",# 0x4E
    "transform_scale_x", # 0x4F
    "transform_scale_y", # 0x50
    "transform_skew_x",  # 0x51
    "transform_skew_y",  # 0x52
    "translate_x",       # 0x53
    "translate_y",       # 0x54
    "margin_left",       # 0x55
    "margin_right",      # 0x56
    "margin_top",        # 0x57
    "margin_bottom",     # 0x58
)

_ENUM_BASE = 0x60
_ENUM_ATTRS = (
    "border_side",       # 0x60
    "align",             # 0x61
    "text_align",        # 0x62
    "text_decor",        # 0x63
    "blend_mode",        # 0x64
    "bg_grad_dir",       # 0x65
    "flex_flow",         # 0x66
    "flex_cross_place",  # 0x67
    "flex_main_place",   # 0x68
    "flex_track_place",  # 0x69
)

_BOOL_BASE = 0x70
_BOOL_ATTRS = (
    "arc_rounded",       # 0x70
    "border_post",       # 0x71
    "clip_corner",       # 0x72
    "bg_image_tiled",    # 0x73
    "line_rounded",      # 0x74
)

# Group constants (int, no dict needed)
_GRP_COLOR = 1
_GRP_FONT  = 2
_GRP_OPA   = 3
_GRP_INT   = 4
_GRP_ENUM  = 5
_GRP_BOOL  = 6


# ─────────────────────────────────────────────────────────────────────────────
# Compile-side helpers  (attr_name ↔ prop_id, value encoding)
# Used on PC and optionally on-device with SD card.
# ─────────────────────────────────────────────────────────────────────────────

def _attr_to_prop_id(attr_name):
    """Return (prop_id, group) for *attr_name*, or (None, None) if unsupported."""
    for i, a in enumerate(_COLOR_ATTRS):
        if a == attr_name:
            return (_COLOR_BASE + i, _GRP_COLOR)
    if attr_name == "text_font":
        return (_FONT_BASE, _GRP_FONT)
    for i, a in enumerate(_OPA_ATTRS):
        if a == attr_name:
            return (_OPA_BASE + i, _GRP_OPA)
    for i, a in enumerate(_INT_ATTRS):
        if a == attr_name:
            return (_INT_BASE + i, _GRP_INT)
    for i, a in enumerate(_ENUM_ATTRS):
        if a == attr_name:
            return (_ENUM_BASE + i, _GRP_ENUM)
    for i, a in enumerate(_BOOL_ATTRS):
        if a == attr_name:
            return (_BOOL_BASE + i, _GRP_BOOL)
    return (None, None)


def _color_ref_to_palette_idx(name):
    """Map a colour palette name like 'primary' to SpecterColorPalette int.
    Returns None if unknown."""
    val = getattr(SpecterColorPalette, name.upper(), None)
    if isinstance(val, int):
        return val
    return None


def _font_ref_to_palette_idx(name):
    """Map a font palette name like 'text' to SpecterFontPalette int.
    Returns None if unknown."""
    val = getattr(SpecterFontPalette, name.upper(), None)
    if isinstance(val, int):
        return val
    return None


def _lit_index(lit_builder, s):
    """Return the index of string *s* in *lit_builder*, appending if not present."""
    for i, existing in enumerate(lit_builder):
        if existing == s:
            return i
    idx = len(lit_builder)
    lit_builder.append(s)
    return idx


def _encode_value(attr_name, group, raw_val, lit_builder):
    """Encode one attribute value into (val_type, index) for a 3-byte op.

    *lit_builder* is a list used to accumulate unique LIT strings.
    Returns (val_type, index) tuple or None on error.
    """
    val_str = str(raw_val) if not isinstance(raw_val, str) else raw_val

    if group == _GRP_COLOR:
        if isinstance(raw_val, str) and raw_val.startswith("@"):
            idx = _color_ref_to_palette_idx(raw_val[1:])
            if idx is None:
                print("Warning: unknown color palette ref '{}' for attr '{}'".format(raw_val, attr_name))
                return None
            return (VAL_COLOR_PAL, idx)
        # Everything else (shade(...), #RRGGBB) stored as LIT string
        return (VAL_LIT, _lit_index(lit_builder, val_str))

    if group == _GRP_FONT:
        if isinstance(raw_val, str) and raw_val.startswith("@"):
            idx = _font_ref_to_palette_idx(raw_val[1:])
            if idx is None:
                print("Warning: unknown font palette ref '{}' for attr '{}'".format(raw_val, attr_name))
                return None
            return (VAL_FONT_PAL, idx)
        print("Warning: non-palette font value '{}' for '{}' — skipping".format(raw_val, attr_name))
        return None

    # OPA, INT, ENUM, BOOL — all stored as LIT strings
    return (VAL_LIT, _lit_index(lit_builder, val_str))


# ─────────────────────────────────────────────────────────────────────────────
# Runtime-side helpers (device path — if/elif avoids dict heap allocation)
# ─────────────────────────────────────────────────────────────────────────────

def _group_from_prop_id(prop_id):
    """Return group constant for *prop_id*, or None if unknown."""
    if 0x01 <= prop_id <= 0x0B:
        return _GRP_COLOR
    if prop_id == 0x10:
        return _GRP_FONT
    if 0x20 <= prop_id <= 0x2E:
        return _GRP_OPA
    if 0x30 <= prop_id <= 0x58:
        return _GRP_INT
    if 0x60 <= prop_id <= 0x69:
        return _GRP_ENUM
    if 0x70 <= prop_id <= 0x74:
        return _GRP_BOOL
    return None


def _attr_name_from_prop_id(prop_id):
    """Return the LVGL attribute name for *prop_id*, or None."""
    if 0x01 <= prop_id <= 0x0B:
        return _COLOR_ATTRS[prop_id - _COLOR_BASE]
    if prop_id == 0x10:
        return "text_font"
    if 0x20 <= prop_id <= 0x2E:
        return _OPA_ATTRS[prop_id - _OPA_BASE]
    if 0x30 <= prop_id <= 0x58:
        return _INT_ATTRS[prop_id - _INT_BASE]
    if 0x60 <= prop_id <= 0x69:
        return _ENUM_ATTRS[prop_id - _ENUM_BASE]
    if 0x70 <= prop_id <= 0x74:
        return _BOOL_ATTRS[prop_id - _BOOL_BASE]
    return None


def _resolve_enum(prop_id, value_str):
    """Resolve an ENUM LIT string to its lv constant. Returns None on error."""
    if prop_id == 0x60:
        v = getattr(lv.BORDER_SIDE, value_str, None)
    elif prop_id == 0x61:
        v = getattr(lv.ALIGN, value_str, None)
    elif prop_id == 0x62:
        v = getattr(lv.TEXT_ALIGN, value_str, None)
    elif prop_id == 0x63:
        v = getattr(lv.TEXT_DECOR, value_str, None)
    elif prop_id == 0x64:
        v = getattr(lv.BLEND_MODE, value_str, None)
    elif prop_id == 0x65:
        v = getattr(lv.GRAD_DIR, value_str, None)
    elif prop_id == 0x66:
        v = getattr(lv.FLEX_FLOW, value_str, None)
    elif 0x67 <= prop_id <= 0x69:
        v = getattr(lv.FLEX_ALIGN, value_str, None)
    else:
        v = None
    if v is None:
        print("Warning: unknown ENUM value '{}' for prop_id 0x{:02X}".format(value_str, prop_id))
    return v


def _resolve_shade_expr(expr, context):
    """Parse 'shade(@name, +n)' or 'shade(@name, n)' and return lv.color_t.
    *context* must have get_color(palette_idx) -> lv.color_t.
    Returns None on parse/resolution error."""
    try:
        inner = expr[len("shade("):-1].strip()
        comma = inner.rfind(",")
        if comma < 0:
            print("Warning: malformed shade expression: " + expr)
            return None
        color_tok = inner[:comma].strip()
        level_str = inner[comma + 1:].strip().lstrip("+")
        level = int(level_str)
        if color_tok.startswith("@"):
            palette_idx = _color_ref_to_palette_idx(color_tok[1:])
            if palette_idx is None:
                print("Warning: unknown color ref in shade: " + color_tok)
                return None
            base_color = context.get_color(palette_idx)
            if base_color is None:
                return None
        elif color_tok.startswith("#"):
            base_color = to_lv_color(color_tok)
        else:
            print("Warning: unresolvable color token in shade: " + color_tok)
            return None
        return shade(base_color, level)
    except Exception as e:
        print("Warning: error resolving shade '{}': {}".format(expr, e))
        return None


def _resolve_lit(lit_str, prop_id, context):
    """Resolve a LIT dict string to the correct Python/LVGL value.
    *context* is a ThemeCompiler instance (provides get_color). Returns None on error."""
    group = _group_from_prop_id(prop_id)
    if group == _GRP_COLOR:
        if lit_str.startswith("shade("):
            return _resolve_shade_expr(lit_str, context)
        if lit_str.startswith("#") or lit_str.lower().startswith("0x"):
            return to_lv_color(lit_str)
        print("Warning: unrecognised color literal: " + lit_str)
        return None
    if group == _GRP_OPA:
        if lit_str.lstrip("-").isdigit():
            return int(lit_str)
        v = getattr(lv.OPA, lit_str, None)
        if v is None:
            print("Warning: unknown OPA constant: " + lit_str)
        return v
    if group == _GRP_INT:
        try:
            return int(lit_str)
        except ValueError:
            print("Warning: expected int literal, got: " + lit_str)
            return None
    if group == _GRP_ENUM:
        return _resolve_enum(prop_id, lit_str)
    if group == _GRP_BOOL:
        return lit_str == "true"
    print("Warning: _resolve_lit: unknown group for prop_id 0x{:02X}".format(prop_id))
    return None


# ─────────────────────────────────────────────────────────────────────────────
# LIT dict binary I/O
# ─────────────────────────────────────────────────────────────────────────────

_DICT_MARKER = b"DICT"
_DICT_MARKER_SIZE = 4
_DICT_COUNT_SIZE  = 2
_DICT_ENTRY_OFFSET_SIZE = 2   # per-entry 2-byte offset in LIT index


def _encode_lit_dict(lit_list):
    """Encode *lit_list* into the binary LIT dict block starting with b'DICT'.
    Returns bytearray."""
    count = len(lit_list)
    encoded = [s.encode("utf-8") + b"\x00" for s in lit_list]

    # Offsets are relative to start of b"DICT" block
    header_size = _DICT_MARKER_SIZE + _DICT_COUNT_SIZE + count * _DICT_ENTRY_OFFSET_SIZE
    offsets = []
    pos = header_size
    for enc in encoded:
        offsets.append(pos)
        pos += len(enc)

    buf = bytearray()
    buf.extend(_DICT_MARKER)
    buf.extend(struct.pack("<H", count))
    for off in offsets:
        buf.extend(struct.pack("<H", off))
    for enc in encoded:
        buf.extend(enc)
    return buf


def _open_lit_dict(f):
    """Locate and validate the LIT dict block on file handle *f*.

    Computes the start by walking the style index backwards, then verifies
    the b"DICT" marker and reads the entry count.

    Returns (block_off, count) on success, or (-1, 0) on any error.
    """
    try:
        f.seek(MAGIC_SIZE + VERSION_SIZE)
        style_key_count = struct.unpack("<I", f.read(KEY_COUNT_SIZE))[0]
        style_index_start = HEADER_SIZE
        style_index_end   = style_index_start + style_key_count * OFFSET_SIZE

        block_off = style_index_end   # fallback: all entries absent
        for i in range(style_key_count - 1, -1, -1):
            f.seek(style_index_start + i * OFFSET_SIZE)
            off = struct.unpack("<I", f.read(OFFSET_SIZE))[0]
            if off == 0xFFFFFFFF or off < style_index_end:
                continue
            f.seek(off)
            op_count = struct.unpack("B", f.read(1))[0]
            block_off = off + 1 + op_count * 3
            break

        f.seek(block_off)
        if f.read(_DICT_MARKER_SIZE) != _DICT_MARKER:
            print("Warning: LIT dict marker missing")
            return (-1, 0)
        raw_lit_count = f.read(_DICT_COUNT_SIZE)
        if len(raw_lit_count) < _DICT_COUNT_SIZE:
            print("Warning: truncated LIT dict header")
            return (-1, 0)
        return (block_off, struct.unpack("<H", raw_lit_count)[0])

    except Exception:
        return (-1, 0)


def read_lit_dict_from_binary(file_path):
    """Read and validate the LIT dict block from a styles binary.
    Returns list of strings indexed by LIT index, or [] on error.

    Validation: after reading `_open_lit_dict`, the file handle sits at the
    start of the first string (right after the index table).  Each subsequent
    `_read_cstring` advances it to the start of the next string.  Before
    reading entry i, we compare the current file position with the offset
    declared in the index — a mismatch means a badly written or corrupt entry.
    On mismatch we seek to the declared offset to recover and continue."""
    try:
        with open(file_path, "rb") as f:
            block_off, count = _open_lit_dict(f)
            if block_off < 0:
                print("Warning: could not open LIT dict in " + file_path)
                return []
            f.seek(block_off + _DICT_MARKER_SIZE + _DICT_COUNT_SIZE)
            raw_index = f.read(count * _DICT_ENTRY_OFFSET_SIZE)
            if len(raw_index) < count * _DICT_ENTRY_OFFSET_SIZE:
                print("Warning: LIT index truncated in " + file_path)
                return []
            # File handle now sits at block_off + entry_off_0 (first string).
            result = []
            for i in range(count):
                entry_off = struct.unpack_from("<H", raw_index, i * _DICT_ENTRY_OFFSET_SIZE)[0]
                expected = block_off + entry_off
                actual   = f.tell()
                if actual != expected:
                    print("Warning: LIT entry {} offset mismatch in {} "
                          "(index says {}, file at {}) — seeking to recover".format(
                          i, file_path, expected, actual))
                    f.seek(expected)
                result.append(read_cstring(f))
        return result
    except Exception as e:
        print("Warning: could not read LIT dict from {}: {}".format(file_path, e))
        return []



def key_to_style_index(key_str):
    """Map a theme JSON key string like 'WIDGET.BUTTON' to its SPECTER_STYLES int constant.
    Returns None if the key is not known."""
    parts = key_str.split(".")
    obj = SPECTER_STYLES
    for part in parts:
        obj = getattr(obj, part, None)
        if obj is None:
            return None
    if isinstance(obj, int):
        return obj
    return None


# ─────────────────────────────────────────────────────────────────────────────
# StylePaletteCompiler
# ─────────────────────────────────────────────────────────────────────────────

class StylePaletteCompiler(ThemeSectionCompiler):
    """Compiler for Specter UI style palette."""

    BINARY_FILE_PREFIX = "styles_"
    MAGIC_BYTES = b"STYL"
    SETTINGS_KEY = "styles"
    RECURSIVE_KEYS = True

    def __init__(self):
        # LIT dict accumulator: populated during json_to_binary, cleared after
        self._lit_builder = []

    def convert_setting_to_binary(self, entry):
        """Encode one style dict into binary ops.

        *entry* is a dict: { "style": "@OTHER"|["@A","@B"], "bg_color": ..., ... }
        Returns bytearray: [op_count u8] + [op_count x 3-byte ops].
        """
        if not isinstance(entry, dict):
            print("Warning: style entry is not a dict, skipping")
            return bytearray(b"\x00")

        ops = []

        for key, raw_val in entry.items():
            if key == "style":
                refs = [raw_val] if isinstance(raw_val, str) else list(raw_val)
                for ref in refs:
                    if not isinstance(ref, str) or not ref.startswith("@"):
                        print("Warning: 'style' value must start with '@', got: " + str(ref))
                        continue
                    style_idx = key_to_style_index(ref[1:])
                    if style_idx is None:
                        print("Warning: unknown style ref '{}' — skipping".format(ref))
                        continue
                    if style_idx > 255:
                        print("Warning: style index {} > 255 for '{}' — skipping".format(style_idx, ref))
                        continue
                    ops.append((PROP_STYLE_INHERIT, VAL_STYLE_PAL, style_idx))
                continue

            prop_id, group = _attr_to_prop_id(key)
            if prop_id is None:
                print("Warning: unsupported style attr '{}' — skipping".format(key))
                continue

            result = _encode_value(key, group, raw_val, self._lit_builder)
            if result is None:
                continue
            val_type, index = result
            if index > 255:
                print("Warning: LIT index {} > 255 for '{}' — skipping".format(index, key))
                continue
            ops.append((prop_id, val_type, index))

        if len(ops) > 255:
            print("Warning: style has {} ops, truncating to 255".format(len(ops)))
            ops = ops[:255]

        buf = bytearray()
        buf.append(len(ops))
        for prop_id, val_type, index in ops:
            buf.append(prop_id)
            buf.append(val_type)
            buf.append(index)
        return buf

    def reconstruct_setting_from_binary(self, f):
        """Read raw style ops at the current file position.

        Returns list of (prop_id, val_type, index) tuples, or None on error.
        To build an lv.style_t use read_setting_from_binary(),
        which keeps the file open while applying the ops.
        """
        try:
            raw = f.read(1)
            if not raw:
                print("Warning: unexpected EOF reading style op_count")
                return None
            op_count = raw[0]
            ops_raw = f.read(op_count * 3)
            if len(ops_raw) < op_count * 3:
                print("Warning: truncated style ops data")
                return None
            return [(ops_raw[i*3], ops_raw[i*3+1], ops_raw[i*3+2])
                    for i in range(op_count)]
        except Exception as e:
            print("Warning: reconstruct_setting_from_binary failed: " + str(e))
            return None

    def read_setting_from_binary(self, file_path, style_idx, context=None):
        """Override: build one lv.style_t from a styles binary file.

        *context*: ThemeCompiler providing get_color / get_font.

        Returns (lv.style_t, None) or (None, error_str).
        """
        if context is None:
            return (None, "context_required")
        
        with open(file_path, "rb") as f:
            return self._reconstruct_style_from_handle(f, style_idx, context)

    def _reconstruct_style_from_handle(self, f, style_idx, context, s=None, in_progress=None):
        """Internal: build one lv.style_t from an already-open file handle."""
        if in_progress is None:
            in_progress = set()
        if style_idx in in_progress:
            return (None, "cycle_detected")
        in_progress.add(style_idx)
        try:
            ops, err = self._read_ops_from_handle(f, style_idx)
            if ops is None:
                return (None, err)
            if s is None:
                s = lv.style_t()
                s.init()
            self._apply_ops_to_style(f, ops, s, context, in_progress)
            return (s, None)
        finally:
            in_progress.discard(style_idx)

    def _read_ops_from_handle(self, f, style_index):
        """Internal: read ops from an already-open file handle."""
        try:
            f.seek(0)
            magic = f.read(MAGIC_SIZE)
            if magic != self.MAGIC_BYTES:
                print("Warning: bad magic")
                return (None, "bad_magic")
            f.read(VERSION_SIZE)
            key_count = struct.unpack("<I", f.read(KEY_COUNT_SIZE))[0]

            if style_index < 0 or style_index >= key_count:
                return (None, f"style out of bounds: {style_index}")
            f.seek(HEADER_SIZE + style_index * OFFSET_SIZE)
            entry_off = struct.unpack("<I", f.read(OFFSET_SIZE))[0]
            if entry_off == 0xFFFFFFFF:
                return (None, f"style_not_found_{style_index}")
            f.seek(entry_off)
            result = self.reconstruct_setting_from_binary(f)
            if result is None:
                return (None, f"read_ops_failed_{style_index}")
            return (result, None)
        except Exception:
            return (None, f"_read_ops_failed_{style_index}")

    def _apply_ops_to_style(self, f, ops, s, context, in_progress):
        """Apply a decoded ops list onto lv.style_t *s*.
        STYLE_INHERIT ops are inlined recursively using the open file handle *f*."""
        for prop_id, val_type, index in ops:
            if prop_id == PROP_STYLE_INHERIT:
                self._reconstruct_style_from_handle(f, index, context, s, in_progress)
                continue
            attr_name = _attr_name_from_prop_id(prop_id)
            if attr_name is None:
                print("Warning: unknown prop_id 0x{:02X}".format(prop_id))
                continue
            setter = getattr(s, "set_" + attr_name, None)
            if setter is None:
                print("Warning: lv.style_t has no set_{}".format(attr_name))
                continue
            value = self._resolve_op(f, prop_id, val_type, index, context)
            if value is None:
                print("Warning: could not resolve value for attr '{}'".format(attr_name))
                continue
            try:
                setter(value)
            except Exception as e:
                print("Warning: set_{}({}) failed: {}".format(attr_name, value, e))

    def after_binary_written(self, output_path):
        """Append the accumulated LIT dict to the styles binary file."""
        try:
            lit_block = _encode_lit_dict(self._lit_builder)
            with open(output_path, "ab") as f:
                f.write(lit_block)
            print("  LIT dict: {} unique entries".format(len(self._lit_builder)))
        except Exception as e:
            print("Error: could not write LIT dict to '{}': {}".format(output_path, e))
        finally:
            self._lit_builder = []

    def validate_binary_file(self, binary_path, keys_class=None):
        """Validate structural integrity of styles binary including LIT dict."""
        ok, err = super().validate_binary_file(binary_path, keys_class)
        if not ok:
            return (ok, err)
        lits = read_lit_dict_from_binary(binary_path)
        print("  LIT dict entries: {}".format(len(lits)))
        return (True, None)

    def _read_lit_string_from_handle(self, f, lit_idx):
        """Internal: read one LIT string from an already-open file handle."""
        try:
            block_off, count = _open_lit_dict(f)
            if block_off < 0:
                print("Warning: LIT dict not found")
                return None
            if lit_idx < 0 or lit_idx >= count:
                print("Warning: LIT index {} out of range".format(lit_idx))
                return None
            f.seek(block_off + _DICT_MARKER_SIZE + _DICT_COUNT_SIZE
                   + lit_idx * _DICT_ENTRY_OFFSET_SIZE)
            entry_off = struct.unpack("<H", f.read(_DICT_ENTRY_OFFSET_SIZE))[0]
            f.seek(block_off + entry_off)
            return read_cstring(f)
        except Exception as e:
            print("Warning: _read_lit_string_from_handle failed: " + str(e))
            return None

    def _resolve_op(self, f, prop_id, val_type, index, context):
        """Resolve one op value using *context* for palette refs and *f* for LIT reads."""
        if val_type == VAL_COLOR_PAL:
            return context.get_color(index)
        if val_type == VAL_FONT_PAL:
            return context.get_font(index)
        if val_type == VAL_LIT:
            lit_str = self._read_lit_string_from_handle(f, index)
            if lit_str is None:
                return None
            return _resolve_lit(lit_str, prop_id, context)
        print("Warning: unknown val_type 0x{:02X}".format(val_type))
        return None


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    StylePaletteCompiler().main()


if __name__ == "__main__":
    main()