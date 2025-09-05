import os
import csv
from PIL import Image
import numpy as np
import time

# Check whether the pixel points meet the GAP condition
def check_gap_conditions(gray_array, row, col):
    # Condition 1: Grayscale value between 5-30 (inclusive)
    if not (5 <= gray_array[row, col] <= 30):
        return 0
    
    # Condition 2: At least one adjacent pixel has 20 contiguous pixels meeting the grayscale condition
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
    height, width = gray_array.shape
    
    for dr, dc in directions:
        contiguous_count = 0
        r, c = row, col
        
        # Check 20 pixels in this direction
        for _ in range(20):
            r += dr
            c += dc
            
            # Check if we're still within bounds
            if 0 <= r < height and 0 <= c < width:
                if 5 <= gray_array[r, c] <= 30:
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
    # Ensure output directory exists
    output_directory = os.path.join(os.path.dirname(input_directory), "ALL_RESULT", "CLAUDE", "T1S1", "backup2")
    os.makedirs(output_directory, exist_ok=True)
    
    # Get all image files with "Li_" prefix
    image_files = [f for f in os.listdir(input_directory) 
                  if f.startswith("Li_") and (f.lower().endswith('.png') or f.lower().endswith('.jpg'))]
    
    print(f"Found {len(image_files)} images to process")
    
    for image_file in image_files:
        print(f"Processing {image_file}...")
        image_path = os.path.join(input_directory, image_file)
        
        # Open image and convert to grayscale
        with Image.open(image_path) as img:
            gray_img = img.convert('L')
            gray_array = np.array(gray_img)
            
            # Create a new RGB image for highlighting GAP pixels
            highlighted_img = img.convert('RGB')
            highlighted_array = np.array(highlighted_img)
            
            # Prepare CSV data
            csv_data = []
            
            # Process each pixel
            height, width = gray_array.shape
            for row in range(height):
                for col in range(width):
                    gray_value = gray_array[row, col]
                    gap_flag = check_gap_conditions(gray_array, row, col)
                    
                    # Add to CSV data
                    csv_data.append([row, col, gray_value, gap_flag])
                    
                    # Highlight GAP pixels in red
                    if gap_flag == 1:
                        highlighted_array[row, col] = [255, 0, 0]
            
            # Save highlighted image
            base_name = os.path.splitext(image_file)[0]
            highlighted_img = Image.fromarray(highlighted_array)
            highlighted_img_path = os.path.join(output_directory, f"{base_name}_gap_highlighted.png")
            highlighted_img.save(highlighted_img_path)
            
            # Save CSV data
            csv_path = os.path.join(output_directory, f"{base_name}_gap_analysis.csv")
            save_csv(csv_path, csv_data)
            
            print(f"Saved highlighted image to {highlighted_img_path}")
            print(f"Saved CSV data to {csv_path}")

# Stores all pixel analysis data
def save_csv(csv_path, csv_data):
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Row', 'Column', 'Grayscale Value', 'GAP Flag'])
        writer.writerows(csv_data)

if __name__ == "__main__":
    start_time = time.time()
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    end_time = time.time()
    print(f"Processed all the images in {end_time - start_time:.2f} seconds!")
