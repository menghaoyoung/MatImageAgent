import os
import csv
import cv2
from PIL import Image
import numpy as np

def read_voice_transcript(file_path):
    """
    Reads the voice transcript file if it exists.
    Returns the content as a string, else returns empty string.
    """
    if os.path.isfile(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    return ""

def merge_task_with_transcript(md_description, transcript_text):
    """
    Merge the MD task description with the voice transcript content concisely.
    Returns a merged summary string.
    """
    merged_summary = (
        "Task requires per-pixel GAP detection in grayscale images. "
        "Generate CSV and highlighted PNG per image. Input images located in "
        "'C:/MatImageAgent/MatImageAgent/Images'. Output in "
        "'C:/MatImageAgent/MatImageAgent/Results'. Use GAP condition: grayscale "
        "value 1-155 inclusive and pixel neighbors having 25 contiguous pixels "
        "meeting grayscale condition. Additionally, prepare to generate a detailed "
        "simulation report in Word format based on results and graphs, following "
        "instructions from the voice transcript."
    )
    return merged_summary

def enhance_spot_image(img_gray):
    """
    Apply CLAHE (contrast limited adaptive histogram equalization) to enhance image.
    """
    clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(8, 8))
    enhanced = clahe.apply(img_gray)
    return enhanced

def check_gap_conditions(img_gray):
    """
    For each pixel in grayscale image, check GAP conditions:
    (1) Grayscale value between 1 and 155 inclusive
    (2) At least one adjacent pixel (up/down/left/right) has 25 contiguous pixels 
        meeting grayscale condition.
    Return a 2D numpy array of GAP flags (0 or 1).
    """
    rows, cols = img_gray.shape
    gap_flag = np.zeros_like(img_gray, dtype=np.uint8)

    # Condition 1 mask
    mask_condition1 = (img_gray >= 1) & (img_gray <= 155)

    # To find if adjacent pixel has 25 contiguous pixels meeting grayscale condition,
    # we will find connected components where grayscale within [1,155].
    condition_mask = mask_condition1.astype(np.uint8)

    # Find connected components for pixels within grayscale range
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(condition_mask, connectivity=4)

    # Create a map of size of connected component per pixel
    comp_sizes = np.zeros(num_labels, dtype=np.int32)
    for i in range(1, num_labels):
        comp_sizes[i] = stats[i, cv2.CC_STAT_AREA]

    comp_size_map = np.zeros_like(img_gray, dtype=np.int32)
    for r in range(rows):
        for c in range(cols):
            label = labels[r, c]
            comp_size_map[r, c] = comp_sizes[label] if label > 0 else 0

    # Iterate over all pixels to check GAP condition
    # For each pixel with grayscale in [1,155], check neighbors if any neighbor has
    # contiguous region of size >= 25 meeting grayscale condition
    for r in range(rows):
        for c in range(cols):
            if not mask_condition1[r, c]:
                continue
            neighbors = []
            if r - 1 >= 0:
                neighbors.append(comp_size_map[r - 1, c])
            if r + 1 < rows:
                neighbors.append(comp_size_map[r + 1, c])
            if c - 1 >= 0:
                neighbors.append(comp_size_map[r, c - 1])
            if c + 1 < cols:
                neighbors.append(comp_size_map[r, c + 1])
            if neighbors and any(sz >= 25 for sz in neighbors):
                gap_flag[r, c] = 1

    return gap_flag

def process_new_image(gap_flag, original_image_name, output_dir):
    """
    Generate new PNG image as per specification:
    Pixels with GAP=1 -> black (0,0,0)
    Pixels with GAP=0 -> white (255,255,255)
    Save as {original_image_name}_gap.png
    Return the new image path.
    """
    rows, cols = gap_flag.shape
    output_img = np.zeros((rows, cols, 3), dtype=np.uint8)
    # Set all pixels white (255,255,255)
    output_img[:, :, :] = 255
    # Set pixels with GAP=1 black
    output_img[gap_flag == 1] = [0, 0, 0]
    output_path = os.path.join(output_dir, f"{original_image_name}_gap.png")
    Image.fromarray(output_img).save(output_path)
    return output_path

def save_csv(gap_flag, img_gray, original_image_name, output_dir):
    """
    Save CSV file with columns:
    row, column, grayscale_value, GAP_flag
    Filename: {original_image_name}_gap_analysis.csv
    """
    csv_path = os.path.join(output_dir, f"{original_image_name}_gap_analysis.csv")
    with open(csv_path, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(['row', 'column', 'grayscale_value', 'GAP_flag'])
        rows, cols = img_gray.shape
        for r in range(rows):
            for c in range(cols):
                writer.writerow([r, c, int(img_gray[r, c]), int(gap_flag[r, c])])
    return csv_path

def process_images(input_directory, output_directory):
    """
    Process all images in the input directory whose filenames start with 'Poly_'
    """
    # Verify input and output directories
    if not os.path.isdir(input_directory):
        print(f"Input directory '{input_directory}' does not exist. Exiting.")
        return

    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)

    files_processed = 0
    for filename in os.listdir(input_directory):
        if filename.startswith("Poly_") and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            full_path = os.path.join(input_directory, filename)
            original_image_name = os.path.splitext(filename)[0]
            # Load image in grayscale
            img_gray = cv2.imread(full_path, cv2.IMREAD_GRAYSCALE)
            if img_gray is None:
                print(f"Failed to load image: {full_path}, skipping.")
                continue

            # Enhance image - optional enhancement as per framework
            img_gray_enhanced = enhance_spot_image(img_gray)

            # Compute GAP flag matrix
            gap_flag = check_gap_conditions(img_gray_enhanced)

            # Save CSV
            csv_path = save_csv(gap_flag, img_gray_enhanced, original_image_name, output_directory)
            print(f"Saved CSV to: {csv_path}")

            # Save new image highlighting GAP pixels
            new_img_path = process_new_image(gap_flag, original_image_name, output_directory)
            print(f"Saved gap-highlighted image to: {new_img_path}")

            files_processed += 1

    if files_processed == 0:
        print("No images starting with 'Poly_' found in the input directory.")
    else:
        print(f"Processed {files_processed} image(s) successfully.")

if __name__ == "__main__":
    # Read voice transcript if exists and merge with MD description
    VOICE_TRANSCRIPT_PATH = "C:/MatImageAgent/MatImageAgent/Voice_demo.txt"
    voice_text = read_voice_transcript(VOICE_TRANSCRIPT_PATH)

    MD_DESCRIPTION = """Task requires per-pixel pixel GAP detection in grayscale images.
Generate CSV and highlighted PNG per image using conditions:
Grayscale 1-155 inclusive,
and pixel neighbors with contiguous 25 pixels within grayscale condition.
Input images in 'C:/MatImageAgent/MatImageAgent/Images',
output to 'C:/MatImageAgent/MatImageAgent/Results'.
Prepare for final report generation from outputs."""

    merged_summary = merge_task_with_transcript(MD_DESCRIPTION, voice_text)
    print(f"Merged Task Summary:\n{merged_summary}\n")

    # Set input/output directories (with fallback logic)
    base_input_dir = "C:/MatImageAgent/MatImageAgent/Images"
    base_output_dir = "C:/MatImageAgent/MatImageAgent/Results"

    # Fallback to local folders if paths do not exist or invalid on Windows
    def valid_windows_path(path):
        if os.path.exists(path) and not path.startswith("/share/"):
            return True
        else:
            return False

    if not valid_windows_path(base_input_dir):
        base_input_dir = os.path.join(os.getcwd(), "Images")
    if not valid_windows_path(base_output_dir):
        base_output_dir = os.path.join(os.getcwd(), "Results")

    print(f"Using input directory: {base_input_dir}")
    print(f"Using output directory: {base_output_dir}")

    process_images(base_input_dir, base_output_dir)

    print("Proceed all the images！")
