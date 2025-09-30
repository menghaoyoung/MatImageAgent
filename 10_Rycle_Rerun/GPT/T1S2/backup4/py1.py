import os
import csv
import argparse
from PIL import Image
import numpy as np

# Define output directory
OUTPUT_DIR = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S2\backup4"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def check_gap_conditions(gray_img, row, col):
    """
    GAP pixel conditions:
    (1) Grayscale value between 5–30 (inclusive)
    (2) At least one adjacent direction (up/down/left/right) has 20 contiguous pixels
        (in that direction) also in [5,30]
    """
    h, w = gray_img.shape
    pixel_val = gray_img[row, col]
    if not (5 <= pixel_val <= 30):
        return 0  # Not even meet grayscale

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
    for dr, dc in directions:
        count = 0
        for i in range(1, 21):  # 20 contiguous pixels
            nr, nc = row + dr * i, col + dc * i
            if 0 <= nr < h and 0 <= nc < w:
                if 5 <= gray_img[nr, nc] <= 30:
                    count += 1
                else:
                    break
            else:
                break
        if count == 20:
            return 1  # Found a direction
    return 0

def save_csv(pixel_data, path, header):
    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(pixel_data)

def process_images(input_directory, re):
    for fname in os.listdir(input_directory):
        if fname.startswith("Li_") and fname.lower().endswith(('.png', '.jpg', '.jpeg')):
            full_path = os.path.join(input_directory, fname)
            print(f"Processing: {fname}")
            img = Image.open(full_path).convert('L')
            gray = np.array(img)
            h, w = gray.shape

            # Prepare data for CSV and image output
            pixel_csv_data = []
            gap_mask = np.zeros_like(gray, dtype=np.uint8)
            gap_pixel_rows_per_col = [[] for _ in range(w)]  # For Gap height calculation

            for row in range(h):
                for col in range(w):
                    gap_flag = check_gap_conditions(gray, row, col)
                    pixel_csv_data.append([row, col, int(gray[row, col]), gap_flag])
                    if gap_flag:
                        gap_mask[row, col] = 1
                        gap_pixel_rows_per_col[col].append(row)

            # Save pixel analysis CSV
            outname_base = os.path.splitext(fname)[0]
            csv_pixel_path = os.path.join(OUTPUT_DIR, f"{outname_base}_gap_analysis.csv")
            save_csv(pixel_csv_data, csv_pixel_path, ['row', 'col', 'grayscale', 'GAP_flag'])
            print(f"Saved pixel analysis CSV: {csv_pixel_path}")

            # Calculate GAP heights per column
            gap_heights = []
            for col in range(w):
                if gap_pixel_rows_per_col[col]:
                    min_row = min(gap_pixel_rows_per_col[col])
                    max_row = max(gap_pixel_rows_per_col[col])
                    height = (max_row - min_row + 1) * re  # in micron
                    gap_heights.append([col, height])  # column index, height
                else:
                    gap_heights.append([col, 0.0])

            # Save GAP_height CSV
            csv_height_path = os.path.join(OUTPUT_DIR, f"{outname_base}_gap_height.csv")
            save_csv(gap_heights, csv_height_path, ['column', 'GAP_height(um)'])
            print(f"Saved gap heights CSV: {csv_height_path}")

            # Save TXT file: (1) Physical dimension (um/pixel) (2) Height statistics (max height um)
            max_height = max(h[1] for h in gap_heights) if gap_heights else 0.0
            txt_path = os.path.join(OUTPUT_DIR, f"{outname_base}_gap_height_stats.txt")
            with open(txt_path, 'w') as ftxt:
                ftxt.write(f"Physical dimension (μm/pixel): {re}\n")
                ftxt.write(f"Max GAP height (μm): {max_height}\n")
            print(f"Saved stats TXT: {txt_path}")

            # Generate new PNG image highlighting GAP points in red
            color_img = img.convert('RGB')
            color_arr = np.array(color_img)
            # Set GAP points to red
            color_arr[gap_mask == 1] = [255, 0, 0]
            outimg = Image.fromarray(color_arr)
            img_out_path = os.path.join(OUTPUT_DIR, f"{outname_base}_gap_highlight.png")
            outimg.save(img_out_path)
            print(f"Saved highlighted image: {img_out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GAP pixel analysis")
    parser.add_argument('-re', type=float, required=True, help='physical dimension (um/pixel)')
    args = parser.parse_args()
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory, args.re)
    print("Proceed all the images！")
