import os
import csv
import cv2
from PIL import Image
import numpy as np

def enhance_spot_image(img, clipLimit=3, tileGridSize=(10, 10)):
    """Apply CLAHE to the input image."""
    clahe = cv2.createCLAHE(clipLimit=clipLimit, tileGridSize=tileGridSize)
    if len(img.shape) == 3 and img.shape[2] == 3:
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = img
    clahe_img = clahe.apply(img_gray)
    return clahe_img

def check_gap_conditions(gray_img, row, col):
    """
    Check if pixel at (row, col) is GAP pixel:
    (1) Grayscale value between 1–150 (inclusive)
    (2) At least one direction (up/down/left/right) has 25 contiguous pixels with grayscale in [1,150]
    """
    h, w = gray_img.shape
    pixel_val = gray_img[row, col]
    if not (1 <= pixel_val <= 150):
        return 0

    directions = [(-1,0), (1,0), (0,-1), (0,1)] # up, down, left, right
    for dr, dc in directions:
        count = 1
        for i in range(1, 25):
            nr, nc = row + dr*i, col + dc*i
            if 0 <= nr < h and 0 <= nc < w and (1 <= gray_img[nr, nc] <= 150):
                count += 1
            else:
                break
        if count == 25:
            return 1
    return 0

def save_csv(csv_path, pixel_data):
    """Save the pixel data to a CSV file."""
    with open(csv_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['row', 'column', 'grayscale', 'GAP_flag'])
        writer.writerows(pixel_data)

def process_new_images(out_image_path, gap_flags):
    """Generate PNG image visualizing GAP flags."""
    gap_img = np.where(gap_flags==1, 0, 255).astype(np.uint8)
    rgb_img = np.stack([gap_img]*3, axis=2) # convert to RGB
    Image.fromarray(rgb_img).save(out_image_path)

def process_images(input_directory):
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T3\backup9"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    img_files = [f for f in os.listdir(input_directory) if f.startswith("Poly_") and f.lower().endswith(('.png','.jpg','.jpeg'))]
    print(f"Found {len(img_files)} matching images.")

    for fname in img_files:
        img_path = os.path.join(input_directory, fname)
        print(f"Processing image: {img_path}")
        img = cv2.imread(img_path)
        if img is None:
            print(f"Warning: Unable to read image {img_path}. Skipping.")
            continue

        # CLAHE enhancement
        clahe_img = enhance_spot_image(img)
        clahe_out_path = os.path.join(output_directory, f"{os.path.splitext(fname)[0]}_CLAHE.png")
        cv2.imwrite(clahe_out_path, clahe_img)
        print(f"Saved CLAHE-enhanced image to {clahe_out_path}")

        # Load CLAHE image with PIL
        pil_img = Image.fromarray(clahe_img)
        gray_img = np.array(pil_img)

        # Prepare per-pixel GAP flag array and CSV data
        h, w = gray_img.shape
        gap_flags = np.zeros_like(gray_img, dtype=np.uint8)
        pixel_data = []
        for row in range(h):
            for col in range(w):
                gray_val = int(gray_img[row, col])
                gap_flag = check_gap_conditions(gray_img, row, col)
                gap_flags[row, col] = gap_flag
                pixel_data.append([row, col, gray_val, gap_flag])

        # Save CSV
        csv_path = os.path.join(output_directory, f"{os.path.splitext(fname)[0]}_gap_analysis.csv")
        save_csv(csv_path, pixel_data)
        print(f"Saved pixel analysis CSV to {csv_path}")

        # Generate output PNG
        out_image_path = os.path.join(output_directory, f"{os.path.splitext(fname)[0]}_gap_map.png")
        process_new_images(out_image_path, gap_flags)
        print(f"Saved GAP visualization image to {out_image_path}")

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    print("Proceed all the images！")
