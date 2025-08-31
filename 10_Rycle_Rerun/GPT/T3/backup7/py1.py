import os
import cv2
import csv
from PIL import Image
import numpy as np

def enhance_spot_image(img_path, out_path):
    """Apply CLAHE enhancement to image and save result."""
    img = cv2.imread(img_path)
    if img is None:
        print(f"Failed to read image: {img_path}")
        return False
    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)
    clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(10, 10))
    img_yuv[:, :, 0] = clahe.apply(img_yuv[:, :, 0])
    img_clahe = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)
    cv2.imwrite(out_path, img_clahe)
    print(f"CLAHE enhanced image saved: {out_path}")
    return True

def check_gap_conditions(gray_arr, row, col):
    """Check if pixel at (row, col) is a GAP pixel as per criteria."""
    rows, cols = gray_arr.shape
    pixel_val = gray_arr[row, col]
    # Check pixel value in 1-150
    if not (1 <= pixel_val <= 150):
        return 0
    directions = [(-1,0), (1,0), (0,-1), (0,1)]  # up, down, left, right
    for dr, dc in directions:
        count = 0
        for i in range(1,26):  # check next 25 pixels in this direction
            rr = row + dr*i
            cc = col + dc*i
            if 0 <= rr < rows and 0 <= cc < cols:
                if 1 <= gray_arr[rr, cc] <= 150:
                    count += 1
                else:
                    break
            else:
                break
        if count == 25:
            return 1
    return 0

def save_csv(csv_path, data):
    """Save CSV with columns: row, col, grayscale, gap_flag."""
    with open(csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['row', 'col', 'grayscale', 'gap_flag'])
        writer.writerows(data)
    print(f"CSV saved: {csv_path}")

def process_new_images(gray_arr, gap_arr, out_img_path):
    """Generate new image highlighting GAP pixels."""
    rows, cols = gray_arr.shape
    out_img = np.zeros((rows, cols, 3), dtype=np.uint8)
    # GAP=1->black, GAP=0->white
    out_img[gap_arr==1] = [0,0,0]
    out_img[gap_arr==0] = [255,255,255]
    out_pil = Image.fromarray(out_img)
    out_pil.save(out_img_path)
    print(f"Gap highlight image saved: {out_img_path}")

def process_images(input_directory):
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T3\backup7"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    img_files = [f for f in os.listdir(input_directory) if (f.startswith("Poly_") and f.lower().endswith(('.png','.jpg','.jpeg')))]
    print(f"Found {len(img_files)} Poly_ images in {input_directory}")
    for imgname in img_files:
        img_path = os.path.join(input_directory, imgname)
        base_name = os.path.splitext(imgname)[0]
        enhanced_path = os.path.join(output_directory, base_name + '_CLAHE.png')
        # 1. CLAHE enhancement
        success = enhance_spot_image(img_path, enhanced_path)
        if not success:
            continue
        # 2. Grayscale with PIL
        pil_img = Image.open(enhanced_path).convert('L')
        gray_arr = np.array(pil_img)
        rows, cols = gray_arr.shape
        gap_arr = np.zeros_like(gray_arr, dtype=np.uint8)
        csv_data = []
        # 3. Per-pixel analysis
        for r in range(rows):
            for c in range(cols):
                gap_flag = check_gap_conditions(gray_arr, r, c)
                gap_arr[r, c] = gap_flag
                csv_data.append([r, c, int(gray_arr[r, c]), int(gap_flag)])
        # 4. Save CSV
        csv_path = os.path.join(output_directory, f"{base_name}_gap_analysis.csv")
        save_csv(csv_path, csv_data)
        # 5. Save GAP/white-black image
        out_img_path = os.path.join(output_directory, f"{base_name}_gap_highlight.png")
        process_new_images(gray_arr, gap_arr, out_img_path)
        print(f"Processed image: {imgname}")

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    print("Proceed all the images！")
