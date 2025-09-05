import os
import csv
import argparse
from PIL import Image
import numpy as np
from collections import defaultdict
import time

def check_gap_conditions(image_array, row, col, grayscale_min=5, grayscale_max=30, contiguous_pixels=20):
    """
    Check whether the pixel points meet the GAP condition:
    (1) Grayscale value between 5–30 (inclusive)
    (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition.
    """
    height, width = image_array.shape
    pixel_value = image_array[row, col]
    
    # Check first condition: grayscale value between 5-30
    if not (grayscale_min <= pixel_value <= grayscale_max):
        return False
    
    # Check second condition: at least one adjacent direction has 20 contiguous pixels
    # Direction vectors: up, right, down, left
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    
    for dr, dc in directions:
        contiguous_count = 0
        
        # Check pixels in this direction
        for i in range(1, contiguous_pixels + 1):
            r, c = row + i * dr, col + i * dc
            
            # Check if within image boundaries
            if 0 <= r < height and 0 <= c < width:
                if grayscale_min <= image_array[r, c] <= grayscale_max:
                    contiguous_count += 1
                else:
                    break
            else:
                break
        
        if contiguous_count >= contiguous_pixels - 1:  # -1 because we're not counting the pixel itself
            return True
    
    return False

def calculate_gap_height(gap_pixels, resolution):
    """
    Calculate GAP height per column.
    GAP_height = [(max_row - min_row + 1) × resolution] μm
    """
    column_heights = {}
    
    # Group GAP pixels by column
    column_pixels = defaultdict(list)
    for row, col in gap_pixels:
        column_pixels[col].append(row)
    
    # Calculate height for each column
    for col, rows in column_pixels.items():
        if rows:
            min_row = min(rows)
            max_row = max(rows)
            height_um = (max_row - min_row + 1) * resolution
            column_heights[col] = height_um
    
    return column_heights

def process_images(input_directory, resolution):
    """
    Process all images in the directory whose filenames start with "Li_"
    """
    # Ensure output directory exists
    output_dir = os.path.join(os.path.dirname(input_directory), "ALL_RESULT", "CLAUDE", "T1S2", "backup7")
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all image files with "Li_" prefix
    image_files = [f for f in os.listdir(input_directory) 
                  if f.startswith("Li_") and (f.lower().endswith('.png') or f.lower().endswith('.jpg'))]
    
    for image_file in image_files:
        print(f"Processing {image_file}...")
        image_path = os.path.join(input_directory, image_file)
        
        # Open image and convert to grayscale
        with Image.open(image_path) as img:
            grayscale_img = img.convert('L')
            image_array = np.array(grayscale_img)
            
            # Create a copy of the original image for highlighting GAP pixels
            highlighted_img = img.convert('RGB')
            highlighted_array = np.array(highlighted_img)
            
            height, width = image_array.shape
            
            # Analyze each pixel
            pixel_data = []
            gap_pixels = []
            
            for row in range(height):
                for col in range(width):
                    grayscale_value = image_array[row, col]
                    is_gap = 1 if check_gap_conditions(image_array, row, col) else 0
                    
                    pixel_data.append((row, col, grayscale_value, is_gap))
                    
                    if is_gap:
                        gap_pixels.append((row, col))
                        # Highlight GAP pixels in red
                        highlighted_array[row, col] = [255, 0, 0]
            
            # Calculate GAP heights
            gap_heights = calculate_gap_height(gap_pixels, resolution)
            
            # Get max height for statistics
            max_height_um = max(gap_heights.values()) if gap_heights else 0
            
            # Save the highlighted image
            image_name = os.path.splitext(image_file)[0]
            highlighted_img = Image.fromarray(highlighted_array)
            highlighted_img.save(os.path.join(output_dir, f"{image_name}_highlighted.png"))
            
            # Save pixel analysis data to CSV
            with open(os.path.join(output_dir, f"{image_name}_gap_analysis.csv"), 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Row', 'Column', 'Grayscale Value', 'GAP Flag'])
                writer.writerows(pixel_data)
            
            # Save GAP heights to CSV
            with open(os.path.join(output_dir, f"{image_name}_gap_height.csv"), 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Column', 'Height (μm)'])
                for col, height in gap_heights.items():
                    writer.writerow([col, height])
            
            # Save statistics to TXT file
            with open(os.path.join(output_dir, f"{image_name}_statistics.txt"), 'w') as txtfile:
                txtfile.write(f"Physical dimension parameter: {resolution} μm/pixel\n")
                txtfile.write(f"Maximum GAP height: {max_height_um} μm\n")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Analyze GAP in images')
    parser.add_argument('-re', '--resolution', type=float, required=True, help='Resolution in μm/pixel')
    args = parser.parse_args()
    
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    
    # Process all images
    process_images(input_directory, args.resolution)
    
    print("Processed all the images!")
