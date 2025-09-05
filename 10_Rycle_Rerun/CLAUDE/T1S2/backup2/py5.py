import os
import csv
import argparse
from PIL import Image
import numpy as np
from collections import defaultdict
import time

def check_gap_conditions(img_array, row, col, min_gray, max_gray):
    """
    Check whether the pixel points meet the GAP condition:
    (1) Grayscale value between 5–30 (inclusive)
    (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition.
    """
    height, width = img_array.shape
    pixel_value = img_array[row, col]
    
    # Check condition 1: Grayscale value between 5-30 (inclusive)
    if not (min_gray <= pixel_value <= max_gray):
        return False
    
    # Check condition 2: At least one adjacent pixel has 20 contiguous pixels meeting grayscale condition
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
    
    for dr, dc in directions:
        count = 0
        r, c = row, col
        
        # Check 20 pixels in this direction
        for _ in range(20):
            r, c = r + dr, c + dc
            if 0 <= r < height and 0 <= c < width and min_gray <= img_array[r, c] <= max_gray:
                count += 1
            else:
                break
                
        if count >= 20:
            return True
            
    return False

def process_images(input_directory, resolution):
    """
    Process all images in the directory whose filenames start with "Li_"
    """
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(input_directory), "ALL_RESULT", "CLAUDE", "T1S2", "backup2")
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all image files starting with "Li_"
    image_files = [f for f in os.listdir(input_directory) 
                   if f.startswith("Li_") and (f.lower().endswith('.png') or f.lower().endswith('.jpg'))]
    
    for image_file in image_files:
        print(f"Processing {image_file}...")
        image_path = os.path.join(input_directory, image_file)
        
        # Open image and convert to grayscale
        img = Image.open(image_path).convert('L')
        img_array = np.array(img)
        height, width = img_array.shape
        
        # Create RGB image for visualization
        rgb_img = Image.new('RGB', (width, height), color=(0, 0, 0))
        rgb_pixels = rgb_img.load()
        
        # Prepare data for CSV
        gap_data = []
        gap_pixels_by_column = defaultdict(list)
        
        # Process each pixel
        for row in range(height):
            for col in range(width):
                pixel_value = img_array[row, col]
                is_gap = check_gap_conditions(img_array, row, col, 5, 30)
                
                # Store data for CSV
                gap_data.append((row, col, pixel_value, 1 if is_gap else 0))
                
                # Update visualization
                if is_gap:
                    rgb_pixels[col, row] = (255, 0, 0)  # Red for GAP pixels
                    gap_pixels_by_column[col].append(row)
                else:
                    rgb_pixels[col, row] = (pixel_value, pixel_value, pixel_value)  # Grayscale for non-GAP pixels
        
        # Calculate GAP height for each column
        gap_heights = []
        for col in range(width):
            if gap_pixels_by_column[col]:
                min_row = min(gap_pixels_by_column[col])
                max_row = max(gap_pixels_by_column[col])
                gap_height_um = (max_row - min_row + 1) * resolution
                gap_heights.append((col, gap_height_um))
        
        # Find maximum GAP height
        max_gap_height = max([h for _, h in gap_heights]) if gap_heights else 0
        
        # Save results
        base_name = os.path.splitext(image_file)[0]
        
        # Save the gap analysis CSV
        gap_analysis_csv = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
        with open(gap_analysis_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Row', 'Column', 'Grayscale Value', 'GAP Flag'])
            writer.writerows(gap_data)
        
        # Save the gap height CSV
        gap_height_csv = os.path.join(output_dir, f"{base_name}_gap_height.csv")
        with open(gap_height_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Column', 'GAP Height (μm)'])
            writer.writerows(gap_heights)
        
        # Save the TXT file with statistics
        txt_file = os.path.join(output_dir, f"{base_name}_stats.txt")
        with open(txt_file, 'w') as f:
            f.write(f"Physical dimension parameter: {resolution} μm/pixel\n")
            f.write(f"Maximum GAP height: {max_gap_height:.4f} μm\n")
        
        # Save the visualization image
        vis_image_path = os.path.join(output_dir, f"{base_name}_gap_visualization.png")
        rgb_img.save(vis_image_path)
        
        print(f"Processed {image_file}. Results saved to {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze GAP in images.')
    parser.add_argument('-re', '--resolution', type=float, required=True,
                        help='Resolution in μm/pixel')
    
    args = parser.parse_args()
    
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory, args.resolution)
    print("Processed all the images!")
