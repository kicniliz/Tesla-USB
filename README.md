# USB Drive Data Recovery Tool

This tool is designed to recover video files from FAT32 USB drives, particularly those used in certain vehicle recording systems. It can retrieve footage that may no longer be directly accessible through normal means.

The repository contains a Python script that scans a FAT32 USB drive for MP4 files that are no longer listed in the file system, and copies them to a directory for viewing.

Note: This tool is intended for users with some technical knowledge of Python and file systems.

# Instructions

These instructions are primarily for macOS users. Linux users should find the process very similar, and Windows users may need to make minor adjustments.

1. Connect your USB drive to your computer.
2. Run the script: `./run.sh`
3. Follow the on-screen prompts.

Please note that this process can be time-consuming and may require significant free disk space (potentially up to twice the capacity of your drive).

Once the script is running, you should see video files being recovered to the specified directory.

# Advanced Usage

For users with more specific needs or limited disk space, the script includes functionality for navigating the file system, printing detailed information, and exporting individual files. If you're familiar with Python, you can modify the script to perform a more targeted search for specific files.

Some recording systems store files contiguously and in order. If you can locate the cluster for an intact file near your time frame of interest, you may be able to scan a subset of clusters instead of the entire disk. See the comments in run.py for more details.

# Handling Unplayable MP4s

If some of the recovered MP4 files don't play, it's likely because they were fragmented across multiple cluster runs. This can occur when the recording system needs to write around previously saved videos. The script doesn't automatically extract these fragmented files, but you can do so manually with some effort.

The filename of each MP4 indicates the start cluster of the file. To extract a fragmented video, you should read all clusters starting from that point, skipping over clusters used by active file system entries. (This process could potentially be automated with additional scripting; contributions are welcome.)
