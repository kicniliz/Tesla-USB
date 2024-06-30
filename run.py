#!/usr/bin/python

import os
import sys
import struct

def dump_binary(data):
    """Used for debugging: prints binary data in hexadecimal format."""
    for offset, byte in enumerate(data):
        print(f'{ord(byte):02X} ', end='')
        if (offset + 1) % 16 == 0:
            print()
        elif (offset + 1) % 8 == 0:
            print(' ', end='')
    print()

def sect_to_byte(sect):
    return sect * bytes_per_sector

def clust_to_byte(clust):
    return sect_to_byte(reserved_sectors + number_of_fats * sectors_per_fat +
                        max_root_dir_entries * 32 // bytes_per_sector +
                        (clust - 2) * sectors_per_cluster)

def is_nonzero(data):
    return any(ord(x) != 0x00 for x in data)

def read_boot_sector(file):
    boot_sector = file.read(512)
    return {
        'bytes_per_sector': struct.unpack("<H", boot_sector[0x0B:0x0D])[0],
        'sectors_per_cluster': struct.unpack("<B", boot_sector[0x0D])[0],
        'reserved_sectors': struct.unpack("<H", boot_sector[0x0E:0x10])[0],
        'number_of_fats': struct.unpack("<B", boot_sector[0x10])[0],
        'max_root_dir_entries': struct.unpack("<H", boot_sector[0x11:0x13])[0],
        'total_sectors': struct.unpack("<H", boot_sector[0x13:0x15])[0],
        'sectors_per_fat': struct.unpack("<I", boot_sector[0x24:0x28])[0],
        'root_directory_cluster': struct.unpack("<I", boot_sector[0x2c:0x30])[0]
    }

def read_fat(file, start_offset, sectors_per_fat, bytes_per_sector):
    file.seek(start_offset)
    fat = file.read(sectors_per_fat * bytes_per_sector)
    return [struct.unpack("<I", fat[j:j+4])[0] & 0x0FFFFFFF
            for j in range(0, len(fat), 4)]

def read_directory(file, directory_cluster, tabs, path='/', root=False):
    pad = '\t' * tabs
    while True:
        file.seek(clust_to_byte(directory_cluster))
        lfn = ''
        for _ in range(bytes_per_cluster // 32):
            entry = file.read(32)
            attributes = ord(entry[11])
            
            if attributes == 0x0F:  # Long file name
                lfn = entry[0x01:0x0B] + entry[0x0E:0x1A] + entry[0x1C:0x20] + lfn
                continue
            
            short_filename = entry[0:8].decode('ascii').strip()
            extension = entry[8:11].decode('ascii').strip()
            cluster = (struct.unpack("<H", entry[0x14:0x16])[0] << 16) | struct.unpack("<H", entry[0x1A:0x1C])[0]
            filesize = struct.unpack("<I", entry[28:32])[0]
            
            if attributes == 0 and cluster == 0:
                continue
            
            filename = lfn.replace('\xff', '').replace('\0', '') if lfn else f"{short_filename}.{extension}"
            
            print(f"\n{pad}Filename: {filename}")
            print(f"{pad}Attributes: 0x{attributes:02X}")
            print(f"{pad}Filesize: {filesize}")
            
            # Print last modified time and clusters
            # (implementation omitted for brevity)
            
            if attributes & 0x10 and short_filename not in ['.', '..']:
                print(f"{pad}Entering directory...")
                os.makedirs(f"{output_dir}{path}{filename}", exist_ok=True)
                previous_position = file.tell()
                read_directory(file, cluster, tabs + 1, f"{path}{filename}/")
                file.seek(previous_position)
            elif short_filename not in ['.', '..'] and filesize != 0xFFFFFFFF:
                # File export logic here (omitted for brevity)
                pass
            
            lfn = ''
        
        directory_cluster = fat_entries[directory_cluster]
        if (directory_cluster & 0xFFFFFF8) == 0xFFFFFF8:
            break

def extract_mp4s(file, start_cluster, end_cluster, max_size):
    os.makedirs(f"{output_dir}/mp4s", exist_ok=True)
    
    print(f"--- Extracting MP4s from cluster {start_cluster} to {end_cluster}")
    
    for cluster in range(start_cluster, end_cluster):
        if cluster % 1000 == 0:
            print(f"- Processing cluster {cluster}")
        
        file.seek(clust_to_byte(cluster))
        header = file.read(12)
        
        if header == b'\0\0\0 ftypmp42':
            print(f"Found MP4 at cluster {cluster}")
            with open(f"{output_dir}/mp4s/{cluster}.mp4", 'wb') as fout:
                cur_cluster = cluster
                bytes_written = 0
                while bytes_written < max_size:
                    file.seek(clust_to_byte(cur_cluster))
                    data = file.read(bytes_per_cluster)
                    if bytes_written > 0 and data[:12] == b'\0\0\0 ftypmp42':
                        break
                    fout.write(data)
                    bytes_written += bytes_per_cluster
                    cur_cluster += 1

def main():
    if len(sys.argv) < 3:
        print("Teslacam recovery tool")
        print(f"Usage: {sys.argv[0]} input output_dir [starting_cluster]")
        print(f"Ex:    {sys.argv[0]} /dev/disk2s1 ~/Downloads/")
        sys.exit(1)

    input_file = sys.argv[1]
    global output_dir
    output_dir = sys.argv[2]
    starting_cluster = int(sys.argv[3]) if len(sys.argv) >= 4 else 0

    with open(input_file, 'rb') as f:
        boot_info = read_boot_sector(f)
        globals().update(boot_info)  # Add boot sector info to global namespace

        global bytes_per_cluster
        bytes_per_cluster = bytes_per_sector * sectors_per_cluster

        total_clusters = total_sectors // sectors_per_cluster

        print("File system information:")
        for key, value in boot_info.items():
            print(f"{key.replace('_', ' ').capitalize()}: {value}")
        print(f"Total clusters: {total_clusters}")

        global fat_entries
        fat_entries = read_fat(f, sect_to_byte(reserved_sectors), sectors_per_fat, bytes_per_sector)

        # Uncomment to read directories
        # print("Reading directories...")
        # read_directory(f, root_directory_cluster, 1)

        print("--- Finding MP4 files...")
        extract_mp4s(f, starting_cluster, total_clusters, 40_000_000)

if __name__ == "__main__":
    main()