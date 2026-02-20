#!/usr/bin/env python3
"""
Master script to generate Python icon definitions from PNG files.

This script orchestrates the complete workflow:
1. Convert all PNG files to ARGB8888 C arrays (using batch_convert_png.py)
2. Extract alpha channels and generate Python definitions (using c_to_python_alpha.py)

Usage:
    python3 generate_python_icons_from_png.py <png_folder> <c_folder> <output_py_file>

Example:
    python3 generate_python_icons_from_png.py \
        ../../../bitcoin_icons/Bitcoin-Icons/png/filled \
        ../../../bitcoin_icons/Bitcoin-Icons/c/filled \
        ../btc_icons.py
"""

import sys
import subprocess
from pathlib import Path


def convert_pngs_to_c(png_folder, c_folder, batch_script, lvgl_script):
    """
    Step 1: Convert all PNG files to C arrays using batch_convert_png.py
    
    Args:
        png_folder: Path to folder containing PNG files
        c_folder: Path to folder where C files will be created
        batch_script: Path to batch_convert_png.py
        lvgl_script: Path to LVGLImage.py script
    """
    print(f"Step 1: Converting PNG files to C arrays...")
    print(f"  Source: {png_folder}")
    print(f"  Target: {c_folder}\n")
    
    # Run batch_convert_png.py
    result = subprocess.run(
        [
            sys.executable,
            str(batch_script),
            png_folder,
            c_folder,
            str(lvgl_script)
        ],
        capture_output=True,
        text=True
    )
    
    # Print the output
    print(result.stdout)
    
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"PNG to C conversion failed with exit code {result.returncode}")
    
    print()


def generate_python_file(c_folder, output_py_file, c_to_python_script):
    """
    Step 2: Extract alpha channels and generate Python icon definitions.
    
    Args:
        c_folder: Path to folder containing C files
        output_py_file: Path to output Python file
        c_to_python_script: Path to c_to_python_alpha.py
    """
    c_path = Path(c_folder)
    output_path = Path(output_py_file)
    
    if not c_path.exists():
        raise FileNotFoundError(f"C folder not found: {c_folder}")
    
    # Find all C files
    c_files = sorted(c_path.glob("*.c"))
    
    if not c_files:
        raise ValueError(f"No C files found in {c_folder}")
    
    print(f"Step 2: Extracting alpha channels from {len(c_files)} C files...")
    print(f"  Generating: {output_path}\n")
    
    # Run c_to_python_alpha.py for all C files and capture output
    result = subprocess.run(
        [sys.executable, str(c_to_python_script)] + [str(f) for f in c_files],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"Alpha extraction failed with exit code {result.returncode}")
    
    # Parse the output to get icon definitions
    icon_output = result.stdout
    
    # Generate the complete Python file with header
    header = '''"""Bitcoin icon library - Auto-generated from Bitcoin-Icons PNG files."""

from .icon import Icon


class BTC_ICONS:
    """
    Library of Bitcoin-themed icons.
    
    All icons are 24x24 pixels with 8-bit alpha channel for anti-aliasing.
    Icons can be colored by calling them with a color parameter:
        BTC_ICONS.WALLET(lv.color_hex(0xFF0000))  # Red wallet icon
        BTC_ICONS.QR_CODE(GREEN_HEX)               # Green QR code icon
        BTC_ICONS.BITCOIN                          # White bitcoin icon (default)
    """
'''
    
    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(header)
        f.write(icon_output)
    
    print(f"  ✓ Generated {len(c_files)} icon definitions")
    print(f"  ✓ Output: {output_path}")
    print("\nDone! 🎉")


def main():
    """Main entry point."""
    if len(sys.argv) != 4:
        print("Usage: python3 generate_python_icons_from_png.py <png_folder> <c_folder> <output_py_file>")
        print()
        print("Arguments:")
        print("  png_folder:      Directory containing PNG icon files")
        print("  c_folder:        Directory where C array files will be stored")
        print("  output_py_file:  Path to output Python file (e.g., ../btc_icons.py)")
        print()
        print("Example:")
        print("  python3 generate_python_icons_from_png.py \\")
        print("      ../../../bitcoin_icons/Bitcoin-Icons/png/filled \\")
        print("      ../../../bitcoin_icons/Bitcoin-Icons/c/filled \\")
        print("      ../btc_icons.py")
        sys.exit(1)
    
    png_folder = sys.argv[1]
    c_folder = sys.argv[2]
    output_py_file = sys.argv[3]
    
    # Find helper scripts in the same directory
    script_dir = Path(__file__).parent
    batch_script = script_dir / "batch_convert_png.py"
    c_to_python_script = script_dir / "c_to_python_alpha.py"
    lvgl_script = script_dir / "LVGLImage.py"
    
    # Verify helper scripts exist
    missing = []
    if not batch_script.exists():
        missing.append(str(batch_script))
    if not c_to_python_script.exists():
        missing.append(str(c_to_python_script))
    if not lvgl_script.exists():
        missing.append(str(lvgl_script))
    
    if missing:
        print("Error: Required helper scripts not found:", file=sys.stderr)
        for script in missing:
            print(f"  - {script}", file=sys.stderr)
        print("\nPlease ensure all helper scripts are in the helper/ directory:", file=sys.stderr)
        print("  - batch_convert_png.py", file=sys.stderr)
        print("  - c_to_python_alpha.py", file=sys.stderr)
        print("  - LVGLImage.py", file=sys.stderr)
        sys.exit(1)
    
    print("=" * 70)
    print("Python Icons Generator from PNG")
    print("=" * 70)
    print(f"PNG source:  {png_folder}")
    print(f"C output:    {c_folder}")
    print(f"Python file: {output_py_file}")
    print("=" * 70)
    print()
    
    try:
        # Step 1: Convert PNGs to C
        convert_pngs_to_c(png_folder, c_folder, batch_script, lvgl_script)
        
        # Step 2: Extract alpha and generate Python
        generate_python_file(c_folder, output_py_file, c_to_python_script)
        
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
