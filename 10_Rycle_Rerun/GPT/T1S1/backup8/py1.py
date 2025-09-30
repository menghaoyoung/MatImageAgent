import os
import csv
from PIL import Image
import numpy as np

def check_gap_conditions(gray_img, row, col, min_gray=5, max_gray=30, contiguous_length=20):
    """
    Check if the pixel at (row, col) is a GAP pixel:
    (1) Grayscale value between 5–30 (inclusive)
    (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels
        meeting the grayscale condition.
    """
    rows, cols = gray_img.shape
    g = gray_img[row, col]
    if not (min_gray <= g <= max_gray):
        return 0  # Not in grayscale threshold

    # Direction vectors: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in directions:
        contiguous = 0
        for i in range(1, contiguous_length+1):
            r, c = row + dr*i, col + dc*i
            if 0 <= r < rows and 0 <= c < cols:
                if min_gray <= gray_img[r, c] <= max_gray:
                    contiguous += 1
                else:
                    break
            else:
                break
        if contiguous == contiguous_length:
            return 1
    return 0

def save_csv(output_csv_path, data):
    """
    Save analysis data to csv.
    Each row: row, col, grayscale_value, is_gap
    """
    with open(output_csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['row', 'col', 'grayscale_value', 'GAP_flag'])
        for row in data:
            writer.writerow(row)

def process_images(input_directory):
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S1\backup8"
    os.makedirs(output_dir, exist_ok=True)
    img_files = [f for f in os.listdir(input_directory) if f.startswith('Li_') and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"Found {len(img_files)} images to process.")

    for img_name in img_files:
        img_path = os.path.join(input_directory, img_name)
        with Image.open(img_path) as img:
            gray = img.convert('L')  # to grayscale
        gray_np = np.array(gray)
        rows, cols = gray_np.shape

        gap_mask = np.zeros_like(gray_np, dtype=np.uint8)
        analysis_data = []
        for r in range(rows):
            for c in range(cols):
                g_val = int(gray_np[r, c])
                is_gap = check_gap_conditions(gray_np, r, c)
                gap_mask[r, c] = 255 if is_gap else 0
                analysis_data.append([r, c, g_val, is_gap])

        # Save CSV
        base_name = os.path.splitext(img_name)[0]
        output_csv = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
        save_csv(output_csv, analysis_data)
        print(f"Saved CSV: {output_csv}")

        # Save highlighted image
        rgb_img = img.convert('RGB')
        rgb_np = np.array(rgb_img)
        # Set GAP pixels to red
        red_mask = gap_mask.astype(bool)
        rgb_np[red_mask] = [255, 0, 0]
        output_img = Image.fromarray(rgb_np)
        output_img_path = os.path.join(output_dir, f"{base_name}_gap_highlight.png")
        output_img.save(output_img_path)
        print(f"Saved Highlighted Image: {output_img_path}")

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    print("Proceed all the images！")
