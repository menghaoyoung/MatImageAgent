import os
import csv
import cv2
from PIL import Image
import numpy as np

# CLAHE parameters as specified
def enhance_spot_image(img_bgr):
    # Convert to LAB color space
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(10, 10))
    cl = clahe.apply(l)
    limg = cv2.merge((cl, a, b))
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return enhanced_img

# GAP condition:
# (1) Grayscale value between 1–150 (inclusive)
# (2) At least one adjacent pixel (up/down/left/right) has 25 contiguous pixels meeting the grayscale condition.
def check_gap_conditions(gray_img):
    h, w = gray_img.shape
    gap_flags = np.zeros((h, w), dtype=np.uint8)
    # Precompute mask of pixels in grayscale range
    mask = ((gray_img >= 1) & (gray_img <= 150)).astype(np.uint8)
    for y in range(h):
        for x in range(w):
            if mask[y, x]:  # (1)
                found = False
                # up
                if y >= 25 and np.all(mask[y-25:y, x]):
                    found = True
                # down
                if not found and y+25 <= h-1 and np.all(mask[y+1:y+26, x]):
                    found = True
                # left
                if not found and x >= 25 and np.all(mask[y, x-25:x]):
                    found = True
                # right
                if not found and x+25 <= w-1 and np.all(mask[y, x+1:x+26]):
                    found = True
                if found:
                    gap_flags[y, x] = 1
    return gap_flags

def save_csv(csv_path, gray_img, gap_flags):
    h, w = gray_img.shape
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['row', 'column', 'grayscale', 'gap_flag'])
        for y in range(h):
            for x in range(w):
                writer.writerow([y, x, int(gray_img[y, x]), int(gap_flags[y, x])])

def process_new_image(out_img_path, gap_flags):
    # GAP=1: black(0,0,0), GAP=0: white(255,255,255)
    img_out = np.where(gap_flags[..., None] == 1, [0, 0, 0], [255, 255, 255]).astype(np.uint8)
    img_pil = Image.fromarray(img_out)
    img_pil.save(out_img_path)

def process_images(input_directory):
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T3\backup6"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    image_filenames = [f for f in os.listdir(input_directory) if (f.startswith('Poly_') and f.lower().endswith(('.png', '.jpg', '.jpeg')))]
    print(f"Found {len(image_filenames)} images to process.")
    for fname in image_filenames:
        img_path = os.path.join(input_directory, fname)
        print(f"Processing: {img_path}")
        img_bgr = cv2.imread(img_path)
        if img_bgr is None:
            print(f"Failed to read {img_path}. Skipping.")
            continue
        # Enhance using CLAHE
        enhanced_bgr = enhance_spot_image(img_bgr)
        # Save CLAHE result as PNG
        clahe_filename = os.path.splitext(fname)[0] + '_clahe.png'
        clahe_path = os.path.join(output_dir, clahe_filename)
        cv2.imwrite(clahe_path, enhanced_bgr)
        print(f"Saved CLAHE enhanced image: {clahe_path}")
        # Convert to grayscale with PIL
        enhanced_rgb = cv2.cvtColor(enhanced_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(enhanced_rgb)
        pil_gray = pil_img.convert('L')
        gray_arr = np.array(pil_gray)
        # GAP analysis
        gap_flags = check_gap_conditions(gray_arr)
        # Save CSV
        csv_filename = os.path.splitext(fname)[0] + '_gap_analysis.csv'
        csv_path = os.path.join(output_dir, csv_filename)
        save_csv(csv_path, gray_arr, gap_flags)
        print(f"Saved CSV: {csv_path}")
        # Save new image (GAP map)
        out_img_filename = os.path.splitext(fname)[0] + '_gap_map.png'
        out_img_path = os.path.join(output_dir, out_img_filename)
        process_new_image(out_img_path, gap_flags)
        print(f"Saved GAP map image: {out_img_path}")

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    print("Proceed all the images！")
