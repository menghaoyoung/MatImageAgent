import os
import argparse
import csv
from PIL import Image
import numpy as np
import sys

def compute_run_lengths(arr, axis):
    """Compute run-length encoding along specified axis (0=vertical, 1=horizontal)"""
    if axis == 1:  # Horizontal
        run_lengths = np.zeros_like(arr, dtype=int)
        for i in range(arr.shape[0]):
            j = 0
            while j < arr.shape[1]:
                if arr[i, j]:
                    start = j
                    while j < arr.shape[1] and arr[i, j]:
                        j += 1
                    run_lengths[i, start:j] = j - start
                else:
                    j += 1
        return run_lengths
    else:  # Vertical
        run_lengths = np.zeros_like(arr, dtype=int)
        for j in range(arr.shape[1]):
            i = 0
            while i < arr.shape[0]:
                if arr[i, j]:
                    start = i
                    while i < arr.shape[0] and arr[i, j]:
                        i += 1
                    run_lengths[start:i, j] = i - start
                else:
                    i += 1
        return run_lengths

def process_image(image_path, re, output_dir):
    """Process a single image to detect GAP pixels and compute heights"""
    img = Image.open(image_path).convert('L')
    gray = np.array(img)
    height, width = gray.shape
    
    # Create candidate mask (5-30 grayscale)
    candidate_mask = (gray >= 5) & (gray <= 30)
    
    # Compute run lengths
    horizontal_runs = compute_run_lengths(candidate_mask, axis=1)
    vertical_runs = compute_run_lengths(candidate_mask, axis=0)
    
    # Initialize gap flag array
    gap_flag = np.zeros_like(gray, dtype=np.uint8)
    
    # Check gap conditions
    for i in range(height):
        for j in range(width):
            if candidate_mask[i, j]:
                # Check 4 neighbors for run-length >= 20
                neighbors = []
                if i > 0: neighbors.append((i-1, j))
                if i < height-1: neighbors.append((i+1, j))
                if j > 0: neighbors.append((i, j-1))
                if j < width-1: neighbors.append((i, j+1))
                
                for ni, nj in neighbors:
                    if horizontal_runs[ni, nj] >= 20 or vertical_runs[ni, nj] >= 20:
                        gap_flag[i, j] = 1
                        break
    
    # Generate per-pixel CSV
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    analysis_csv = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
    with open(analysis_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['row', 'col', 'grayscale', 'gap_flag'])
        for i in range(height):
            for j in range(width):
                writer.writerow([i, j, gray[i, j], gap_flag[i, j]])
    
    # Calculate gap height per column
    gap_heights = []
    for j in range(width):
        gap_rows = np.where(gap_flag[:, j] == 1)[0]
        if len(gap_rows) > 0:
            min_row, max_row = np.min(gap_rows), np.max(gap_rows)
            gap_heights.append((max_row - min_row + 1) * re)
        else:
            gap_heights.append(0.0)
    
    # Save gap heights CSV
    height_csv = os.path.join(output_dir, f"{base_name}_gap_height.csv")
    with open(height_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['column', 'gap_height_um'])
        for j, h in enumerate(gap_heights):
            writer.writerow([j, round(h, 6)])
    
    # Generate TXT report
    max_height = round(max(gap_heights), 6) if gap_heights else 0.0
    txt_path = os.path.join(output_dir, f"{base_name}_gap_report.txt")
    with open(txt_path, 'w') as f:
        f.write(f"Physical dimension parameter (μm/pixel): {re}\n")
        f.write(f"Max height (μm): {max_height}\n")
    
    # Create highlighted image
    rgb_img = np.repeat(gray[:, :, np.newaxis], 3, axis=2)
    rgb_img[gap_flag.astype(bool)] = [255, 0, 0]
    highlight_img = Image.fromarray(rgb_img.astype(np.uint8))
    highlight_img.save(os.path.join(output_dir, f"{base_name}_gap_highlight.png"))
    
    return max_height

def process_images(input_dir, output_dir, re):
    """Process all images with Li_ prefix in input directory"""
    os.makedirs(output_dir, exist_ok=True)
    image_exts = ('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG')
    
    for filename in os.listdir(input_dir):
        if filename.startswith('Li_') and filename.lower().endswith(image_exts):
            image_path = os.path.join(input_dir, filename)
            process_image(image_path, re, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Detect GAP pixels and compute gap heights')
    parser.add_argument('-re', type=float, required=True, help='Physical dimension in μm per pixel')
    args = parser.parse_args()
    
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S2\backup5"
    
    process_images(input_directory, output_directory, args.re)
    print("Processed all images!")

# NO-RUN-PY
