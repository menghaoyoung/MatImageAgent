import os
import csv
from PIL import Image
import numpy as np

# Check whether the pixel at (row, col) meets the GAP condition
def check_gap_conditions(gray_img, row, col):
    # (1) Grayscale value between 5–30 (inclusive)
    h, w = gray_img.shape
    gval = gray_img[row, col]
    if gval < 5 or gval > 30:
        return False

    # (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition.
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
    for dr, dc in directions:
        count = 0
        for i in range(1, 21):  # 1 to 20
            nr = row + dr * i
            nc = col + dc * i
            if 0 <= nr < h and 0 <= nc < w:
                nval = gray_img[nr, nc]
                if 5 <= nval <= 30:
                    count += 1
                else:
                    break
            else:
                break
        if count == 20:
            return True
    return False

# Stores all pixel analysis data, naming: {original_image_name}_gap_analysis.csv
def save_csv(output_csv_path, gray_img, gap_flags):
    h, w = gray_img.shape
    with open(output_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['row', 'column', 'gray_value', 'GAP_flag'])
        for i in range(h):
            for j in range(w):
                writer.writerow([i, j, int(gray_img[i, j]), int(gap_flags[i, j])])

# Generate a new PNG image for each input image, highlighting points with GAP flag = 1 in red (RGB: 255, 0, 0)
def save_gap_image(output_img_path, orig_img, gap_flags):
    # orig_img is a PIL Image in RGB or L mode
    rgb_img = orig_img.convert('RGB')
    rgb_arr = np.array(rgb_img)
    h, w = gap_flags.shape

    # Set GAP pixels to red
    red = np.array([255, 0, 0], dtype=np.uint8)
    mask = gap_flags == 1
    rgb_arr[mask] = red

    new_img = Image.fromarray(rgb_arr)
    new_img.save(output_img_path)

# Process all images in the directory whose filenames start with "Li_"
def process_images(input_directory):
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S1\backup5"
    os.makedirs(output_directory, exist_ok=True)
    supported_ext = ('.png', '.jpg', '.jpeg')
    image_files = [f for f in os.listdir(input_directory)
                   if f.startswith('Li_') and f.lower().endswith(supported_ext)]

    print(f"Found {len(image_files)} image(s) starting with 'Li_' in {input_directory}")
    for fname in image_files:
        fpath = os.path.join(input_directory, fname)
        print(f"Processing {fname}...")
        orig_img = Image.open(fpath)
        gray_img = orig_img.convert('L')
        gray_np = np.array(gray_img)
        h, w = gray_np.shape

        gap_flags = np.zeros((h, w), dtype=np.uint8)

        # Check GAP condition for each pixel
        for i in range(h):
            for j in range(w):
                if check_gap_conditions(gray_np, i, j):
                    gap_flags[i, j] = 1

        # Save CSV
        base_name, _ = os.path.splitext(fname)
        csv_name = f"{base_name}_gap_analysis.csv"
        csv_path = os.path.join(output_directory, csv_name)
        save_csv(csv_path, gray_np, gap_flags)
        print(f"CSV saved to {csv_path}")

        # Save GAP image
        out_img_name = f"{base_name}_gap_highlighted.png"
        out_img_path = os.path.join(output_directory, out_img_name)
        save_gap_image(out_img_path, orig_img, gap_flags)
        print(f"Highlight image saved to {out_img_path}")

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    print("Proceed all the images！")
