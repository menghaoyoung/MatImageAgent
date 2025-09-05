import os
import csv
import argparse
from PIL import Image
import numpy as np
from collections import defaultdict
import time

def check_gap_conditions(gray_array, row, col, grayscale_value):
    # Check condition 1: Grayscale value between 5-30 (inclusive)
    if not (5 <= grayscale_value <= 30):
        return False
    
    # Check condition 2: At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
    height, width = gray_array.shape
    
    for dr, dc in directions:
        contiguous_count = 0
        r, c = row, col
        
        # Check 20 pixels in this direction
        for _ in range(20):
            r, c = r + dr, c + dc
            if 0 <= r < height and 0 <= c < width and 5 <= gray_array[r, c] <= 30:
                contiguous_count += 1
            else:
                break
        
        if contiguous_count >= 20:
            return True
    
    return False

def calculate_gap_height(gap_pixels, resolution):
    # Group GAP pixels by column
    column_gaps = defaultdict(list)
    for row, col in gap_pixels:
        column_gaps[col].append(row)
    
    # Calculate GAP height for each column
    gap_heights = {}
    for col, rows in column_gaps.items():
        if rows:  # If there are GAP pixels in this column
            min_row = min(rows)
            max_row = max(rows)
            gap_height = (max_row - min_row + 1) * resolution
            gap_heights[col] = gap_height
    
    return gap_heights

def process_images(input_directory, resolution):
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(input_directory), "ALL_RESULT", "CLAUDE", "T1S2", "backup8")
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all image files with "Li_" prefix
    image_files = [f for f in os.listdir(input_directory) 
                  if (f.startswith("Li_") and 
                      (f.lower().endswith('.png') or f.lower().endswith('.jpg')))]
    
    for image_file in image_files:
        start_time = time.time()
        print(f"Processing {image_file}...")
        
        # Open the image and convert to grayscale
        img_path = os.path.join(input_directory, image_file)
        img = Image.open(img_path)
        gray_img = img.convert('L')
        gray_array = np.array(gray_img)
        
        # Create a new RGB image for highlighting GAP pixels
        highlight_img = img.convert('RGB')
        highlight_array = np.array(highlight_img)
        
        # Analyze each pixel
        height, width = gray_array.shape
        gap_pixels = []
        pixel_data = []
        
        for row in range(height):
            for col in range(width):
                grayscale_value = gray_array[row, col]
                is_gap = check_gap_conditions(gray_array, row, col, grayscale_value)
                
                # Store pixel data
                pixel_data.append([row, col, grayscale_value, 1 if is_gap else 0])
                
                # If it's a GAP pixel, add to list and highlight in red
                if is_gap:
                    gap_pixels.append((row, col))
                    highlight_array[row, col] = [255, 0, 0]  # Red color
        
        # Calculate GAP heights
        gap_heights = calculate_gap_height(gap_pixels, resolution)
        
        # Save the highlighted image
        base_name = os.path.splitext(image_file)[0]
        highlight_img_path = os.path.join(output_dir, f"{base_name}_gap_highlighted.png")
        highlight_img = Image.fromarray(highlight_array)
        highlight_img.save(highlight_img_path)
        
        # Save pixel analysis to CSV
        csv_path = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Row', 'Column', 'Grayscale Value', 'GAP Flag'])
            writer.writerows(pixel_data)
        
        # Save GAP heights to CSV
        gap_height_path = os.path.join(output_dir, f"{base_name}_gap_height.csv")
        with open(gap_height_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Column', 'GAP Height (μm)'])
            for col, height in gap_heights.items():
                writer.writerow([col, height])
        
        # Save statistics to TXT
        txt_path = os.path.join(output_dir, f"{base_name}_gap_statistics.txt")
        with open(txt_path, 'w') as txtfile:
            txtfile.write(f"Physical Dimension Parameter: {resolution} μm/pixel\n")
            if gap_heights:
                max_height = max(gap_heights.values())
                txtfile.write(f"Maximum GAP Height: {max_height:.4f} μm\n")
            else:
                txtfile.write("No GAP pixels detected in this image.\n")
        
        end_time = time.time()
        print(f"Completed processing {image_file} in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Analyze GAP pixels in images')
    parser.add_argument('-re', '--resolution', type=float, required=True, 
                        help='Resolution in μm/pixel')
    args = parser.parse_args()
    
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory, args.resolution)
    print("Processed all the images!")
