import os
import csv
import cv2
import numpy as np

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL (Pillow) not installed. Image saving in PNG format will be limited.")

def read_voice_transcript(file_path):
    """
    Reads the voice transcript file if it exists.
    Returns the content as a string, else returns empty string.
    """
    try:
        if os.path.isfile(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
    except Exception as e:
        print(f"Error reading voice transcript: {e}")
    return ""

def merge_task_with_transcript(md_description, transcript_text):
    """
    Merge the MD task description with the voice transcript content concisely.
    Returns a merged summary string.
    """
    # Simple merge - if transcript exists, enrich summary, else just MD description summary
    if transcript_text:
        merged_summary = (
            "Merged task: Per-pixel GAP detection in grayscale images with conditions: "
            "grayscale between 1-155 inclusive and adjacent pixel regions of at least "
            "25 contiguous pixels within that grayscale range. "
            "Generate CSV and black-white highlight PNG per image. "
            "Input images located in 'Images' folder relative to script; output results in 'Results'. "
            "Also generate a detailed simulation report in Word format based on outputs and graphs."
        )
    else:
        merged_summary = (
            "Task requires per-pixel GAP detection in grayscale images. "
            "Generate CSV and highlighted PNG per image. Input images in 'Images' folder, "
            "output in 'Results' folder. Use GAP condition: grayscale value 1-155 inclusive "
            "and pixel neighbors having 25 contiguous pixels meeting grayscale condition. "
            "Prepare a final simulation report based on results."
        )
    return merged_summary

def enhance_spot_image(img_gray):
    """
    Apply CLAHE (contrast limited adaptive histogram equalization) to enhance image.
    """
    try:
        clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(8, 8))
        enhanced = clahe.apply(img_gray)
        return enhanced
    except Exception as e:
        print(f"Error during CLAHE enhancement: {e}. Returning original image.")
        return img_gray

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

    mask_condition1 = (img_gray >= 1) & (img_gray <= 155)
    condition_mask = mask_condition1.astype(np.uint8)

    try:
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(condition_mask, connectivity=4)
    except Exception as e:
        print(f"Error doing connected components: {e}")
        # Fallback - no connected components, return zeros
        return gap_flag

    comp_sizes = np.zeros(num_labels, dtype=np.int32)
    for i in range(1, num_labels):
        comp_sizes[i] = stats[i, cv2.CC_STAT_AREA]

    # Create a map size per pixel of the labeled connected component
    comp_size_map = np.zeros_like(img_gray, dtype=np.int32)
    for r in range(rows):
        for c in range(cols):
            label = labels[r, c]
            comp_size_map[r, c] = comp_sizes[label] if label > 0 else 0

    # Check GAP conditions per pixel
    for r in range(rows):
        for c in range(cols):
            if not mask_condition1[r, c]:
                continue
            neighbors_sizes = []
            if r - 1 >= 0:
                neighbors_sizes.append(comp_size_map[r - 1, c])
            if r + 1 < rows:
                neighbors_sizes.append(comp_size_map[r + 1, c])
            if c - 1 >= 0:
                neighbors_sizes.append(comp_size_map[r, c - 1])
            if c + 1 < cols:
                neighbors_sizes.append(comp_size_map[r, c + 1])
            if neighbors_sizes and any(sz >= 25 for sz in neighbors_sizes):
                gap_flag[r, c] = 1

    return gap_flag

def process_new_image(gap_flag, original_image_name, output_dir):
    """
    Generate new PNG image as per specification:
    Pixels with GAP=1 -> black (0,0,0)
    Pixels with GAP=0 -> white (255,255,255)
    Save as {original_image_name}_gap.png
    Return the new image path or None if saving failed.
    """
    rows, cols = gap_flag.shape
    output_img = np.full((rows, cols, 3), 255, dtype=np.uint8)  # white default
    output_img[gap_flag == 1] = [0, 0, 0]  # black for GAP==1

    output_path = os.path.join(output_dir, f"{original_image_name}_gap.png")
    try:
        if PIL_AVAILABLE:
            Image.fromarray(output_img).save(output_path)
        else:
            # Fallback: use cv2 to save PNG grayscale 0 or 255
            # Create single channel image with 0 or 255 per gap_flag
            gray_img = np.where(gap_flag == 1, 0, 255).astype(np.uint8)
            cv2.imwrite(output_path, gray_img)
        return output_path
    except Exception as e:
        print(f"Failed to save gap-highlighted image '{output_path}': {e}")
        return None

def save_csv(gap_flag, img_gray, original_image_name, output_dir):
    """
    Save CSV file with columns:
    row, column, grayscale_value, GAP_flag
    Filename: {original_image_name}_gap_analysis.csv
    """
    csv_path = os.path.join(output_dir, f"{original_image_name}_gap_analysis.csv")
    try:
        with open(csv_path, mode='w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['row', 'column', 'grayscale_value', 'GAP_flag'])
            rows, cols = img_gray.shape
            for r in range(rows):
                for c in range(cols):
                    writer.writerow([r, c, int(img_gray[r, c]), int(gap_flag[r, c])])
        return csv_path
    except Exception as e:
        print(f"Failed to save CSV '{csv_path}': {e}")
        return None

def process_images(input_directory, output_directory):
    """
    Process all images in the input directory whose filenames start with 'Poly_'.
    Produces per image: CSV and highlighted PNG.
    """
    if not os.path.isdir(input_directory):
        print(f"Input directory '{input_directory}' does not exist. Exiting.")
        return

    if not os.path.isdir(output_directory):
        try:
            os.makedirs(output_directory)
        except Exception as e:
            print(f"Failed to create output directory '{output_directory}': {e}")
            return

    files_processed = 0
    for filename in os.listdir(input_directory):
        if filename.startswith("Poly_") and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
            full_path = os.path.join(input_directory, filename)
            original_image_name = os.path.splitext(filename)[0]
            try:
                img_gray = cv2.imread(full_path, cv2.IMREAD_GRAYSCALE)
                if img_gray is None:
                    print(f"Failed to load image: {full_path}, skipping.")
                    continue

                img_gray_enhanced = enhance_spot_image(img_gray)
                gap_flag = check_gap_conditions(img_gray_enhanced)

                csv_path = save_csv(gap_flag, img_gray_enhanced, original_image_name, output_directory)
                if csv_path:
                    print(f"Saved CSV to: {csv_path}")
                else:
                    print(f"CSV not saved for image '{filename}' due to error.")

                new_img_path = process_new_image(gap_flag, original_image_name, output_directory)
                if new_img_path:
                    print(f"Saved gap-highlighted image to: {new_img_path}")
                else:
                    print(f"Gap-highlighted image not saved for '{filename}' due to error.")

                files_processed += 1
            except Exception as e:
                print(f"Exception processing image '{filename}': {e}")
    if files_processed == 0:
        print("No images starting with 'Poly_' found in the input directory or processable.")
    else:
        print(f"Processed {files_processed} image(s) successfully.")

if __name__ == "__main__":
    # Relative paths default
    VOICE_TRANSCRIPT_PATH = os.path.join(os.getcwd(), "Voice_demo.txt")
    MD_DESCRIPTION = (
        "Task requires per-pixel pixel GAP detection in grayscale images.\n"
        "Generate CSV and highlighted PNG per image using conditions:\n"
        "Grayscale 1-155 inclusive, and pixel neighbors with contiguous 25 pixels "
        "within grayscale condition.\nInput images in 'Images', output to 'Results'.\n"
        "Prepare for final report generation from outputs."
    )

    voice_text = read_voice_transcript(VOICE_TRANSCRIPT_PATH)
    merged_summary = merge_task_with_transcript(MD_DESCRIPTION, voice_text)
    print(f"Merged Task Summary:\n{merged_summary}\n")

    base_input_dir = os.path.join(os.getcwd(), "Images")
    base_output_dir = os.path.join(os.getcwd(), "Results")

    if not os.path.isdir(base_input_dir):
        print(f"Warning: Input directory '{base_input_dir}' does not exist.")

    if not os.path.isdir(base_output_dir):
        try:
            os.makedirs(base_output_dir)
            print(f"Created output directory '{base_output_dir}'.")
        except Exception as e:
            print(f"Failed to create output directory '{base_output_dir}': {e}")

    print(f"Using input directory: {base_input_dir}")
    print(f"Using output directory: {base_output_dir}")

    process_images(base_input_dir, base_output_dir)

    print("Proceed all the images！")
