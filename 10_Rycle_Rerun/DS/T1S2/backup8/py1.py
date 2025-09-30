import os
import csv
import argparse
from PIL import Image
import numpy as np
from collections import deque

def check_gap_conditions(gray_img):
    """Identify GAP pixels using connected component analysis."""
    # Create binary mask for pixels in grayscale range [5,30]
    mask = (gray_img >= 5) & (gray_img <= 30)
    height, width = gray_img.shape
    gap_flag = np.zeros_like(gray_img, dtype=np.uint8)
    visited = np.zeros_like(mask, dtype=bool)
    directions = [(1,0), (-1,0), (0,1), (0,-1)]  # Down, Up, Right, Left
    
    for i in range(height):
        for j in range(width):
            if mask[i,j] and not visited[i,j]:
                component = []
                queue = deque([(i,j)])
                visited[i,j] = True
                
                # BFS to find connected components
                while queue:
                    x, y = queue.popleft()
                    component.append((x,y))
                    for dx, dy in directions:
                        nx, ny = x+dx, y+dy
                        if 0 <= nx < height and 0 <= ny < width:
                            if mask[nx,ny] and not visited[nx,ny]:
                                visited[nx,ny] = True
                                queue.append((nx,ny))
                
                # Mark component if large enough
                if len(component) >= 20:
                    for (x,y) in component:
                        gap_flag[x,y] = 1
    return gap_flag

def process_image(image_path, re, output_dir):
    """Process single image and generate output files."""
    with Image.open(image_path) as img:
        # Convert to grayscale and get numpy array
        gray_img = np.array(img.convert('L'))
        height, width = gray_img.shape
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        
        # Get GAP flags
        gap_flag = check_gap_conditions(gray_img)
        
        # Save pixel-level CSV
        csv_path = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Row', 'Column', 'Grayscale', 'GAP_Flag'])
            for i in range(height):
                for j in range(width):
                    writer.writerow([i, j, gray_img[i,j], gap_flag[i,j]])
        
        # Calculate GAP heights per column
        gap_heights = []
        for j in range(width):
            rows = np.where(gap_flag[:, j] == 1)[0]
            if rows.size > 0:
                min_row, max_row = np.min(rows), np.max(rows)
                gap_heights.append((max_row - min_row + 1) * re)
            else:
                gap_heights.append(0.0)
        
        # Save column heights CSV
        height_csv = os.path.join(output_dir, f"{base_name}_gap_height.csv")
        with open(height_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Column', 'GAP_Height(um)'])
            for j, h in enumerate(gap_heights):
                writer.writerow([j, h])
                
        # Generate highlighted image
        rgb_img = img.convert('RGB')
        highlight = np.array(rgb_img)
        highlight[gap_flag == 1] = [255, 0, 0]  # Red highlights
        Image.fromarray(highlight).save(os.path.join(output_dir, f"{base_name}_gap_highlight.png"))
        
        # Create text file with summary
        max_height = max(gap_heights) if gap_heights else 0
        txt_path = os.path.join(output_dir, f"{base_name}_gap_info.txt")
        with open(txt_path, 'w') as f:
            f.write(f"Physical dimension parameter: {re} um/pixel\n")
            f.write(f"Max height: {max_height} um\n")

def process_images(input_dir, re, output_dir):
    """Process all matching images in input directory."""
    os.makedirs(output_dir, exist_ok=True)
    for f in os.listdir(input_dir):
        if f.startswith("Li_") and f.lower().endswith(('.png', '.jpg', '.jpeg')):
            process_image(os.path.join(input_dir, f), re, output_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-re', type=float, required=True,
                        help='Physical dimension in um/pixel (e.g., 0.0187)')
    args = parser.parse_args()

    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S2\backup8"
    
    process_images(input_dir, args.re, output_dir)
    print("Processed all images!")
