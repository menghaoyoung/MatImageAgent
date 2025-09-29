import os
import sys
import csv
import numpy as np
from PIL import Image

# Precompute directional run-length arrays for in_range pixels
def compute_run_arrays(in_range):
    height, width = in_range.shape
    left_run = np.zeros((height, width), dtype=int)
    right_run = np.zeros((height, width), dtype=int)
    up_run = np.zeros((height, width), dtype=int)
    down_run = np.zeros((height, width), dtype=int)
    
    # Compute left_run (left to right)
    for i in range(height):
        for j in range(width):
            if in_range[i, j]:
                left_run[i, j] = 1 if j == 0 else left_run[i, j-1] + 1
    
    # Compute right_run (right to left)
    for i in range(height):
        for j in range(width-1, -1, -1):
            if in_range[i, j]:
                right_run[i, j] = 1 if j == width-1 else right_run[i, j+1] + 1
    
    # Compute up_run (top to bottom)
    for j in range(width):
        for i in range(height):
            if in_range[i, j]:
                up_run[i, j] = 1 if i == 0 else up_run[i-1, j] + 1
    
    # Compute down_run (bottom to top)
    for j in range(width):
        for i in range(height-1, -1, -1):
            if in_range[i, j]:
                down_run[i, j] = 1 if i == height-1 else down_run[i+1, j] + 1
                
    return left_run, right_run, up_run, down_run

# Save pixel data to CSV file
def save_csv(gray_array, gap_flag, csv_path):
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['row', 'column', 'grayscale_value', 'GAP_flag'])
        height, width = gray_array.shape
        for i in range(height):
            for j in range(width):
                writer.writerow([i, j, gray_array[i, j], gap_flag[i, j]])

# Process all images in the directory
def process_images(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    for filename in os.listdir(input_directory):
        if filename.startswith("Li_") and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = os.path.join(input_directory, filename)
            try:
                with Image.open(img_path) as img:
                    # Convert to grayscale and get pixel values
                    gray_img = img.convert('L')
                    gray_array = np.array(gray_img)
                    height, width = gray_array.shape
                    
                    # Create in_range mask (5-30 inclusive)
                    in_range = (gray_array >= 5) & (gray_array <= 30)
                    
                    # Compute directional runs
                    left_run, right_run, up_run, down_run = compute_run_arrays(in_range)
                    
                    # Initialize gap_flag array
                    gap_flag = np.zeros((height, width), dtype=int)
                    
                    # Identify GAP pixels
                    for i in range(height):
                        for j in range(width):
                            if in_range[i, j]:
                                # Check adjacent pixels for 20+ contiguous runs
                                if (j > 0 and in_range[i, j-1] and left_run[i, j-1] >= 20) or \
                                   (j < width-1 and in_range[i, j+1] and right_run[i, j+1] >= 20) or \
                                   (i > 0 and in_range[i-1, j] and up_run[i-1, j] >= 20) or \
                                   (i < height-1 and in_range[i+1, j] and down_run[i+1, j] >= 20):
                                    gap_flag[i, j] = 1
                    
                    # Save CSV
                    base_name = os.path.splitext(filename)[0]
                    csv_filename = f"{base_name}_gap_analysis.csv"
                    csv_path = os.path.join(output_directory, csv_filename)
                    save_csv(gray_array, gap_flag, csv_path)
                    
                    # Create highlighted image
                    rgb_img = img.convert('RGB')
                    rgb_pixels = rgb_img.load()
                    for i in range(height):
                        for j in range(width):
                            if gap_flag[i, j] == 1:
                                rgb_pixels[j, i] = (255, 0, 0)  # Set to red
                    
                    img_filename = f"{base_name}_gap_highlight.png"
                    img_path_out = os.path.join(output_directory, img_filename)
                    rgb_img.save(img_path_out)
                    
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    # Input directory (from command line argument)
    input_directory = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    
    # Fixed output directory
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1\backup3"
    
    # Process images
    process_images(input_directory, output_directory)
    print("Processed all images!")
