import os
import csv
from PIL import Image
import numpy as np
import time

def check_gap_conditions(gray_array, row, col):
    # Check condition 1: Grayscale value between 5-30 (inclusive)
    if not (5 <= gray_array[row, col] <= 30):
        return False
    
    # Check condition 2: At least one adjacent pixel has 20 contiguous pixels meeting grayscale condition
    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # right, down, left, up
    height, width = gray_array.shape
    
    for dr, dc in directions:
        count = 0
        r, c = row, col
        
        # Check 20 pixels in this direction
        for _ in range(20):
            r, c = r + dr, c + dc
            if 0 <= r < height and 0 <= c < width and 5 <= gray_array[r, c] <= 30:
                count += 1
            else:
                break
        
        if count >= 20:
            return True
    
    return False

def process_images(input_directory):
    # Ensure output directory exists
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T1S1"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get all files in the directory
    for filename in os.listdir(input_directory):
        # Check if file starts with "Li_" and is an image
        if filename.startswith("Li_") and (filename.lower().endswith('.png') or filename.lower().endswith('.jpg')):
            image_path = os.path.join(input_directory, filename)
            
            # Open image and convert to grayscale
            img = Image.open(image_path)
            gray_img = img.convert('L')
            
            # Convert to numpy array for processing
            gray_array = np.array(gray_img)
            height, width = gray_array.shape
            
            # Create a new RGB image to highlight GAP pixels
            highlight_img = img.convert('RGB')
            highlight_array = np.array(highlight_img)
            
            # Prepare CSV data
            csv_data = []
            
            # Process each pixel
            for row in range(height):
                for col in range(width):
                    gray_value = gray_array[row, col]
                    is_gap = 1 if check_gap_conditions(gray_array, row, col) else 0
                    
                    # Store pixel data
                    csv_data.append([row, col, gray_value, is_gap])
                    
                    # Highlight GAP pixels in red
                    if is_gap:
                        highlight_array[row, col] = [255, 0, 0]
            
            # Save the highlighted image
            base_name = os.path.splitext(filename)[0]
            highlight_img = Image.fromarray(highlight_array)
            highlight_img.save(os.path.join(output_dir, f"{base_name}_gap_highlighted.png"))
            
            # Save CSV file
            csv_filename = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
            with open(csv_filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Row', 'Column', 'Grayscale_Value', 'GAP_Flag'])
                writer.writerows(csv_data)

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    print("Processed all the images!")