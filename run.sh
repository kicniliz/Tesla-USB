#!/bin/bash

# Configuration
diskId="disk2"
deviceNode="/dev/${diskId}s1"
outputDir="$HOME/Downloads/teslacam"

# Function to check if the device is a USB drive
check_usb_drive() {
    echo "=== $diskId info"
    diskutil list "$diskId"
    
    info=$(diskutil info "$diskId" | grep -E 'Protocol|Whole|Media Name|Removable')
    
    protocol=$(echo "$info" | grep -m1 Protocol | cut -d ':' -f 2 | xargs)
    whole=$(echo "$info" | grep -m1 Whole | cut -d ':' -f 2 | xargs)
    
    echo "Protocol: $protocol"
    echo "Whole: $whole"
    
    if [[ "$protocol" != *"USB"* ]]; then
        echo "Not a USB device. Exiting."
        exit 1
    fi
    
    if [[ "$whole" != "Yes" ]]; then
        echo "Not a whole USB device. Exiting."
        exit 1
    fi
    
    echo "$info"
}

# Main script
check_usb_drive

echo
read -p "Please confirm that $deviceNode is your TeslaCam USB drive? (y/n) " answer

if [[ "$answer" != "y" ]]; then 
    echo "Edit the 'diskId' variable in this script to match your USB drive."
    exit 1
fi

diskutil unmount "$deviceNode"

mkdir -p "$outputDir"

sudo ./run.py "$deviceNode" "$outputDir" 0
