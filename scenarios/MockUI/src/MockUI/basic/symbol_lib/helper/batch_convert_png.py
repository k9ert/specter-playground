#!/usr/bin/env python3
"""
Batch convert PNG files to LVGL C array format (ARGB8888).

Usage: 
    python3 batch_convert_png.py <source_dir> <target_dir> [lvgl_script_path]

Arguments:
    source_dir: Directory containing PNG files
    target_dir: Directory where C files will be created
    lvgl_script_path: (Optional) Path to LVGLImage.py script
                     Default: looks in Bitcoin-Icons directory
"""
import os
import sys
import subprocess
from pathlib import Path


def find_lvgl_script():
    """Try to find LVGLImage.py in common locations."""
    # Try relative to this script
    script_dir = Path(__file__).parent
    
    # Common locations to check
    search_paths = [
        script_dir / "LVGLImage.py",  # Same directory
        script_dir.parent.parent / "bitcoin_icons" / "Bitcoin-Icons-0.1.10" / "LVGLImage.py",
    ]
    
    for path in search_paths:
        if path.exists():
            return path
    
    return None


def convert_pngs_to_c(source_dir, target_dir, lvgl_script_path=None):
    """
    Convert all PNG files in source_dir to C arrays in target_dir.
    
    Args:
        source_dir: Directory containing PNG files
        target_dir: Directory where C files will be created
        lvgl_script_path: Optional path to LVGLImage.py script
    
    Returns:
        bool: True if all conversions succeeded, False otherwise
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Check if source directory exists
    if not source_path.exists():
        print(f"Error: Source directory '{source_dir}' does not exist", file=sys.stderr)
        return False
    
    # Create target directory if it doesn't exist
    target_path.mkdir(parents=True, exist_ok=True)
    
    # Find or use provided LVGLImage.py script
    if lvgl_script_path:
        lvgl_script = Path(lvgl_script_path)
    else:
        lvgl_script = find_lvgl_script()
    
    if not lvgl_script or not lvgl_script.exists():
        print(f"Error: LVGLImage.py not found. Searched:", file=sys.stderr)
        if lvgl_script:
            print(f"  - {lvgl_script}", file=sys.stderr)
        print(f"\nPlease provide path as third argument:", file=sys.stderr)
        print(f"  python3 {Path(__file__).name} <source> <target> <path/to/LVGLImage.py>", file=sys.stderr)
        return False
    
    # Find all PNG files in source directory
    png_files = list(source_path.glob("*.png")) + list(source_path.glob("*.PNG"))
    
    if not png_files:
        print(f"Warning: No PNG files found in '{source_dir}'")
        return True
    
    print(f"Found {len(png_files)} PNG file(s) to convert")
    print(f"Using LVGL script: {lvgl_script}")
    
    # Convert each PNG file
    converted = 0
    failed = 0
    
    for png_file in sorted(png_files):
        # Generate output name (replace hyphens with underscores for valid C identifiers)
        base_name = png_file.stem.replace('-', '_')
        
        print(f"Converting {png_file.name} -> {base_name}.c ...", end=" ")
        
        try:
            # Run LVGLImage.py to convert the PNG
            result = subprocess.run(
                [
                    sys.executable,
                    str(lvgl_script),
                    "--ofmt", "C",
                    "--cf", "ARGB8888",
                    "-o", str(target_path),
                    "--name", base_name,
                    str(png_file)
                ],
                capture_output=True,
                text=True,
                check=True
            )
            
            print("✓")
            converted += 1
            
        except subprocess.CalledProcessError as e:
            print(f"✗ FAILED")
            print(f"  Error: {e.stderr}", file=sys.stderr)
            failed += 1
    
    print(f"\nConversion complete: {converted} successful, {failed} failed")
    return failed == 0


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 batch_convert_png.py <source_dir> <target_dir> [lvgl_script_path]")
        print()
        print("Arguments:")
        print("  source_dir: Directory containing PNG files")
        print("  target_dir: Directory where C files will be created")
        print("  lvgl_script_path: (Optional) Path to LVGLImage.py script")
        print()
        print("Example:")
        print("  python3 batch_convert_png.py ../../bitcoin_icons/png/filled ../../bitcoin_icons/c/filled")
        sys.exit(1)
    
    source_dir = sys.argv[1]
    target_dir = sys.argv[2]
    lvgl_script = sys.argv[3] if len(sys.argv) > 3 else None
    
    success = convert_pngs_to_c(source_dir, target_dir, lvgl_script)
    sys.exit(0 if success else 1)
