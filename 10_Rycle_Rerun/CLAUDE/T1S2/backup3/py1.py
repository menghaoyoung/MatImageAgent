import os
import csv
import argparse
from PIL import Image
import numpy as np
from collections import defaultdict
import time

def check_gap_conditions(image_array, row, col, min_gray, max_gray):
    """
    Check whether the pixel points meet the GAP condition:
    (1) Grayscale value between 5–30 (inclusive)
    (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition.
    """
    height, width = image_array.shape
    
    # Check first condition: grayscale value between min_gray and max_gray
    if not (min_gray <= image_array[row, col] <= max_gray):
        return False
    
    # Check second condition: at least one adjacent pixel has 20 contiguous pixels meeting the grayscale condition
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
    
    for dr, dc in directions:
        contiguous_count = 0
        r, c = row, col
        
        for _ in range(20):  # Check for 20 contiguous pixels
            r, c = r + dr, c + dc
            
            # Check if the pixel is within the image boundaries
            if 0 <= r < height and 0 <= c < width:
                if min_gray <= image_array[r, c] <= max_gray:
                    contiguous_count += 1
                else:
                    break
            else:
                break
        
        if contiguous_count >= 20:
            return True
    
    return False

def calculate_gap_height(gap_pixels, resolution):
    """
    Calculate GAP height per column
    GAP_height = [(max_row - min_row + 1) × resolution] μm
    """
    column_heights = {}
    
    # Group GAP pixels by column
    column_groups = defaultdict(list)
    for row, col in gap_pixels:
        column_groups[col].append(row)
    
    # Calculate height for each column
    for col, rows in column_groups.items():
        if rows:  # If there are GAP pixels in this column
            min_row = min(rows)
            max_row = max(rows)
            height_um = (max_row - min_row + 1) * resolution
            column_heights[col] = height_um
    
    return column_heights

def process_images(input_directory, resolution):
    """
    Process all images in the directory whose filenames start with "Li_"
    """
    # Create output directory if it doesn't exist
    output_directory = os.path.join(os.path.dirname(input_directory), "ALL_RESULT", "CLAUDE", "T1S2", "backup3")
    os.makedirs(output_directory, exist_ok=True)
    
    # Define grayscale thresholds
    min_gray = 5
    max_gray = 30
    
    # Process each image
    for filename in os.listdir(input_directory):
        if filename.startswith("Li_") and (filename.lower().endswith(".png") or filename.lower().endswith(".jpg")):
            start_time = time.time()
            image_path = os.path.join(input_directory, filename)
            print(f"Processing {filename}...")
            
            # Open and convert image to grayscale
            image = Image.open(image_path).convert('L')
            image_array = np.array(image)
            height, width = image_array.shape
            
            # Create a color image for highlighting GAP pixels
            highlighted_image = Image.open(image_path).convert('RGB')
            highlighted_array = np.array(highlighted_image)
            
            # Process each pixel and identify GAP pixels
            gap_pixels = []
            pixel_data = []
            
            for row in range(height):
                for col in range(width):
                    gray_value = image_array[row, col]
                    is_gap = 0
                    
                    # Check if the pixel meets GAP conditions
                    if min_gray <= gray_value <= max_gray:
                        if check_gap_conditions(image_array, row, col, min_gray, max_gray):
                            is_gap = 1
                            gap_pixels.append((row, col))
                            # Highlight GAP pixels in red
                            highlighted_array[row, col] = [255, 0, 0]
                    
                    # Store pixel data
                    pixel_data.append((row, col, gray_value, is_gap))
            
            # Calculate GAP heights
            gap_heights = calculate_gap_height(gap_pixels, resolution)
            
            # Save the highlighted image
            image_name = os.path.splitext(filename)[0]
            highlighted_image = Image.fromarray(highlighted_array)
            highlighted_image_path = os.path.join(output_directory, f"{image_name}_highlighted.png")
            highlighted_image.save(highlighted_image_path)
            
            # Save pixel analysis data to CSV
            csv_path = os.path.join(output_directory, f"{image_name}_gap_analysis.csv")
            with open(csv_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Row', 'Column', 'Grayscale Value', 'GAP Flag'])
                writer.writerows(pixel_data)
            
            # Save GAP heights to CSV
            heights_csv_path = os.path.join(output_directory, f"{image_name}_gap_height.csv")
            with open(heights_csv_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Column', 'GAP Height (μm)'])
                for col, height in gap_heights.items():
                    writer.writerow([col, height])
            
            # Save statistics to TXT
            txt_path = os.path.join(output_directory, f"{image_name}_stats.txt")
            with open(txt_path, 'w') as txtfile:
                txtfile.write(f"Physical dimension parameter: {resolution} μm/pixel\n")
                max_height = max(gap_heights.values()) if gap_heights else 0
                txtfile.write(f"Maximum GAP height: {max_height} μm\n")
            
            end_time = time.time()
            print(f"Processed {filename} in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process images and identify GAP pixels.')
    parser.add_argument('-re', '--resolution', type=float, required=True, help='Resolution in μm/pixel')
    
    args = parser.parse_args()
    
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory, args.resolution)
    print("Processed all the images!")
