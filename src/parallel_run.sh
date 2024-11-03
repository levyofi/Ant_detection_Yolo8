#!/bin/bash

# Enable stdout and stderr output to terminal and log
exec > >(tee -i output.log)
exec 2>&1

# Make the Python script executable (if not already)
chmod +x video_tracking.py

# Function to call the Python script
process_image() {
    # local model_path="$1"
    local image_file="$1"
    local output_dir="$2"
    echo "Processing file: $image_file with output directory: $output_dir"  # Debugging output
    python video_tracking.py "$image_file" "$output_dir"
}

# Export the function so that parallel can access it
export -f process_image

# model_path="/data/models-yolov8/blue_ants_refined/300epochs8batchsize8x/best.pt"

# Output directory
output_dir="/home/nathan/"

# Find image files and use null termination (-print0)
find "/data/ants_example/" -type f -name "masked_WSCT????.mov" -print0 | \
# Process images in parallel using -0 to handle null-terminated strings
parallel -0 -j 4 process_image {} "$output_dir"
