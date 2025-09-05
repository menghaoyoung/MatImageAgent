import os
import csv
from PIL import Image
import numpy as np
from collections import defaultdict
import time

# Check whether the pixel points meet the GAP condition:
# (1) Grayscale value between 5-30 (inclusive)
# (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition.
def check_gap_conditions(gray_image, row, col):
    # Check first condition: grayscale value between 5-30
    pixel_value = gray_image[row, col]
    if not (5 <= pixel_value <= 30):
        return 0
    
    # Check second condition: at least one adjacent pixel has 20 contiguous pixels
    # Define directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    height, width = gray_image.shape
    
    for dr, dc in directions:
        adj_row, adj_col = row + dr, col + dc
        
        # Check if adjacent pixel is within image boundaries
        if 0 <= adj_row < height and 0 <= adj_col < width:
            # Count contiguous pixels in this direction
            count = 0
            curr_row, curr_col = adj_row, adj_col
            
            while (0 <= curr_row < height and 
                   0 <= curr_col < width and 
                   5 <= gray_image[curr_row, curr_col] <= 30):
                count += 1
                if count >= 20:  # Found 20 contiguous pixels
                    return 1
                curr_row += dr
                curr_col += dc
    
    return 0

# Process all images in the directory whose filenames start with "Li_"
def process_images(input_directory):
    # Create output directory if it doesn't exist
    output_directory = os.path.join(os.path.dirname(input_directory), "ALL_RESULT", "CLAUDE", "T1S1", "backup4")
    os.makedirs(output_directory, exist_ok=True)
    
    # Get all image files with "Li_" prefix
    image_files = [f for f in os.listdir(input_directory) 
                  if f.startswith("Li_") and (f.lower().endswith('.png') or f.lower().endswith('.jpg'))]
    
    print(f"Found {len(image_files)} images to process")
    
    for image_file in image_files:
        print(f"Processing {image_file}...")
        image_path = os.path.join(input_directory, image_file)
        
        # Open image and convert to grayscale
        img = Image.open(image_path).convert('L')
        gray_array = np.array(img)
        
        # Create a new RGB image for highlighting GAP pixels
        highlighted_img = Image.open(image_path).convert('RGB')
        highlighted_array = np.array(highlighted_img)
        
        height, width = gray_array.shape
        
        # Create CSV data
        csv_data = []
        
        # Process each pixel
        for row in range(height):
            for col in range(width):
                gray_value = gray_array[row, col]
                gap_flag = check_gap_conditions(gray_array, row, col)
                
                # Add to CSV data
                csv_data.append([row, col, int(gray_value), gap_flag])
                
                # Highlight GAP pixels in red
                if gap_flag == 1:
                    highlighted_array[row, col] = [255, 0, 0]  # Red color
        
        # Save CSV file
        base_name = os.path.splitext(image_file)[0]
        csv_filename = f"{base_name}_gap_analysis.csv"
        csv_path = os.path.join(output_directory, csv_filename)
        
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Row', 'Column', 'Grayscale Value', 'GAP Flag'])
            writer.writerows(csv_data)
        
        # Save highlighted image
        highlighted_img = Image.fromarray(highlighted_array)
        highlighted_filename = f"{base_name}_highlighted.png"
        highlighted_path = os.path.join(output_directory, highlighted_filename)
        highlighted_img.save(highlighted_path)
        
        print(f"Saved {csv_filename} and {highlighted_filename}")

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    start_time = time.time()
    process_images(input_directory)
    end_time = time.time()
    print(f"Processed all the images! Time taken: {end_time - start_time:.2f} seconds")
