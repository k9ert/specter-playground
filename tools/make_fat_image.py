#!/usr/bin/env python3
"""
Create a FAT12 filesystem image for STM32F469 internal flash storage.

Replicates what MicroPython's factory_reset_create_filesystem() does:
    f_mkfs(&vfs.fatfs, FM_FAT, 0, working_buf, sizeof(working_buf))
    f_setlabel(&vfs.fatfs, "pybflash")

Parameters matched to STM32F469 flashbdev.c / oofatfs ff.c:
  - Sector size: 512 bytes
  - Total sectors: 96KB / 512 = 192 sectors (FLASH_FS region)
  - FAT type: FAT12 (auto-selected by oofatfs for small volumes)
  - FATs: 1
  - Root dir entries: 512 (oofatfs default for FM_FAT)
  - Volume label: "pybflash"
  - Cluster size: 1 sector (auto for small volume, 1 sector = 512 bytes)

Usage:
    python3 tools/make_fat_image.py \\
        --source build/flash_image \\
        --output build/flash_fs.img

    # With explicit label:
    python3 tools/make_fat_image.py \\
        --source build/flash_image \\
        --output build/flash_fs.img \\
        --label pybflash
"""

import argparse
import os
import struct
import sys
from pathlib import Path

# --- Geometry (must match STM32F469 MicroPython config) ---
SECTOR_SIZE = 512           # FF_MAX_SS = 512 in oofatfs ffconf.h
TOTAL_SECTORS = 192         # 96KB / 512 = 192  (FLASH_FS region)
NUM_FATS = 1                # oofatfs uses 1 FAT for FM_FAT on small volumes
ROOT_DIR_ENTRIES = 512      # oofatfs default n_rootdir
CLUSTER_SIZE = 1            # sectors per cluster (auto → 1 for small volumes)
RESERVED_SECTORS = 1        # standard FAT12: 1 reserved sector (boot sector)
VOLUME_LABEL = "pybflash"  # MICROPY_HW_FLASH_FS_LABEL default

# Derived geometry
ROOT_DIR_SECTORS = (ROOT_DIR_ENTRIES * 32 + SECTOR_SIZE - 1) // SECTOR_SIZE  # = 32
DATA_SECTORS = TOTAL_SECTORS - RESERVED_SECTORS - ROOT_DIR_SECTORS  # to be adjusted after FAT sectors known
# FAT12: each entry = 1.5 bytes; clusters = (DATA_SECTORS / CLUSTER_SIZE)
# FAT size in sectors (iterative calc below)


def _calc_fat12_size(total_sectors, reserved, num_fats, root_sectors, spc):
    """Calculate FAT12 table size in sectors (iterated to converge)."""
    # Initial guess: no FAT space
    fat_size = 0
    for _ in range(8):  # iterate to convergence
        data_secs = total_sectors - reserved - num_fats * fat_size - root_sectors
        n_clust = data_secs // spc
        # FAT12: 12 bits per cluster, round up to sector boundary
        fat_bytes = (n_clust + 2) * 3 // 2   # +2 for reserved entries 0 and 1
        fat_size = (fat_bytes + SECTOR_SIZE - 1) // SECTOR_SIZE
    return fat_size, n_clust


def _pack_fat12(entries):
    """Pack a list of 12-bit FAT12 entries into bytes."""
    buf = bytearray()
    i = 0
    while i < len(entries):
        lo = entries[i]
        hi = entries[i + 1] if i + 1 < len(entries) else 0
        # two 12-bit values packed into 3 bytes: lo[7:0], hi[3:0]lo[11:8], hi[11:4]
        buf.append(lo & 0xFF)
        buf.append(((lo >> 8) & 0x0F) | ((hi & 0x0F) << 4))
        buf.append((hi >> 4) & 0xFF)
        i += 2
    return buf


def _needs_lfn(name):
    """Check if a filename requires Long File Name entries."""
    if len(name) > 12:
        return True
    if '.' in name:
        base, ext = name.rsplit('.', 1)
        if len(base) > 8 or len(ext) > 3:
            return True
    elif len(name) > 8:
        return True
    # Check for lowercase or special chars that 8.3 can't represent
    for c in name:
        if c.islower() or c in ' +,;=[]':
            return True
    return False


def _dos83(name, existing_short_names=None):
    """Convert a filename to FAT 8.3 format (11 bytes, space-padded).
    
    If the name needs LFN, generate a ~N short name to avoid collisions.
    existing_short_names: set of already-used 11-byte short names (for uniqueness).
    """
    if existing_short_names is None:
        existing_short_names = set()
    
    upper_name = name.upper()
    if '.' in upper_name:
        base, ext = upper_name.rsplit('.', 1)
    else:
        base, ext = upper_name, ''
    ext = ext[:3].ljust(3)
    
    if not _needs_lfn(name):
        # Simple 8.3 name
        result = (base[:8].ljust(8) + ext).encode('ascii')
        return result
    
    # Strip invalid chars for short name basis
    basis = ''
    for c in base:
        if c.isalnum() or c in '_-':
            basis += c
    basis = basis[:6]  # Leave room for ~N
    
    # Generate unique ~N suffix
    for n in range(1, 100):
        suffix = f'~{n}'
        short_base = (basis[:8 - len(suffix)] + suffix).ljust(8)
        candidate = (short_base + ext).encode('ascii')
        if candidate not in existing_short_names:
            return candidate
    
    # Fallback (shouldn't happen with <100 files)
    return (basis[:6] + '~1').ljust(8).encode('ascii') + ext.encode('ascii')


def _lfn_checksum(short_name_11):
    """Compute the LFN checksum over an 11-byte 8.3 directory name."""
    chk = 0
    for b in short_name_11:
        chk = ((chk & 1) * 0x80 + (chk >> 1) + b) & 0xFF
    return chk


def _make_lfn_entries(long_name, short_name_11):
    """Create LFN directory entries (in disk order: last ordinal first).
    
    Returns a list of 32-byte entries to prepend before the 8.3 entry.
    """
    ATTR_LFN = 0x0F
    chk = _lfn_checksum(short_name_11)
    
    # Encode name as UTF-16LE, pad with 0xFFFF after null terminator
    ucs2 = long_name.encode('utf-16-le')
    # Add null terminator (2 bytes)
    ucs2 += b'\x00\x00'
    # Pad to multiple of 26 bytes (13 chars × 2 bytes each)
    while len(ucs2) % 26 != 0:
        ucs2 += b'\xFF\xFF'
    
    n_entries = len(ucs2) // 26
    entries = []
    
    for i in range(n_entries):
        ordinal = i + 1
        if i == n_entries - 1:
            ordinal |= 0x40  # Last LFN entry marker
        
        chunk = ucs2[i * 26:(i + 1) * 26]
        entry = bytearray(32)
        entry[0] = ordinal
        entry[1:11] = chunk[0:10]    # Chars 1-5
        entry[11] = ATTR_LFN
        entry[12] = 0                # Type
        entry[13] = chk              # Checksum
        entry[14:26] = chunk[10:22]  # Chars 6-11
        entry[26:28] = b'\x00\x00'   # First cluster (always 0)
        entry[28:32] = chunk[22:26]  # Chars 12-13
        entries.append(bytes(entry))
    
    # Reverse: on disk, highest ordinal comes first
    entries.reverse()
    return entries


def _fat_date(year=2026, month=2, day=19):
    return ((year - 1980) << 9) | (month << 5) | day


def _fat_time(hour=0, minute=0, second=0):
    return (hour << 11) | (minute << 5) | (second // 2)


def make_fat_image(source_dir, output_path, label=VOLUME_LABEL, total_sectors=TOTAL_SECTORS):
    """
    Build a FAT12 image containing all files from source_dir tree.
    Matches MicroPython's f_mkfs(FM_FAT) output for the STM32F469.
    """
    label = label.upper()[:11].ljust(11)

    spc = CLUSTER_SIZE  # sectors per cluster
    fat_size, n_clust = _calc_fat12_size(total_sectors, RESERVED_SECTORS, NUM_FATS, ROOT_DIR_SECTORS, spc)

    # Re-derive final data area layout
    data_start = RESERVED_SECTORS + NUM_FATS * fat_size + ROOT_DIR_SECTORS
    data_sectors = total_sectors - data_start
    actual_clusters = data_sectors // spc

    print(f"FAT12 geometry:")
    print(f"  Total sectors : {total_sectors}  ({total_sectors * SECTOR_SIZE // 1024} KB)")
    print(f"  Reserved      : {RESERVED_SECTORS}")
    print(f"  FAT sectors   : {fat_size} × {NUM_FATS} FAT(s)")
    print(f"  Root dir secs : {ROOT_DIR_SECTORS}  ({ROOT_DIR_ENTRIES} entries)")
    print(f"  Data start    : sector {data_start}")
    print(f"  Data clusters : {actual_clusters}  ({actual_clusters * spc * SECTOR_SIZE // 1024} KB)")

    # ---- Collect files from source directory ----
    files = []  # list of (rel_path_parts, bytes)
    if source_dir and os.path.isdir(source_dir):
        for root, dirs, filenames in os.walk(source_dir):
            dirs.sort()
            for fname in sorted(filenames):
                fpath = os.path.join(root, fname)
                rel = os.path.relpath(fpath, source_dir)
                parts = Path(rel).parts
                with open(fpath, 'rb') as f:
                    data = f.read()
                files.append((parts, data))
                print(f"  + {rel}  ({len(data)} bytes)")

    # ---- Allocate clusters ----
    # FAT chain: cluster 0 and 1 are reserved; data starts at cluster 2
    fat = [0] * (actual_clusters + 2)
    fat[0] = 0xFF8   # media type
    fat[1] = 0xFFF   # end-of-chain marker

    # Cluster → sector (in data area)
    def cluster_to_sector(c):
        return data_start + (c - 2) * spc

    next_free_cluster = 2

    def alloc_file(data):
        """Allocate clusters for file data, return (first_cluster, chain)."""
        nonlocal next_free_cluster
        if len(data) == 0:
            return 0, []
        n_needed = (len(data) + SECTOR_SIZE * spc - 1) // (SECTOR_SIZE * spc)
        if next_free_cluster + n_needed - 1 >= actual_clusters + 2:
            raise RuntimeError(f"Not enough space: need {n_needed} clusters, only {actual_clusters + 2 - next_free_cluster} free")
        chain = list(range(next_free_cluster, next_free_cluster + n_needed))
        first = chain[0]
        for i, c in enumerate(chain):
            fat[c] = chain[i + 1] if i + 1 < len(chain) else 0xFFF
        next_free_cluster += n_needed
        return first, chain

    # ---- Build directory structure ----
    # Root dir: flat list of direntry dicts
    # Subdirs: stored as files within root dir (one level deep supported)

    # We need to lay out:
    #   - Root dir entries (512 slots × 32 bytes = 16 KB)
    #   - Subdir cluster contents
    #   - File data clusters

    # Two-pass: first build the tree structure, then emit

    class DirEntry:
        def __init__(self, name83, attr, first_cluster, size, date, time):
            self.name83 = name83          # 11 bytes
            self.attr = attr              # 1 byte
            self.first_cluster = first_cluster  # uint16
            self.size = size              # uint32
            self.date = date              # uint16
            self.time = time              # uint16

        def pack(self):
            # FAT directory entry: 32 bytes total
            # Offset 0:  8+3 name (11 bytes)
            # Offset 11: attr (1), NTRes (1), CrtTimeTenth (1)
            # Offset 14: CrtTime (2), CrtDate (2), LstAccDate (2)
            # Offset 20: FstClusHI (2)  <- always 0 for FAT12
            # Offset 22: WrtTime (2), WrtDate (2)
            # Offset 26: FstClusLO (2)
            # Offset 28: FileSize (4)
            entry = bytearray(32)
            entry[0:11] = self.name83
            entry[11] = self.attr
            entry[12] = 0           # NTRes
            entry[13] = 0           # CrtTimeTenth
            struct.pack_into('<H', entry, 14, self.time)         # CrtTime
            struct.pack_into('<H', entry, 16, self.date)         # CrtDate
            struct.pack_into('<H', entry, 18, self.date)         # LstAccDate
            struct.pack_into('<H', entry, 20, 0)                 # FstClusHI
            struct.pack_into('<H', entry, 22, self.time)         # WrtTime
            struct.pack_into('<H', entry, 24, self.date)         # WrtDate
            struct.pack_into('<H', entry, 26, self.first_cluster)  # FstClusLO
            struct.pack_into('<I', entry, 28, self.size)         # FileSize
            return bytes(entry)

    ATTR_READ_ONLY = 0x01
    ATTR_DIRECTORY = 0x10
    ATTR_VOLUME_ID = 0x08

    date_val = _fat_date()
    time_val = _fat_time()

    root_entries = []  # list of (lfn_prefix_bytes, DirEntry)
    # Volume label entry (never needs LFN)
    vol_entry = DirEntry(label.encode('ascii'), ATTR_VOLUME_ID, 0, 0, date_val, time_val)
    root_entries.append((b'', vol_entry))

    # Track short names per directory for uniqueness
    root_short_names = set()
    # Map: subdir_name → [(lfn_prefix_bytes, DirEntry)]
    subdirs = {}
    subdir_short_names = {}  # per-subdir short name tracking

    # Separate files into root-level and one level of subdirectories
    for parts, data in files:
        if len(parts) == 1:
            # Root-level file
            fname = parts[0]
            fc, _ = alloc_file(data)
            short_name = _dos83(fname, root_short_names)
            root_short_names.add(short_name)
            e = DirEntry(short_name, 0x20, fc, len(data), date_val, time_val)
            e._data = data
            e._chain = _ if _ else []
            # Generate LFN entries if needed
            lfn_prefix = b''
            if _needs_lfn(fname):
                lfn_entries = _make_lfn_entries(fname, short_name)
                lfn_prefix = b''.join(lfn_entries)
            root_entries.append((lfn_prefix, e))
        elif len(parts) == 2:
            # One-level subdir
            dname, fname = parts[0].upper(), parts[1]
            if dname not in subdirs:
                subdirs[dname] = []
                subdir_short_names[dname] = set()
            fc, chain = alloc_file(data)
            short_name = _dos83(fname, subdir_short_names[dname])
            subdir_short_names[dname].add(short_name)
            e = DirEntry(short_name, 0x20, fc, len(data), date_val, time_val)
            e._data = data
            e._chain = chain
            # Generate LFN entries if needed
            lfn_prefix = b''
            if _needs_lfn(fname):
                lfn_entries = _make_lfn_entries(fname, short_name)
                lfn_prefix = b''.join(lfn_entries)
            subdirs[dname].append((lfn_prefix, e))
        else:
            print(f"WARNING: Deeper than 1-level nesting not supported: {'/'.join(parts)}", file=sys.stderr)

    # Create subdir entries in root
    for dname, dentries in sorted(subdirs.items()):
        # Build subdir cluster content (. and .. + file entries with LFN)
        dot_cluster_placeholder = next_free_cluster  # will be updated after alloc
        
        # Serialize subdir content: dot entries + LFN/file entries
        dot_entry = DirEntry(b'.          ', ATTR_DIRECTORY, dot_cluster_placeholder, 0, date_val, time_val)
        dotdot_entry = DirEntry(b'..         ', ATTR_DIRECTORY, 0, 0, date_val, time_val)
        
        subdir_bytes = dot_entry.pack() + dotdot_entry.pack()
        for lfn_prefix, fe in dentries:
            subdir_bytes += lfn_prefix + fe.pack()
        
        # Pad to cluster boundary
        cluster_bytes = spc * SECTOR_SIZE
        pad_len = (-len(subdir_bytes)) % cluster_bytes
        subdir_bytes += b'\x00' * pad_len

        # Alloc subdir cluster(s)
        fc_dir, chain_dir = alloc_file(subdir_bytes)

        # Fix up '.' entry first_cluster now that we know it
        dot_entry.first_cluster = fc_dir
        # Re-serialize with corrected '.' cluster
        subdir_bytes = dot_entry.pack() + dotdot_entry.pack()
        for lfn_prefix, fe in dentries:
            subdir_bytes += lfn_prefix + fe.pack()
        pad_len = (-len(subdir_bytes)) % cluster_bytes
        subdir_bytes += b'\x00' * pad_len

        # Add to root (directory names are always short/uppercase, no LFN needed)
        dir_short_name = _dos83(dname, root_short_names)
        root_short_names.add(dir_short_name)
        e_dir = DirEntry(dir_short_name, ATTR_DIRECTORY, fc_dir, 0, date_val, time_val)
        e_dir._data = subdir_bytes
        e_dir._chain = chain_dir
        root_entries.append((b'', e_dir))

    # ---- Assemble image ----
    image = bytearray(b'\xFF' * (total_sectors * SECTOR_SIZE))

    # --- Boot Sector (sector 0) ---
    oem = b'MSDOS5.0'
    boot = bytearray(SECTOR_SIZE)
    # Jump boot
    boot[0:3] = b'\xEB\x3C\x90'
    # OEM name
    boot[3:11] = oem
    # BPB
    struct.pack_into('<H', boot, 11, SECTOR_SIZE)          # BytsPerSec
    boot[13] = spc                                         # SecPerClus
    struct.pack_into('<H', boot, 14, RESERVED_SECTORS)     # RsvdSecCnt
    boot[16] = NUM_FATS                                    # NumFATs
    struct.pack_into('<H', boot, 17, ROOT_DIR_ENTRIES)     # RootEntCnt
    struct.pack_into('<H', boot, 19, total_sectors & 0xFFFF)  # TotSec16
    boot[21] = 0xF8                                        # Media (fixed disk)
    struct.pack_into('<H', boot, 22, fat_size)             # FATSz16
    struct.pack_into('<H', boot, 24, 63)                   # SecPerTrk (dummy)
    struct.pack_into('<H', boot, 26, 255)                  # NumHeads (dummy)
    struct.pack_into('<I', boot, 28, 0)                    # HiddSec
    struct.pack_into('<I', boot, 32, 0)                    # TotSec32 (0 since TotSec16 set)
    # Extended BPB (FAT12/16)
    boot[36] = 0x80                                        # DrvNum
    boot[37] = 0                                           # Reserved1
    boot[38] = 0x29                                        # BootSig
    struct.pack_into('<I', boot, 39, 0x12345678)           # VolID
    boot[43:54] = label.encode('ascii')                    # VolLab
    boot[54:62] = b'FAT12   '                              # FilSysType
    boot[510] = 0x55                                       # Signature
    boot[511] = 0xAA
    image[0:SECTOR_SIZE] = boot

    # --- FAT table(s) ---
    fat_bytes = _pack_fat12(fat)
    fat_sector_data = fat_bytes + b'\x00' * (fat_size * SECTOR_SIZE - len(fat_bytes))
    if len(fat_sector_data) > fat_size * SECTOR_SIZE:
        fat_sector_data = fat_sector_data[:fat_size * SECTOR_SIZE]
    for f_idx in range(NUM_FATS):
        offset = (RESERVED_SECTORS + f_idx * fat_size) * SECTOR_SIZE
        image[offset:offset + len(fat_sector_data)] = fat_sector_data

    # --- Root directory ---
    root_bytes = b''
    for lfn_prefix, e in root_entries:
        root_bytes += lfn_prefix + e.pack()
    # Pad to full root dir area
    root_area = ROOT_DIR_SECTORS * SECTOR_SIZE
    root_bytes = root_bytes[:root_area].ljust(root_area, b'\x00')
    root_offset = (RESERVED_SECTORS + NUM_FATS * fat_size) * SECTOR_SIZE
    image[root_offset:root_offset + root_area] = root_bytes

    # --- File and subdir data clusters ---
    def write_data_to_clusters(chain, data):
        padded = data + b'\xFF' * ((-len(data)) % (spc * SECTOR_SIZE))
        for i, c in enumerate(chain):
            sec = cluster_to_sector(c)
            chunk = padded[i * spc * SECTOR_SIZE:(i + 1) * spc * SECTOR_SIZE]
            off = sec * SECTOR_SIZE
            image[off:off + len(chunk)] = chunk

    for _lfn_prefix, e in root_entries:
        if hasattr(e, '_chain') and e._chain:
            write_data_to_clusters(e._chain, e._data)

    # Handle file entries inside subdirs
    for dname, dentries in subdirs.items():
        for _lfn_prefix, fe in dentries:
            if hasattr(fe, '_chain') and fe._chain:
                write_data_to_clusters(fe._chain, fe._data)

    # ---- Write output ----
    with open(output_path, 'wb') as f:
        f.write(image)
    print(f"\n✓ FAT12 image written: {output_path}  ({len(image)} bytes, {len(image)//1024} KB)")
    return True


def main():
    parser = argparse.ArgumentParser(
        description='Create a FAT12 filesystem image for STM32F469 MicroPython flash storage'
    )
    parser.add_argument('--source', required=True, help='Source directory of files to include')
    parser.add_argument('--output', required=True, help='Output image file path')
    parser.add_argument('--label', default=VOLUME_LABEL, help=f'Volume label (default: {VOLUME_LABEL})')
    parser.add_argument('--sectors', type=int, default=TOTAL_SECTORS,
                        help=f'Total sectors (default: {TOTAL_SECTORS} = 96KB)')
    args = parser.parse_args()

    ok = make_fat_image(args.source, args.output, label=args.label, total_sectors=args.sectors)
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
