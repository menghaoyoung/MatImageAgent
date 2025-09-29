import os
import csv
import sys
import numpy as np
from PIL import Image

def check_gap_condition_at_pixel(gray_array, r, c, height, width):
    """Check if a pixel meets the GAP condition (grayscale value between 5-30 and 
    at least one adjacent direction has 20 contiguous qualifying pixels)."""
    # Condition 1: Grayscale value between 5-30
    if not (5 <= gray_array[r, c] <= 30):
        return False
    
    # Directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for dr, dc in directions:
        nr, nc = r + dr, c + dc  # Start from adjacent pixel
        count = 0
        # Traverse in the current direction
        while 0 <= nr < height and 0 <= nc < width:
            if 5 <= gray_array[nr, nc] <= 30:
                count += 1
                if count >= 20:
                    return True  # Condition satisfied
            else:
                break  # Break on non-qualifying pixel
            nr += dr
            nc += dc
    return False

def process_image(image_path, output_dir):
    """Process a single image: convert to grayscale, detect GAP pixels, 
    generate CSV and highlighted PNG."""
    # Open image and convert to grayscale
    img = Image.open(image_path)
    gray_img = img.convert('L')
    gray_array = np.array(gray_img)
    height, width = gray_array.shape
    
    # Initialize gap_flags array (0=no gap, 1=gap)
    gap_flags = np.zeros((height, width), dtype=int)
    
    # Process each pixel
    for r in range(height):
        for c in range(width):
            if check_gap_condition_at_pixel(gray_array, r, c, height, width):
                gap_flags[r, c] = 1
    
    # Generate CSV output
    base_name = os.path.basename(image_path).split('.')[0]
    csv_path = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['row', 'column', 'gray_value', 'gap_flag'])
        for r in range(height):
            for c in range(width):
                writer.writerow([r, c, gray_array[r, c], gap_flags[r, c]])
    
    # Generate highlighted PNG image
    rgb_array = np.stack((gray_array,) * 3, axis=-1)  # Convert to RGB
    red_pixels = np.where(gap_flags[..., None] == 1, [255, 0, 0], rgb_array)
    highlight_img = Image.fromarray(red_pixels.astype('uint8'))
    highlight_img.save(os.path.join(output_dir, f"{base_name}_gap_highlighted.png"))

def process_images(input_dir):
    """Process all Li_*.png/jpg images in the input directory."""
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1\backup4"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Find relevant images
    for filename in os.listdir(input_dir):
        if filename.startswith("Li_"):
            ext = os.path.splitext(filename)[1].lower()
            if ext in ('.png', '.jpg'):
                image_path = os.path.join(input_dir, filename)
                process_image(image_path, output_dir)

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    if len(sys.argv) > 1:
        input_directory = sys.argv[1]  # Allow command-line override
    process_images(input_directory)
    print("Processed all images!")
