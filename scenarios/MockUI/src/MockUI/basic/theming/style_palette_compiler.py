#!/usr/bin/env python3
"""
Style Palette Compiler for Specter UI Theming System

Converts JSON style palette sections in theme JSON files to efficient binary
format for flash storage and reconstructs lv.style_t objects at runtime.

Binary format for the styles section:
  [HEADER 44 bytes]  b"STYL" | version u32le | key_count u32le | name (32)
  [STYLE INDEX]      key_count x 4-byte absolute file offsets (0xFFFFFFFF = absent)
  [STYLE ENTRIES]    one entry per key — either a leaf or a role container (below)
  [LIT DICT header]  b"DICT" | lit_count u16le |
  [LIT INDEX]        lit_count x 2-byte offsets from start of DICT block
  [LIT_ENTRIES]      for each: key (null-terminated UTF-8), value (null-terminated UTF-8)

STYLE ENTRIES
-------------

The high bit of an entry's first byte selects the framing (0 = leaf, 1 = role
container); the remaining 7 bits are op_count / role_count respectively, so a
style is capped at MAX_OPS = 127 ops.

A style's properties are encoded as a list of 3-byte ops:
  op =  prop_id u8 | val_type u8 | index u8

  Leaf (0):
    byte0     op_count (high bit 0)
    ops       op_count x 3-byte op

  Container (1) — a style and its roles in one entry:
    byte0     0x80 | role_count
    table     role_count x { role_code u8 | offset u16le }   (sorted by role_code)
    styles    role_count style bodies, inline, each = [op_count u8][ops]

  role_code   a StyleRole u8; MAIN (0) is the style's own body.
  offset      a role style's byte position relative to the entry start — read
              by seeking entry_start + offset, without parsing other roles.

val_type constants:
  0x01 COLOR_PAL  — index into SpecterColorPalette
  0x02 FONT_PAL   — index into SpecterFontPalette
  0x03 STYLE_PAL  — SPECTER_STYLES int value (STYLE_INHERIT op only, prop_id 0xFF)
  0x04 LIT        — index into LIT dict
  0x05 ARRAY      — index = array length N; next N ops are elements (same 3-byte format)

PROP_ID ranges (device side uses range checks, not a dict):
  0x01-0x1F  COLOR attrs  (31 slots)
  0x20       FONT attr    (text_font)
  0x40-0x5F  OPA attrs    (32 slots)
  0x60-0x9F  INT attrs    (64 slots)
  0xA0-0xBF  ENUM attrs   (32 slots)
  0xC0-0xCF  BOOL attrs   (16 slots)
  0xD0-0xDF  ARRAY attrs  (16 slots, e.g. grid track descriptors)
  0xFF       STYLE_INHERIT (special)

INT attrs accept special string values:
  "SIZE_CONTENT"  — resolves to lv.SIZE_CONTENT
  "pct(N)"        — resolves to lv.pct(N)
  "FR(N)"         — resolves to lv.grid_fr(N) (grid track descriptors)
"""

import struct

if '.' in __name__:
    from .theme_section_compiler import ThemeSectionCompiler
    from .theme_schema import (
        SpecterStylePalette, SpecterColorPalette, SpecterFontPalette, StyleRole,
    )
    from ..templates.settings_file_compiler import (
        MAGIC_SIZE, VERSION_SIZE, KEY_COUNT_SIZE, HEADER_SIZE, OFFSET_SIZE,
        read_cstring, collect_int_constants
    )
    from .color_palette_compiler import to_lv_color, shade, color_ref_to_palette_idx
    from .font_palette_compiler import font_ref_to_palette_idx
    from ..utils.generic_utils import resolve_obj
else:
    import sys as _sys, pathlib as _pathlib
    _sys.path.insert(0, str(_pathlib.Path(__file__).parent.parent / "templates"))
    _sys.path.insert(0, str(_pathlib.Path(__file__).parent.parent / "utils"))
    _sys.path.insert(0, str(_pathlib.Path(__file__).parent))
    from theme_section_compiler import ThemeSectionCompiler
    from theme_schema import (
        SpecterStylePalette, SpecterColorPalette, SpecterFontPalette, StyleRole,
    )
    from settings_file_compiler import (
        MAGIC_SIZE, VERSION_SIZE, KEY_COUNT_SIZE, HEADER_SIZE, OFFSET_SIZE,
        read_cstring, collect_int_constants
    )
    from color_palette_compiler import to_lv_color, shade, color_ref_to_palette_idx
    from font_palette_compiler import font_ref_to_palette_idx
    from generic_utils import resolve_obj

try:
    import lvgl as lv
except ImportError:
    lv = None

# ─────────────────────────────────────────────────────────────────────────────
# val_type constants
# ─────────────────────────────────────────────────────────────────────────────

VAL_COLOR_PAL = 0x01
VAL_FONT_PAL  = 0x02
VAL_STYLE_PAL = 0x03
VAL_LIT       = 0x04
VAL_ARRAY     = 0x05

PROP_STYLE_INHERIT = 0xFF

# ─────────────────────────────────────────────────────────────────────────────
# PROP_ID tables — tuples live in code flash when frozen; no heap for the
# structure itself (only for temporaries during a call).
#
# Ranges are spaced generously to allow future expansion without breaking.
# ─────────────────────────────────────────────────────────────────────────────

_COLOR_BASE = 0x01
_COLOR_ATTRS = (
    "bg_color",                    # 0x01
    "bg_grad_color",               # 0x02
    "text_color",                  # 0x03
    "border_color",                # 0x04
    "shadow_color",                # 0x05
    "outline_color",               # 0x06
    "arc_color",                   # 0x07
    "line_color",                  # 0x08
    "image_recolor",               # 0x09
    "bg_image_recolor",            # 0x0A
    "recolor",                     # 0x0B
    "text_outline_stroke_color",   # 0x0C
)

_FONT_BASE = 0x20
# text_font is the only FONT attr; handled directly by range check.

_OPA_BASE = 0x40
_OPA_ATTRS = (
    "bg_opa",                # 0x40
    "bg_grad_opa",           # 0x41
    "bg_main_opa",           # 0x42
    "border_opa",            # 0x43
    "text_opa",              # 0x44
    "shadow_opa",            # 0x45
    "outline_opa",           # 0x46
    "arc_opa",               # 0x47
    "line_opa",              # 0x48
    "image_opa",             # 0x49
    "bg_image_opa",          # 0x4A
    "bg_image_recolor_opa",  # 0x4B
    "opa",                   # 0x4C
    "opa_layered",           # 0x4D
    "color_filter_opa",      # 0x4E
    "text_outline_stroke_opa",  # 0x4F
)

_INT_BASE = 0x60
_INT_ATTRS = (
    "border_width",          # 0x60
    "radius",                # 0x61
    "pad_all",               # 0x62
    "pad_top",               # 0x63
    "pad_bottom",            # 0x64
    "pad_left",              # 0x65
    "pad_right",             # 0x66
    "pad_hor",               # 0x67
    "pad_ver",               # 0x68
    "pad_row",               # 0x69
    "pad_column",            # 0x6A
    "pad_gap",               # 0x6B
    "pad_radial",            # 0x6C
    "shadow_width",          # 0x6D
    "shadow_spread",         # 0x6E
    "shadow_offset_x",       # 0x6F
    "shadow_offset_y",       # 0x70
    "outline_width",         # 0x71
    "outline_pad",           # 0x72
    "arc_width",             # 0x73
    "line_width",            # 0x74
    "line_dash_width",       # 0x75
    "line_dash_gap",         # 0x76
    "text_letter_space",     # 0x77
    "text_line_space",       # 0x78
    "text_outline_stroke_width",  # 0x79
    "width",                 # 0x7A
    "height",                # 0x7B
    "min_width",             # 0x7C
    "max_width",             # 0x7D
    "min_height",            # 0x7E
    "max_height",            # 0x7F
    "transform_rotation",    # 0x80
    "transform_scale_x",     # 0x81
    "transform_scale_y",     # 0x82
    "transform_skew_x",      # 0x83
    "transform_skew_y",      # 0x84
    "translate_x",           # 0x85
    "translate_y",           # 0x86
    "margin_left",           # 0x87
    "margin_right",          # 0x88
    "margin_top",            # 0x89
    "margin_bottom",         # 0x8A
    "x",                     # 0x8B
    "y",                     # 0x8C
    "flex_grow",             # 0x8D
    "grid_cell_column_pos",  # 0x8E
    "grid_cell_row_pos",     # 0x8F
    "grid_cell_column_span", # 0x90
    "grid_cell_row_span",    # 0x91
    "anim_duration",         # 0x92
)

_ENUM_BASE = 0xA0
_ENUM_ATTRS = (
    "border_side",           # 0xA0
    "align",                 # 0xA1
    "text_align",            # 0xA2
    "text_decor",            # 0xA3
    "blend_mode",            # 0xA4
    "bg_grad_dir",           # 0xA5
    "flex_flow",             # 0xA6
    "flex_cross_place",      # 0xA7
    "flex_main_place",       # 0xA8
    "flex_track_place",      # 0xA9
    "layout",                # 0xAA
    "base_dir",              # 0xAB
    "grid_column_align",     # 0xAC
    "grid_row_align",        # 0xAD
    "grid_cell_x_align",     # 0xAE
    "grid_cell_y_align",     # 0xAF
)

_BOOL_BASE = 0xC0
_BOOL_ATTRS = (
    "arc_rounded",           # 0xC0
    "border_post",           # 0xC1
    "clip_corner",           # 0xC2
    "bg_image_tiled",        # 0xC3
    "line_rounded",          # 0xC4
)

_ARRAY_BASE = 0xD0
_ARRAY_ATTRS = (
    "grid_column_dsc_array", # 0xD0
    "grid_row_dsc_array",    # 0xD1
)

# Group constants (int, no dict needed)
_GRP_COLOR = 1
_GRP_FONT  = 2
_GRP_OPA   = 3
_GRP_INT   = 4
_GRP_ENUM  = 5
_GRP_BOOL  = 6
_GRP_ARRAY = 7


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
    for i, a in enumerate(_ARRAY_ATTRS):
        if a == attr_name:
            return (_ARRAY_BASE + i, _GRP_ARRAY)
    return (None, None)

def style_ref_to_palette_idx(name):
    """Map a style palette name like 'WIDGET.BUTTON' to SpecterStylePalette int.
    Returns None if unknown."""
    result = resolve_obj(name, SpecterStylePalette)
    if result is None:
        print("Warning: unknown style palette ref '{}'".format(name))
        return None
    if isinstance(result, int):
        return result

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
    For ARRAY group, returns list of (val_type, index) tuples for elements.
    """
    val_str = str(raw_val) if not isinstance(raw_val, str) else raw_val

    if group == _GRP_COLOR:
        if isinstance(raw_val, str) and raw_val.startswith("@"):
            idx = color_ref_to_palette_idx(raw_val[1:])
            if idx is None:
                print("Warning: unknown color palette ref '{}' for attr '{}'".format(raw_val, attr_name))
                return None
            return (VAL_COLOR_PAL, idx)
        # Everything else (shade(...), #RRGGBB) stored as LIT string
        return (VAL_LIT, _lit_index(lit_builder, val_str))

    if group == _GRP_FONT:
        if isinstance(raw_val, str) and raw_val.startswith("@"):
            idx = font_ref_to_palette_idx(raw_val[1:])
            if idx is None:
                print("Warning: unknown font palette ref '{}' for attr '{}'".format(raw_val, attr_name))
                return None
            return (VAL_FONT_PAL, idx)
        print("Warning: non-palette font value '{}' for '{}' — skipping".format(raw_val, attr_name))
        return None

    if group == _GRP_ARRAY:
        if not isinstance(raw_val, list):
            print("Warning: ARRAY attr '{}' requires a list value, got: {}".format(attr_name, type(raw_val).__name__))
            return None
        if len(raw_val) > 255:
            print("Warning: ARRAY attr '{}' has {} elements, max 255".format(attr_name, len(raw_val)))
            return None
        # Return a list of (val_type, index) for each element
        elements = []
        for elem in raw_val:
            elem_str = str(elem) if not isinstance(elem, str) else elem
            elements.append((VAL_LIT, _lit_index(lit_builder, elem_str)))
        return elements

    # OPA, INT, ENUM, BOOL — all stored as LIT strings
    return (VAL_LIT, _lit_index(lit_builder, val_str))


# ─────────────────────────────────────────────────────────────────────────────
# Runtime-side helpers (device path — if/elif avoids dict heap allocation)
# ─────────────────────────────────────────────────────────────────────────────

def _prop_id_to_group(prop_id):
    """Return group constant for *prop_id*, or None if unknown."""
    if 0x01 <= prop_id <= 0x1F:
        return _GRP_COLOR
    if prop_id == 0x20:
        return _GRP_FONT
    if 0x40 <= prop_id <= 0x5F:
        return _GRP_OPA
    if 0x60 <= prop_id <= 0x9F:
        return _GRP_INT
    if 0xA0 <= prop_id <= 0xBF:
        return _GRP_ENUM
    if 0xC0 <= prop_id <= 0xCF:
        return _GRP_BOOL
    if 0xD0 <= prop_id <= 0xDF:
        return _GRP_ARRAY
    return None


def _prop_id_to_attr_name(prop_id):
    """Return the LVGL attribute name for *prop_id*, or None."""
    if 0x01 <= prop_id <= 0x1F:
        idx = prop_id - _COLOR_BASE
        return _COLOR_ATTRS[idx] if idx < len(_COLOR_ATTRS) else None
    if prop_id == 0x20:
        return "text_font"
    if 0x40 <= prop_id <= 0x5F:
        idx = prop_id - _OPA_BASE
        return _OPA_ATTRS[idx] if idx < len(_OPA_ATTRS) else None
    if 0x60 <= prop_id <= 0x9F:
        idx = prop_id - _INT_BASE
        return _INT_ATTRS[idx] if idx < len(_INT_ATTRS) else None
    if 0xA0 <= prop_id <= 0xBF:
        idx = prop_id - _ENUM_BASE
        return _ENUM_ATTRS[idx] if idx < len(_ENUM_ATTRS) else None
    if 0xC0 <= prop_id <= 0xCF:
        idx = prop_id - _BOOL_BASE
        return _BOOL_ATTRS[idx] if idx < len(_BOOL_ATTRS) else None
    if 0xD0 <= prop_id <= 0xDF:
        idx = prop_id - _ARRAY_BASE
        return _ARRAY_ATTRS[idx] if idx < len(_ARRAY_ATTRS) else None
    return None


def _resolve_enum(prop_id, value_str):
    """Resolve an ENUM LIT string to its lv constant. Returns None on error."""
    if prop_id == 0xA0:
        v = getattr(lv.BORDER_SIDE, value_str, None)
    elif prop_id == 0xA1:
        v = getattr(lv.ALIGN, value_str, None)
    elif prop_id == 0xA2:
        v = getattr(lv.TEXT_ALIGN, value_str, None)
    elif prop_id == 0xA3:
        v = getattr(lv.TEXT_DECOR, value_str, None)
    elif prop_id == 0xA4:
        v = getattr(lv.BLEND_MODE, value_str, None)
    elif prop_id == 0xA5:
        v = getattr(lv.GRAD_DIR, value_str, None)
    elif prop_id == 0xA6:
        v = getattr(lv.FLEX_FLOW, value_str, None)
    elif 0xA7 <= prop_id <= 0xA9:
        v = getattr(lv.FLEX_ALIGN, value_str, None)
    elif prop_id == 0xAA:
        v = getattr(lv.LAYOUT, value_str, None)
    elif prop_id == 0xAB:
        v = getattr(lv.BASE_DIR, value_str, None)
    elif 0xAC <= prop_id <= 0xAF:
        v = getattr(lv.GRID_ALIGN, value_str, None)
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
            palette_idx = color_ref_to_palette_idx(color_tok[1:])
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
    group = _prop_id_to_group(prop_id)
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
        return _resolve_int_lit(lit_str)
    if group == _GRP_ENUM:
        return _resolve_enum(prop_id, lit_str)
    if group == _GRP_BOOL:
        return lit_str == "true"
    print("Warning: _resolve_lit: unknown group for prop_id 0x{:02X}".format(prop_id))
    return None


def _resolve_int_lit(lit_str):
    """Resolve an INT literal string, supporting plain ints, SIZE_CONTENT,
    pct(N), and FR(N) for grid track descriptors."""
    if lit_str == "SIZE_CONTENT":
        return lv.SIZE_CONTENT
    if lit_str.startswith("pct(") and lit_str.endswith(")"):
        try:
            return lv.pct(int(lit_str[4:-1]))
        except (ValueError, TypeError):
            print("Warning: bad pct() expression: " + lit_str)
            return None
    if lit_str.startswith("FR(") and lit_str.endswith(")"):
        try:
            return lv.grid_fr(int(lit_str[3:-1]))
        except (ValueError, TypeError, AttributeError):
            print("Warning: bad FR() expression: " + lit_str)
            return None
    try:
        return int(lit_str)
    except ValueError:
        print("Warning: expected int literal, got: " + lit_str)
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Style-entry framing (leaf vs. role container) — runtime-side read helpers
# ─────────────────────────────────────────────────────────────────────────────

_CONTAINER_FLAG = 0x80        # high bit of an entry's first byte marks a container
_ROLE_ENTRY_SIZE = 3          # role table entry: role_code u8 + offset u16


def _read_entry_header(f, entry_off):
    """Read a style entry's framing byte (and role table) at *entry_off*.

    Returns ``(is_container, count, role_table)``:
      - leaf:      ``(False, op_count, None)``
      - container: ``(True, role_count, {role_code: abs_body_off, ...})``
    Returns None on EOF/truncation."""
    f.seek(entry_off)
    raw = f.read(1)
    if not raw:
        return None
    first = raw[0]
    if not (first & _CONTAINER_FLAG):
        return (False, first, None)
    role_count = first & 0x7F
    role_table = {}
    for i in range(role_count):
        f.seek(entry_off + 1 + i * _ROLE_ENTRY_SIZE)
        code_raw = f.read(1)
        off_raw = f.read(2)
        if len(code_raw) < 1 or len(off_raw) < 2:
            return None
        role_table[code_raw[0]] = entry_off + struct.unpack("<H", off_raw)[0]
    return (True, role_count, role_table)


def _style_body_length(f, pos):
    """Byte length of a style body starting at *pos* ([op_count][ops]).

    Returns None on EOF (no body at *pos*)."""
    f.seek(pos)
    raw = f.read(1)
    if not raw:
        return None
    return 1 + raw[0] * 3


def _entry_length(f, entry_off):
    """Total byte length of the style entry at *entry_off* (leaf or container).

    Returns None if there is no entry at *entry_off* (EOF)."""
    header = _read_entry_header(f, entry_off)
    if header is None:
        return None
    is_container, count, role_table = header
    if not is_container:
        return 1 + count * 3                      # leaf: count = op_count
    if count == 0:
        return 1
    # The last style body in the table is the entry's tail; offsets are absolute.
    last_body_off = max(role_table.values())
    body_len = _style_body_length(f, last_body_off)
    if body_len is None:
        return None
    return (last_body_off - entry_off) + body_len


def _read_role_offset(f, entry_off, role_code):
    """Return the absolute file position of *role_code*'s style body in the
    entry at *entry_off*, or None if the entry is a leaf / has no such role.

    Defaults to MAIN (code 0) when *role_code* is None."""
    want = StyleRole.MAIN if role_code is None else role_code
    header = _read_entry_header(f, entry_off)
    if header is None:
        return None
    is_container, _, role_table = header
    if not is_container:
        # Leaf: the entry IS a single style body.  Only MAIN exists.
        return entry_off if want == StyleRole.MAIN else None
    return role_table.get(want)


def _read_op_list(f, op_count):
    """Read *op_count* 3-byte ops from *f* (positioned after the count byte).
    Returns list of (prop_id, val_type, index) or None on truncation."""
    ops_raw = f.read(op_count * 3)
    if len(ops_raw) < op_count * 3:
        print("Warning: truncated style ops data")
        return None
    return [(ops_raw[i*3], ops_raw[i*3+1], ops_raw[i*3+2])
            for i in range(op_count)]


def _read_style_body(f, pos):
    """Read one style body at absolute offset *pos* (``[op_count][ops]``).
    Returns list of (prop_id, val_type, index) or None on truncation/EOF."""
    f.seek(pos)
    raw = f.read(1)
    if not raw:
        return None
    return _read_op_list(f, raw[0])


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
            entry_len = _entry_length(f, off)
            if entry_len is None:
                # The entry is present but unreadable 
                # -> the binary is corrupt, and the LIT dict offset
                # can't be derived. Fail rather than guess.
                print("Warning: style entry {} unreadable (corrupt styles binary)".format(i))
                return (-1, 0)
            block_off = off + entry_len
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

    except Exception as e:
        print("Warning: exception occurred while opening LIT dict:" + str(e))
        return (-1, 0)


def _read_lit_string(f, lit_idx):
    """Read one LIT string by index from an already-open styles binary handle."""
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
        print("Warning: _read_lit_string failed: " + str(e))
        return None


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

    # Max ops in a single style body. op_count shares its byte with the
    # role-container flag (high bit), so op_count is limited to 7 bits (127).
    # This is a designed cap: the compiler supports ~103 distinct settable
    # properties (so a style cannot exceed ~110 ops).
    # Exceeding it is a hard compile error, not silent truncation.
    MAX_OPS = 127

    def _encode_style_body(self, entry):
        """Encode a plain style dict (no ``roles`` block) into a style body.

        *entry* is a dict: { "style": "@OTHER"|["@A","@B"], "bg_color": ..., ... }
        Returns a bytearray ``[op_count u8][op_count x 3-byte ops]`` (op_count
        high bit clear).  op_count must fit in 7 bits (the high bit is the
        container flag at the entry level); exceeding MAX_OPS is a hard compile
        error.
        """
        # Reserve byte 0 for op_count; written once the count is final.
        buf = bytearray(b"\x00")
        op_count = 0

        def add_op(prop_id, val_type, index):
            nonlocal op_count
            if index > 255:
                print("Warning: index {} > 255 for prop 0x{:02X} — skipping".format(index, prop_id))
                return
            buf.append(prop_id)
            buf.append(val_type)
            buf.append(index)
            op_count += 1

        for key, raw_val in entry.items():
            if key == "style":
                refs = [raw_val] if isinstance(raw_val, str) else list(raw_val)
                for ref in refs:
                    if not isinstance(ref, str) or not ref.startswith("@"):
                        print("Warning: 'style' value must start with '@', got: " + str(ref))
                        continue
                    style_idx = style_ref_to_palette_idx(ref[1:])
                    if style_idx is None:
                        print("Warning: unknown style ref '{}' — skipping".format(ref))
                        continue
                    if style_idx > 255:
                        print("Warning: style index {} > 255 for '{}' — skipping".format(style_idx, ref))
                        continue
                    add_op(PROP_STYLE_INHERIT, VAL_STYLE_PAL, style_idx)
                continue

            prop_id, group = _attr_to_prop_id(key)
            if prop_id is None:
                print("Warning: unsupported style attr '{}' — skipping".format(key))
                continue

            result = _encode_value(key, group, raw_val, self._lit_builder)
            if result is None:
                continue

            if group == _GRP_ARRAY:
                # result is a list of (val_type, index) for each element
                elements = result
                if len(elements) > 255:
                    print("Warning: array too long for '{}' — skipping".format(key))
                    continue
                # Header op: prop_id, VAL_ARRAY, length; then one op per element
                # (prop_id repeated, val_type, lit_index)
                add_op(prop_id, VAL_ARRAY, len(elements))
                for val_type, index in elements:
                    add_op(prop_id, val_type, index)
            else:
                val_type, index = result
                add_op(prop_id, val_type, index)

            if op_count > self.MAX_OPS:
                raise ValueError(
                    "style has > {} ops (op_count high bit is the role-container "
                    "flag)".format(self.MAX_OPS))

        # Write the reserved op_count byte now that the count is final.
        buf[0] = op_count
        return buf

    def convert_setting_to_binary(self, entry):
        """Encode one style entry into binary.

        A style without a ``roles`` block is encoded as a leaf
        ``[op_count][ops]`` (op_count high bit clear).

        A style with a ``roles`` block is encoded as a role container:
        ``[0x80|role_count][role_count x (role_code u8, offset u16)]`` then each
        role's style body inline.  ``MAIN`` (code 0) holds the style's own ops;
        offsets are byte positions within this entry.
        """
        if not isinstance(entry, dict):
            print("Warning: style entry is not a dict, skipping")
            return bytearray(b"\x00")

        roles = entry.get("roles")
        main_body = self._encode_style_body({k: v for k, v in entry.items() if k != "roles"})

        if not roles:
            # Leaf — high bit clear, no role table.
            return main_body

        # ── Container: build each role's style body, then table + bodies inline ──
        role_codes = collect_int_constants(StyleRole)

        # body list: MAIN first, then roles sorted by role_code (stable order).
        bodies = [(StyleRole.MAIN, main_body)]
        for role_name, role_entry in sorted(
                roles.items(), key=lambda kv: role_codes.get(str(kv[0]).upper(), 0xFF)):
            code = role_codes.get(str(role_name).upper())
            if code is None:
                print("Warning: unknown role '{}' — skipped (known: {})"
                      .format(role_name, sorted(role_codes)))
                continue
            if not isinstance(role_entry, dict):
                print("Warning: role '{}' entry is not a dict — skipped".format(role_name))
                continue
            bodies.append((code, self._encode_style_body(role_entry)))

        header_size = 1 + len(bodies) * 3  # flag|count byte + per-role (code, offset u16)
        buf = bytearray()
        buf.append(0x80 | len(bodies))
        offset = header_size
        for code, body in bodies:
            buf.append(code)
            buf.extend(struct.pack("<H", offset))
            offset += len(body)
        for code, body in bodies:
            buf.extend(body)
        return buf

    def reconstruct_setting_from_binary(self, f):
        """Read a style entry at the current file position.

        Leaf entry (first byte high bit clear): returns a flat list of
        (prop_id, val_type, index) op tuples — the style body.

        Role container (first byte = ``0x80|role_count``): reads the role table
        and each role body, returning a dict ``{role_code: [ops...]}``.  The
        dict is non-None on success, which is all the generic framework callers
        (``validate_binary_file``, base ``read_setting_from_binary``) require —
        they only check for None / exception.

        Returns None on error."""
        try:
            entry_off = f.tell()
            header = _read_entry_header(f, entry_off)
            if header is None:
                print("Warning: unexpected EOF reading style entry")
                return None
            is_container, count, role_table = header
            if not is_container:
                # Leaf: count is op_count; body starts at the entry.
                return _read_style_body(f, entry_off)
            # Container: read each role's body via the parsed role table.
            roles = {}
            for code, body_off in role_table.items():
                ops = _read_style_body(f, body_off)
                if ops is None:
                    return None
                roles[code] = ops
            return roles
        except Exception as e:
            print("Warning: reconstruct_setting_from_binary failed: " + str(e))
            return None

    def read_setting_from_binary(self, file_path, style_idx, context=None, role_code=None):
        """Build one lv.style_t from a styles binary file.

        *context*: ThemeCompiler providing get_color / get_font.
        *role_code*: a ``StyleRole`` code selecting a role within the style's
        role container; ``None`` = the MAIN role (the style's own body).

        Returns (lv.style_t, None) or (None, error_str).
        """
        if context is None:
            return (None, "context_required")

        with open(file_path, "rb") as f:
            return self._reconstruct_style_from_handle(f, style_idx, context, role_code=role_code)

    def _reconstruct_style_from_handle(self, f, style_idx, context, s=None, in_progress=None, role_code=None):
        """Internal: build one lv.style_t from an already-open file handle."""
        if in_progress is None:
            in_progress = set()
        if style_idx in in_progress:
            return (None, "cycle_detected")
        in_progress.add(style_idx)
        try:
            ops, err = self._read_ops_from_handle(f, style_idx, role_code)
            if ops is None:
                return (None, err)
            if s is None:
                s = lv.style_t()
                s.init()
            self._apply_ops_to_style(f, ops, s, context, in_progress)
            return (s, None)
        finally:
            in_progress.discard(style_idx)

    def _read_ops_from_handle(self, f, style_index, role_code=None):
        """Internal: read the ops of one role (default MAIN) of a style entry."""
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
            body_pos = _read_role_offset(f, entry_off, role_code)
            if body_pos is None:
                return (None, f"role_{role_code}_not_found_{style_index}")
            f.seek(body_pos)
            result = _read_style_body(f, body_pos)
            if result is None:
                return (None, f"read_ops_failed_{style_index}")
            return (result, None)
        except Exception:
            return (None, f"_read_ops_failed_{style_index}")

    def _apply_ops_to_style(self, f, ops, s, context, in_progress):
        """Apply a decoded ops list onto lv.style_t *s*.
        STYLE_INHERIT ops are inlined recursively using the open file handle *f*.
        ARRAY ops consume the next N ops as array elements."""
        i = 0
        while i < len(ops):
            prop_id, val_type, index = ops[i]
            i += 1
            if prop_id == PROP_STYLE_INHERIT:
                self._reconstruct_style_from_handle(f, index, context, s, in_progress)
                continue
            if val_type == VAL_ARRAY:
                # index = array length N; next N ops are elements
                arr_len = index
                elements = []
                for _ in range(arr_len):
                    if i >= len(ops):
                        print("Warning: truncated array for prop_id 0x{:02X}".format(prop_id))
                        break
                    _, elem_val_type, elem_index = ops[i]
                    i += 1
                    value = self._resolve_op(f, prop_id, elem_val_type, elem_index, context)
                    if value is not None:
                        elements.append(value)
                # Auto-append LV_GRID_TEMPLATE_LAST for grid track descriptors
                if hasattr(lv, "GRID_TEMPLATE_LAST"):
                    elements.append(lv.GRID_TEMPLATE_LAST)
                attr_name = _prop_id_to_attr_name(prop_id)
                if attr_name is None:
                    print("Warning: unknown array prop_id 0x{:02X}".format(prop_id))
                    continue
                setter = getattr(s, "set_" + attr_name, None)
                if setter is None:
                    print("Warning: lv.style_t has no set_{}".format(attr_name))
                    continue
                try:
                    setter(elements)
                except Exception as e:
                    print("Warning: set_{}({}) failed: {}".format(attr_name, elements, e))
                continue
            attr_name = _prop_id_to_attr_name(prop_id)
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

    def _resolve_op(self, f, prop_id, val_type, index, context):
        """Resolve one op value using *context* for palette refs and *f* for LIT reads."""
        if val_type == VAL_COLOR_PAL:
            return context.get_color(index)
        if val_type == VAL_FONT_PAL:
            return context.get_font(index)
        if val_type == VAL_LIT:
            lit_str = _read_lit_string(f, index)
            if lit_str is None:
                return None
            # For ARRAY attrs, resolve elements as INT literals (supports FR(N), pct(N), etc.)
            group = _prop_id_to_group(prop_id)
            if group == _GRP_ARRAY:
                return _resolve_int_lit(lit_str)
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