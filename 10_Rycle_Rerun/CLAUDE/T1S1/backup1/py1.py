import os
import csv
from PIL import Image
import numpy as np
from collections import defaultdict
import time
import shutil

# Check whether the pixel points meet the GAP condition：
# (1) Grayscale value between 5–30 (inclusive)
# (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition.
def check_gap_conditions(img_array, row, col):
    # Check first condition: grayscale value between 5-30
    pixel_value = img_array[row, col]
    if not (5 <= pixel_value <= 30):
        return 0
    
    # Check second condition: at least one adjacent pixel has 20 contiguous pixels meeting the grayscale condition
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
    height, width = img_array.shape
    
    for dr, dc in directions:
        contiguous_count = 0
        r, c = row, col
        
        # Check in this direction
        for _ in range(20):  # Look for 20 contiguous pixels
            r += dr
            c += dc
            
            # Check if within bounds
            if 0 <= r < height and 0 <= c < width:
                if 5 <= img_array[r, c] <= 30:
                    contiguous_count += 1
                else:
                    break
            else:
                break
        
        # If we found 20 contiguous pixels in this direction
        if contiguous_count >= 20:
            return 1
    
    return 0

# Process all images in the directory whose filenames start with "Li_"
def process_images(input_directory):
    # Create output directory if it doesn't exist
    output_directory = os.path.join(os.path.dirname(input_directory), "ALL_RESULT", "CLAUDE", "T1S1", "backup1")
    os.makedirs(output_directory, exist_ok=True)
    
    # Get all image files with "Li_" prefix
    image_files = [f for f in os.listdir(input_directory) if f.startswith("Li_") and (f.lower().endswith('.png') or f.lower().endswith('.jpg'))]
    
    for image_file in image_files:
        print(f"Processing {image_file}...")
        image_path = os.path.join(input_directory, image_file)
        
        # Open image and convert to grayscale
        img = Image.open(image_path).convert('L')
        img_array = np.array(img)
        height, width = img_array.shape
        
        # Create a new RGB image for highlighting GAP pixels
        highlighted_img = Image.new('RGB', (width, height), (0, 0, 0))
        highlighted_pixels = highlighted_img.load()
        
        # Create CSV file
        base_name = os.path.splitext(image_file)[0]
        csv_filename = f"{base_name}_gap_analysis.csv"
        csv_path = os.path.join(output_directory, csv_filename)
        
        with open(csv_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['Row', 'Column', 'Grayscale_Value', 'GAP_Flag'])
            
            # Process each pixel
            for row in range(height):
                for col in range(width):
                    pixel_value = img_array[row, col]
                    gap_flag = check_gap_conditions(img_array, row, col)
                    
                    # Write to CSV
                    csvwriter.writerow([row, col, pixel_value, gap_flag])
                    
                    # Set pixel in highlighted image
                    if gap_flag == 1:
                        highlighted_pixels[col, row] = (255, 0, 0)  # Red for GAP pixels
                    else:
                        highlighted_pixels[col, row] = (pixel_value, pixel_value, pixel_value)  # Grayscale for non-GAP
        
        # Save highlighted image
        highlighted_img_filename = f"{base_name}_highlighted.png"
        highlighted_img_path = os.path.join(output_directory, highlighted_img_filename)
        highlighted_img.save(highlighted_img_path)
        
        print(f"Saved {csv_filename} and {highlighted_img_filename}")

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    start_time = time.time()
    process_images(input_directory)
    end_time = time.time()
    print(f"Processed all images in {end_time - start_time:.2f} seconds!")
