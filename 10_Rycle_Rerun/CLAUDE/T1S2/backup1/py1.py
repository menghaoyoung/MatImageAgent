import os
import csv
import argparse
from PIL import Image
import numpy as np
from collections import defaultdict
import time

def check_gap_conditions(gray_array, row, col, grayscale_min=5, grayscale_max=30, contiguous_threshold=20):
    """
    Check whether the pixel points meet the GAP condition:
    (1) Grayscale value between 5–30 (inclusive)
    (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition.
    """
    # Check if current pixel is within grayscale range
    pixel_value = gray_array[row, col]
    if not (grayscale_min <= pixel_value <= grayscale_max):
        return False, pixel_value
    
    height, width = gray_array.shape
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
    
    # Check each direction for contiguous pixels
    for dr, dc in directions:
        contiguous_count = 0
        r, c = row, col
        
        # Count contiguous pixels in this direction
        for _ in range(contiguous_threshold):
            r += dr
            c += dc
            
            # Check if position is valid and pixel is within grayscale range
            if (0 <= r < height and 0 <= c < width and 
                grayscale_min <= gray_array[r, c] <= grayscale_max):
                contiguous_count += 1
            else:
                break
        
        # If we found enough contiguous pixels in this direction
        if contiguous_count >= contiguous_threshold - 1:  # -1 because we're not counting the starting pixel
            return True, pixel_value
    
    return False, pixel_value

def calculate_gap_height(gap_pixels, resolution):
    """
    Calculate GAP height per column
    GAP_height = [(max_row - min_row + 1) × resolution] μm
    """
    gap_heights = {}
    
    # Group gap pixels by column
    columns = defaultdict(list)
    for row, col in gap_pixels:
        columns[col].append(row)
    
    # Calculate height for each column
    for col, rows in columns.items():
        if rows:
            min_row = min(rows)
            max_row = max(rows)
            height_um = (max_row - min_row + 1) * resolution
            gap_heights[col] = height_um
    
    return gap_heights

def process_images(input_directory, resolution):
    """
    Process all images in the directory whose filenames start with "Li_"
    """
    # Ensure output directory exists
    output_dir = os.path.join(os.path.dirname(input_directory), "ALL_RESULT", "CLAUDE", "T1S2", "backup1")
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all Li_ images
    image_files = [f for f in os.listdir(input_directory) 
                  if f.startswith("Li_") and (f.lower().endswith('.png') or f.lower().endswith('.jpg'))]
    
    for image_file in image_files:
        print(f"Processing {image_file}...")
        image_path = os.path.join(input_directory, image_file)
        
        # Open image and convert to grayscale
        img = Image.open(image_path).convert('L')
        gray_array = np.array(img)
        height, width = gray_array.shape
        
        # Create a colored version for highlighting
        highlighted_img = Image.open(image_path).convert('RGB')
        highlighted_array = np.array(highlighted_img)
        
        # Process each pixel
        pixel_data = []
        gap_pixels = []
        
        for row in range(height):
            for col in range(width):
                is_gap, pixel_value = check_gap_conditions(gray_array, row, col)
                
                # Store pixel data
                pixel_data.append((row, col, pixel_value, 1 if is_gap else 0))
                
                # If it's a GAP pixel, store for height calculation and highlight
                if is_gap:
                    gap_pixels.append((row, col))
                    highlighted_array[row, col] = [255, 0, 0]  # Red color
        
        # Calculate GAP heights
        gap_heights = calculate_gap_height(gap_pixels, resolution)
        
        # Save results
        base_name = os.path.splitext(image_file)[0]
        
        # Save pixel analysis CSV
        analysis_csv_path = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
        with open(analysis_csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Row', 'Column', 'Grayscale', 'GAP_Flag'])
            writer.writerows(pixel_data)
        
        # Save GAP heights CSV
        heights_csv_path = os.path.join(output_dir, f"{base_name}_gap_height.csv")
        with open(heights_csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Column', 'Height_um'])
            for col, height in gap_heights.items():
                writer.writerow([col, height])
        
        # Save TXT file with statistics
        txt_path = os.path.join(output_dir, f"{base_name}_stats.txt")
        with open(txt_path, 'w') as txtfile:
            txtfile.write(f"Physical dimension parameter: {resolution} μm/pixel\n")
            max_height = max(gap_heights.values()) if gap_heights else 0
            txtfile.write(f"Maximum GAP height: {max_height:.4f} μm\n")
        
        # Save highlighted image
        highlighted_img = Image.fromarray(highlighted_array)
        highlighted_path = os.path.join(output_dir, f"{base_name}_highlighted.png")
        highlighted_img.save(highlighted_path)
        
        print(f"Completed processing {image_file}")

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='GAP Analysis Tool')
    parser.add_argument('-re', '--resolution', type=float, required=True,
                       help='Resolution in μm/pixel')
    args = parser.parse_args()
    
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory, args.resolution)
    print("Processed all the images!")
