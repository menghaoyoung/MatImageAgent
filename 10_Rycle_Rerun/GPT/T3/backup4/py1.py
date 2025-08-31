import os
import csv
import cv2
from PIL import Image
import numpy as np

def enhance_spot_image(img_path, save_path):
    """
    Reads an image, applies CLAHE (clipLimit=3, tileGridSize=(10,10)), and saves the result.
    """
    img = cv2.imread(img_path)
    if img is None:
        print(f"Failed to read {img_path}")
        return False
    img_lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(img_lab)
    clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(10, 10))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    cv2.imwrite(save_path, enhanced_img)
    print(f"CLAHE enhanced image saved: {save_path}")
    return True

def check_gap_conditions(gray_img, row, col):
    """
    Checks if the pixel at (row, col) meets GAP conditions:
    (1) Grayscale value between 1-150 (inclusive)
    (2) At least one of its up/down/left/right directions has 25 contiguous pixels meeting the grayscale condition.
    """
    h, w = gray_img.shape
    if not (1 <= gray_img[row, col] <= 150):
        return 0  # Not in grayscale range

    # Directions: (delta_row, delta_col)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right
    for dr, dc in directions:
        count = 0
        for step in range(1, 26):  # 1 to 25 steps
            nr = row + dr * step
            nc = col + dc * step
            if 0 <= nr < h and 0 <= nc < w:
                if 1 <= gray_img[nr, nc] <= 150:
                    count += 1
                else:
                    break
            else:
                break
        if count == 25:
            return 1  # Meets the GAP condition
    return 0

def save_csv(csv_path, data):
    """
    Saves pixel analysis data to CSV.
    data: list of tuples (row, col, gray, gap_flag)
    """
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['row', 'col', 'grayscale', 'GAP_flag'])
        writer.writerows(data)
    print(f"CSV file saved: {csv_path}")

def process_new_images(output_img_path, gap_map):
    """
    Generates a new PNG image highlighting GAP flag pixels.
    gap_map: 2D numpy array of 0 (non-GAP) or 1 (GAP)
    """
    out_img = np.where(gap_map == 1, 0, 255).astype(np.uint8)  # GAP=1: black, else white
    rgb_img = np.stack([out_img]*3, axis=2)  # Grayscale to RGB
    Image.fromarray(rgb_img).save(output_img_path)
    print(f"GAP highlight image saved: {output_img_path}")

def process_images(input_directory):
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T3\backup4"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    temp_clahe_dir = os.path.join(output_directory, "CLAHE_TEMP")
    if not os.path.exists(temp_clahe_dir):
        os.makedirs(temp_clahe_dir)

    # Acceptable image extensions
    img_exts = ('.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG')

    # Get all images starting with "Poly_"
    image_files = [f for f in os.listdir(input_directory)
                   if f.startswith("Poly_") and f.lower().endswith(img_exts)]
    if not image_files:
        print("No matching images found in input directory.")
        return

    for img_name in image_files:
        img_path = os.path.join(input_directory, img_name)
        # 1. CLAHE enhancement
        clahe_img_name = img_name.rsplit('.', 1)[0] + '_clahe.png'
        clahe_img_path = os.path.join(temp_clahe_dir, clahe_img_name)
        if not enhance_spot_image(img_path, clahe_img_path):
            continue

        # 2. Grayscale conversion using PIL
        with Image.open(clahe_img_path) as pil_img:
            gray_img = pil_img.convert('L')
            gray_np = np.array(gray_img)

        h, w = gray_np.shape
        pixel_data = []
        gap_map = np.zeros((h, w), dtype=np.uint8)

        print(f"Analyzing pixels for GAP condition in {img_name}...")
        for row in range(h):
            for col in range(w):
                gray_val = gray_np[row, col]
                gap_flag = check_gap_conditions(gray_np, row, col)
                gap_map[row, col] = gap_flag
                pixel_data.append((row, col, int(gray_val), gap_flag))
            if row % 100 == 0:
                print(f"  Processed {row}/{h} rows")

        # 3. Save CSV file
        csv_name = img_name.rsplit('.', 1)[0] + '_gap_analysis.csv'
        csv_path = os.path.join(output_directory, csv_name)
        save_csv(csv_path, pixel_data)

        # 4. Generate output PNG
        out_img_name = img_name.rsplit('.', 1)[0] + '_GAP_map.png'
        out_img_path = os.path.join(output_directory, out_img_name)
        process_new_images(out_img_path, gap_map)

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    print("Proceed all the images！")
