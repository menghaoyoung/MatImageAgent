import os
import csv
import argparse
from PIL import Image
import numpy as np

# Set output directory
OUTPUT_DIR = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S2"

def check_gap_conditions(gray_img, row, col):
    """
    Check if the pixel at (row, col) meets GAP conditions:
    1. Grayscale value between 5 and 30 (inclusive).
    2. At least one adjacent (up/down/left/right) pixel has 20 contiguous pixels (in a line) meeting grayscale condition.
    """
    value = gray_img[row, col]
    if value < 5 or value > 30:
        return False

    rows, cols = gray_img.shape

    # Helper function to check contiguous pixels in one direction
    def check_direction(dr, dc):
        for adj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # up, down, left, right
            adj_row, adj_col = row + adj[0], col + adj[1]
            if 0 <= adj_row < rows and 0 <= adj_col < cols:
                # For each direction, check up to 20 in that direction
                count = 0
                r, c = adj_row, adj_col
                for _ in range(20):
                    if 0 <= r < rows and 0 <= c < cols and 5 <= gray_img[r, c] <= 30:
                        count += 1
                        r += dr
                        c += dc
                    else:
                        break
                if count == 20:
                    return True
        return False

    # Check up (dr=-1, dc=0), down (1,0), left (0,-1), right (0,1)
    # For each direction, only the direct neighbors are considered as starting points
    # but contiguous check is always in the same direction
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in directions:
        adj_row, adj_col = row + dr, col + dc
        if 0 <= adj_row < rows and 0 <= adj_col < cols:
            # Now move in this direction for up to 20 pixels
            count = 0
            r, c = adj_row, adj_col
            for _ in range(20):
                if 0 <= r < rows and 0 <= c < cols and 5 <= gray_img[r, c] <= 30:
                    count += 1
                    r += dr
                    c += dc
                else:
                    break
            if count == 20:
                return True
    return False

def save_csv(csv_path, pixel_data):
    with open(csv_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['row', 'col', 'grayscale', 'GAP_flag'])
        for row, col, gray, gap in pixel_data:
            writer.writerow([row, col, gray, gap])

def save_txt(txt_path, re, gap_heights):
    max_height = max(gap_heights) if gap_heights else 0
    with open(txt_path, 'w') as f:
        f.write(f"Physical dimension parameter (μm/pixel): {re}\n")
        f.write(f"Max GAP height (μm): {max_height:.4f}\n")

def highlight_gap_pixels(orig_img, gap_flags):
    """Return a new RGB image with GAP pixels highlighted in red."""
    rgb_img = orig_img.convert('RGB')
    arr = np.array(rgb_img)
    for row, col in gap_flags:
        arr[row, col] = [255, 0, 0]  # Red
    new_img = Image.fromarray(arr)
    return new_img

def process_images(input_directory, re):
    # Find all images with prefix "Li_" and suffix .png or .jpg/.jpeg
    files = [f for f in os.listdir(input_directory)
             if f.startswith('Li_') and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    for img_name in files:
        img_path = os.path.join(input_directory, img_name)
        print(f"Processing {img_name}...")
        img = Image.open(img_path)
        gray_img = img.convert('L')
        gray_np = np.array(gray_img)
        rows, cols = gray_np.shape

        pixel_data = []
        gap_flags = []  # List of (row, col) for GAP pixels

        # First pass: determine GAP flag for each pixel
        gap_map = np.zeros_like(gray_np, dtype=np.uint8)
        for i in range(rows):
            for j in range(cols):
                gray = gray_np[i, j]
                is_gap = check_gap_conditions(gray_np, i, j)
                gap_flag = 1 if is_gap else 0
                pixel_data.append((i, j, int(gray), gap_flag))
                if gap_flag:
                    gap_flags.append((i, j))
                    gap_map[i, j] = 1

        # Save CSV
        base_name = os.path.splitext(img_name)[0]
        csv_path = os.path.join(OUTPUT_DIR, f"{base_name}_gap_analysis.csv")
        save_csv(csv_path, pixel_data)

        # Calculate GAP height per column
        gap_heights = []
        for col in range(cols):
            gap_rows = np.where(gap_map[:, col] == 1)[0]
            if len(gap_rows) > 0:
                min_row, max_row = np.min(gap_rows), np.max(gap_rows)
                gap_height = (max_row - min_row + 1) * re
                gap_heights.append(gap_height)
        # Save TXT
        txt_path = os.path.join(OUTPUT_DIR, f"{base_name}_gap_stat.txt")
        save_txt(txt_path, re, gap_heights)

        # Save highlighted image
        highlighted_img = highlight_gap_pixels(img, gap_flags)
        out_img_path = os.path.join(OUTPUT_DIR, f"{base_name}_gap_highlight.png")
        highlighted_img.save(out_img_path)
        print(f"Saved CSV: {csv_path}")
        print(f"Saved TXT: {txt_path}")
        print(f"Saved highlighted image: {out_img_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='GAP Pixel Analyzer')
    parser.add_argument('-re', type=float, required=True, help='Physical dimension (μm/pixel)')
    args = parser.parse_args()
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory, args.re)
    print("Proceed all the images！")
