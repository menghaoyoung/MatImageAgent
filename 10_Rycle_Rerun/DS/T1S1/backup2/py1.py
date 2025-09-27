import os
import sys
import csv
import numpy as np
from PIL import Image

def has_contiguous(gray_array, i, j, dr, dc, count=20, min_gray=5, max_gray=30):
    """Check if 20 contiguous pixels exist starting from adjacent (i+dr, j+dc) in direction (dr,dc)."""
    h, w = gray_array.shape
    for step in range(1, count + 1):
        r = i + dr * step
        c = j + dc * step
        if r < 0 or r >= h or c < 0 or c >= w:
            return False
        if not (min_gray <= gray_array[r, c] <= max_gray):
            return False
    return True

def process_images(input_directory, output_directory):
    """Process all Li_ prefix images: generate CSV outputs and highlighted PNGs."""
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # (dr,dc): up, down, left, right
    
    for filename in os.listdir(input_directory):
        if filename.startswith("Li_") and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"Processing {filename}...")
            img_path = os.path.join(input_directory, filename)
            
            # Load and convert images
            img_rgb = Image.open(img_path).convert('RGB')
            img_gray = img_rgb.convert('L')
            gray_array = np.array(img_gray)
            rgb_array = np.array(img_rgb)
            h, w = gray_array.shape
            
            # Precompute condition1 (grayscale 5-30)
            condition1 = (gray_array >= 5) & (gray_array <= 30)
            gap_flags = np.zeros((h, w), dtype=np.uint8)
            
            # Check GAP conditions for qualifying pixels
            for i in range(h):
                for j in range(w):
                    if condition1[i, j]:
                        for dr, dc in directions:
                            if has_contiguous(gray_array, i, j, dr, dc):
                                gap_flags[i, j] = 1
                                break  # Only one valid direction needed
            
            # Save CSV
            base_name = os.path.splitext(filename)[0]
            csv_path = os.path.join(output_directory, f"{base_name}_gap_analysis.csv")
            with open(csv_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['row', 'column', 'grayscale_value', 'GAP_flag'])
                for i in range(h):
                    for j in range(w):
                        writer.writerow([i, j, gray_array[i, j], gap_flags[i, j]])
            
            # Save highlighted image (GAP=1 pixels in red)
            rgb_array[gap_flags == 1] = [255, 0, 0]  # Assign red to GAP pixels
            img_out = Image.fromarray(rgb_array)
            img_out.save(os.path.join(output_directory, f"{base_name}_gap_highlight.png"))

if __name__ == "__main__":
    # Input directory from command line or default
    input_directory = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    
    # Hardcoded output directory
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1\backup2"
    
    process_images(input_directory, output_directory)
    print("[DEBUG] Processed all images!")
