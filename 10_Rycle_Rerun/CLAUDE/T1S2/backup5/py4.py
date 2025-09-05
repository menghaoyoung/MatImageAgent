import os
import csv
import argparse
from PIL import Image
import numpy as np
from collections import defaultdict
import time

def check_gap_conditions(img_array, row, col, grayscale_min=5, grayscale_max=30, contiguous_count=20):
    """
    Check whether the pixel points meet the GAP condition:
    (1) Grayscale value between 5–30 (inclusive)
    (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition
    """
    # Check if current pixel is within grayscale range
    if not (grayscale_min <= img_array[row, col] <= grayscale_max):
        return False
    
    height, width = img_array.shape
    
    # Check adjacent pixels (up, down, left, right)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for dr, dc in directions:
        count = 0
        r, c = row, col
        
        # Check contiguous pixels in this direction
        for _ in range(contiguous_count):
            r += dr
            c += dc
            
            # Check if pixel is within image boundaries and meets grayscale condition
            if (0 <= r < height and 0 <= c < width and 
                grayscale_min <= img_array[r, c] <= grayscale_max):
                count += 1
            else:
                break
        
        # If we found enough contiguous pixels in this direction
        if count >= contiguous_count - 1:  # -1 because we start counting from adjacent pixel
            return True
    
    return False

def process_images(input_directory, resolution):
    """
    Process all images in the directory whose filenames start with "Li_"
    """
    # Ensure output directories exist
    output_dir = os.path.join(os.path.dirname(input_directory), "ALL_RESULT", "CLAUDE", "T1S2", "backup5")
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all image files with "Li_" prefix
    image_files = [f for f in os.listdir(input_directory) 
                  if f.startswith("Li_") and (f.lower().endswith('.png') or f.lower().endswith('.jpg'))]
    
    for image_file in image_files:
        print(f"Processing image: {image_file}")
        
        # Open image and convert to grayscale
        img_path = os.path.join(input_directory, image_file)
        img = Image.open(img_path).convert('L')
        img_array = np.array(img)
        height, width = img_array.shape
        
        # Create a new RGB image for highlighting GAP pixels
        highlighted_img = Image.new('RGB', (width, height), color=(0, 0, 0))
        highlighted_pixels = highlighted_img.load()
        
        # Copy original grayscale values to RGB image
        for y in range(height):
            for x in range(width):
                gray_value = img_array[y, x]
                highlighted_pixels[x, y] = (gray_value, gray_value, gray_value)
        
        # Analyze pixels and store results
        pixel_data = []
        gap_pixels_by_column = defaultdict(list)
        
        for row in range(height):
            for col in range(width):
                gray_value = img_array[row, col]
                is_gap = 1 if check_gap_conditions(img_array, row, col) else 0
                
                pixel_data.append((row, col, gray_value, is_gap))
                
                if is_gap:
                    # Highlight GAP pixel in red
                    highlighted_pixels[col, row] = (255, 0, 0)
                    # Store row position for GAP height calculation
                    gap_pixels_by_column[col].append(row)
        
        # Save highlighted image
        image_name = os.path.splitext(image_file)[0]
        highlighted_img_path = os.path.join(output_dir, f"{image_name}_gap_highlighted.png")
        highlighted_img.save(highlighted_img_path)
        
        # Save pixel analysis data to CSV
        analysis_csv_path = os.path.join(output_dir, f"{image_name}_gap_analysis.csv")
        with open(analysis_csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Row', 'Column', 'Grayscale', 'GAP_Flag'])
            writer.writerows(pixel_data)
        
        # Calculate and save GAP heights
        gap_heights = []
        max_height_um = 0
        
        for col, rows in gap_pixels_by_column.items():
            if rows:
                min_row = min(rows)
                max_row = max(rows)
                gap_height_pixels = max_row - min_row + 1
                gap_height_um = gap_height_pixels * resolution
                gap_heights.append((col, gap_height_um))
                
                if gap_height_um > max_height_um:
                    max_height_um = gap_height_um
        
        # Save GAP heights to CSV
        heights_csv_path = os.path.join(output_dir, f"{image_name}_gap_height.csv")
        with open(heights_csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Column', 'GAP_Height(μm)'])
            writer.writerows(gap_heights)
        
        # Save statistics to TXT file
        stats_txt_path = os.path.join(output_dir, f"{image_name}_statistics.txt")
        with open(stats_txt_path, 'w') as txtfile:
            txtfile.write(f"Physical dimension parameter: {resolution} μm/pixel\n")
            txtfile.write(f"Maximum GAP height: {max_height_um:.4f} μm\n")
        
        print(f"Completed processing: {image_file}")

if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Analyze GAP in images')
    parser.add_argument('-re', '--resolution', type=float, required=True, 
                        help='Resolution in μm/pixel')
    
    args = parser.parse_args()
    
    start_time = time.time()
    
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory, args.resolution)
    
    elapsed_time = time.time() - start_time
    print(f"Processed all images in {elapsed_time:.2f} seconds!")
