import os
import csv
from PIL import Image
import numpy as np
from collections import defaultdict
import time

# Check whether the pixel points meet the GAP condition: 
# (1) Grayscale value between 5–30 (inclusive) 
# (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition.
def check_gap_conditions(img_array, row, col):
    # Check first condition: grayscale value between 5-30
    if not (5 <= img_array[row, col] <= 30):
        return False
    
    # Check second condition: at least one adjacent pixel has 20 contiguous pixels meeting grayscale condition
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
    height, width = img_array.shape
    
    for dr, dc in directions:
        count = 0
        r, c = row, col
        
        # Check up to 20 pixels in this direction
        for _ in range(20):
            r += dr
            c += dc
            
            # Check if position is valid and meets grayscale condition
            if (0 <= r < height and 0 <= c < width and 5 <= img_array[r, c] <= 30):
                count += 1
            else:
                break
                
        if count >= 19:  # We need 19 more pixels (plus the original one makes 20)
            return True
            
    return False

# Process all images in the directory whose filenames start with "Li_"
def process_images(input_directory):
    # Ensure output directory exists
    output_dir = os.path.join(input_directory, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all image files with "Li_" prefix
    image_files = [f for f in os.listdir(input_directory) 
                  if f.startswith("Li_") and (f.lower().endswith('.png') or f.lower().endswith('.jpg'))]
    
    print(f"Found {len(image_files)} images to process")
    
    for image_file in image_files:
        print(f"Processing {image_file}...")
        
        # Load and convert image to grayscale
        img_path = os.path.join(input_directory, image_file)
        img = Image.open(img_path).convert('L')
        img_array = np.array(img)
        
        # Create output image (RGB for highlighting GAP pixels)
        output_img = Image.new('RGB', img.size)
        output_pixels = output_img.load()
        
        # Create CSV file
        csv_filename = os.path.splitext(image_file)[0] + "_gap_analysis.csv"
        csv_path = os.path.join(output_dir, csv_filename)
        
        with open(csv_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Row', 'Column', 'Grayscale Value', 'GAP Flag'])
            
            # Process each pixel
            height, width = img_array.shape
            gap_count = 0
            
            for row in range(height):
                for col in range(width):
                    gray_value = img_array[row, col]
                    
                    # Check if pixel meets GAP conditions
                    gap_flag = 1 if check_gap_conditions(img_array, row, col) else 0
                    
                    # Write to CSV
                    csv_writer.writerow([row, col, gray_value, gap_flag])
                    
                    # Set pixel color in output image
                    if gap_flag == 1:
                        output_pixels[col, row] = (255, 0, 0)  # Red for GAP pixels
                        gap_count += 1
                    else:
                        # Use grayscale value for non-GAP pixels
                        output_pixels[col, row] = (gray_value, gray_value, gray_value)
            
            print(f"Found {gap_count} GAP pixels in {image_file}")
        
        # Save output image
        output_img_filename = os.path.splitext(image_file)[0] + "_gap_highlighted.png"
        output_img_path = os.path.join(output_dir, output_img_filename)
        output_img.save(output_img_path)
        
        print(f"Saved {csv_filename} and {output_img_filename}")

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    start_time = time.time()
    process_images(input_directory)
    end_time = time.time()
    print(f"Processed all images in {end_time - start_time:.2f} seconds!")
