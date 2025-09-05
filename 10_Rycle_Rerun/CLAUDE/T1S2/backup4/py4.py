import os
import csv
import argparse
from PIL import Image
import numpy as np
from collections import defaultdict
import time

def check_gap_conditions(grayscale_array, row, col, min_gray=5, max_gray=30, contiguous_count=20):
    """
    Check whether the pixel meets the GAP conditions:
    1. Grayscale value between min_gray and max_gray (inclusive)
    2. At least one adjacent pixel (up/down/left/right) has contiguous_count
       contiguous pixels meeting the grayscale condition
    """
    height, width = grayscale_array.shape
    
    # Check first condition: grayscale value between 5-30
    if not (min_gray <= grayscale_array[row, col] <= max_gray):
        return False
    
    # Check second condition: at least one adjacent pixel has 20 contiguous pixels
    # Define directions: up, right, down, left
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    
    for dr, dc in directions:
        adj_row, adj_col = row + dr, col + dc
        
        # Skip if adjacent pixel is out of bounds
        if not (0 <= adj_row < height and 0 <= adj_col < width):
            continue
        
        # Check if adjacent pixel meets grayscale condition
        if min_gray <= grayscale_array[adj_row, adj_col] <= max_gray:
            # Count contiguous pixels in this direction
            count = 1  # Start with 1 for the adjacent pixel
            curr_row, curr_col = adj_row, adj_col
            
            while count < contiguous_count:
                curr_row, curr_col = curr_row + dr, curr_col + dc
                
                # Break if out of bounds
                if not (0 <= curr_row < height and 0 <= curr_col < width):
                    break
                
                # Break if grayscale condition not met
                if not (min_gray <= grayscale_array[curr_row, curr_col] <= max_gray):
                    break
                
                count += 1
            
            # If we found contiguous_count pixels, return True
            if count >= contiguous_count:
                return True
    
    # No direction had enough contiguous pixels
    return False

def process_image(image_path, resolution):
    """Process a single image and return analysis results"""
    print(f"Processing image: {image_path}")
    
    # Open image and convert to grayscale
    img = Image.open(image_path).convert('L')
    grayscale_array = np.array(img)
    height, width = grayscale_array.shape
    
    # Create a new RGB image to highlight GAP pixels
    highlighted_img = Image.new('RGB', (width, height), color='white')
    highlighted_pixels = highlighted_img.load()
    
    # Copy original grayscale values to RGB image
    for row in range(height):
        for col in range(width):
            gray_value = grayscale_array[row, col]
            highlighted_pixels[col, row] = (gray_value, gray_value, gray_value)
    
    # Analyze pixels and store results
    pixel_data = []
    gap_pixels_by_column = defaultdict(list)
    
    for row in range(height):
        for col in range(width):
            gray_value = grayscale_array[row, col]
            is_gap = check_gap_conditions(grayscale_array, row, col)
            
            # Store pixel data
            pixel_data.append((row, col, gray_value, 1 if is_gap else 0))
            
            # If it's a GAP pixel, highlight it in red and store for height calculation
            if is_gap:
                highlighted_pixels[col, row] = (255, 0, 0)  # Red color
                gap_pixels_by_column[col].append(row)
    
    # Calculate GAP heights for each column
    gap_heights = []
    for col, rows in gap_pixels_by_column.items():
        if rows:  # If there are any GAP pixels in this column
            min_row = min(rows)
            max_row = max(rows)
            gap_height_um = (max_row - min_row + 1) * resolution
            gap_heights.append((col, gap_height_um))
    
    # Get max height for statistics
    max_height_um = max([height for _, height in gap_heights]) if gap_heights else 0
    
    # Save the highlighted image
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    # Return results
    return {
        'base_name': base_name,
        'pixel_data': pixel_data,
        'gap_heights': gap_heights,
        'max_height_um': max_height_um,
        'resolution': resolution,
        'original_image': image_path,
        'grayscale_array': grayscale_array,
        'highlighted_img': highlighted_img
    }

def save_results(results, output_dir):
    """Save analysis results to CSV and TXT files"""
    base_name = results['base_name']
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save highlighted image
    highlighted_img_path = os.path.join(output_dir, f"{base_name}_gap_highlighted.png")
    results['highlighted_img'].save(highlighted_img_path)
    
    # Save pixel analysis data to CSV
    pixel_csv_path = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
    with open(pixel_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Row', 'Column', 'Grayscale', 'GAP_Flag'])
        writer.writerows(results['pixel_data'])
    
    # Save GAP heights to CSV
    heights_csv_path = os.path.join(output_dir, f"{base_name}_gap_height.csv")
    with open(heights_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Column', 'GAP_Height(μm)'])
        writer.writerows(results['gap_heights'])
    
    # Save statistics to TXT
    txt_path = os.path.join(output_dir, f"{base_name}_statistics.txt")
    with open(txt_path, 'w') as txtfile:
        txtfile.write(f"Physical dimension parameter: {results['resolution']} μm/pixel\n")
        txtfile.write(f"Maximum GAP height: {results['max_height_um']:.4f} μm\n")
    
    return {
        'pixel_csv': pixel_csv_path,
        'heights_csv': heights_csv_path,
        'txt': txt_path,
        'highlighted_img_path': highlighted_img_path
    }

def process_images(input_directory, resolution, output_directory):
    """Process all images in the directory whose filenames start with 'Li_'"""
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    # Get all image files that start with "Li_"
    image_files = []
    for filename in os.listdir(input_directory):
        if filename.startswith("Li_") and (filename.lower().endswith('.png') or filename.lower().endswith('.jpg')):
            image_files.append(os.path.join(input_directory, filename))
    
    print(f"Found {len(image_files)} images to process")
    
    # Process each image
    all_results = []
    for image_path in image_files:
        results = process_image(image_path, resolution)
        file_paths = save_results(results, output_directory)
        all_results.append({**results, **file_paths})
    
    return all_results

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Analyze GAP in images")
    parser.add_argument("-re", "--resolution", type=float, required=True, 
                        help="Resolution in μm/pixel")
    parser.add_argument("-i", "--input", type=str, 
                        default=r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images",
                        help="Input directory containing images")
    parser.add_argument("-o", "--output", type=str, 
                        default=r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T1S2\backup4",
                        help="Output directory for results")
    
    args = parser.parse_args()
    
    start_time = time.time()
    
    # Process images
    results = process_images(args.input, args.resolution, args.output)
    
    end_time = time.time()
    print(f"Processed all images in {end_time - start_time:.2f} seconds!")
