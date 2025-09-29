import os
import sys
import csv
import numpy as np
from PIL import Image

def precompute_streaks(gray_array):
    h, w = gray_array.shape
    in_range = (5 <= gray_array) & (gray_array <= 30)
    streaks = np.zeros((h, w, 4), dtype=int)  # [left, right, up, down]
    
    # Left streak (scan left to right)
    for i in range(h):
        for j in range(w):
            if in_range[i, j]:
                streaks[i, j, 0] = streaks[i, j-1, 0] + 1 if j > 0 else 1
    
    # Right streak (scan right to left)
    for i in range(h):
        for j in range(w-1, -1, -1):
            if in_range[i, j]:
                streaks[i, j, 1] = streaks[i, j+1, 1] + 1 if j < w-1 else 1
    
    # Up streak (scan top to bottom)
    for j in range(w):
        for i in range(h):
            if in_range[i, j]:
                streaks[i, j, 2] = streaks[i-1, j, 2] + 1 if i > 0 else 1
    
    # Down streak (scan bottom to top)
    for j in range(w):
        for i in range(h-1, -1, -1):
            if in_range[i, j]:
                streaks[i, j, 3] = streaks[i+1, j, 3] + 1 if i < h-1 else 1
    
    max_streak = np.max(streaks, axis=2)
    return max_streak

def process_images(input_dir):
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1\backup8"
    os.makedirs(output_dir, exist_ok=True)
    
    for filename in os.listdir(input_dir):
        if filename.startswith("Li_") and filename.lower().endswith(('.png', '.jpg')):
            img_path = os.path.join(input_dir, filename)
            try:
                img = Image.open(img_path)
                gray_img = img.convert('L')
                gray_array = np.array(gray_img)
                h, w = gray_array.shape
                
                max_streak = precompute_streaks(gray_array)
                gap_flags = np.zeros((h, w), dtype=int)
                
                # Check GAP conditions
                for i in range(h):
                    for j in range(w):
                        if 5 <= gray_array[i, j] <= 30:
                            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                                ni, nj = i + dx, j + dy
                                if 0 <= ni < h and 0 <= nj < w:
                                    if max_streak[ni, nj] >= 20:
                                        gap_flags[i, j] = 1
                                        break
                
                # Generate CSV
                base_name = os.path.splitext(filename)[0]
                csv_path = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
                with open(csv_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['row', 'column', 'grayscale', 'gap_flag'])
                    for i in range(h):
                        for j in range(w):
                            writer.writerow([i, j, gray_array[i, j], gap_flags[i, j]])
                
                # Generate highlighted image
                rgb_img = Image.new('RGB', (w, h))
                for i in range(h):
                    for j in range(w):
                        if gap_flags[i, j] == 1:
                            rgb_img.putpixel((j, i), (255, 0, 0))
                        else:
                            g = gray_array[i, j]
                            rgb_img.putpixel((j, i), (g, g, g))
                img_path_out = os.path.join(output_dir, f"{base_name}_gap_highlight.png")
                rgb_img.save(img_path_out)
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python py1.py <input_directory>")
        sys.exit(1)
    input_directory = sys.argv[1]
    process_images(input_directory)
    print("Processed all images!")
