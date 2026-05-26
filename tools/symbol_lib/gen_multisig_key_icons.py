#!/usr/bin/env python3
"""Generate KEY_MULTI_BACK and KEY_MULTI_FRONT icon files from two-keys SVG paths."""

import subprocess
import sys
import tempfile
from pathlib import Path
from PIL import Image

PATH_BACK = (
    "M20.854 10.308c.6 2.411-.923 4.867-3.403 5.486-.31.077-.621.122-.928.137"
    "l-2.666 4.298a2 2 0 01-1.216.887l-1.236.308a1 1 0 01-1.212-.729l-.28-1.12"
    "a2 2 0 01.241-1.538l2.445-3.943a4.38 4.38 0 01-.728-1.547c-.6-2.411.922-4.867"
    " 3.403-5.486 2.48-.618 4.978.835 5.58 3.247z"
    "m-3.872 1.48c.552-.137.89-.683.756-1.219-.133-.536-.688-.859-1.24-.721"
    "-.55.137-.89.683-.756 1.219s.69.859 1.24.721z"
)

PATH_FRONT = (
    "M11.251 12.187c2.48-.619 4.004-3.075 3.403-5.486-.601-2.412-3.1-3.865"
    "-5.58-3.247-2.48.618-4.004 3.075-3.402 5.486.143.575.394 1.096.728 1.547"
    "l-2.445 3.942a2 2 0 00-.241 1.538l.28 1.121a1 1 0 001.211.728l1.236-.308"
    "a2 2 0 001.216-.886l2.666-4.298c.307-.015.618-.06.928-.137z"
    "m.288-5.225c.133.536-.205 1.082-.756 1.219s-1.106-.186-1.24-.721"
    "c-.134-.536.205-1.082.756-1.22.551-.137 1.106.186 1.24.722z"
)

ICON_SIZE = 42

PY_TEMPLATE = (
    '"""AUTO-GENERATED -- do not edit. Regenerate with'
    ' tools/symbol_lib/gen_multisig_key_icons.py"""\n'
    "from ..icon import Icon\n\n"
    "# bytes literals -- stored in flash (ROM) in frozen bytecode, zero heap\n"
    "{name} = Icon(\n"
    "    pattern=(\n"
    "{rows}"
    "    ),\n"
    "    width={w},\n"
    "    height={h},\n"
    ")\n"
)


def render_svg_to_alpha(path_d, size):
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="black">\n'
        '  <path fill-rule="evenodd" clip-rule="evenodd" d="' + path_d + '"/>\n'
        "</svg>\n"
    )
    with tempfile.TemporaryDirectory() as tmp:
        svg_path = Path(tmp) / "icon.svg"
        png_path = Path(tmp) / "icon.png"
        svg_path.write_text(svg)
        subprocess.run(
            ["inkscape",
             "--export-width=" + str(size),
             "--export-height=" + str(size),
             "--export-type=png",
             "--export-filename=" + str(png_path),
             str(svg_path)],
            check=True, capture_output=True,
        )
        img = Image.open(str(png_path)).convert("RGBA")
        ab = bytearray()
        for y in range(img.height):
            for x in range(img.width):
                ab.append(img.getpixel((x, y))[3])
        return bytes(ab)


def alpha_to_py(name, alpha, width, height):
    rows = []
    for y in range(height):
        row = alpha[y * width:(y + 1) * width]
        rows.append('        b"' + "".join("\\x{:02x}".format(b) for b in row) + '"\n')
    return PY_TEMPLATE.format(name=name, rows="".join(rows), w=width, h=height)


def main():
    out_dir = (
        Path(sys.argv[1]) if len(sys.argv) > 1
        else Path(__file__).resolve().parent.parent.parent
             / "scenarios/MockUI/src/MockUI/basic/symbol_lib/icons"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    for var_name, path_d, filename in [
        ("KEY_MULTI_BACK",  PATH_BACK,  "key_multi_back.py"),
        ("KEY_MULTI_FRONT", PATH_FRONT, "key_multi_front.py"),
    ]:
        print("Rendering {} ...".format(var_name), flush=True)
        alpha = render_svg_to_alpha(path_d, ICON_SIZE)
        py_src = alpha_to_py(var_name, alpha, ICON_SIZE, ICON_SIZE)
        out_path = out_dir / filename
        out_path.write_text(py_src)
        print("  -> {}  ({} non-zero pixels)".format(out_path, sum(1 for b in alpha if b > 0)))
    print("Done.")


if __name__ == "__main__":
    main()
