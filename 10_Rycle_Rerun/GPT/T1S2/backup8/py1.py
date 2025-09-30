import os
import csv
import argparse
from PIL import Image
import numpy as np

def check_gap_conditions(gray_img, row, col):
    """
    Check if the pixel at (row, col) satisfies:
    (1) Grayscale value between 5–30 (inclusive)
    (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition.
    Returns: True if GAP, False otherwise.
    """
    height, width = gray_img.shape
    if gray_img[row, col] < 5 or gray_img[row, col] > 30:
        return False

    directions = [(-1,0), (1,0), (0,-1), (0,1)]  # up, down, left, right
    for dr, dc in directions:
        contiguous = 0
        for i in range(1, 21):
            nr, nc = row + dr*i, col + dc*i
            if 0 <= nr < height and 0 <= nc < width:
                if 5 <= gray_img[nr, nc] <= 30:
                    contiguous += 1
                else:
                    break
            else:
                break
        if contiguous == 20:
            return True
    return False

def save_csv(pixel_data, gap_heights, img_name, output_dir):
    # Save per-pixel analysis CSV
    analysis_csv = os.path.join(output_dir, f"{img_name}_gap_analysis.csv")
    with open(analysis_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['row', 'col', 'gray', 'GAP'])
        writer.writerows(pixel_data)
    print(f"Saved: {analysis_csv}")

    # Save per-column GAP heights CSV
    height_csv = os.path.join(output_dir, f"{img_name}_gap_height.csv")
    with open(height_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['col', 'GAP_height(um)'])
        for col, height in gap_heights.items():
            writer.writerow([col, height])
    print(f"Saved: {height_csv}")

def save_txt(re, gap_heights, img_name, output_dir):
    txt_path = os.path.join(output_dir, f"{img_name}_gap_height.txt")
    max_height = max(gap_heights.values()) if gap_heights else 0
    with open(txt_path, 'w') as f:
        f.write(f"Physical dimension parameter (μm/pixel): {re}\n")
        f.write(f"Max GAP height (μm): {max_height}\n")
    print(f"Saved: {txt_path}")

def save_gap_png(original_img, gap_mask, img_name, output_dir):
    # Overlay red on GAP pixels
    rgb_img = original_img.convert("RGB")
    arr = np.array(rgb_img)
    arr[gap_mask == 1] = [255, 0, 0]  # Set to red where GAP
    out_img = Image.fromarray(arr)
    out_path = os.path.join(output_dir, f"{img_name}_GAP.png")
    out_img.save(out_path)
    print(f"Saved: {out_path}")

def process_images(input_directory, output_directory, re):
    os.makedirs(output_directory, exist_ok=True)
    for fname in os.listdir(input_directory):
        if fname.startswith("Li_") and fname.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(input_directory, fname)
            img_name = os.path.splitext(fname)[0]
            print(f"Processing: {fname}")

            img = Image.open(img_path)
            gray_img = img.convert('L')
            gray_np = np.array(gray_img)
            height, width = gray_np.shape

            pixel_data = []
            gap_mask = np.zeros((height, width), dtype=np.uint8)
            gap_rows_by_col = dict()

            # Pass 1: determine GAP flag for each pixel
            for row in range(height):
                for col in range(width):
                    is_gap = int(check_gap_conditions(gray_np, row, col))
                    pixel_data.append([row, col, int(gray_np[row, col]), is_gap])
                    gap_mask[row, col] = is_gap

            # Pass 2: compute GAP height per column
            gap_heights = {}
            for col in range(width):
                gap_rows = np.where(gap_mask[:, col]==1)[0]
                if len(gap_rows) > 0:
                    min_row = gap_rows.min()
                    max_row = gap_rows.max()
                    gap_height = (max_row - min_row + 1) * re
                    gap_heights[col] = round(gap_height, 4)
                else:
                    gap_heights[col] = 0

            # Save outputs
            save_csv(pixel_data, gap_heights, img_name, output_directory)
            save_txt(re, gap_heights, img_name, output_directory)
            save_gap_png(img, gap_mask, img_name, output_directory)
    print("Proceed all the images！")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process GAP images.')
    parser.add_argument('-re', '--resolution', type=float, required=True, help='Physical dimension parameter (μm/pixel)')
    args = parser.parse_args()
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S2\backup8"
    process_images(input_directory, output_directory, args.resolution)
