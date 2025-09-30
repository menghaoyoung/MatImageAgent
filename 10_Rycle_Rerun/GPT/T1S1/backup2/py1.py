import os
import csv
from PIL import Image
import numpy as np

# Check whether the pixel point (i, j) meets the GAP condition
def check_gap_conditions(gray_img, i, j):
    """
    gray_img: 2D numpy array of grayscale values
    i, j: pixel coordinates
    Returns: True if GAP, False otherwise
    """
    value = gray_img[i, j]
    if value < 5 or value > 30:
        return False

    h, w = gray_img.shape

    # Directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dx, dy in directions:
        ni, nj = i + dx, j + dy
        # Check if adjacent pixel is within bounds
        if ni < 0 or ni >= h or nj < 0 or nj >= w:
            continue
        # Now, for this direction, check for 20 contiguous pixels meeting grayscale condition
        count = 0
        for k in range(20):
            xi, yj = i + dx * k, j + dy * k
            if xi < 0 or xi >= h or yj < 0 or yj >= w:
                break
            if 5 <= gray_img[xi, yj] <= 30:
                count += 1
            else:
                break
        if count == 20:
            return True
    return False

def save_csv(csv_path, rows):
    with open(csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['row', 'column', 'grayscale', 'GAP_flag'])
        writer.writerows(rows)

def process_images(input_directory):
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S1\backup3"
    os.makedirs(output_dir, exist_ok=True)
    img_files = [f for f in os.listdir(input_directory) if (f.startswith("Li_") and f.lower().endswith(('.png', '.jpg', '.jpeg')))]
    print(f"Found {len(img_files)} images to process.")

    for img_file in img_files:
        img_path = os.path.join(input_directory, img_file)
        # Open image and convert to grayscale
        with Image.open(img_path) as img:
            gray_img = img.convert('L')
            gray_np = np.array(gray_img)
            h, w = gray_np.shape

            # Prepare CSV data and GAP_flag array
            csv_rows = []
            gap_mask = np.zeros((h, w), dtype=np.uint8)

            # Check each pixel
            for i in range(h):
                for j in range(w):
                    gray_val = int(gray_np[i, j])
                    gap_flag = 1 if check_gap_conditions(gray_np, i, j) else 0
                    csv_rows.append([i, j, gray_val, gap_flag])
                    gap_mask[i, j] = 255 if gap_flag else 0

            # Save CSV
            base_name = os.path.splitext(img_file)[0]
            csv_name = f"{base_name}_gap_analysis.csv"
            csv_path = os.path.join(output_dir, csv_name)
            save_csv(csv_path, csv_rows)
            print(f"Saved CSV: {csv_path}")

            # Generate new image: copy original grayscale and paint GAP pixels red
            img_rgb = img.convert('RGB')
            img_rgb_np = np.array(img_rgb)
            # Highlight GAP pixels in red
            red = [255, 0, 0]
            mask_indices = np.where(gap_mask == 255)
            img_rgb_np[mask_indices] = red
            out_img = Image.fromarray(img_rgb_np)
            out_img_name = f"{base_name}_gap_highlight.png"
            out_img_path = os.path.join(output_dir, out_img_name)
            out_img.save(out_img_path)
            print(f"Saved highlighted image: {out_img_path}")

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    print("Proceed all the images！")
