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
        count = 0
        r, c = row, col
        
        # Check 20 pixels in this direction
        for _ in range(20):
            r += dr
            c += dc
            
            # Check if within image boundaries
            if 0 <= r < height and 0 <= c < width:
                if 5 <= img_array[r, c] <= 30:
                    count += 1
                else:
                    break
            else:
                break
        
        if count >= 20:
            return True
    
    return False

# Process all images in the directory whose filenames start with "Li_"
def process_images(input_directory):
    # Ensure output directory exists
    output_dir = os.path.join(os.path.dirname(input_directory), "ALL_RESULT", "CLAUDE", "T1S1", "backup7")
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all image files with "Li_" prefix
    image_files = [f for f in os.listdir(input_directory) 
                  if f.startswith("Li_") and (f.lower().endswith('.png') or f.lower().endswith('.jpg'))]
    
    for image_file in image_files:
        print(f"Processing {image_file}...")
        start_time = time.time()
        
        # Open image and convert to grayscale
        img_path = os.path.join(input_directory, image_file)
        img = Image.open(img_path).convert('L')
        img_array = np.array(img)
        height, width = img_array.shape
        
        # Create a new RGB image for highlighting GAP pixels
        highlighted_img = Image.new('RGB', (width, height), (0, 0, 0))
        highlighted_pixels = highlighted_img.load()
        
        # Create original grayscale RGB image
        original_rgb = Image.new('RGB', (width, height), (0, 0, 0))
        for y in range(height):
            for x in range(width):
                gray_value = img_array[y, x]
                original_rgb.putpixel((x, y), (gray_value, gray_value, gray_value))
        
        # Prepare CSV data
        csv_data = []
        
        # Check each pixel
        for row in range(height):
            for col in range(width):
                gray_value = img_array[row, col]
                is_gap = check_gap_conditions(img_array, row, col)
                gap_flag = 1 if is_gap else 0
                
                # Add to CSV data
                csv_data.append([row, col, gray_value, gap_flag])
                
                # Set pixel in highlighted image
                if is_gap:
                    highlighted_pixels[col, row] = (255, 0, 0)  # Red for GAP pixels
                else:
                    highlighted_pixels[col, row] = (gray_value, gray_value, gray_value)
        
        # Save highlighted image
        base_name = os.path.splitext(image_file)[0]
        highlighted_img_path = os.path.join(output_dir, f"{base_name}_gap_highlighted.png")
        highlighted_img.save(highlighted_img_path)
        
        # Save CSV file
        csv_path = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
        save_csv(csv_path, csv_data)
        
        end_time = time.time()
        print(f"Completed processing {image_file} in {end_time - start_time:.2f} seconds")

# Stores all pixel analysis data
def save_csv(csv_path, data):
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Row', 'Column', 'Grayscale Value', 'GAP Flag'])
        writer.writerows(data)

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    print("Processed all the images!")
