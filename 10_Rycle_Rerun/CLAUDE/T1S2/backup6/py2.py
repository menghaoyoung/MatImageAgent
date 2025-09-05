import os
import csv
import argparse
from PIL import Image
import numpy as np
from collections import defaultdict
import time

def check_gap_conditions(grayscale_array, row, col, grayscale_threshold=(5, 30)):
    """
    Check whether the pixel points meet the GAP condition:
    (1) Grayscale value between 5–30 (inclusive)
    (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition.
    """
    height, width = grayscale_array.shape
    
    # Check if the pixel's grayscale value is within the threshold
    pixel_value = grayscale_array[row, col]
    if not (grayscale_threshold[0] <= pixel_value <= grayscale_threshold[1]):
        return False, pixel_value
    
    # Define the four directions (up, down, left, right)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    # Check each direction
    for dr, dc in directions:
        contiguous_count = 0
        r, c = row, col
        
        # Count contiguous pixels in this direction
        for _ in range(20):  # Check for 20 contiguous pixels
            r += dr
            c += dc
            
            # Check if the new position is valid
            if 0 <= r < height and 0 <= c < width:
                if grayscale_threshold[0] <= grayscale_array[r, c] <= grayscale_threshold[1]:
                    contiguous_count += 1
                else:
                    break
            else:
                break
        
        # If we found 20 contiguous pixels in any direction, return True
        if contiguous_count >= 20:
            return True, pixel_value
    
    return False, pixel_value

def calculate_gap_height(gap_pixels, resolution):
    """
    Calculate GAP height per column.
    GAP_height = [(max_row - min_row + 1) × resolution] μm
    """
    column_heights = {}
    
    # Group gap pixels by column
    column_pixels = defaultdict(list)
    for row, col in gap_pixels:
        column_pixels[col].append(row)
    
    # Calculate height for each column
    for col, rows in column_pixels.items():
        if rows:
            min_row = min(rows)
            max_row = max(rows)
            gap_height = (max_row - min_row + 1) * resolution
            column_heights[col] = gap_height
    
    return column_heights

def process_images(input_directory, resolution):
    """
    Process all images in the directory whose filenames start with "Li_"
    """
    # Create output directory if it doesn't exist
    output_directory = os.path.join(os.path.dirname(os.path.dirname(input_directory)), "ALL_RESULT", "CLAUDE", "T1S2", "backup6")
    os.makedirs(output_directory, exist_ok=True)
    
    print(f"Output directory: {output_directory}")
    
    # Get all image files with "Li_" prefix
    image_files = [f for f in os.listdir(input_directory) 
                   if f.startswith("Li_") and (f.lower().endswith('.png') or f.lower().endswith('.jpg'))]
    
    print(f"Found {len(image_files)} images to process")
    
    for image_file in image_files:
        start_time = time.time()
        print(f"Processing {image_file}...")
        
        # Load image and convert to grayscale
        image_path = os.path.join(input_directory, image_file)
        image = Image.open(image_path).convert('L')
        grayscale_array = np.array(image)
        
        height, width = grayscale_array.shape
        print(f"Image dimensions: {width}x{height}")
        
        # Create a copy of the original image to highlight GAP pixels
        highlight_image = Image.open(image_path).convert('RGB')
        highlight_array = np.array(highlight_image)
        
        # Create a list to store pixel data
        pixel_data = []
        gap_pixels = []
        
        # Process each pixel
        for row in range(height):
            for col in range(width):
                is_gap, pixel_value = check_gap_conditions(grayscale_array, row, col)
                
                # Store pixel data
                pixel_data.append((row, col, pixel_value, 1 if is_gap else 0))
                
                # If it's a GAP pixel, highlight it in red and add to gap_pixels list
                if is_gap:
                    highlight_array[row, col] = [255, 0, 0]  # Red color
                    gap_pixels.append((row, col))
        
        print(f"Found {len(gap_pixels)} GAP pixels")
        
        # Calculate GAP heights
        column_heights = calculate_gap_height(gap_pixels, resolution)
        
        # Save the pixel analysis data to CSV
        base_name = os.path.splitext(image_file)[0]
        csv_file_path = os.path.join(output_directory, f"{base_name}_gap_analysis.csv")
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Row', 'Column', 'Grayscale Value', 'GAP Flag'])
            writer.writerows(pixel_data)
        
        # Save the GAP heights to CSV
        heights_csv_path = os.path.join(output_directory, f"{base_name}_gap_height.csv")
        with open(heights_csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Column', 'GAP Height (μm)'])
            for col, height in column_heights.items():
                writer.writerow([col, height])
        
        # Save the highlighted image
        highlight_image = Image.fromarray(highlight_array)
        highlight_image_path = os.path.join(output_directory, f"{base_name}_highlighted.png")
        highlight_image.save(highlight_image_path)
        
        # Save statistics to TXT file
        txt_file_path = os.path.join(output_directory, f"{base_name}_statistics.txt")
        with open(txt_file_path, 'w') as txtfile:
            txtfile.write(f"Physical dimension parameter: {resolution} μm/pixel\n")
            max_height = max(column_heights.values()) if column_heights else 0
            txtfile.write(f"Maximum GAP height: {max_height} μm\n")
        
        end_time = time.time()
        print(f"Processed {image_file} in {end_time - start_time:.2f} seconds")
        print(f"Output files saved to {output_directory}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze GAP pixels in images.')
    parser.add_argument('-re', '--resolution', type=float, required=True, 
                        help='Resolution in μm/pixel')
    
    args = parser.parse_args()
    
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory, args.resolution)
    print("Processed all the images!")
