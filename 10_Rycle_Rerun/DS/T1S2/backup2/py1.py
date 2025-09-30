import os
import csv
import argparse
from PIL import Image
import numpy as np
from collections import defaultdict
import time

def compute_contiguous_runs(mask):
    """Compute horizontal and vertical contiguous runs for True pixels in a mask."""
    height, width = mask.shape
    # Horizontal runs
    hor_runs = np.zeros_like(mask, dtype=int)
    for i in range(height):
        j = 0
        while j < width:
            if mask[i, j]:
                start_j = j
                while j < width and mask[i, j]:
                    j += 1
                run_length = j - start_j
                hor_runs[i, start_j:j] = run_length
            else:
                j += 1
    
    # Vertical runs
    ver_runs = np.zeros_like(mask, dtype=int)
    for j in range(width):
        i = 0
        while i < height:
            if mask[i, j]:
                start_i = i
                while i < height and mask[i, j]:
                    i += 1
                run_length = i - start_i
                ver_runs[start_i:i, j] = run_length
            else:
                i += 1
                
    return hor_runs, ver_runs

def detect_gap_pixels(img_array):
    """Detect GAP pixels based on grayscale conditions."""
    # Condition (1): Grayscale between 5-30
    cond1_mask = (img_array >= 5) & (img_array <= 30)
    hor_runs, ver_runs = compute_contiguous_runs(cond1_mask)
    
    height, width = img_array.shape
    gap_mask = np.zeros_like(cond1_mask, dtype=bool)
    
    # Directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for i in range(height):
        for j in range(width):
            if not cond1_mask[i, j]:
                continue
                
            # Check neighbors for condition (2)
            neighbor_qualifies = False
            for dx, dy in directions:
                ni, nj = i + dx, j + dy
                if 0 <= ni < height and 0 <= nj < width and cond1_mask[ni, nj]:
                    if hor_runs[ni, nj] >= 20 or ver_runs[ni, nj] >= 20:
                        neighbor_qualifies = True
                        break
            gap_mask[i, j] = neighbor_qualifies
            
    return gap_mask

def process_image(image_path, re, output_dir):
    """Process a single image to detect GAP pixels and generate outputs."""
    with Image.open(image_path) as img:
        # Convert to grayscale and extract array
        gray_img = img.convert('L')
        img_array = np.array(gray_img)
        height, width = img_array.shape
        
        # Detect GAP pixels
        gap_mask = detect_gap_pixels(img_array)
        
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        
        # Generate per-pixel CSV file
        analysis_csv = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
        with open(analysis_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['row', 'column', 'grayscale_value', 'GAP_flag'])
            for i in range(height):
                for j in range(width):
                    gap_flag = 1 if gap_mask[i, j] else 0
                    writer.writerow([i, j, int(img_array[i, j]), gap_flag])
        
        # Calculate GAP height per column
        gap_heights = []
        for j in range(width):
            gap_rows_in_col = np.where(gap_mask[:, j])[0]
            if gap_rows_in_col.size > 0:
                min_row, max_row = np.min(gap_rows_in_col), np.max(gap_rows_in_col)
                gap_height = (max_row - min_row + 1) * re
            else:
                gap_height = 0.0
            gap_heights.append(gap_height)
        
        height_csv = os.path.join(output_dir, f"{base_name}_gap_height.csv")
        with open(height_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['column', 'GAP_height_um'])
            for j, h in enumerate(gap_heights):
                writer.writerow([j, round(h, 4)])
        
        # Generate TXT report
        max_height = max(gap_heights) if gap_heights else 0.0
        report_txt = os.path.join(output_dir, f"{base_name}_gap_report.txt")
        with open(report_txt, 'w') as f:
            f.write(f"Physical dimension parameter (μm/pixel): {re}\n")
            f.write(f"Max gap height (μm): {round(max_height, 4)}\n")
        
        # Create highlighted image (GAP pixels in red)
        if img.mode != 'RGB':
            rgb_img = img.convert('RGB')
        else:
            rgb_img = img.copy()
        rgb_array = np.array(rgb_img)
        rgb_array[gap_mask] = [255, 0, 0]  # Set GAP pixels to red
        highlighted_img = Image.fromarray(rgb_array)
        highlighted_img.save(os.path.join(output_dir, f"{base_name}_gap_highlighted.png"))
        
        return max_height

def process_images(input_dir, re, output_dir):
    """Process all valid images in the input directory."""
    valid_exts = ('.png', '.jpg', '.jpeg')
    images = [f for f in os.listdir(input_dir) 
              if f.startswith('Li_') and f.lower().endswith(valid_exts)]
    
    if not images:
        print("No valid images found.")
        return
    
    for img_file in images:
        img_path = os.path.join(input_dir, img_file)
        print(f"Processing: {img_file}")
        max_height = process_image(img_path, re, output_dir)
        print(f"  - Max gap height: {max_height:.4f} μm")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Detect GAP pixels in images.")
    parser.add_argument("-re", type=float, required=True, 
                        help="Physical dimension in micrometers per pixel")
    args = parser.parse_args()
    
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S2\backup2"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)
    
    start_time = time.time()
    process_images(input_directory, args.re, output_directory)
    elapsed = time.time() - start_time
    
    print(f"Processed all images in {elapsed:.2f} seconds!")
