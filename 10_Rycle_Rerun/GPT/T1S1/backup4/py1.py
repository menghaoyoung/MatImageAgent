import os
import csv
from PIL import Image
import numpy as np

# GAP pixel: (1) Grayscale value between 5–30 (inclusive)
# (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition

def check_gap_condition(img_gray, row, col, gap_mask):
    h, w = img_gray.shape
    # First, check if this pixel is in range
    val = img_gray[row, col]
    if not (5 <= val <= 30):
        return 0

    # For each direction, check if at least one neighbor (up/down/left/right) has a segment of 20 contiguous pixels
    # in that direction (starting from the neighbor) with all values in 5-30
    directions = [(-1,0), (1,0), (0,-1), (0,1)] # up, down, left, right
    for dr, dc in directions:
        r, c = row + dr, col + dc
        segment = []
        for i in range(20):
            nr = r + dr*i
            nc = c + dc*i
            if 0 <= nr < h and 0 <= nc < w:
                segment.append(img_gray[nr, nc])
            else:
                break
        # Check if we have a full segment of 20
        if len(segment) == 20 and all(5 <= v <= 30 for v in segment):
            return 1
    return 0

def process_single_image(img_path, output_dir):
    base_name = os.path.splitext(os.path.basename(img_path))[0]
    print(f"Processing image: {base_name}")

    try:
        img = Image.open(img_path).convert('L')
        img_gray = np.array(img)

        h, w = img_gray.shape
        gap_mask = np.zeros((h, w), dtype=np.uint8)

        # CSV output list
        csv_rows = []

        for i in range(h):
            for j in range(w):
                gap_flag = check_gap_condition(img_gray, i, j, gap_mask)
                gap_mask[i, j] = gap_flag
                csv_rows.append([i, j, int(img_gray[i, j]), gap_flag])

        # Save CSV file
        csv_name = f"{base_name}_gap_analysis.csv"
        csv_path = os.path.join(output_dir, csv_name)
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['row', 'col', 'grayscale', 'GAP'])
            writer.writerows(csv_rows)
        print(f"Saved CSV: {csv_path}")

        # Create color output image
        out_img = np.stack([img_gray]*3, axis=-1)
        # Highlight GAP pixels in red
        out_img[gap_mask==1] = [255, 0, 0]
        out_img_pil = Image.fromarray(out_img.astype(np.uint8))
        out_img_name = f"{base_name}_gap_highlight.png"
        out_img_path = os.path.join(output_dir, out_img_name)
        out_img_pil.save(out_img_path)
        print(f"Saved output image: {out_img_path}")

    except Exception as e:
        print(f"Error processing {img_path}: {e}")

def process_images(input_directory):
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S1\backup4"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for fname in os.listdir(input_directory):
        if fname.startswith('Li_') and fname.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(input_directory, fname)
            process_single_image(img_path, output_directory)

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    print("Proceed all the images！")
