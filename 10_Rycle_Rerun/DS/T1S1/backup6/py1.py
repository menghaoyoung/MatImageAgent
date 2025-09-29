import os
import csv
import numpy as np
from PIL import Image

def check_gap_conditions(image_array):
    """
    Identify GAP pixels based on grayscale conditions.
    (1) Grayscale value between 5-30 (inclusive)
    (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels in [5,30]
    """
    in_range = (image_array >= 5) & (image_array <= 30)
    height, width = image_array.shape
    
    # Initialize direction arrays
    right_length = np.zeros((height, width), dtype=int)
    left_length = np.zeros((height, width), dtype=int)
    up_length = np.zeros((height, width), dtype=int)
    down_length = np.zeros((height, width), dtype=int)
    
    # Compute contiguous pixel lengths in all four directions
    # Right (left-to-right traversal)
    for i in range(height):
        for j in range(width-1, -1, -1):
            if in_range[i, j]:
                right_length[i, j] = 1 if j == width-1 else right_length[i, j+1] + 1
    
    # Left (right-to-left traversal)
    for i in range(height):
        for j in range(width):
            if in_range[i, j]:
                left_length[i, j] = 1 if j == 0 else left_length[i, j-1] + 1
    
    # Down (top-to-bottom traversal)
    for j in range(width):
        for i in range(height-1, -1, -1):
            if in_range[i, j]:
                down_length[i, j] = 1 if i == height-1 else down_length[i+1, j] + 1
    
    # Up (bottom-to-top traversal)
    for j in range(width):
        for i in range(height):
            if in_range[i, j]:
                up_length[i, j] = 1 if i == 0 else up_length[i-1, j] + 1
    
    # Check GAP conditions
    gap_flags = np.zeros((height, width), dtype=int)
    
    for i in range(height):
        for j in range(width):
            if not in_range[i, j]:
                continue  # Skip if condition (1) fails
            
            # Check adjacent pixels for condition (2)
            if (j < width-1 and right_length[i, j+1] >= 20) or \
               (j > 0 and left_length[i, j-1] >= 20) or \
               (i > 0 and up_length[i-1, j] >= 20) or \
               (i < height-1 and down_length[i+1, j] >= 20):
                gap_flags[i, j] = 1
    
    return gap_flags

def process_images(input_directory):
    """Process all Li_ prefix images in directory, generate CSV and highlighted PNGs."""
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1\backup6"
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_directory):
        if not (filename.startswith("Li_") and 
                filename.lower().endswith(('.png', '.jpg', '.jpeg'))):
            continue
            
        # Load original and grayscale images
        img_path = os.path.join(input_directory, filename)
        orig_img = Image.open(img_path)
        gray_img = orig_img.convert('L')
        gray_array = np.array(gray_img)
        
        # Get GAP flags
        gap_flags = check_gap_conditions(gray_array)
        
        # Save CSV analysis
        base_name = os.path.splitext(filename)[0]
        csv_path = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['row', 'column', 'grayscale_value', 'GAP_flag'])
            height, width = gray_array.shape
            for i in range(height):
                for j in range(width):
                    writer.writerow([i, j, int(gray_array[i, j]), gap_flags[i, j]])
        
        # Generate highlighted image
        if orig_img.mode != 'RGB':
            output_img = orig_img.convert('RGB')
        else:
            output_img = orig_img.copy()
            
        pixels = output_img.load()
        for i in range(gray_array.shape[0]):
            for j in range(gray_array.shape[1]):
                if gap_flags[i, j] == 1:
                    pixels[j, i] = (255, 0, 0)  # Set to red
        
        img_out_path = os.path.join(output_dir, f"{base_name}_gap_highlighted.png")
        output_img.save(img_out_path)

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    print("Processed all images!")
