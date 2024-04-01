#!/bin/bash

# safelink.sh

# Using ln -s, make a file at TO_PATH that behaves as if it were the file at FROM_PATH

# Typically called the "target" of a link, it is the actual file that contains data
FROM_PATH="$1"
# Typically called the "name" of a link, it is the new file which behaves like the actual file but really is a link file
TO_PATH="$2"

# Check if TO_PATH already exists as a link or a regular file
if [ -e "$TO_PATH" ]; then
    echo "The path $TO_PATH already exists. Removing it."
    # Remove the existing file/link
    rm -f "$TO_PATH"
fi

# Create a new symbolic link from FROM_PATH to TO_PATH
ln -s "$FROM_PATH" "$TO_PATH"
echo "Symbolic link created from $FROM_PATH to $TO_PATH."
