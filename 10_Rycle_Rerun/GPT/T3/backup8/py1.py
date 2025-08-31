import os
import csv
import cv2
from PIL import Image
import numpy as np

def enhance_spot_image(img, clahe):
    """
    Apply CLAHE enhancement to the input image.
    """
    if len(img.shape) == 3:
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = img.copy()
    enhanced_img = clahe.apply(img_gray)
    return enhanced_img

def check_gap_conditions(gray_arr, row, col):
    """
    Return 1 if the pixel at (row, col) is a GAP pixel.
    GAP pixel: (1) grayscale in [1,150]; (2) at least one direction (up/down/left/right) has 25 contiguous pixels with grayscale in [1,150].
    """
    value = gray_arr[row, col]
    if value < 1 or value > 150:
        return 0

    h, w = gray_arr.shape
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
    for d in directions:
        cnt = 0
        for step in range(1, 26):  # 1~25
            nr = row + d[0]*step
            nc = col + d[1]*step
            if 0 <= nr < h and 0 <= nc < w:
                if 1 <= gray_arr[nr, nc] <= 150:
                    cnt += 1
                else:
                    break
            else:
                break
        if cnt == 25:
            return 1
    return 0

def save_csv(pixel_data, csv_path):
    """
    Save pixel analysis data to CSV.
    """
    with open(csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['row', 'col', 'gray_value', 'GAP_flag'])
        for row, col, gray, gap_flag in pixel_data:
            writer.writerow([row, col, gray, gap_flag])

def process_new_images(gray_arr, gap_arr, out_img_path):
    """
    Generate a new PNG image highlighting GAP pixels in black and others in white.
    """
    h, w = gap_arr.shape
    out_img = np.zeros((h, w, 3), dtype=np.uint8)
    out_img[gap_arr == 1] = [0, 0, 0]
    out_img[gap_arr == 0] = [255, 255, 255]
    out_pil = Image.fromarray(out_img)
    out_pil.save(out_img_path)

def process_images(input_directory):
    clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(10, 10))
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T3\backup8"
    os.makedirs(output_directory, exist_ok=True)
    img_files = [f for f in os.listdir(input_directory) if (f.startswith("Poly_") and f.lower().endswith(('.png', '.jpg', '.jpeg')))]
    print(f"Found {len(img_files)} images to process in '{input_directory}'.")
    for img_name in img_files:
        img_path = os.path.join(input_directory, img_name)
        print(f"Processing image: {img_name}")
        # Step 1: Read and CLAHE
        img = cv2.imread(img_path)
        if img is None:
            print(f"Warning: Failed to read {img_path}, skipping.")
            continue
        enhanced_img = enhance_spot_image(img, clahe)
        # Save CLAHE image for record (optional)
        clahe_name = os.path.splitext(img_name)[0] + "_CLAHE.png"
        clahe_path = os.path.join(output_directory, clahe_name)
        cv2.imwrite(clahe_path, enhanced_img)
        print(f"Saved CLAHE image to {clahe_path}")

        # Step 2: Convert to grayscale (already gray), extract pixels
        gray_arr = enhanced_img
        h, w = gray_arr.shape
        gap_arr = np.zeros((h, w), dtype=np.uint8)
        pixel_data = []
        # Step 3: Check GAP condition for each pixel
        for row in range(h):
            for col in range(w):
                gray_val = int(gray_arr[row, col])
                gap_flag = check_gap_conditions(gray_arr, row, col)
                gap_arr[row, col] = gap_flag
                pixel_data.append((row, col, gray_val, gap_flag))
            if row % 50 == 0:
                print(f"  {row}/{h} rows processed...")

        # Step 4: Save CSV
        csv_name = os.path.splitext(img_name)[0] + "_gap_analysis.csv"
        csv_path = os.path.join(output_directory, csv_name)
        save_csv(pixel_data, csv_path)
        print(f"Saved pixel CSV to {csv_path}")

        # Step 5: Save new highlighted image
        out_img_name = os.path.splitext(img_name)[0] + "_gap_map.png"
        out_img_path = os.path.join(output_directory, out_img_name)
        process_new_images(gray_arr, gap_arr, out_img_path)
        print(f"Saved GAP map image to {out_img_path}")

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    print("Proceed all the images！")
