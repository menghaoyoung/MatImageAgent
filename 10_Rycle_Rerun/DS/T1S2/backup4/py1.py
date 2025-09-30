import os
import csv
import argparse
import numpy as np
from PIL import Image

def compute_contiguous_arrays(condition_a_mask):
    height, width = condition_a_mask.shape
    left = np.zeros((height, width), dtype=int)
    right = np.zeros((height, width), dtype=int)
    up = np.zeros((height, width), dtype=int)
    down = np.zeros((height, width), dtype=int)
    
    # Left contiguous count
    for i in range(height):
        for j in range(width):
            if condition_a_mask[i, j]:
                if j == 0:
                    left[i, j] = 1
                else:
                    left[i, j] = left[i, j-1] + 1
    
    # Right contiguous count
    for i in range(height):
        for j in range(width-1, -1, -1):
            if condition_a_mask[i, j]:
                if j == width-1:
                    right[i, j] = 1
                else:
                    right[i, j] = right[i, j+1] + 1
    
    # Up contiguous count
    for j in range(width):
        for i in range(height):
            if condition_a_mask[i, j]:
                if i == 0:
                    up[i, j] = 1
                else:
                    up[i, j] = up[i-1, j] + 1
    
    # Down contiguous count
    for j in range(width):
        for i in range(height-1, -1, -1):
            if condition_a_mask[i, j]:
                if i == height-1:
                    down[i, j] = 1
                else:
                    down[i, j] = down[i+1, j] + 1
                    
    return left, right, up, down

def process_images(input_dir, output_dir, re_val):
    image_exts = ('.png', '.jpg', '.jpeg')
    for img_name in os.listdir(input_dir):
        if img_name.startswith("Li_") and img_name.lower().endswith(image_exts):
            img_path = os.path.join(input_dir, img_name)
            base_name = os.path.splitext(img_name)[0]
            
            with Image.open(img_path) as img:
                # Convert to grayscale and get numpy array
                gray_img = img.convert('L')
                gray_array = np.array(gray_img)
                height, width = gray_array.shape
                
                # Condition A: Grayscale between 5-30 inclusive
                condition_a_mask = (gray_array >= 5) & (gray_array <= 30)
                
                # Compute contiguous arrays
                left, right, up, down = compute_contiguous_arrays(condition_a_mask)
                
                # Identify pixels meeting condition B (any direction >=20)
                condition_b_mask = (left >= 20) | (right >= 20) | (up >= 20) | (down >= 20)
                
                # Initialize gap flag array (all zeros)
                gap_flag = np.zeros((height, width), dtype=np.uint8)
                
                # Set gap_flag=1 only where condition A is True AND 
                # at least one neighbor has condition B True
                for i in range(height):
                    for j in range(width):
                        if not condition_a_mask[i, j]:
                            continue
                            
                        neighbors = []
                        if i > 0: 
                            neighbors.append(condition_b_mask[i-1, j])
                        if i < height-1: 
                            neighbors.append(condition_b_mask[i+1, j])
                        if j > 0: 
                            neighbors.append(condition_b_mask[i, j-1])
                        if j < width-1: 
                            neighbors.append(condition_b_mask[i, j+1])
                            
                        if any(neighbors):
                            gap_flag[i, j] = 1
                
                # Generate analysis CSV
                analysis_path = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
                with open(analysis_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['row', 'column', 'grayscale_value', 'gap_flag'])
                    for i in range(height):
                        for j in range(width):
                            writer.writerow([i, j, gray_array[i, j], gap_flag[i, j]])
                
                # Calculate gap heights per column
                min_row = [height] * width
                max_row = [-1] * width
                for j in range(width):
                    for i in range(height):
                        if gap_flag[i, j] == 1:
                            if i < min_row[j]:
                                min_row[j] = i
                            if i > max_row[j]:
                                max_row[j] = i
                
                gap_heights = []
                for j in range(width):
                    if min_row[j] <= max_row[j]:
                        gap_heights.append((max_row[j] - min_row[j] + 1) * re_val)
                    else:
                        gap_heights.append(0.0)
                
                # Save gap heights CSV
                height_path = os.path.join(output_dir, f"{base_name}_gap_height.csv")
                with open(height_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['column', 'gap_height_um'])
                    for col_idx, gh in enumerate(gap_heights):
                        writer.writerow([col_idx, gh])
                
                # Generate text summary
                max_height = max(gap_heights) if any(gap_heights) else 0.0
                txt_path = os.path.join(output_dir, f"{base_name}_gap_info.txt")
                with open(txt_path, 'w') as f:
                    f.write(f"Physical dimension parameter (μm/pixel): {re_val}\n")
                    f.write(f"Max gap height (μm): {max_height}\n")
                
                # Create highlighted image
                if img.mode != 'RGB':
                    rgb_img = img.convert('RGB')
                else:
                    rgb_img = img.copy()
                
                rgb_array = np.array(rgb_img)
                rgb_array[gap_flag == 1] = [255, 0, 0]  # Red for gap pixels
                highlight_img = Image.fromarray(rgb_array)
                highlight_img.save(os.path.join(output_dir, f"{base_name}_gap_highlighted.png"))

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-re', dest='re_val', type=float, required=True,
                        help='Physical dimension in micrometers per pixel')
                        
    args = parser.parse_args()
    
    # Configure paths
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S2\backup4"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Process all images
    process_images(input_dir, output_dir, args.re_val)
    print("Processed all images!")
