import os
import csv
import argparse
import numpy as np
from PIL import Image

def check_gap_conditions(img_array, row, col):
    """Check if a pixel meets GAP conditions."""
    gray = img_array[row, col]
    if gray < 5 or gray > 30:
        return False
        
    height, width = img_array.shape
    directions = [
        (0, 1),   # right
        (0, -1),  # left
        (1, 0),   # down
        (-1, 0)   # up
    ]
    
    for dr, dc in directions:
        adjacent_row, adjacent_col = row + dr, col + dc
        if 0 <= adjacent_row < height and 0 <= adjacent_col < width:
            count = 0
            # Check 20 contiguous pixels starting from adjacent pixel
            for step in range(20):
                r = adjacent_row + dr * step
                c = adjacent_col + dc * step
                if not (0 <= r < height and 0 <= c < width) or not (5 <= img_array[r, c] <= 30):
                    break
                count += 1
                if count == 20:
                    return True
    return False

def process_image(image_path, re, output_dir):
    """Process a single image: analyze pixels and generate outputs."""
    img = Image.open(image_path)
    img_gray = img.convert('L')
    img_array = np.array(img_gray)
    height, width = img_array.shape
    gap_flags = np.zeros_like(img_array, dtype=np.uint8)
    
    # Identify GAP pixels
    for row in range(height):
        for col in range(width):
            if check_gap_conditions(img_array, row, col):
                gap_flags[row, col] = 1
    
    # Save pixel analysis CSV
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    analysis_path = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
    with open(analysis_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['row', 'column', 'grayscale_value', 'GAP_flag'])
        for row in range(height):
            for col in range(width):
                writer.writerow([row, col, img_array[row, col], gap_flags[row, col]])
    
    # Calculate GAP height per column
    gap_heights = []
    for col in range(width):
        rows_with_gap = np.where(gap_flags[:, col] == 1)[0]
        if rows_with_gap.size > 0:
            min_row, max_row = np.min(rows_with_gap), np.max(rows_with_gap)
            gap_height = (max_row - min_row + 1) * re
            gap_heights.append([col, gap_height])
    
    # Save GAP height CSV
    height_path = os.path.join(output_dir, f"{base_name}_gap_height.csv")
    with open(height_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['column', 'GAP_height_um'])
        writer.writerows(gap_heights)
    
    # Save TXT summary
    txt_path = os.path.join(output_dir, f"{base_name}_summary.txt")
    max_height = max([h[1] for h in gap_heights]) if gap_heights else 0
    with open(txt_path, 'w') as f:
        f.write(f"Physical dimension parameter: {re} μm/pixel\n")
        f.write(f"Max gap height: {max_height} μm\n")
    
    # Generate highlighted image (GAP pixels in red)
    img_color = img.convert('RGB')
    pixels = img_color.load()
    for row in range(height):
        for col in range(width):
            if gap_flags[row, col] == 1:
                pixels[col, row] = (255, 0, 0)  # (col, row) for PIL
    img_color.save(os.path.join(output_dir, f"{base_name}_gap_highlight.png"))

def process_images(input_dir, re, output_dir):
    """Process all images in the input directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for filename in os.listdir(input_dir):
        if filename.startswith("Li_") and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            process_image(os.path.join(input_dir, filename), re, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process images to identify GAP pixels.')
    parser.add_argument('-re', type=float, required=True, help='Physical dimension (μm/pixel)')
    args = parser.parse_args()
    
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S2\backup3"
    
    process_images(input_directory, args.re, output_directory)
    print("Processed all images!")
