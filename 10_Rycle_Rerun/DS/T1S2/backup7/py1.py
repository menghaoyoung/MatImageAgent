import os
import csv
import argparse
import numpy as np
from PIL import Image

def precompute_runs(gray_array):
    """Precompute contiguous runs in all directions for optimized gap detection."""
    height, width = gray_array.shape
    # Initialize run-length arrays
    left_run = np.zeros_like(gray_array, dtype=np.uint16)
    right_run = np.zeros_like(gray_array, dtype=np.uint16)
    top_run = np.zeros_like(gray_array, dtype=np.uint16)
    bottom_run = np.zeros_like(gray_array, dtype=np.uint16)
    
    # Condition mask (5 <= value <= 30)
    valid_mask = (gray_array >= 5) & (gray_array <= 30)
    
    # Horizontal runs (left to right)
    for i in range(height):
        for j in range(width):
            if valid_mask[i, j]:
                left_run[i, j] = left_run[i, j-1] + 1 if j > 0 else 1
    
    # Horizontal runs (right to left)
    for i in range(height):
        for j in range(width-1, -1, -1):
            if valid_mask[i, j]:
                right_run[i, j] = right_run[i, j+1] + 1 if j < width-1 else 1
                
    # Vertical runs (top to bottom)
    for j in range(width):
        for i in range(height):
            if valid_mask[i, j]:
                top_run[i, j] = top_run[i-1, j] + 1 if i > 0 else 1
                
    # Vertical runs (bottom to top)
    for j in range(width):
        for i in range(height-1, -1, -1):
            if valid_mask[i, j]:
                bottom_run[i, j] = bottom_run[i+1, j] + 1 if i < height-1 else 1
                
    return left_run, right_run, top_run, bottom_run

def check_gap_conditions(gray_array, runs):
    """Identify gap pixels using precomputed run-length data."""
    left_run, right_run, top_run, bottom_run = runs
    height, width = gray_array.shape
    gap_flag = np.zeros_like(gray_array, dtype=np.uint8)
    valid_mask = (gray_array >= 5) & (gray_array <= 30)
    
    # Precompute neighbor offsets
    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for i in range(height):
        for j in range(width):
            if not valid_mask[i, j]:
                continue
                
            # Check neighbor conditions
            for dx, dy in neighbors:
                ni, nj = i + dx, j + dy
                if 0 <= ni < height and 0 <= nj < width and valid_mask[ni, nj]:
                    # Check horizontal contiguous run
                    if (left_run[ni, nj] + right_run[ni, nj] - 1) >= 20:
                        gap_flag[i, j] = 1
                        break
                    # Check vertical contiguous run
                    if (top_run[ni, nj] + bottom_run[ni, nj] - 1) >= 20:
                        gap_flag[i, j] = 1
                        break
    return gap_flag

def process_images(input_dir, output_dir, re_value):
    """Process all Li_ prefix images in input directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for filename in os.listdir(input_dir):
        if filename.startswith("Li_") and filename.lower().endswith(('.png', '.jpg')):
            img_path = os.path.join(input_dir, filename)
            img = Image.open(img_path)
            base_name = os.path.splitext(filename)[0]
            
            # Convert to grayscale and get numpy array
            gray_img = img.convert('L')
            gray_array = np.array(gray_img)
            height, width = gray_array.shape
            
            # Precompute runs and get gap flags
            runs = precompute_runs(gray_array)
            gap_flag = check_gap_conditions(gray_array, runs)
            
            # Generate per-pixel CSV
            csv_pixel_path = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
            with open(csv_pixel_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['row', 'col', 'grayscale', 'gap_flag'])
                for i in range(height):
                    for j in range(width):
                        writer.writerow([i, j, gray_array[i, j], gap_flag[i, j]])
            
            # Calculate gap heights per column
            gap_heights = []
            for j in range(width):
                gap_rows = np.where(gap_flag[:, j] == 1)[0]
                if gap_rows.size > 0:
                    min_row, max_row = gap_rows.min(), gap_rows.max()
                    gap_heights.append((max_row - min_row + 1) * re_value)
                else:
                    gap_heights.append(0.0)
            
            # Save height CSV
            csv_height_path = os.path.join(output_dir, f"{base_name}_gap_height.csv")
            with open(csv_height_path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['column_index', 'gap_height_um'])
                for j, height_val in enumerate(gap_heights):
                    writer.writerow([j, height_val])
            
            # Generate TXT file with metadata
            max_height = max(gap_heights) if gap_heights else 0.0
            txt_path = os.path.join(output_dir, f"{base_name}_info.txt")
            with open(txt_path, 'w') as f:
                f.write(f"Physical dimension parameter (μm/pixel): {re_value}\n")
                f.write(f"Height statistics (max height in μm): {max_height}\n")
            
            # Create highlighted image (GAP pixels in red)
            if img.mode != 'RGB':
                rgb_img = img.convert('RGB')
            else:
                rgb_img = img.copy()
            rgb_array = np.array(rgb_img)
            rgb_array[gap_flag == 1] = [255, 0, 0]  # Set gap pixels to red
            Image.fromarray(rgb_array).save(os.path.join(output_dir, f"{base_name}_gap_highlight.png"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='GAP Pixel Detection')
    parser.add_argument('-re', type=float, required=True, help='Microns per pixel resolution')
    args = parser.parse_args()
    
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S2\backup7"
    
    process_images(input_directory, output_directory, args.re)
    print("Processed all images!")
