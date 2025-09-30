import os
import csv
from PIL import Image
import numpy as np

# Output directory for all results
OUTPUT_DIR = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S2"

def check_gap_conditions(gray_img, row, col):
    """
    Check if a pixel at (row, col) is a GAP pixel:
    1. Grayscale value between 5–30 (inclusive)
    2. At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels
       (in a line, not necessarily all adjacent) meeting the grayscale condition.
    """
    h, w = gray_img.shape
    val = gray_img[row, col]
    if val < 5 or val > 30:
        return 0  # Not in grayscale range

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right

    for dr, dc in directions:
        cnt = 0
        for i in range(1, 21):  # look ahead up to 20 pixels in this direction
            nr, nc = row + dr * i, col + dc * i
            if 0 <= nr < h and 0 <= nc < w:
                nval = gray_img[nr, nc]
                if 5 <= nval <= 30:
                    cnt += 1
                else:
                    break
            else:
                break
        if cnt == 20:
            return 1
    return 0

def save_csv(csv_path, rows):
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['row', 'col', 'gray_value', 'GAP_flag'])
        writer.writerows(rows)

def process_images(input_directory, re=0.0187):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    image_files = [f for f in os.listdir(input_directory)
                   if (f.startswith("Li_") and f.lower().endswith(('.png', '.jpg', '.jpeg')))]
    print(f"Found {len(image_files)} Li_ images.")

    for img_file in image_files:
        img_path = os.path.join(input_directory, img_file)
        img_name_noext = os.path.splitext(img_file)[0]
        print(f"Processing {img_file}...")

        # Load and convert to grayscale
        img = Image.open(img_path).convert('L')
        gray_img = np.array(img)
        h, w = gray_img.shape

        # Prepare data for CSV and for marking GAP pixels
        csv_rows = []
        gap_flag_img = np.zeros((h, w), dtype=np.uint8)
        gap_pixels_per_col = {}

        for col in range(w):
            gap_rows_in_col = []
            for row in range(h):
                gray_value = gray_img[row, col]
                gap_flag = check_gap_conditions(gray_img, row, col)
                csv_rows.append([row, col, int(gray_value), gap_flag])
                if gap_flag:
                    gap_flag_img[row, col] = 1
                    gap_rows_in_col.append(row)
            if gap_rows_in_col:
                gap_pixels_per_col[col] = (min(gap_rows_in_col), max(gap_rows_in_col))
            else:
                gap_pixels_per_col[col] = (None, None)

        # Save CSV
        csv_path = os.path.join(OUTPUT_DIR, f"{img_name_noext}_gap_analysis.csv")
        save_csv(csv_path, csv_rows)
        print(f"Saved pixel analysis to: {csv_path}")

        # Compute GAP heights per column and max height
        gap_heights = []
        for col, (min_row, max_row) in gap_pixels_per_col.items():
            if min_row is not None:
                gap_height = (max_row - min_row + 1) * re  # in μm
                gap_heights.append(gap_height)
            else:
                gap_heights.append(0)
        max_height = max(gap_heights) if gap_heights else 0

        # Save TXT
        txt_path = os.path.join(OUTPUT_DIR, f"{img_name_noext}_gap_height.txt")
        with open(txt_path, 'w') as f:
            f.write(f"Physical dimension parameter (μm/pixel): {re:.4f}\n")
            f.write(f"Max GAP height per column (μm): {max_height:.4f}\n")
        print(f"Saved height statistics to: {txt_path}")

        # Generate highlighted PNG image
        rgb_img = img.convert('RGB')
        rgb_arr = np.array(rgb_img)
        # Set GAP pixels to red
        red_mask = gap_flag_img == 1
        rgb_arr[red_mask] = [255, 0, 0]
        out_img = Image.fromarray(rgb_arr)
        png_path = os.path.join(OUTPUT_DIR, f"{img_name_noext}_GAP_RED.png")
        out_img.save(png_path)
        print(f"Saved highlighted image to: {png_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='GAP pixel analysis for Li_ images.')
    parser.add_argument('-re', '--resolution', type=float, default=0.0187,
                        help='Physical size per pixel in μm (default: 0.0187)')
    args = parser.parse_args()
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory, re=args.resolution)
    print("Proceed all the images！")
