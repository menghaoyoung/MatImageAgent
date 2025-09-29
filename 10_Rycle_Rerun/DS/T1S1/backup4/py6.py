import os
import csv
import sys
import time
import numpy as np
from PIL import Image

def check_gap_conditions(gray_array, r, c, height, width):
    """Efficient GAP condition check with directional scanning"""
    # Verify grayscale condition first
    if not (5 <= gray_array[r, c] <= 30):
        return False
    
    # Directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for dr, dc in directions:
        count = 0
        nr, nc = r + dr, c + dc
        
        # Check contiguous pixels in current direction
        while 0 <= nr < height and 0 <= nc < width:
            if 5 <= gray_array[nr, nc] <= 30:
                count += 1
                if count >= 20:
                    return True
            else:
                break  # Break on non-qualifying pixel
            nr += dr
            nc += dc
            
    return False

def process_image(img_path, output_dir):
    """Process a single image with optimized I/O operations"""
    try:
        # Open and convert image to grayscale
        with Image.open(img_path) as img:
            gray_img = img.convert('L')
            gray_array = np.array(gray_img, dtype=np.uint8)
            height, width = gray_array.shape
            
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        csv_path = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
        png_path = os.path.join(output_dir, f"{base_name}_gap_highlighted.png")
        
        # Skip processing if outputs already exist
        if os.path.exists(csv_path) and os.path.exists(png_path):
            return
        
        # Initialize gap flags array
        gap_flags = np.zeros((height, width), dtype=bool)
                    
        # Process each pixel to detect GAP conditions
        for r in range(height):
            for c in range(width):
                if check_gap_conditions(gray_array, r, c, height, width):
                    gap_flags[r, c] = True
        
        # Create highlighted version showing GAP pixels in red
        color_img = np.stack([gray_array] * 3, axis=-1)
        color_img[gap_flags] = [255, 0, 0]  # Set GAP pixels to red
        with Image.fromarray(color_img.astype('uint8')) as highlight_img:
            highlight_img.save(png_path)
        
        # Write CSV with streaming to conserve memory
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['row', 'column', 'gray_value', 'gap_flag'])
            
            for r in range(height):
                for c in range(width):
                    writer.writerow([r, c, gray_array[r, c], 1 if gap_flags[r, c] else 0])
                    
    except Exception as e:
        print(f"Error processing {img_path}: {str(e)}")
        import traceback
        traceback.print_exc()

def process_images(input_dir):
    """Process all Li_* images with progress tracking"""
    output_dir = os.path.join(
        r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1\backup4"
    )
    os.makedirs(output_dir, exist_ok=True)
    
    # Collect all Li_ images
    images = []
    for f in os.listdir(input_dir):
        if f.startswith('Li_') and f.lower().endswith(('.png', '.jpg')):
            images.append(os.path.join(input_dir, f))
    
    total = len(images)
    print(f"Found {total} images to process")
    
    # Process each image sequentially
    for i, img_path in enumerate(images, 1):
        print(f"Processing image {i}/{total}: {os.path.basename(img_path)}")
        start_time = time.time()
        process_image(img_path, output_dir)
        elapsed = time.time() - start_time
        print(f"  Completed in {elapsed:.2f} seconds")
    
    return total

if __name__ == "__main__":
    # Set default input directory
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    
    # Allow command-line override
    if len(sys.argv) > 1:
        input_directory = sys.argv[1]
    
    start_time = time.time()
    processed_count = process_images(input_directory)
    total_time = time.time() - start_time
    
    # Get absolute path for output directory without raw string in f-string
    output_path = os.path.abspath(
        r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1\backup4"
    )
    
    print(f"\nSuccessfully processed {processed_count} images")
    print(f"Total execution time: {total_time:.2f} seconds")
    print(f"Output files saved to: {output_path}")
