import os
import csv
import sys
import numpy as np
from PIL import Image
from concurrent.futures import ProcessPoolExecutor
import warnings
warnings.filterwarnings('ignore', category=RuntimeWarning)

def check_gap_conditions(gray_array, r, c, height, width):
    """Optimized GAP condition check using dynamic programming"""
    if not (5 <= gray_array[r, c] <= 30):
        return False
    
    # Directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        count = 0
        
        # Check boundary immediately
        if not (0 <= nr < height and 0 <= nc < width):
            continue
            
        # Fast contiguous check with early termination
        for _ in range(20):
            if 5 <= gray_array[nr, nc] <= 30:
                count += 1
                if count >= 20:
                    return True
                # Move in direction
                nr += dr
                nc += dc
                if not (0 <= nr < height and 0 <= nc < width):
                    break
            else:
                break
                
    return False

def process_image_segment(gray_array, start_row, end_row):
    """Process image segment in parallel"""
    height, width = gray_array.shape
    segment_flags = np.zeros((end_row - start_row, width), dtype=np.uint8)
    
    for r in range(start_row, end_row):
        for c in range(width):
            if check_gap_conditions(gray_array, r, c, height, width):
                segment_flags[r - start_row, c] = 1
    return segment_flags, start_row, end_row

def process_image(image_path, output_dir):
    """Process image with parallel processing and optimized I/O"""
    try:
        # Open and convert image
        with Image.open(image_path) as img:
            gray_img = img.convert('L')
            gray_array = np.array(gray_img)
            height, width = gray_array.shape
        
        base_name = os.path.basename(image_path).split('.')[0]
        csv_path = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
        png_path = os.path.join(output_dir, f"{base_name}_gap_highlighted.png")
        
        # Skip if files already exist
        if os.path.exists(csv_path) and os.path.exists(png_path):
            return
            
        # Parallel processing setup
        num_processes = min(4, os.cpu_count() or 1)
        chunk_size = max(100, height // (num_processes * 2))
        gap_flags = np.zeros((height, width), dtype=np.uint8)
        
        with ProcessPoolExecutor(max_workers=num_processes) as executor:
            futures = []
            for start_row in range(0, height, chunk_size):
                end_row = min(start_row + chunk_size, height)
                futures.append(executor.submit(
                    process_image_segment, 
                    gray_array, 
                    start_row, 
                    end_row
                ))
            
            for future in futures:
                segment, start, end = future.result()
                gap_flags[start:end, :] = segment
        
        # Generate highlighted image
        color_img = np.stack([gray_array] * 3, axis=-1)
        color_img[gap_flags == 1] = [255, 0, 0]
        with Image.fromarray(color_img.astype('uint8')) as highlight_img:
            highlight_img.save(png_path, optimize=True)
        
        # Stream CSV writing to reduce memory
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['row', 'column', 'gray_value', 'gap_flag'])
            for r in range(height):
                for c in range(width):
                    writer.writerow([r, c, gray_array[r, c], gap_flags[r, c]])
                    
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")

def process_images(input_dir):
    """Process all Li_* images with error handling"""
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1\backup4"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Find all Li_ images
    images = []
    for f in os.listdir(input_dir):
        if f.startswith('Li_') and f.lower().endswith(('.png', '.jpg')):
            images.append(os.path.join(input_dir, f))
    
    # Process each image
    total = len(images)
    for i, img_path in enumerate(images, 1):
        print(f"Processing image {i}/{total}: {os.path.basename(img_path)}")
        process_image(img_path, output_dir)
    
    print(f"Processing completed for {total} images")

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    if len(sys.argv) > 1:
        input_directory = sys.argv[1]
    
    start_time = time.time()
    process_images(input_directory)
    print(f"Total execution time: {time.time() - start_time:.2f} seconds")
