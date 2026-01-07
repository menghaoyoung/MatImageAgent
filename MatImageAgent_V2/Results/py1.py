import os
import csv
import cv2
from PIL import Image
import numpy as np
from collections import defaultdict
import time

def read_voice_transcript():
    """Read voice transcript if available and merge with task description"""
    merged_description = "Task: Generate per-pixel CSV with coordinates, grayscale values, and GAP flags. Create new images highlighting GAP points."
    
    try:
        if os.path.exists("./Voice_demo.txt"):
            with open("./Voice_demo.txt", "r") as f:
                voice_content = f.read().strip()
                merged_description += f"\nVoice transcript: {voice_content}"
                print("Voice transcript merged with task description.")
        else:
            print("No voice transcript found. Proceeding with original task description.")
    except Exception as e:
        print(f"Error reading voice transcript: {e}")
    
    print("Merged task summary:")
    print(merged_description)
    return merged_description

def enhance_spot_image(image):
    """Enhance the image for better analysis"""
    # Convert to grayscale if not already
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Apply CLAHE enhancement
    clahe = cv2.createCLAHE(clipLimit=3, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    return enhanced

def check_gap_conditions(image, row, col):
    """
    Check whether the pixel points meet the GAP condition:
    (1) Grayscale value between 1–155 (inclusive)
    (2) At least one adjacent pixel (up/down/left/right) has 25 contiguous pixels meeting the grayscale condition.
    """
    height, width = image.shape
    grayscale_value = image[row, col]
    
    # Check condition 1: Grayscale value between 1-155
    if not (1 <= grayscale_value <= 155):
        return 0, grayscale_value
    
    # Define directions: up, down, left, right
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for dr, dc in directions:
        contiguous_count = 0
        r, c = row, col
        
        # Check 25 contiguous pixels in this direction
        for _ in range(25):
            r += dr
            c += dc
            
            # Check if the pixel is within image boundaries
            if 0 <= r < height and 0 <= c < width:
                if 1 <= image[r, c] <= 155:
                    contiguous_count += 1
                else:
                    break
            else:
                break
        
        # If we found 25 contiguous pixels meeting the condition
        if contiguous_count >= 25:
            return 1, grayscale_value
    
    return 0, grayscale_value

def process_images(input_directory):
    """Process all images in the directory whose filenames start with 'Poly_'"""
    # Create results directory if it doesn't exist
    results_dir = "./Results"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # Check if the provided directory exists
    if not os.path.exists(input_directory):
        print(f"Directory {input_directory} does not exist. Using fallback directory './Images'")
        input_directory = "./Images"
        
        # Create Images directory if it doesn't exist
        if not os.path.exists(input_directory):
            os.makedirs(input_directory)
            print(f"Created directory {input_directory}")
    
    # Get all files starting with "Poly_" in the input directory
    image_files = [f for f in os.listdir(input_directory) if f.startswith("Poly_") and 
                  (f.lower().endswith('.png') or f.lower().endswith('.jpg') or f.lower().endswith('.jpeg'))]
    
    if not image_files:
        print(f"No images starting with 'Poly_' found in {input_directory}")
        return
    
    for image_file in image_files:
        print(f"Processing image: {image_file}")
        image_path = os.path.join(input_directory, image_file)
        
        # Read the image
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
            print(f"Failed to read image: {image_path}")
            continue
        
        # Enhance the image
        enhanced_image = enhance_spot_image(image)
        
        # Create output file names
        base_name = os.path.splitext(image_file)[0]
        csv_file = os.path.join(results_dir, f"{base_name}_gap_analysis.csv")
        new_image_file = os.path.join(results_dir, f"{base_name}_gap_highlighted.png")
        
        # Process the image and save results
        process_pixel_data(enhanced_image, csv_file, new_image_file, base_name)

def process_pixel_data(image, csv_file, new_image_file, base_name):
    """Process pixel data, create CSV and new image"""
    height, width = image.shape
    
    # Create a new image to highlight GAP points
    highlighted_image = np.ones((height, width, 3), dtype=np.uint8) * 255  # White background
    
    # Open CSV file for writing
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Row', 'Column', 'Grayscale', 'GAP_Flag'])
        
        # Process each pixel
        for row in range(height):
            for col in range(width):
                gap_flag, grayscale = check_gap_conditions(image, row, col)
                
                # Write to CSV
                writer.writerow([row, col, grayscale, gap_flag])
                
                # Update highlighted image
                if gap_flag == 1:
                    highlighted_image[row, col] = [0, 0, 0]  # Black for GAP=1
    
    # Save the highlighted image
    cv2.imwrite(new_image_file, highlighted_image)
    
    print(f"Saved CSV data to: {csv_file}")
    print(f"Saved highlighted image to: {new_image_file}")

if __name__ == "__main__":
    # Read voice transcript if available
    merged_description = read_voice_transcript()
    
    # Set input directory with fallback
    input_directory = "./Images"
    if input_directory.startswith("/share/") and not os.path.exists(input_directory):
        input_directory = "./Images"
    
    print(f"Processing images from: {input_directory}")
    process_images(input_directory)
    print("Processed all the images!")
