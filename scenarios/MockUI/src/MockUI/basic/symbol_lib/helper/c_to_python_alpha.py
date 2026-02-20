#!/usr/bin/env python3
"""
Extract alpha channel from LVGL C array files (ARGB8888 format) and convert to Python Icon format.

The C files store data as BGRA (Blue, Green, Red, Alpha) - we extract only the Alpha channel.

Usage:
    python3 c_to_python_alpha.py <c_file1> [c_file2 ...]
    
Example:
    python3 c_to_python_alpha.py ../../bitcoin_icons/c/filled/wallet.c
"""
import re
import sys


def extract_alpha_from_c_array(c_file_path):
    """
    Extract the alpha channel from an ARGB8888 C array file.
    
    ARGB8888 is stored as BGRA in memory (little-endian):
    [Blue, Green, Red, Alpha] for each pixel
    
    We extract every 4th byte (the Alpha channel).
    
    Args:
        c_file_path: Path to the C file containing ARGB8888 bitmap data
        
    Returns:
        tuple: (name, width, height, alpha_values)
    """
    with open(c_file_path, 'r') as f:
        content = f.read()
    
    # Find the array data between braces
    match = re.search(r'uint8_t\s+(\w+)_map\[\]\s+=\s+\{([^}]+)\}', content, re.DOTALL)
    if not match:
        raise ValueError(f"Could not find bitmap array in {c_file_path}")
    
    name = match.group(1)
    array_str = match.group(2)
    
    # Extract all hex values
    hex_values = re.findall(r'0x[0-9a-fA-F]{2}', array_str)
    
    # ARGB8888 format: each pixel is 4 bytes [Blue, Green, Red, Alpha]
    # Extract only the alpha channel (every 4th byte starting from index 3)
    alpha_values = []
    for i in range(3, len(hex_values), 4):  # Start at index 3, step by 4
        alpha_values.append(hex_values[i])
    
    # Find dimensions from the image descriptor
    width_match = re.search(r'\.w\s*=\s*(\d+)', content)
    height_match = re.search(r'\.h\s*=\s*(\d+)', content)
    
    if not width_match or not height_match:
        raise ValueError(f"Could not find dimensions in {c_file_path}")
    
    width = int(width_match.group(1))
    height = int(height_match.group(1))
    
    # Verify we have the right number of alpha values
    expected_pixels = width * height
    if len(alpha_values) != expected_pixels:
        raise ValueError(
            f"Alpha channel mismatch: expected {expected_pixels} pixels "
            f"({width}x{height}), got {len(alpha_values)}"
        )
    
    return name, width, height, alpha_values


def format_as_python_icon(name, width, height, alpha_values):
    """
    Format the alpha channel data as Python Icon code.
    
    Args:
        name: Icon variable name
        width: Icon width in pixels
        height: Icon height in pixels
        alpha_values: List of alpha hex values (as strings like '0xff')
        
    Returns:
        str: Python code for Icon definition
    """
    # Group into rows matching the image width (one row per pixel row)
    rows = []
    for i in range(0, len(alpha_values), width):
        row = alpha_values[i:i+width]
        rows.append('            ' + ', '.join(row) + ',')
    
    alpha_data = '\n'.join(rows)
    
    python_code = f'''    # {name.upper()} icon - {width}x{height} pixels
    {name.upper()} = Icon(
        pattern=bytes([
{alpha_data}
        ]),
        width={width},
        height={height}
    )'''
    
    return python_code


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 c_to_python_alpha.py <c_file1> [c_file2 ...]")
        print()
        print("Extracts alpha channel from ARGB8888 C arrays and generates Python Icon code.")
        print()
        print("Example:")
        print("  python3 c_to_python_alpha.py ../../bitcoin_icons/c/filled/wallet.c")
        sys.exit(1)
    
    for c_file in sys.argv[1:]:
        try:
            name, width, height, alpha_values = extract_alpha_from_c_array(c_file)
            python_code = format_as_python_icon(name, width, height, alpha_values)
            print(python_code)
            print()
        except Exception as e:
            print(f"Error processing {c_file}: {e}", file=sys.stderr)
            sys.exit(1)
