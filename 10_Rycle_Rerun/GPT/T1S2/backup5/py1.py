import os
import csv
import argparse
from PIL import Image
import numpy as np

# Output directory for result files
OUTPUT_DIR = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S2\backup5"

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def get_image_files(input_directory):
    files = []
    for fname in os.listdir(input_directory):
        if fname.startswith("Li_") and fname.lower().endswith(('.png', '.jpg', '.jpeg')):
            files.append(fname)
    return files

def load_image_gray(image_path):
    img = Image.open(image_path).convert('L')
    return np.array(img), img

def check_gap_conditions(image_gray):
    """
    For each pixel, check:
    1. Grayscale value between 5 and 30 (inclusive)
    2. At least one adjacent direction (up/down/left/right) having 20 contiguous pixels in that direction
       ALL with grayscale between 5 and 30 (inclusive)
    Returns: gap_flag array (1 if GAP, else 0)
    """
    rows, cols = image_gray.shape
    gap_flag = np.zeros((rows, cols), dtype=np.uint8)

    # Condition 1: grayscale mask
    gray_mask = ((image_gray >= 5) & (image_gray <= 30)).astype(np.uint8)

    for r in range(rows):
        for c in range(cols):
            if gray_mask[r, c] == 0:
                continue
            found = False
            # up
            if r - 20 >= 0 and np.all(gray_mask[r-20:r, c]):
                found = True
            # down
            if not found and r + 20 < rows and np.all(gray_mask[r+1:r+21, c]):
                found = True
            # left
            if not found and c - 20 >= 0 and np.all(gray_mask[r, c-20:c]):
                found = True
            # right
            if not found and c + 20 < cols and np.all(gray_mask[r, c+1:c+21]):
                found = True
            if found:
                gap_flag[r, c] = 1
    return gap_flag

def save_pixel_csv(image_gray, gap_flag, out_csv_path):
    rows, cols = image_gray.shape
    with open(out_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['row', 'col', 'gray', 'GAP'])
        for r in range(rows):
            for c in range(cols):
                writer.writerow([r, c, int(image_gray[r, c]), int(gap_flag[r, c])])

def calc_gap_height_csv(gap_flag, re, out_csv_path):
    """
    For each column, find all rows with GAP_flag=1.
    For each column, GAP_height = (max_row - min_row + 1) * re (μm).
    Output: column, min_row, max_row, GAP_height
    """
    rows, cols = gap_flag.shape
    with open(out_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['column', 'min_row', 'max_row', 'GAP_height(um)'])
        for c in range(cols):
            gap_rows = np.where(gap_flag[:, c] == 1)[0]
            if len(gap_rows) == 0:
                writer.writerow([c, '', '', 0])
            else:
                min_row, max_row = int(np.min(gap_rows)), int(np.max(gap_rows))
                gap_height = (max_row - min_row + 1) * re
                writer.writerow([c, min_row, max_row, gap_height])

def write_txt_report(re, gap_height_csv, out_txt_path):
    """
    TXT file: contains (1) Physical dimension parameter (μm/pixel)
    (2) Height statistics (max height in μm)
    """
    max_height = 0
    with open(gap_height_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                h = float(row['GAP_height(um)'])
                if h > max_height:
                    max_height = h
            except:
                continue
    with open(out_txt_path, 'w') as f:
        f.write(f"Physical dimension (μm/pixel): {re}\n")
        f.write(f"Max GAP height (μm): {max_height}\n")

def make_gap_image(image, gap_flag, out_img_path):
    # image: original PIL image (grayscale)
    color_img = image.convert('RGB')
    arr = np.array(color_img)
    # Highlight GAP points in red
    red_points = np.where(gap_flag == 1)
    arr[red_points[0], red_points[1]] = [255, 0, 0]
    new_img = Image.fromarray(arr)
    new_img.save(out_img_path)

def process_images(input_directory, re):
    ensure_dir(OUTPUT_DIR)
    image_files = get_image_files(input_directory)

    for fname in image_files:
        base_name = os.path.splitext(fname)[0]
        img_path = os.path.join(input_directory, fname)
        print(f"Processing {fname}...")

        # Step 1: Load image and grayscale
        image_gray, pil_gray = load_image_gray(img_path)

        # Step 2: GAP flag calculation
        gap_flag = check_gap_conditions(image_gray)

        # Step 3: Per-pixel CSV
        pixel_csv = os.path.join(OUTPUT_DIR, f"{base_name}_gap_analysis.csv")
        save_pixel_csv(image_gray, gap_flag, pixel_csv)

        # Step 4: GAP height per column
        gap_height_csv = os.path.join(OUTPUT_DIR, f"{base_name}_gap_height.csv")
        calc_gap_height_csv(gap_flag, re, gap_height_csv)

        # Step 5: TXT report
        txt_report = os.path.join(OUTPUT_DIR, f"{base_name}_result.txt")
        write_txt_report(re, gap_height_csv, txt_report)

        # Step 6: Highlight image
        out_img = os.path.join(OUTPUT_DIR, f"{base_name}_gap_highlighted.png")
        make_gap_image(pil_gray, gap_flag, out_img)

        print(f"Output for {fname}:")
        print(f"  pixel_csv: {pixel_csv}")
        print(f"  gap_height_csv: {gap_height_csv}")
        print(f"  txt_report: {txt_report}")
        print(f"  highlighted image: {out_img}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='GAP pixel analysis for images.')
    parser.add_argument('-re', type=float, required=True, help='Physical dimension parameter (μm/pixel)')
    args = parser.parse_args()

    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory, args.re)
    print("Proceed all the images！")
