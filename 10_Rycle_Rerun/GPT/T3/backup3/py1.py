import os
import csv
import cv2
from PIL import Image
import numpy as np

def enhance_spot_image(img_path, save_path):
    """
    Read an image, apply CLAHE (clipLimit=3, tileGridSize=(10, 10)), save enhanced image.
    """
    img = cv2.imread(img_path)
    if img is None:
        print(f"Failed to read image: {img_path}")
        return False

    # Convert to LAB color space
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(10, 10))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    cv2.imwrite(save_path, enhanced_img)
    print(f"CLAHE-enhanced image saved to: {save_path}")
    return True

def check_gap_conditions(gray_arr, row, col):
    """
    Check if pixel at (row, col) is a GAP pixel:
    (1) Grayscale value in [1,150]
    (2) At least one direction (up/down/left/right) has 25 contiguous pixels (including self) in [1,150]
    """
    h, w = gray_arr.shape
    if not (1 <= gray_arr[row, col] <= 150):
        return 0

    directions = [(-1,0), (1,0), (0,-1), (0,1)] # up, down, left, right
    for dr, dc in directions:
        count = 0
        r, c = row, col
        for i in range(25):
            nr, nc = r + dr * i, c + dc * i
            if 0 <= nr < h and 0 <= nc < w and (1 <= gray_arr[nr, nc] <= 150):
                count += 1
            else:
                break
        if count == 25:
            return 1  # GAP pixel
    return 0

def process_new_images(gray_arr, gap_flags, save_path):
    """
    Generate a new PNG image, where GAP=1 pixels are black (0,0,0), others white (255,255,255)
    """
    h, w = gray_arr.shape
    out_img = np.ones((h, w, 3), dtype=np.uint8) * 255
    out_img[gap_flags == 1] = [0, 0, 0]
    Image.fromarray(out_img).save(save_path)
    print(f"GAP highlight image saved to: {save_path}")

def save_csv(gray_arr, gap_flags, save_path):
    """
    Save pixel analysis to CSV: row, column, grayscale value, GAP flag
    """
    h, w = gray_arr.shape
    with open(save_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['row', 'column', 'grayscale_value', 'gap_flag'])
        for r in range(h):
            for c in range(w):
                csvwriter.writerow([r, c, int(gray_arr[r, c]), int(gap_flags[r, c])])
    print(f"CSV saved to: {save_path}")

def process_images(input_directory):
    # Output directory
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T3\backup2"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Find all images starting with 'Poly_' and with .png, .jpg, or .jpeg extension
    image_list = [f for f in os.listdir(input_directory)
                  if (f.startswith('Poly_') and f.lower().endswith(('.png', '.jpg', '.jpeg')))]

    print(f"Found {len(image_list)} images to process.")

    for img_fname in image_list:
        print(f"Processing image: {img_fname}")
        img_path = os.path.join(input_directory, img_fname)
        basename = os.path.splitext(img_fname)[0]
        # 1. CLAHE enhancement
        clahe_img_path = os.path.join(output_directory, f"{basename}_clahe.png")
        ok = enhance_spot_image(img_path, clahe_img_path)
        if not ok:
            continue

        # 2. Use PIL to process CLAHE-enhanced image
        pil_img = Image.open(clahe_img_path).convert('L')  # grayscale
        gray_arr = np.array(pil_img, dtype=np.uint8)
        h, w = gray_arr.shape

        # 3. GAP flag array
        gap_flags = np.zeros((h,w), dtype=np.uint8)
        for r in range(h):
            for c in range(w):
                gap_flags[r, c] = check_gap_conditions(gray_arr, r, c)
        print(f"Pixel analysis complete for {img_fname}")

        # 4. Save CSV
        csv_path = os.path.join(output_directory, f"{basename}_gap_analysis.csv")
        save_csv(gray_arr, gap_flags, csv_path)

        # 5. Save highlight image
        gap_img_path = os.path.join(output_directory, f"{basename}_gap_highlight.png")
        process_new_images(gray_arr, gap_flags, gap_img_path)

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    print("Proceed all the images！")
