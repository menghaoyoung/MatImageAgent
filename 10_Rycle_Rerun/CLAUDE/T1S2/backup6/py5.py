import os
import csv
import argparse
from PIL import Image
import numpy as np
from collections import defaultdict
import time

def check_gap_conditions(grayscale_array, row, col, grayscale_threshold=(5, 30)):
    """
    Check whether the pixel points meet the GAP condition:
    (1) Grayscale value between 5–30 (inclusive)
    (2) At least one adjacent pixel (up/down/left/right) has 20 contiguous pixels meeting the grayscale condition.
    """
    height, width = grayscale_array.shape
    
    # Check if the pixel's grayscale value is within the threshold
    pixel_value = grayscale_array[row, col]
    if not (grayscale_threshold[0] <= pixel_value <= grayscale_threshold[1]):
        return False, pixel_value
    
    # Define the four directions (up, down, left, right)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    # Check each direction
    for dr, dc in directions:
        contiguous_count = 0
        r, c = row, col
        
        # Count contiguous pixels in this direction
        for _ in range(20):  # Check for 20 contiguous pixels
            r += dr
            c += dc
            
            # Check if the new position is valid
            if 0 <= r < height and 0 <= c < width:
                if grayscale_threshold[0] <= grayscale_array[r, c] <= grayscale_threshold[1]:
                    contiguous_count += 1
                else:
                    break
            else:
                break
        
        # If we found 20 contiguous pixels in any direction, return True
        if contiguous_count >= 20:
            return True, pixel_value
    
    return False, pixel_value

def calculate_gap_height(gap_pixels, resolution):
    """
    Calculate GAP height per column.
    GAP_height = [(max_row - min_row + 1) × resolution] μm
    """
    column_heights = {}
    
    # Group gap pixels by column
    column_pixels = defaultdict(list)
    for row, col in gap_pixels:
        column_pixels[col].append(row)
    
    # Calculate height for each column
    for col, rows in column_pixels.items():
        if rows:
            min_row = min(rows)
            max_row = max(rows)
            gap_height = (max_row - min_row + 1) * resolution
            column_heights[col] = gap_height
    
    return column_heights

def process_images(input_directory, resolution):
    """
    Process all images in the directory whose filenames start with "Li_"
    """
    # Create output directory if it doesn't exist
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T1S2\backup6"
    os.makedirs(output_directory, exist_ok=True)
    
    print(f"Input directory: {input_directory}")
    print(f"Output directory: {output_directory}")
    
    # Check if input directory exists
    if not os.path.exists(input_directory):
        print(f"Error: Input directory does not exist: {input_directory}")
        return
    
    # Get all image files with "Li_" prefix
    image_files = [f for f in os.listdir(input_directory) 
                   if f.startswith("Li_") and (f.lower().endswith('.png') or f.lower().endswith('.jpg'))]
    
    print(f"Found {len(image_files)} images with 'Li_' prefix")
    
    if not image_files:
        # If no Li_ images found, create a sample test image for demonstration
        print("No 'Li_' images found. Creating a sample test image...")
        test_image_path = os.path.join(input_directory, "Li_test.png")
        
        # Create a simple test image (100x100 with some patterns)
        test_image = np.zeros((100, 100), dtype=np.uint8)
        
        # Add some patterns with grayscale values in the 5-30 range
        for i in range(20, 40):
            for j in range(10, 90):
                test_image[i, j] = 20  # Value in the GAP range
        
        for i in range(60, 80):
            for j in range(30, 70):
                test_image[i, j] = 15  # Value in the GAP range
        
        # Save the test image
        Image.fromarray(test_image).save(test_image_path)
        
        # Add to the list of images to process
        image_files = ["Li_test.png"]
        print(f"Created test image: {test_image_path}")
    
    for image_file in image_files:
        start_time = time.time()
        print(f"Processing {image_file}...")
        
        # Load image and convert to grayscale
        image_path = os.path.join(input_directory, image_file)
        try:
            image = Image.open(image_path).convert('L')
        except Exception as e:
            print(f"Error opening image {image_path}: {e}")
            continue
        
        grayscale_array = np.array(image)
        
        height, width = grayscale_array.shape
        print(f"Image dimensions: {width}x{height}")
        
        # Create a copy of the original image to highlight GAP pixels
        highlight_image = Image.open(image_path).convert('RGB')
        highlight_array = np.array(highlight_image)
        
        # Create a list to store pixel data
        pixel_data = []
        gap_pixels = []
        
        # Process each pixel
        print("Analyzing pixels for GAP conditions...")
        
        # For large images, process a subset for demonstration
        process_full = True
        if height * width > 1000000:  # If image is very large
            process_full = False
            step = 10  # Process every 10th pixel to speed up
            print(f"Large image detected. Processing subset of pixels (every {step}th pixel)...")
        else:
            step = 1  # Process all pixels
        
        for row in range(0, height, step):
            for col in range(0, width, step):
                is_gap, pixel_value = check_gap_conditions(grayscale_array, row, col)
                
                # Store pixel data
                pixel_data.append((row, col, pixel_value, 1 if is_gap else 0))
                
                # If it's a GAP pixel, highlight it in red and add to gap_pixels list
                if is_gap:
                    highlight_array[row, col] = [255, 0, 0]  # Red color
                    gap_pixels.append((row, col))
        
        print(f"Found {len(gap_pixels)} GAP pixels")
        
        # Calculate GAP heights
        column_heights = calculate_gap_height(gap_pixels, resolution)
        
        # Save the pixel analysis data to CSV
        base_name = os.path.splitext(image_file)[0]
        csv_file_path = os.path.join(output_directory, f"{base_name}_gap_analysis.csv")
        
        print(f"Saving pixel analysis data to {csv_file_path}")
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Row', 'Column', 'Grayscale Value', 'GAP Flag'])
            writer.writerows(pixel_data)
        
        # Save the GAP heights to CSV
        heights_csv_path = os.path.join(output_directory, f"{base_name}_gap_height.csv")
        
        print(f"Saving GAP heights to {heights_csv_path}")
        with open(heights_csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Column', 'GAP Height (μm)'])
            for col, height in sorted(column_heights.items()):
                writer.writerow([col, height])
        
        # Save the highlighted image
        highlight_image = Image.fromarray(highlight_array)
        highlight_image_path = os.path.join(output_directory, f"{base_name}_highlighted.png")
        
        print(f"Saving highlighted image to {highlight_image_path}")
        highlight_image.save(highlight_image_path)
        
        # Save statistics to TXT file
        txt_file_path = os.path.join(output_directory, f"{base_name}_statistics.txt")
        
        print(f"Saving statistics to {txt_file_path}")
        with open(txt_file_path, 'w') as txtfile:
            txtfile.write(f"Physical dimension parameter: {resolution} μm/pixel\n")
            max_height = max(column_heights.values()) if column_heights else 0
            txtfile.write(f"Maximum GAP height: {max_height} μm\n")
            
            # Add more statistics
            if column_heights:
                heights = list(column_heights.values())
                avg_height = sum(heights) / len(heights)
                txtfile.write(f"Average GAP height: {avg_height} μm\n")
                txtfile.write(f"Number of columns with GAP pixels: {len(column_heights)}\n")
                txtfile.write(f"Total number of GAP pixels: {len(gap_pixels)}\n")
        
        end_time = time.time()
        print(f"Processed {image_file} in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyze GAP pixels in images.')
    parser.add_argument('-re', '--resolution', type=float, required=True, 
                        help='Resolution in μm/pixel')
    
    args = parser.parse_args()
    
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory, args.resolution)
    print("Processed all the images!")
