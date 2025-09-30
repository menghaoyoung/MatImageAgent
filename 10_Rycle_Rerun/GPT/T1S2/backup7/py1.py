import os
import csv
import argparse
from PIL import Image
import numpy as np

# Output directory (modify as needed)
OUTPUT_DIR = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S2\backup7"

def check_gap_conditions(gray_img, row, col):
    """
    Checks if the pixel at (row, col) satisfies the GAP condition:
    (1) Grayscale value in [5,30]
    (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition
    """
    h, w = gray_img.shape
    val = gray_img[row, col]
    if val < 5 or val > 30:
        return False

    # Helper to check contiguous pixels condition in direction
    def check_dir(r0, c0, dr, dc):
        count = 0
        for k in range(1, 21):
            r, c = r0 + dr*k, c0 + dc*k
            if 0 <= r < h and 0 <= c < w:
                v = gray_img[r, c]
                if 5 <= v <= 30:
                    count += 1
                else:
                    break
            else:
                break
        return count == 20

    # Up
    if row-1 >= 0 and check_dir(row, col, -1, 0):
        return True
    # Down
    if row+1 < h and check_dir(row, col, 1, 0):
        return True
    # Left
    if col-1 >= 0 and check_dir(row, col, 0, -1):
        return True
    # Right
    if col+1 < w and check_dir(row, col, 0, 1):
        return True

    return False

def save_csv(pixel_data, csv_path):
    """
    Save pixel data to CSV
    """
    with open(csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['row', 'col', 'gray_value', 'GAP_flag'])
        writer.writerows(pixel_data)

def save_gap_heights(gap_indices, re, csv_path):
    """
    gap_indices: list of (row, col) where GAP_flag==1
    re: physical dimension parameter (μm/pixel)
    """
    from collections import defaultdict
    col_dict = defaultdict(list)
    for row, col in gap_indices:
        col_dict[col].append(row)
    with open(csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['column', 'GAP_height_μm'])
        for col in sorted(col_dict):
            rows = col_dict[col]
            min_row = min(rows)
            max_row = max(rows)
            gap_height = (max_row - min_row + 1) * re
            writer.writerow([col, gap_height])

def save_txt(re, gap_heights, txt_path):
    """
    Write physical dimension and max GAP height statistics to TXT
    """
    max_height = max(gap_heights) if gap_heights else 0
    with open(txt_path, 'w') as f:
        f.write(f"Physical dimension parameter (μm/pixel): {re}\n")
        f.write(f"Max GAP height (μm): {max_height}\n")

def highlight_gap_pixels(gray_img, gap_flag_arr):
    """
    Generate RGB image. GAP_flag==1 pixels are red, else grayscale
    """
    h, w = gray_img.shape
    rgb_img = np.stack([gray_img]*3, axis=2).astype(np.uint8)
    # Set GAP pixels to red
    red_mask = gap_flag_arr == 1
    rgb_img[red_mask, 0] = 255  # R
    rgb_img[red_mask, 1] = 0    # G
    rgb_img[red_mask, 2] = 0    # B
    return rgb_img

def process_images(input_directory, re):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    image_files = [f for f in os.listdir(input_directory) if f.startswith("Li_") and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    for img_name in image_files:
        img_path = os.path.join(input_directory, img_name)
        # Open and convert to grayscale
        with Image.open(img_path) as im:
            gray = im.convert('L')
            gray_np = np.array(gray)
        h, w = gray_np.shape

        # Per-pixel GAP analysis
        pixel_data = []
        gap_flag = np.zeros((h, w), dtype=np.uint8)
        gap_indices = []
        for i in range(h):
            for j in range(w):
                flag = 1 if check_gap_conditions(gray_np, i, j) else 0
                pixel_data.append([i, j, int(gray_np[i, j]), flag])
                gap_flag[i, j] = flag
                if flag == 1:
                    gap_indices.append((i, j))

        # Save all pixel analysis CSV
        base_name = os.path.splitext(img_name)[0]
        csv_path = os.path.join(OUTPUT_DIR, f"{base_name}_gap_analysis.csv")
        save_csv(pixel_data, csv_path)

        # Compute GAP height per column and save
        gap_height_csv_path = os.path.join(OUTPUT_DIR, f"{base_name}_gap_height.csv")
        # Compute heights
        from collections import defaultdict
        col_dict = defaultdict(list)
        for row, col in gap_indices:
            col_dict[col].append(row)
        gap_heights = []
        with open(gap_height_csv_path, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['column', 'GAP_height_μm'])
            for col in sorted(col_dict):
                rows = col_dict[col]
                min_row = min(rows)
                max_row = max(rows)
                gap_height = (max_row - min_row + 1) * re
                writer.writerow([col, gap_height])
                gap_heights.append(gap_height)

        # Save TXT file
        txt_path = os.path.join(OUTPUT_DIR, f"{base_name}_gap_result.txt")
        save_txt(re, gap_heights, txt_path)

        # Generate and save highlighted PNG
        out_img = highlight_gap_pixels(gray_np, gap_flag)
        out_img_pil = Image.fromarray(out_img)
        png_path = os.path.join(OUTPUT_DIR, f"{base_name}_GAP_highlighted.png")
        out_img_pil.save(png_path)

        print(f"Processed: {img_name}")
        print(f"  - Pixel analysis CSV: {csv_path}")
        print(f"  - GAP height CSV: {gap_height_csv_path}")
        print(f"  - TXT: {txt_path}")
        print(f"  - Highlighted PNG: {png_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-re", type=float, required=True, help="Physical dimension parameter (μm/pixel)")
    args = parser.parse_args()
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory, args.re)
    print("Proceed all the images！")
