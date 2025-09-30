import os
import csv
from PIL import Image
import numpy as np

def check_gap_conditions(gray_array, row, col, rows, cols):
    """
    Checks if the pixel at (row, col) qualifies as a GAP:
    (1) Grayscale between 5–30 inclusive
    (2) At least one direction (up/down/left/right) has 20 contiguous pixels meeting the grayscale range [5,30]
    """
    val = gray_array[row, col]
    if val < 5 or val > 30:
        return 0  # Not in grayscale range

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right

    for dr, dc in directions:
        cnt = 0
        for k in range(1, 21):  # 1 to 20 steps in this direction
            nr, nc = row + dr * k, col + dc * k
            if 0 <= nr < rows and 0 <= nc < cols:
                nval = gray_array[nr, nc]
                if 5 <= nval <= 30:
                    cnt += 1
                else:
                    break
            else:
                break
        if cnt == 20:
            return 1  # Found at least one direction with 20 contiguous
    return 0

def save_csv(csv_path, pixel_data):
    """
    Save per-pixel data to csv: row, column, grayscale, GAP flag
    """
    with open(csv_path, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['row', 'column', 'grayscale', 'GAP'])
        for row in pixel_data:
            writer.writerow(row)

def process_images(input_directory):
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S1\backup3"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for fname in os.listdir(input_directory):
        if fname.startswith("Li_") and fname.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_directory, fname)
            img = Image.open(image_path).convert('L')  # Grayscale
            gray_array = np.array(img)
            rows, cols = gray_array.shape

            pixel_data = []
            gap_mask = np.zeros((rows, cols), dtype=np.uint8)

            for r in range(rows):
                for c in range(cols):
                    gray_val = int(gray_array[r, c])
                    gap_flag = check_gap_conditions(gray_array, r, c, rows, cols)
                    pixel_data.append([r, c, gray_val, gap_flag])
                    if gap_flag == 1:
                        gap_mask[r, c] = 1

            # Save CSV
            base_name = os.path.splitext(fname)[0]
            csv_path = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
            save_csv(csv_path, pixel_data)
            print(f"Saved CSV: {csv_path}")

            # Highlight GAP pixels in red, others stay grayscale
            img_rgb = img.convert('RGB')
            rgb_array = np.array(img_rgb)
            red = [255, 0, 0]
            rgb_array[gap_mask == 1] = red
            out_img = Image.fromarray(rgb_array)
            out_img_path = os.path.join(output_dir, f"{base_name}_GAP_Highlight.png")
            out_img.save(out_img_path)
            print(f"Saved highlighted image: {out_img_path}")

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    print("Proceed all the images！")
