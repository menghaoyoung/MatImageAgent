import os
import csv
import argparse
import numpy as np
from PIL import Image

def compute_directional_runs(mask, direction):
    """Compute contiguous runs of True values in the specified direction."""
    runs = np.zeros(mask.shape, dtype=np.uint32)
    height, width = mask.shape
    
    if direction == 'left':
        for i in range(height):
            for j in range(width):
                if mask[i, j]:
                    runs[i, j] = runs[i, j-1] + 1 if j > 0 else 1
    elif direction == 'right':
        for i in range(height):
            for j in range(width-1, -1, -1):
                if mask[i, j]:
                    runs[i, j] = runs[i, j+1] + 1 if j < width-1 else 1
    elif direction == 'top':
        for j in range(width):
            for i in range(height):
                if mask[i, j]:
                    runs[i, j] = runs[i-1, j] + 1 if i > 0 else 1
    elif direction == 'bottom':
        for j in range(width):
            for i in range(height-1, -1, -1):
                if mask[i, j]:
                    runs[i, j] = runs[i+1, j] + 1 if i < height-1 else 1
    return runs

def calculate_gap_flags(gray):
    """Calculate GAP flags based on grayscale conditions."""
    height, width = gray.shape
    mask = (gray >= 5) & (gray <= 30)
    
    # Compute directional runs
    left_run = compute_directional_runs(mask, 'left')
    right_run = compute_directional_runs(mask, 'right')
    top_run = compute_directional_runs(mask, 'top')
    bottom_run = compute_directional_runs(mask, 'bottom')
    
    gap_flags = np.zeros((height, width), dtype=np.uint8)
    
    for i in range(height):
        for j in range(width):
            if mask[i, j]:
                neighbors = [(i-1, j), (i+1, j), (i, j-1), (i, j+1)]
                for ni, nj in neighbors:
                    if 0 <= ni < height and 0 <= nj < width and mask[ni, nj]:
                        h_run = left_run[ni, nj] + right_run[ni, nj] - 1
                        v_run = top_run[ni, nj] + bottom_run[ni, nj] - 1
                        if h_run >= 20 or v_run >= 20:
                            gap_flags[i, j] = 1
                            break
    return gap_flags

def process_images(input_dir, output_dir, re_value):
    """Process all images starting with 'Li_' in directory."""
    for filename in os.listdir(input_dir):
        if filename.startswith("Li_") and (filename.lower().endswith('.png') or filename.lower().endswith('.jpg')):
            filepath = os.path.join(input_dir, filename)
            base_name = os.path.splitext(filename)[0]
            
            # Process image
            with Image.open(filepath) as img:
                gray_img = img.convert('L')
                gray = np.array(gray_img)
                height, width = gray.shape
                
                gap_flags = calculate_gap_flags(gray)
                
                # Create highlighted image
                rgb_img = np.stack((gray, gray, gray), axis=-1).astype(np.uint8)
                red_mask = (gap_flags == 1)
                rgb_img[red_mask] = [255, 0, 0]
                Image.fromarray(rgb_img).save(os.path.join(output_dir, f"{base_name}_gap_highlight.png"))
                
                # Save pixel analysis CSV
                with open(os.path.join(output_dir, f"{base_name}_gap_analysis.csv"), 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['row', 'col', 'grayscale_value', 'gap_flag'])
                    for i in range(height):
                        for j in range(width):
                            writer.writerow([i, j, gray[i, j], gap_flags[i, j]])
                
                # Calculate and save gap heights
                gap_heights = []
                for j in range(width):
                    gap_rows = np.where(gap_flags[:, j] == 1)[0]
                    gap_height = (gap_rows.max() - gap_rows.min() + 1) * re_value if gap_rows.size > 0 else 0.0
                    gap_heights.append(gap_height)
                
                with open(os.path.join(output_dir, f"{base_name}_gap_height.csv"), 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Column', 'GAP_Height'])
                    for j, height_val in enumerate(gap_heights):
                        writer.writerow([j, height_val])
                
                # Save text statistics
                max_height = max(gap_heights) if gap_heights else 0.0
                with open(os.path.join(output_dir, f"{base_name}_gap_info.txt"), 'w') as f:
                    f.write(f"Physical dimension parameter (um/pixel): {re_value}\n")
                    f.write(f"Max height (um): {max_height}\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-re', type=float, required=True, help="Pixel resolution (um/pixel)")
    args = parser.parse_args()
    
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S2\backup1"
    
    os.makedirs(output_dir, exist_ok=True)
    process_images(input_dir, output_dir, args.re)
    print("Processed all images!")

if __name__ == "__main__":
    main()
