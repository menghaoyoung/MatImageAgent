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
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
    height, width = img_array.shape
    
    for dr, dc in directions:
        contiguous_count = 0
        r, c = row, col
        
        # Check up to 20 pixels in this direction
        for _ in range(20):
            r += dr
            c += dc
            
            # Check if we're still within the image boundaries
            if 0 <= r < height and 0 <= c < width:
                if 5 <= img_array[r, c] <= 30:
                    contiguous_count += 1
                else:
                    break
            else:
                break
        
        if contiguous_count >= 20:
            return True
    
    return False

# Process all images in the directory whose filenames start with "Li_"
def process_images(input_directory):
    # Create output directory if it doesn't exist
    output_directory = os.path.join(os.path.dirname(input_directory), "ALL_RESULT", "CLAUDE", "T1S1", "backup4")
    os.makedirs(output_directory, exist_ok=True)
    
    # Get all image files starting with "Li_"
    image_files = [f for f in os.listdir(input_directory) 
                  if f.startswith("Li_") and (f.lower().endswith('.png') or f.lower().endswith('.jpg'))]
    
    for image_file in image_files:
        print(f"Processing {image_file}...")
        
        # Load the image and convert to grayscale
        img_path = os.path.join(input_directory, image_file)
        img = Image.open(img_path).convert('L')
        img_array = np.array(img)
        
        # Create a colored version for highlighting GAP pixels
        highlighted_img = Image.open(img_path).convert('RGB')
        highlighted_array = np.array(highlighted_img)
        
        # Create CSV file
        image_name = os.path.splitext(image_file)[0]
        csv_filename = f"{image_name}_gap_analysis.csv"
        csv_path = os.path.join(output_directory, csv_filename)
        
        with open(csv_path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(['Row', 'Column', 'Grayscale_Value', 'GAP_Flag'])
            
            height, width = img_array.shape
            
            # Process each pixel
            for row in range(height):
                for col in range(width):
                    grayscale_value = int(img_array[row, col])
                    
                    # Check if pixel meets GAP conditions
                    gap_flag = 1 if check_gap_conditions(img_array, row, col) else 0
                    
                    # Write to CSV
                    csv_writer.writerow([row, col, grayscale_value, gap_flag])
                    
                    # Highlight GAP pixels in red
                    if gap_flag == 1:
                        highlighted_array[row, col] = [255, 0, 0]  # Red color
            
            # Save the highlighted image
            highlighted_img = Image.fromarray(highlighted_array)
            highlighted_filename = f"{image_name}_highlighted.png"
            highlighted_path = os.path.join(output_directory, highlighted_filename)
            highlighted_img.save(highlighted_path)
            
            print(f"Saved {csv_filename} and {highlighted_filename}")

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    start_time = time.time()
    process_images(input_directory)
    end_time = time.time()
    print(f"Processed all the images in {end_time - start_time:.2f} seconds!")
