import os
import csv
import argparse
from PIL import Image
import numpy as np
from collections import defaultdict, deque

def check_gap_conditions(gray):
    """
    Identify GAP pixels based on grayscale values and contiguous pixel conditions.
    Returns a boolean mask where True indicates GAP pixels.
    """
    # Create mask for grayscale values between 5-30 (inclusive)
    mask = (gray >= 5) & (gray <= 30)
    H, W = gray.shape
    gap_flag = np.zeros_like(mask, dtype=bool)
    
    # Skip if no pixels meet initial condition
    if not np.any(mask):
        return gap_flag
    
    # Connected component analysis with BFS
    visited = np.zeros_like(mask, dtype=bool)
    labels = np.zeros_like(mask, dtype=int)
    component_size = defaultdict(int)
    current_label = 1
    directions = [(1,0), (-1,0), (0,1), (0,-1)]  # Down, Up, Right, Left
    
    for i in range(H):
        for j in range(W):
            if mask[i,j] and not visited[i,j]:
                queue = deque()
                queue.append((i,j))
                visited[i,j] = True
                component_pixels = []
                
                while queue:
                    x, y = queue.popleft()
                    component_pixels.append((x,y))
                    for dx, dy in directions:
                        nx, ny = x+dx, y+dy
                        if 0 <= nx < H and 0 <= ny < W:
                            if mask[nx,ny] and not visited[nx,ny]:
                                visited[nx,ny] = True
                                queue.append((nx,ny))
                
                size = len(component_pixels)
                for (x,y) in component_pixels:
                    labels[x,y] = current_label
                component_size[current_label] = size
                current_label += 1
    
    # Apply gap condition (component size >= 20)
    for i in range(H):
        for j in range(W):
            if mask[i,j]:
                label = labels[i,j]
                if label > 0 and component_size[label] >= 20:
                    gap_flag[i,j] = True
                    
    return gap_flag

def process_images(input_directory, output_directory, re):
    """Process all Li_ prefix images in directory with gap detection and file generation"""
    for filename in os.listdir(input_directory):
        if filename.startswith("Li_") and \
           (filename.lower().endswith('.png') or filename.lower().endswith('.jpg')):
            try:
                # Load and convert image to grayscale
                img_path = os.path.join(input_directory, filename)
                img = Image.open(img_path)
                gray_img = img.convert('L')
                gray_array = np.array(gray_img)
                H, W = gray_array.shape
                base_name = os.path.splitext(filename)[0]
                
                # Detect GAP pixels
                gap_flag = check_gap_conditions(gray_array)
                
                # Save per-pixel CSV analysis
                csv_path = os.path.join(output_directory, f"{base_name}_gap_analysis.csv")
                with open(csv_path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['row', 'column', 'grayscale_value', 'GAP_flag'])
                    for i in range(H):
                        for j in range(W):
                            writer.writerow([i, j, gray_array[i,j], int(gap_flag[i,j])])
                
                # Calculate GAP height per column
                gap_heights = []
                for j in range(W):
                    gap_rows = np.where(gap_flag[:, j])[0]
                    if len(gap_rows) > 0:
                        min_row, max_row = min(gap_rows), max(gap_rows)
                        height_px = max_row - min_row + 1
                        height_um = height_px * re
                    else:
                        height_um = 0.0
                    gap_heights.append(height_um)
                
                # Save column heights CSV
                height_csv = os.path.join(output_directory, f"{base_name}_gap_height.csv")
                with open(height_csv, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['column', 'GAP_height_um'])
                    for j, h in enumerate(gap_heights):
                        writer.writerow([j, h])
                
                # Generate TXT report
                max_height = max(gap_heights) if gap_heights else 0.0
                txt_path = os.path.join(output_directory, f"{base_name}_gap_report.txt")
                with open(txt_path, 'w') as f:
                    f.write(f"Physical dimension parameter (μm/pixel): {re}\n")
                    f.write(f"Max height (μm): {max_height}\n")
                
                # Create highlighted image
                if img.mode != 'RGB':
                    rgb_img = img.convert('RGB')
                else:
                    rgb_img = img.copy()
                rgb_array = np.array(rgb_img)
                rgb_array[gap_flag] = [255, 0, 0]  # Red highlight
                Image.fromarray(rgb_array).save(
                    os.path.join(output_directory, f"{base_name}_gap_highlight.png")
                
                print(f"Processed: {filename}")
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-re', type=float, required=True, 
                        help='Physical dimension parameter (μm per pixel)')
    args = parser.parse_args()
    
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S2\backup6"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    process_images(input_dir, output_dir, args.re)
    print("Processing complete!")
