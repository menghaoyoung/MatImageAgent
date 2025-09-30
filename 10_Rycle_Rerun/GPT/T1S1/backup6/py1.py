import os
import csv
from PIL import Image
import numpy as np

# Constants
INPUT_DIRECTORY = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
OUTPUT_DIRECTORY = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S1\backup6"
GAP_MIN = 5
GAP_MAX = 30

def ensure_output_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def check_gap_conditions(gray_img, row, col):
    """
    (1) Grayscale value between 5–30 (inclusive)
    (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition.
    """
    rows, cols = gray_img.shape
    if gray_img[row, col] < GAP_MIN or gray_img[row, col] > GAP_MAX:
        return 0

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
    for dr, dc in directions:
        cnt = 0
        r, c = row + dr, col + dc
        # Move up to 20 steps in that direction
        for _ in range(20):
            if 0 <= r < rows and 0 <= c < cols:
                if GAP_MIN <= gray_img[r, c] <= GAP_MAX:
                    cnt += 1
                    r += dr
                    c += dc
                else:
                    break
            else:
                break
        if cnt == 20:
            return 1
    return 0

def save_csv(csv_path, data):
    with open(csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['row', 'col', 'grayscale', 'GAP_flag'])
        for row in data:
            writer.writerow(row)

def process_images(input_directory):
    ensure_output_directory(OUTPUT_DIRECTORY)
    files = [f for f in os.listdir(input_directory) if (f.startswith('Li_') and f.lower().endswith(('.png', '.jpg', '.jpeg')))]
    print(f"Found {len(files)} images to process.")
    for fname in files:
        img_path = os.path.join(input_directory, fname)
        with Image.open(img_path) as img:
            gray_img = img.convert('L')
            gray_np = np.array(gray_img)
            rows, cols = gray_np.shape
            gap_flags = np.zeros_like(gray_np, dtype=np.uint8)
            csv_data = []

            print(f"Processing image: {fname} ({rows}x{cols})")

            for r in range(rows):
                for c in range(cols):
                    gap = check_gap_conditions(gray_np, r, c)
                    gap_flags[r, c] = gap
                    csv_data.append([r, c, int(gray_np[r, c]), gap])

            # Save CSV
            base_name = os.path.splitext(fname)[0]
            csv_fname = f"{base_name}_gap_analysis.csv"
            csv_path = os.path.join(OUTPUT_DIRECTORY, csv_fname)
            save_csv(csv_path, csv_data)
            print(f"Saved CSV: {csv_fname}")

            # Generate output image with GAP points highlighted in red
            rgb_img = img.convert('RGB')
            rgb_np = np.array(rgb_img)
            gap_mask = gap_flags == 1
            if rgb_np.ndim == 3 and rgb_np.shape[2] == 3:
                rgb_np[gap_mask] = [255, 0, 0]
            else:  # Safety for single-channel images
                rgb_np = np.stack([gray_np]*3, axis=-1)
                rgb_np[gap_mask] = [255, 0, 0]
            out_img = Image.fromarray(rgb_np)
            out_img_fname = f"{base_name}_GAP_highlight.png"
            out_img_path = os.path.join(OUTPUT_DIRECTORY, out_img_fname)
            out_img.save(out_img_path)
            print(f"Saved highlighted image: {out_img_fname}")

if __name__ == "__main__":
    process_images(INPUT_DIRECTORY)
    print("Proceed all the images！")
