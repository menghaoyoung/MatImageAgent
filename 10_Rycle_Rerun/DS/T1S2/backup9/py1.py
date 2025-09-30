import os
import csv
import argparse
import numpy as np
from PIL import Image

def process_images(input_directory, output_dir, re):
    for filename in os.listdir(input_directory):
        if filename.startswith("Li_") and filename.lower().endswith(('.png', '.jpg')):
            img_path = os.path.join(input_directory, filename)
            try:
                # Open image and convert to grayscale array
                img = Image.open(img_path)
                gray_img = img.convert('L')
                gray_arr = np.array(gray_img)
                rows, cols = gray_arr.shape
                
                # Create mask for pixels in grayscale range [5, 30]
                mask = (gray_arr >= 5) & (gray_arr <= 30)
                
                # Precompute run-lengths in four directions
                left_run = np.zeros_like(gray_arr, dtype=int)
                right_run = np.zeros_like(gray_arr, dtype=int)
                top_run = np.zeros_like(gray_arr, dtype=int)
                bottom_run = np.zeros_like(gray_arr, dtype=int)
                
                # Horizontal runs (left to right)
                for i in range(rows):
                    for j in range(cols):
                        if mask[i, j]:
                            if j == 0:
                                left_run[i, j] = 1
                            else:
                                left_run[i, j] = left_run[i, j-1] + 1
                
                # Horizontal runs (right to left)
                for i in range(rows):
                    for j in range(cols-1, -1, -1):
                        if mask[i, j]:
                            if j == cols-1:
                                right_run[i, j] = 1
                            else:
                                right_run[i, j] = right_run[i, j+1] + 1
                
                # Vertical runs (top to bottom)
                for j in range(cols):
                    for i in range(rows):
                        if mask[i, j]:
                            if i == 0:
                                top_run[i, j] = 1
                            else:
                                top_run[i, j] = top_run[i-1, j] + 1
                
                # Vertical runs (bottom to top)
                for j in range(cols):
                    for i in range(rows-1, -1, -1):
                        if mask[i, j]:
                            if i == rows-1:
                                bottom_run[i, j] = 1
                            else:
                                bottom_run[i, j] = bottom_run[i+1, j] + 1
                
                # Calculate maximum contiguous run length for each pixel
                horiz_run = left_run + right_run - 1
                vert_run = top_run + bottom_run - 1
                max_run = np.maximum(horiz_run, vert_run)
                
                # Identify GAP pixels: condition (a) and (b)
                gap_mask = np.zeros_like(mask, dtype=bool)
                for i in range(rows):
                    for j in range(cols):
                        if mask[i, j]:
                            # Check adjacent pixels for runs ≥20
                            neighbors = []
                            if i > 0 and max_run[i-1, j] >= 20:
                                neighbors.append(True)
                            if i < rows-1 and max_run[i+1, j] >= 20:
                                neighbors.append(True)
                            if j > 0 and max_run[i, j-1] >= 20:
                                neighbors.append(True)
                            if j < cols-1 and max_run[i, j+1] >= 20:
                                neighbors.append(True)
                            if any(neighbors):
                                gap_mask[i, j] = True
                
                # Prepare pixel data and track column min/max
                pixel_data = []
                min_row_per_col = [None] * cols
                max_row_per_col = [None] * cols
                
                # Create highlighted image
                rgb_img = img.convert('RGB')
                rgb_pixels = rgb_img.load()
                
                for i in range(rows):
                    for j in range(cols):
                        gap_flag = 1 if gap_mask[i, j] else 0
                        pixel_data.append([i, j, int(gray_arr[i, j]), gap_flag])
                        
                        # Update min/max rows for columns with GAP pixels
                        if gap_flag == 1:
                            rgb_pixels[j, i] = (255, 0, 0)  # Mark GAP red
                            if min_row_per_col[j] is None or i < min_row_per_col[j]:
                                min_row_per_col[j] = i
                            if max_row_per_col[j] is None or i > max_row_per_col[j]:
                                max_row_per_col[j] = i
                
                # Generate GAP heights per column
                gap_height_data = []
                max_height = 0.0
                for j in range(cols):
                    if min_row_per_col[j] is not None and max_row_per_col[j] is not None:
                        height_um = (max_row_per_col[j] - min_row_per_col[j] + 1) * re
                    else:
                        height_um = 0.0
                    gap_height_data.append([j, height_um])
                    max_height = max(max_height, height_um)
                
                # Save output files
                base_name = os.path.splitext(filename)[0]
                
                # CSV: Per-pixel data
                pixel_csv = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
                with open(pixel_csv, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['row', 'column', 'grayscale', 'gap_flag'])
                    writer.writerows(pixel_data)
                
                # CSV: GAP heights per column
                height_csv = os.path.join(output_dir, f"{base_name}_gap_height.csv")
                with open(height_csv, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['column', 'gap_height_um'])
                    writer.writerows(gap_height_data)
                
                # TXT: Statistics
                txt_path = os.path.join(output_dir, f"{base_name}_stats.txt")
                with open(txt_path, 'w') as f:
                    f.write(f"Physical dimension parameter (μm/pixel): {re}\n")
                    f.write(f"Max height (μm): {max_height}\n")
                
                # Highlighted PNG
                img_out_path = os.path.join(output_dir, f"{base_name}_gap_highlighted.png")
                rgb_img.save(img_out_path)
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    # Configure paths
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S2\backup9"
    os.makedirs(output_dir, exist_ok=True)
    
    # Parse command-line argument
    parser = argparse.ArgumentParser()
    parser.add_argument('-re', type=float, required=True, help='Physical dimension (μm/pixel)')
    args = parser.parse_args()
    
    # Process all images
    process_images(input_dir, output_dir, args.re)
    print("Processed all images!")
