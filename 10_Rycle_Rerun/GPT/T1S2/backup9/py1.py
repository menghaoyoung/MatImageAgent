import os
import csv
import argparse
from PIL import Image
import numpy as np

def check_gap_conditions(gray_img, row, col, thresh_min=5, thresh_max=30):
    """
    Check whether the pixel at (row, col) is a GAP pixel:
    (1) Grayscale value in [5,30]
    (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition.
    Returns: True if GAP, else False
    """
    H, W = gray_img.shape
    val = gray_img[row, col]
    if not (thresh_min <= val <= thresh_max):
        return False

    # Set directions: up, down, left, right
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    for dr, dc in directions:
        contiguous = 0
        for i in range(1, 21):  # 1 to 20
            nr = row + dr * i
            nc = col + dc * i
            if 0 <= nr < H and 0 <= nc < W:
                test_val = gray_img[nr, nc]
                if thresh_min <= test_val <= thresh_max:
                    contiguous += 1
                else:
                    break
            else:
                break
        if contiguous == 20:
            return True
    return False

def save_csv(pixel_data, csv_path):
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['row', 'column', 'grayscale', 'gap_flag'])
        for row in pixel_data:
            writer.writerow(row)

def save_gap_height_csv(gap_heights, csv_path):
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['column', 'GAP_height_μm'])
        for col, height in gap_heights.items():
            writer.writerow([col, f"{height:.4f}"])

def save_txt(result_txt_path, re, gap_heights):
    max_height = max(gap_heights.values()) if gap_heights else 0.0
    with open(result_txt_path, 'w') as f:
        f.write(f"Physical dimension parameter (μm/pixel): {re}\n")
        f.write(f"Max GAP height (μm): {max_height:.4f}\n")

def process_images(input_directory, output_directory, re):
    # Supported formats
    exts = ('.png', '.jpg', '.jpeg')
    img_files = [f for f in os.listdir(input_directory)
                 if f.startswith('Li_') and f.lower().endswith(exts)]

    for img_file in img_files:
        img_path = os.path.join(input_directory, img_file)
        img_name = os.path.splitext(img_file)[0]
        print(f"Processing image: {img_file}")

        # Read and convert to grayscale
        pil_img = Image.open(img_path).convert('L')
        gray_img = np.array(pil_img)
        H, W = gray_img.shape

        pixel_analysis = []
        gap_mask = np.zeros_like(gray_img, dtype=np.uint8)

        # First pass: identify GAP pixels
        for r in range(H):
            for c in range(W):
                is_gap = check_gap_conditions(gray_img, r, c)
                pixel_analysis.append([r, c, int(gray_img[r, c]), int(is_gap)])
                if is_gap:
                    gap_mask[r, c] = 1

        # Save per-pixel analysis
        csv_path = os.path.join(
            output_directory, f"{img_name}_gap_analysis.csv")
        save_csv(pixel_analysis, csv_path)
        print(f"Saved pixel analysis CSV: {csv_path}")

        # Calculate GAP height per column
        gap_heights = {}
        for c in range(W):
            gap_rows = np.where(gap_mask[:, c]==1)[0]
            if gap_rows.size:
                min_row, max_row = gap_rows.min(), gap_rows.max()
                height = (max_row - min_row + 1) * re
                gap_heights[c] = height
            else:
                gap_heights[c] = 0.0  # No GAP pixels in this column

        # Save GAP height CSV
        gap_height_csv_path = os.path.join(
            output_directory, f"{img_name}_gap_height.csv")
        save_gap_height_csv(gap_heights, gap_height_csv_path)
        print(f"Saved GAP height CSV: {gap_height_csv_path}")

        # Save TXT summary
        txt_path = os.path.join(
            output_directory, f"{img_name}_gap_height.txt")
        save_txt(txt_path, re, gap_heights)
        print(f"Saved summary TXT: {txt_path}")

        # Generate image highlighting GAP pixels in red
        rgb_img = pil_img.convert('RGB')
        rgb_img_np = np.array(rgb_img)
        # Set red for GAP pixels
        red_mask = gap_mask.astype(bool)
        rgb_img_np[red_mask] = [255,0,0]
        result_img = Image.fromarray(rgb_img_np)
        result_img_path = os.path.join(
            output_directory, f"{img_name}_gap_highlighted.png")
        result_img.save(result_img_path)
        print(f"Saved highlighted image: {result_img_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GAP pixel analysis and image processing")
    parser.add_argument('-re', type=float, required=True, help="Physical dimension parameter (μm/pixel)")
    parser.add_argument('--input', type=str, default=r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images", help="Input image directory")
    parser.add_argument('--output', type=str, default=r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S2\backup9", help="Output files directory")
    args = parser.parse_args()

    input_directory = args.input
    output_directory = args.output
    re = args.re

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    process_images(input_directory, output_directory, re)
    print("Proceed all the images！")
