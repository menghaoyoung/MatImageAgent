import os
import csv
from PIL import Image
import numpy as np

def check_gap_conditions(gray_img, row, col):
    """
    GAP pixel defined as:
    (1) Grayscale value between 5–30 (inclusive)
    (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition.
    """
    val = gray_img[row, col]
    if not (5 <= val <= 30):
        return 0  # Not GAP

    h, w = gray_img.shape

    # Directions: up, down, left, right
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    for dr, dc in directions:
        cnt = 0
        r, c = row+dr, col+dc
        for _ in range(20):
            if 0 <= r < h and 0 <= c < w and (5 <= gray_img[r, c] <= 30):
                cnt += 1
                r += dr
                c += dc
            else:
                break
        if cnt == 20:
            return 1  # GAP
    return 0

def save_csv(csv_path, data):
    with open(csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['row', 'column', 'grayscale', 'GAP_flag'])
        writer.writerows(data)

def process_images(input_dir):
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S1\backup9"
    os.makedirs(output_dir, exist_ok=True)
    img_names = [f for f in os.listdir(input_dir) if f.startswith("Li_") and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"Found {len(img_names)} images to process.")

    for img_name in img_names:
        img_path = os.path.join(input_dir, img_name)
        img = Image.open(img_path).convert('L')  # Convert to grayscale
        gray_np = np.array(img)
        h, w = gray_np.shape

        # For new image output
        rgb_img = img.convert('RGB')
        rgb_np = np.array(rgb_img)

        analysis_data = []
        gap_mask = np.zeros((h, w), dtype=bool)

        for row in range(h):
            for col in range(w):
                gray_val = int(gray_np[row, col])
                gap_flag = check_gap_conditions(gray_np, row, col)
                analysis_data.append([row, col, gray_val, gap_flag])
                if gap_flag == 1:
                    gap_mask[row, col] = True

        # Save CSV
        img_base = os.path.splitext(img_name)[0]
        csv_name = f"{img_base}_gap_analysis.csv"
        csv_path = os.path.join(output_dir, csv_name)
        save_csv(csv_path, analysis_data)
        print(f"Saved CSV: {csv_path}")

        # Generate new image with GAP pixels in red
        # Set [R,G,B] = [255,0,0] where GAP_flag==1
        rgb_np[gap_mask] = [255,0,0]
        out_img = Image.fromarray(rgb_np)
        out_img_name = f"{img_base}_gap_highlight.png"
        out_img_path = os.path.join(output_dir, out_img_name)
        out_img.save(out_img_path)
        print(f"Saved new image: {out_img_path}")

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    print("Proceed all the images！")
