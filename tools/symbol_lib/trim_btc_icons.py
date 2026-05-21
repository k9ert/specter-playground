#!/usr/bin/env python3
"""trim_btc_icons.py — Remove unused BTC_ICONS from the firmware freeze path.

Overview
--------
The MicroPython manifest freezes the entire scenarios/MockUI/src/ tree, so
every .py file in that tree ends up compiled into the firmware binary regardless
of whether it is actually imported.  This script keeps only the icon files that
are referenced in the MockUI source code inside that tree, and archives the rest
to tools/symbol_lib/icons_available/ (git-tracked but outside the freeze path).

Workflow
--------
Full cycle for adding new icons:

  1. Add SVGs and run the generator:

         python3 tools/symbol_lib/generate_btc_icons.py \\
             <svg_dir> scenarios/MockUI/src/MockUI/basic/symbol_lib

     This populates icons/ with all icons and fully regenerates btc_icons.py
     with every icon active.

  2. Add BTC_ICONS.<NAME> references in MockUI source code.

  3. Run this script to trim:

         python3 tools/symbol_lib/trim_btc_icons.py

     Unused icon files are moved to tools/symbol_lib/icons_available/.
     btc_icons.py is updated: used icons stay uncommented, unused ones are
     commented out (so developers can see what is available and restore them
     quickly by adding a BTC_ICONS.<NAME> usage and re-running the script).

  4. Build:  make mockui

State after trim
----------------
  icons/               — only used icons  (included in firmware freeze)
  icons_available/     — unused but valid icons  (git-tracked; restore by
                         adding a usage and re-running trim)
  btc_icons.py         — active imports for used icons;
                         commented-out lines for unused ones

Validity checks
---------------
An icon file is considered valid when ALL of the following hold:

  1. The file exists on disk.
  2. It parses without Python syntax errors.
  3. It defines the expected constant at module level (e.g. BATTERY_FULL = …).

If a *used* icon fails any check in both icons/ and icons_available/, the icon
is added to build/btc_icons_invalid.txt and the script exits with code 1 after
processing every icon (so all problems are surfaced at once).

If an *unused* icon is invalid or missing everywhere, its btc_icons.py entry is
removed entirely and it is recorded in build/btc_icons_invalid.txt (no build
failure, since it is not referenced).

Output files (both gitignored via build/)
-----------------------------------------
  build/btc_icons_used.txt    — sorted list of used icon names
  build/btc_icons_invalid.txt — invalid icons with reasons (only written when
                                 at least one invalid icon is found)

Usage
-----
    python3 tools/symbol_lib/trim_btc_icons.py [options]

Options
-------
    --dry-run          Print planned actions; make no changes.
    --scan-only        Scan, write build/btc_icons_used.txt, then exit.
    --source-dir PATH  Root of MockUI source to scan.
                       (default: scenarios/MockUI/src/MockUI)
    --symbol-lib-dir   Directory containing btc_icons.py and icons/.
                       (default: …/basic/symbol_lib)
    --archive-dir      Directory for unused-but-available icons.
                       (default: tools/symbol_lib/icons_available)
    --build-dir        Where to write report files.
                       (default: build)
"""

import argparse
import ast
import re
import shutil
import sys
from pathlib import Path

# ── repo root ─────────────────────────────────────────────────────────────────
_SCRIPT_DIR = Path(__file__).resolve().parent   # tools/symbol_lib/
_REPO_ROOT   = _SCRIPT_DIR.parent.parent        # specter-playground/

# ── patterns ──────────────────────────────────────────────────────────────────
# Import line in btc_icons.py, active or commented:
#   from .icons.battery_full import BATTERY_FULL
#   # from .icons.battery_full import BATTERY_FULL
_IMPORT_RE = re.compile(
    r'^(?:#\s*)?from \.icons\.(?P<snake>\w+) import (?P<name>[A-Z_][A-Z0-9_]*)$'
)

# BTC_ICONS.<NAME> usage anywhere in source:
_USAGE_RE = re.compile(r'BTC_ICONS\.([A-Z_][A-Z0-9_]*)')


# ── scan ──────────────────────────────────────────────────────────────────────

def scan_used_icons(source_dir: Path, icons_dir: Path) -> set:
    """Return set of icon NAMEs referenced as BTC_ICONS.<NAME> in source_dir.

    Skips btc_icons.py and all files inside icons/ to avoid counting the
    aggregator's own imports/definitions as "usage".
    """
    used = set()
    icons_dir_str = str(icons_dir.resolve()) + '/'

    for py_file in sorted(source_dir.rglob('*.py')):
        if py_file.name == 'btc_icons.py':
            continue
        if str(py_file.resolve()).startswith(icons_dir_str):
            continue
        text = py_file.read_text(encoding='utf-8', errors='replace')
        for m in _USAGE_RE.finditer(text):
            used.add(m.group(1))

    return used


# ── parse btc_icons.py ────────────────────────────────────────────────────────

def parse_btc_icons(path: Path):
    """Parse btc_icons.py and return (icons: list[dict], lines: list[str]).

    Each icon dict:
        name        str       e.g. 'BATTERY_FULL'
        snake       str       e.g. 'battery_full'
        active      bool      True if not commented out
        import_idx  int       line index of the 'from .icons…' line
        attr_idx    int|None  line index of the '    NAME = NAME' class attr
    """
    raw   = path.read_text(encoding='utf-8')
    lines = raw.splitlines(keepends=True)

    icons   = []
    by_name = {}

    # Pass 1: locate import lines
    for i, line in enumerate(lines):
        m = _IMPORT_RE.match(line.rstrip('\n'))
        if m:
            entry = {
                'name':       m.group('name'),
                'snake':      m.group('snake'),
                'active':     not line.lstrip().startswith('#'),
                'import_idx': i,
                'attr_idx':   None,
            }
            icons.append(entry)
            by_name[entry['name']] = entry

    # Pass 2: locate class-body attribute lines.
    # Both active ('    NAME = NAME') and commented ('# ' + '    NAME = NAME')
    # forms are recognised by stripping the leading '# ' comment marker first.
    for i, line in enumerate(lines):
        stripped = line.rstrip('\n')
        # Remove exactly the '# ' (or '#') comment prefix added by comment_line
        if stripped.startswith('# '):
            core = stripped[2:]
        elif stripped.startswith('#'):
            core = stripped[1:]
        else:
            core = stripped
        m = re.match(r' {4}([A-Z_][A-Z0-9_]*) = \1\s*$', core)
        if m:
            name = m.group(1)
            if name in by_name and by_name[name]['attr_idx'] is None:
                by_name[name]['attr_idx'] = i

    return icons, lines


# ── validate ──────────────────────────────────────────────────────────────────

def validate_icon(icon_path: Path, expected_name: str):
    """Return (ok: bool, reason: str).

    Checks:
      1. File exists.
      2. Valid Python syntax (ast.parse).
      3. Expected constant is assigned at module level.
    """
    if not icon_path.exists():
        return False, 'file not found'

    try:
        source = icon_path.read_text(encoding='utf-8')
        tree   = ast.parse(source, filename=str(icon_path))
    except SyntaxError as exc:
        return False, f'syntax error: {exc}'

    for node in tree.body:
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == expected_name:
                    return True, 'ok'
        elif isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == expected_name:
                return True, 'ok'

    return False, f"constant '{expected_name}' not defined at module level"


# ── line helpers ──────────────────────────────────────────────────────────────

def comment_line(line: str) -> str:
    """Prepend '# ' to *line* (idempotent — skips already-commented lines)."""
    stripped = line.rstrip('\n')
    nl = '\n' if line.endswith('\n') else ''
    if stripped.startswith('#'):
        return line
    return '# ' + stripped + nl


def uncomment_line(line: str) -> str:
    """Remove leading '# ' (or '#') comment marker (idempotent)."""
    stripped = line.rstrip('\n')
    nl = '\n' if line.endswith('\n') else ''
    if stripped.startswith('# '):
        return stripped[2:] + nl
    if stripped.startswith('#'):
        return stripped[1:] + nl
    return line


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description='Trim unused BTC_ICONS from the firmware freeze path.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Print planned actions; make no changes.',
    )
    parser.add_argument(
        '--scan-only', action='store_true',
        help='Scan and write build/btc_icons_used.txt, then exit.',
    )
    parser.add_argument(
        '--source-dir', type=Path,
        default=_REPO_ROOT / 'scenarios' / 'MockUI' / 'src' / 'MockUI',
        help='Root of MockUI source to scan  (default: scenarios/MockUI/src/MockUI)',
    )
    parser.add_argument(
        '--symbol-lib-dir', type=Path,
        default=(_REPO_ROOT / 'scenarios' / 'MockUI' / 'src' / 'MockUI'
                 / 'basic' / 'symbol_lib'),
        help='Directory containing btc_icons.py and icons/  (default: …/basic/symbol_lib)',
    )
    parser.add_argument(
        '--archive-dir', type=Path,
        default=_REPO_ROOT / 'tools' / 'symbol_lib' / 'icons_available',
        help='Archive dir for unused-but-valid icons  (default: tools/symbol_lib/icons_available)',
    )
    parser.add_argument(
        '--build-dir', type=Path,
        default=_REPO_ROOT / 'build',
        help='Where to write report files  (default: build)',
    )
    args = parser.parse_args()

    dry      = args.dry_run
    src_dir  = args.source_dir
    sym_dir  = args.symbol_lib_dir
    arch_dir = args.archive_dir
    bld_dir  = args.build_dir
    ico_dir  = sym_dir / 'icons'
    btc_path = sym_dir / 'btc_icons.py'

    if dry:
        print('[DRY RUN] No files will be modified.\n')

    # ── Phase 1: scan ─────────────────────────────────────────────────────────
    print('Phase 1 — Scanning source for BTC_ICONS usage …')
    used = scan_used_icons(src_dir, ico_dir)
    print(f'  {len(used)} icon(s) in use.')

    if not dry:
        bld_dir.mkdir(parents=True, exist_ok=True)
        used_file = bld_dir / 'btc_icons_used.txt'
        used_file.write_text('\n'.join(sorted(used)) + '\n', encoding='utf-8')
        print(f'  → {used_file}')
    else:
        print('  Used icons:')
        for n in sorted(used):
            print(f'    {n}')

    if args.scan_only:
        return 0

    # ── Phase 2: trim ─────────────────────────────────────────────────────────
    print('\nPhase 2 — Trimming btc_icons.py and icon files …')

    icons, lines = parse_btc_icons(btc_path)

    if not dry:
        arch_dir.mkdir(parents=True, exist_ok=True)

    invalid_entries = []   # list of (name, reason, 'used'|'unused')
    fail = False

    for icon in icons:
        name    = icon['name']
        snake   = icon['snake']
        is_used = name in used

        active_path  = ico_dir  / f'{snake}.py'
        archive_path = arch_dir / f'{snake}.py'
        in_active    = active_path.exists()
        in_archive   = archive_path.exists()

        # Validate whichever copy is available (prefer active)
        if in_active:
            ok, reason = validate_icon(active_path, name)
        elif in_archive:
            ok, reason = validate_icon(archive_path, name)
        else:
            ok, reason = False, 'not found in icons/ or icons_available/'

        # ── Action matrix ─────────────────────────────────────────────────────
        if is_used:
            if ok:
                if in_archive and not in_active:
                    print(f'  RESTORE   {name}  (was archived)')
                    if not dry:
                        shutil.move(str(archive_path), str(active_path))
                # Ensure the entry is uncommented in btc_icons.py
                if not icon['active']:
                    print(f'  UNCOMMENT {name}')
                    if not dry:
                        lines[icon['import_idx']] = uncomment_line(lines[icon['import_idx']])
                        if icon['attr_idx'] is not None:
                            lines[icon['attr_idx']] = uncomment_line(lines[icon['attr_idx']])
                else:
                    if not in_archive or in_active:
                        print(f'  OK        {name}')
            else:
                # Used but invalid / missing everywhere → build fail
                print(f'  FAIL      {name}: {reason}')
                invalid_entries.append((name, reason, 'used'))
                fail = True
                # Keep btc_icons.py entry as-is; the source reference is still there

        else:
            # Unused
            if ok and in_active:
                # Move to archive and comment out
                print(f'  ARCHIVE   {name}')
                if not dry:
                    shutil.move(str(active_path), str(archive_path))
                    if icon['active']:
                        lines[icon['import_idx']] = comment_line(lines[icon['import_idx']])
                        if icon['attr_idx'] is not None:
                            lines[icon['attr_idx']] = comment_line(lines[icon['attr_idx']])

            elif in_archive:
                # Already archived — just ensure the btc_icons.py line is commented
                if icon['active']:
                    print(f'  COMMENT   {name}  (already archived)')
                    if not dry:
                        lines[icon['import_idx']] = comment_line(lines[icon['import_idx']])
                        if icon['attr_idx'] is not None:
                            lines[icon['attr_idx']] = comment_line(lines[icon['attr_idx']])
                else:
                    print(f'  SKIP      {name}  (archived + commented)')

            else:
                # Unused + nowhere (missing or invalid with no file found anywhere)
                note = reason if not ok else 'file missing'
                print(f'  REMOVE    {name}: {note}  (unused, removing entry)')
                invalid_entries.append((name, note, 'unused'))
                if not dry:
                    lines[icon['import_idx']] = ''
                    if icon['attr_idx'] is not None:
                        lines[icon['attr_idx']] = ''

    # ── Write updated btc_icons.py ────────────────────────────────────────────
    if not dry:
        btc_path.write_text(''.join(lines), encoding='utf-8')
        print(f'\n  Updated: {btc_path}')

    # ── Write invalid report ──────────────────────────────────────────────────
    if invalid_entries:
        print(f'\n⚠  Invalid / missing icons ({len(invalid_entries)}):')
        report_lines = []
        for iname, ireason, ikind in invalid_entries:
            tag = '[USED — BUILD FAIL]' if ikind == 'used' else '[UNUSED — REMOVED]'
            msg = f'{iname}: {ireason}  {tag}'
            print(f'    {msg}')
            report_lines.append(msg)
        if not dry:
            inv_file = bld_dir / 'btc_icons_invalid.txt'
            inv_file.write_text('\n'.join(report_lines) + '\n', encoding='utf-8')
            print(f'  → {inv_file}')
    else:
        print('\n  No invalid icons.')

    if fail:
        print('\nERROR: one or more used icons are invalid or missing. Fix before building.')
        return 1

    used_count    = sum(1 for ic in icons if ic['name'] in used)
    archived_count = sum(
        1 for ic in icons
        if ic['name'] not in used and (ico_dir / f"{ic['snake']}.py").exists() == False
        and (arch_dir / f"{ic['snake']}.py").exists()
    )
    print(
        f'\nDone.  {used_count} icon(s) active, '
        f'{len(icons) - used_count - len([e for e in invalid_entries if e[2]=="unused"])} archived, '
        f'{len([e for e in invalid_entries if e[2]=="unused"])} removed (invalid/missing).'
    )
    return 0


if __name__ == '__main__':
    sys.exit(main())
