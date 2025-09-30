import os
import csv
from PIL import Image
import numpy as np

def check_gap_conditions(gray_img, row, col):
    """
    Check if the pixel at (row, col) satisfies the GAP condition:
    (1) Grayscale value between 5–30 (inclusive)
    (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition.
    Returns 1 if GAP, else 0.
    """
    h, w = gray_img.shape
    val = gray_img[row, col]
    if val < 5 or val > 30:
        return 0

    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    for dr, dc in directions:
        contiguous = 0
        for i in range(1, 21):  # 20 contiguous pixels outward
            nr, nc = row + dr*i, col + dc*i
            if 0 <= nr < h and 0 <= nc < w:
                neighbor_val = gray_img[nr, nc]
                if 5 <= neighbor_val <= 30:
                    contiguous += 1
                else:
                    break
            else:
                break
        if contiguous == 20:
            return 1
    return 0

def save_csv(output_path, pixel_data):
    with open(output_path, mode='w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['row', 'col', 'grayscale', 'GAP_flag'])
        csvwriter.writerows(pixel_data)

def process_images(input_directory):
    # Output directory
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S1\backup7"
    os.makedirs(output_dir, exist_ok=True)
    image_files = [f for f in os.listdir(input_directory)
                   if (f.startswith("Li_") and f.lower().endswith(('.png', '.jpg', '.jpeg')))]

    for fname in image_files:
        input_path = os.path.join(input_directory, fname)
        print(f"Processing {fname} ...")
        # Open and convert to grayscale
        img = Image.open(input_path).convert('L')
        gray_img = np.array(img)
        h, w = gray_img.shape

        # Prepare to store pixel data and GAP flags
        pixel_data = []
        gap_map = np.zeros((h, w), dtype=np.uint8)

        for r in range(h):
            for c in range(w):
                gray_val = int(gray_img[r, c])
                gap_flag = check_gap_conditions(gray_img, r, c)
                pixel_data.append([r, c, gray_val, gap_flag])
                gap_map[r, c] = gap_flag

        # Save CSV
        img_name = os.path.splitext(fname)[0]
        csv_out_path = os.path.join(output_dir, f"{img_name}_gap_analysis.csv")
        save_csv(csv_out_path, pixel_data)
        print(f"CSV saved to: {csv_out_path}")

        # Generate color image: highlight GAP pixels in red, others as grayscale
        rgb_img = np.stack([gray_img]*3, axis=2)
        # Set GAP pixels to red
        rgb_img[gap_map == 1] = [255, 0, 0]
        out_img = Image.fromarray(rgb_img.astype('uint8'))
        img_out_path = os.path.join(output_dir, f"{img_name}_gap_highlight.png")
        out_img.save(img_out_path)
        print(f"Highlighted image saved to: {img_out_path}")

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    print("Proceed all the images！")
