#!/usr/bin/env python3
"""
Merge firmware code binary with filesystem image for STM32F469.

Creates a single flashable binary with:
- 0x08000000: Bootloader/ISR vectors (16KB) - from firmware
- 0x08004000: Reserved (16KB) - filled with 0xFF
- 0x08008000: Flash filesystem (96KB) - from filesystem image
- 0x08020000: Firmware code (1920KB) - from firmware

Memory layout from stm32f469xi.ld:
    FLASH_START (rx): ORIGIN = 0x08000000, LENGTH = 16K     /* Sector 0 */
    FLASH_RSV (r)   : ORIGIN = 0x08004000, LENGTH = 16K     /* Sector 1 (reserved) */
    FLASH_FS (r)    : ORIGIN = 0x08008000, LENGTH = 96K     /* Sectors 2, 3, 4 */
    FLASH_TEXT (rx) : ORIGIN = 0x08020000, LENGTH = 1920K   /* Sectors 5 - 23 */

Usage:
    python3 merge_firmware_flash.py \\
        --firmware build-STM32F469DISC/firmware.bin \\
        --filesystem build/flash_fs.img \\
        --output bin/mockui_full.bin
"""

import argparse
import sys

# Memory layout offsets (relative to start of flash at 0x08000000)
FLASH_START_OFFSET = 0x00000000  # ISR vectors, from firmware
FLASH_START_SIZE = 16 * 1024      # 16KB

FLASH_RSV_OFFSET = 0x00004000    # Reserved sector
FLASH_RSV_SIZE = 16 * 1024        # 16KB

FLASH_FS_OFFSET = 0x00008000     # Filesystem
FLASH_FS_SIZE = 96 * 1024         # 96KB (192 sectors × 512 bytes - full FLASH_FS region)

FLASH_TEXT_OFFSET = 0x00020000   # Firmware code
FLASH_TEXT_SIZE = 1920 * 1024     # 1920KB

TOTAL_FLASH_SIZE = 2 * 1024 * 1024  # 2MB


def merge_binaries(firmware_path, filesystem_path, output_path):
    """
    Merge firmware and filesystem into single flashable binary.
    
    The firmware.bin from MicroPython build contains:
    - ISR vectors at start (FLASH_START region)
    - Code starting at FLASH_TEXT offset
    
    We extract these parts and combine with the filesystem image.
    """
    
    print(f"Reading firmware: {firmware_path}")
    with open(firmware_path, 'rb') as f:
        firmware_data = f.read()
    
    print(f"  Size: {len(firmware_data)} bytes ({len(firmware_data)/1024:.1f} KB)")
    
    print(f"Reading filesystem image: {filesystem_path}")
    with open(filesystem_path, 'rb') as f:
        fs_data = f.read()
    
    print(f"  Size: {len(fs_data)} bytes ({len(fs_data)/1024:.1f} KB)")
    
    # Validate filesystem size
    if len(fs_data) != FLASH_FS_SIZE:
        print(f"ERROR: Filesystem image must be exactly {FLASH_FS_SIZE} bytes ({FLASH_FS_SIZE/1024}KB)")
        print(f"       Got {len(fs_data)} bytes ({len(fs_data)/1024:.1f}KB)")
        return False
    
    # Create output buffer filled with 0xFF (erased flash state)
    print(f"\nCreating merged binary ({TOTAL_FLASH_SIZE/1024/1024}MB)...")
    output = bytearray([0xFF] * TOTAL_FLASH_SIZE)
    
    # The firmware.bin from MicroPython contains both ISR vectors and code
    # We need to place the entire firmware as-is starting from offset 0
    print(f"  Copying firmware ({len(firmware_data)} bytes)")
    output[0:len(firmware_data)] = firmware_data
    
    # Place filesystem image at FLASH_FS offset
    print(f"  Placing filesystem at offset 0x{FLASH_FS_OFFSET:08X} ({FLASH_FS_SIZE/1024}KB)")
    output[FLASH_FS_OFFSET:FLASH_FS_OFFSET + len(fs_data)] = fs_data
    
    # Write merged binary
    print(f"\nWriting merged binary: {output_path}")
    with open(output_path, 'wb') as f:
        f.write(output)
    
    print(f"✓ Merged binary created successfully")
    print(f"  Total size: {len(output)} bytes ({len(output)/1024/1024:.1f} MB)")
    print(f"\nMemory layout:")
    print(f"  0x08000000-0x08003FFF: ISR vectors (16KB) - from firmware")
    print(f"  0x08004000-0x08007FFF: Reserved (16KB) - erased (0xFF)")
    print(f"  0x08008000-0x0801FFFF: Filesystem (96KB) - from {filesystem_path}")
    print(f"  0x08020000-0x081FFFFF: Code (~{(len(firmware_data)-FLASH_TEXT_OFFSET)/1024:.0f}KB) - from firmware")
    
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Merge firmware and filesystem images for STM32F469'
    )
    parser.add_argument(
        '--firmware',
        required=True,
        help='Firmware binary (firmware.bin from MicroPython build)'
    )
    parser.add_argument(
        '--filesystem',
        required=True,
        help='Filesystem image (96KB littlefs image)'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output merged binary'
    )
    
    args = parser.parse_args()
    
    if not merge_binaries(args.firmware, args.filesystem, args.output):
        sys.exit(1)


if __name__ == '__main__':
    main()
