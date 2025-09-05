import os
import csv
from PIL import Image
import numpy as np
import time

# Check whether the pixel points meet the GAP condition
def check_gap_conditions(img_array, row, col):
    # Condition 1: Grayscale value between 5-30 (inclusive)
    if not (5 <= img_array[row, col] <= 30):
        return False
    
    # Condition 2: At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition
    height, width = img_array.shape
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
    
    for dr, dc in directions:
        count = 0
        r, c = row, col
        
        # Check 20 pixels in this direction
        for _ in range(20):
            r += dr
            c += dc
            
            # Check if we're still within image boundaries
            if 0 <= r < height and 0 <= c < width:
                if 5 <= img_array[r, c] <= 30:
                    count += 1
                else:
                    break
            else:
                break
        
        # If we found 20 contiguous pixels meeting the condition, return True
        if count >= 20:
            return True
    
    return False

# Process all images in the directory whose filenames start with "Li_"
def process_images(input_directory, output_directory):
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    # Get all image files with "Li_" prefix
    image_files = [f for f in os.listdir(input_directory) 
                  if f.startswith("Li_") and (f.lower().endswith('.png') or f.lower().endswith('.jpg'))]
    
    for img_file in image_files:
        print(f"Processing {img_file}...")
        img_path = os.path.join(input_directory, img_file)
        
        # Open the image and convert to grayscale
        with Image.open(img_path) as img:
            gray_img = img.convert('L')
            img_array = np.array(gray_img)
            
            # Create a copy of the original image for highlighting GAP pixels
            highlight_img = img.convert('RGB')
            highlight_array = np.array(highlight_img)
            
            # Create CSV file
            base_name = os.path.splitext(img_file)[0]
            csv_file = os.path.join(output_directory, f"{base_name}_gap_analysis.csv")
            
            with open(csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Row", "Column", "Grayscale Value", "GAP Flag"])
                
                height, width = img_array.shape
                
                # Process each pixel
                for row in range(height):
                    for col in range(width):
                        gray_value = img_array[row, col]
                        gap_flag = 1 if check_gap_conditions(img_array, row, col) else 0
                        
                        # Write to CSV
                        writer.writerow([row, col, gray_value, gap_flag])
                        
                        # Highlight GAP pixels in red
                        if gap_flag == 1:
                            highlight_array[row, col] = [255, 0, 0]  # Red color
            
            # Save the highlighted image
            highlight_img = Image.fromarray(highlight_array)
            highlight_path = os.path.join(output_directory, f"{base_name}_gap_highlighted.png")
            highlight_img.save(highlight_path)
            
            print(f"Completed processing {img_file}")
            print(f"CSV saved to: {csv_file}")
            print(f"Highlighted image saved to: {highlight_path}")

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T1S1\backup9"
    
    start_time = time.time()
    process_images(input_directory, output_directory)
    end_time = time.time()
    
    print(f"Processed all the images! Time taken: {end_time - start_time:.2f} seconds")
