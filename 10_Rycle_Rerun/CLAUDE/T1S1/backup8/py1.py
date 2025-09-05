import os
import csv
from PIL import Image
import numpy as np
import time

# Check whether the pixel points meet the GAP condition
def check_gap_conditions(img_array, row, col):
    # Check condition 1: Grayscale value between 5-30 (inclusive)
    if not (5 <= img_array[row, col] <= 30):
        return False
    
    # Check condition 2: At least one adjacent pixel has 20 contiguous pixels meeting grayscale condition
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
    height, width = img_array.shape
    
    for dr, dc in directions:
        contiguous_count = 0
        r, c = row, col
        
        # Check 20 pixels in this direction
        for _ in range(20):
            r += dr
            c += dc
            
            # Check if within image boundaries
            if 0 <= r < height and 0 <= c < width:
                if 5 <= img_array[r, c] <= 30:
                    contiguous_count += 1
                else:
                    break
            else:
                break
        
        # If we found 20 contiguous pixels in this direction
        if contiguous_count >= 20:
            return True
    
    return False

# Process all images in the directory whose filenames start with "Li_"
def process_images(input_directory):
    # Ensure output directory exists
    output_dir = os.path.join(os.path.dirname(input_directory), "ALL_RESULT", "CLAUDE", "T1S1", "backup8")
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all image files with "Li_" prefix
    image_files = [f for f in os.listdir(input_directory) 
                  if f.startswith("Li_") and (f.lower().endswith('.png') or f.lower().endswith('.jpg'))]
    
    print(f"Found {len(image_files)} images to process")
    
    for img_file in image_files:
        print(f"Processing {img_file}...")
        img_path = os.path.join(input_directory, img_file)
        
        # Open image and convert to grayscale
        with Image.open(img_path) as img:
            gray_img = img.convert('L')
            img_array = np.array(gray_img)
            height, width = img_array.shape
            
            # Create a new RGB image for highlighting GAP pixels
            highlighted_img = img.convert('RGB')
            highlighted_array = np.array(highlighted_img)
            
            # Create a list to store pixel data
            pixel_data = []
            
            # Process each pixel
            for row in range(height):
                for col in range(width):
                    gray_value = img_array[row, col]
                    gap_flag = 1 if check_gap_conditions(img_array, row, col) else 0
                    
                    # Add to pixel data
                    pixel_data.append([row, col, int(gray_value), gap_flag])
                    
                    # Highlight GAP pixels in red
                    if gap_flag == 1:
                        highlighted_array[row, col] = [255, 0, 0]
            
            # Save the CSV file
            base_name = os.path.splitext(img_file)[0]
            csv_filename = f"{base_name}_gap_analysis.csv"
            csv_path = os.path.join(output_dir, csv_filename)
            
            with open(csv_path, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['Row', 'Column', 'Grayscale_Value', 'GAP_Flag'])
                csv_writer.writerows(pixel_data)
            
            # Save the highlighted image
            highlighted_img = Image.fromarray(highlighted_array)
            highlighted_filename = f"{base_name}_highlighted.png"
            highlighted_path = os.path.join(output_dir, highlighted_filename)
            highlighted_img.save(highlighted_path)
            
            print(f"Saved {csv_filename} and {highlighted_filename}")

if __name__ == "__main__":
    start_time = time.time()
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    end_time = time.time()
    print(f"Processed all the images in {end_time - start_time:.2f} seconds!")
