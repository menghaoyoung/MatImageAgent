import os
import csv
import sys
from PIL import Image
import numpy as np
from collections import deque

def get_gap_flag_map(gray_array):
    """
    Identify GAP pixels based on grayscale conditions:
    (1) Pixel value between 5-30 inclusive
    (2) Component containing adjacent pixel has >=20 contiguous pixels
    """
    height, width = gray_array.shape
    mask = (gray_array >= 5) & (gray_array <= 30)
    labels = np.zeros((height, width), dtype=np.int32)
    comp_sizes = {}
    directions = [(1,0), (-1,0), (0,1), (0,-1)]
    current_label = 1
    
    for i in range(height):
        for j in range(width):
            if mask[i, j] and labels[i, j] == 0:
                component_pixels = []
                queue = deque([(i, j)])
                labels[i, j] = current_label
                while queue:
                    x, y = queue.popleft()
                    component_pixels.append((x, y))
                    for dx, dy in directions:
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < height and 0 <= ny < width and 
                            mask[nx, ny] and labels[nx, ny] == 0):
                            labels[nx, ny] = current_label
                            queue.append((nx, ny))
                comp_size = len(component_pixels)
                comp_sizes[current_label] = comp_size
                current_label += 1
    
    gap_flag = np.zeros_like(gray_array, dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            if mask[i, j]:
                comp_size = comp_sizes.get(labels[i, j], 0)
                if comp_size >= 20:
                    gap_flag[i, j] = 1
    return gap_flag

def save_gap_csv(gray_array, gap_flag, csv_path):
    """Save pixel analysis data to CSV file"""
    height, width = gray_array.shape
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['row', 'column', 'grayscale_value', 'gap_flag'])
        for i in range(height):
            for j in range(width):
                writer.writerow([i, j, int(gray_array[i, j]), int(gap_flag[i, j])])

def create_highlighted_image(original_img, gap_flag, output_path):
    """Create output image with GAP pixels highlighted in red"""
    if original_img.mode != 'RGB':
        img_rgb = original_img.convert('RGB')
    else:
        img_rgb = original_img.copy()
    
    pixels = img_rgb.load()
    gap_points = np.argwhere(gap_flag == 1)
    for y, x in gap_points:
        pixels[x, y] = (255, 0, 0)  # Set pixel to red
    img_rgb.save(output_path, 'PNG')

def process_images(input_directory):
    """Process all 'Li_' prefix images in directory"""
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1\backup9"
    os.makedirs(output_dir, exist_ok=True)
    
    valid_exts = ('.png', '.jpg', '.jpeg')
    processed_files = []
    for filename in os.listdir(input_directory):
        if filename.startswith("Li_") and filename.lower().endswith(valid_exts):
            img_path = os.path.join(input_directory, filename)
            try:
                img = Image.open(img_path)
                gray_img = img.convert('L')
                gray_array = np.array(gray_img)
                
                gap_flag = get_gap_flag_map(gray_array)
                
                base_name = os.path.splitext(filename)[0]
                csv_path = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
                save_gap_csv(gray_array, gap_flag, csv_path)
                
                img_out_path = os.path.join(output_dir, f"{base_name}_gap_highlighted.png")
                create_highlighted_image(img, gap_flag, img_out_path)
                
                processed_files.append(filename)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
    
    return processed_files

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python py1.py <input_directory>")
        sys.exit(1)
    
    input_directory = sys.argv[1]
    processed = process_images(input_directory)
    print(f"Processed {len(processed)} images: {', '.join(processed)}")
