import os
import csv
from PIL import Image

def check_gap_conditions(gray_img):
    height = len(gray_img)
    width = len(gray_img[0])
    
    # Create mask for pixels in grayscale range [5,30]
    condition1_mask = []
    for r in range(height):
        row_mask = []
        for c in range(width):
            pixel_val = gray_img[r][c]
            row_mask.append(5 <= pixel_val <= 30)
        condition1_mask.append(row_mask)
    
    # Initialize gap_flag matrix with zeros
    gap_flag = [[0] * width for _ in range(height)]
    
    # Helper function to check contiguous pixels in a direction
    def check_contiguous(r, c, dr, dc):
        count = 0
        # Start from the adjacent pixel (r+dr, c+dc)
        r_pos, c_pos = r + dr, c + dc
        while (0 <= r_pos < height and 0 <= c_pos < width and count < 20):
            if condition1_mask[r_pos][c_pos]:
                count += 1
            else:
                break
            r_pos += dr
            c_pos += dc
        return count >= 20
    
    # Check each qualifying pixel for adjacent line condition
    for r in range(height):
        for c in range(width):
            if condition1_mask[r][c]:
                # Check four directions: up, down, left, right
                directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                for dr, dc in directions:
                    if check_contiguous(r, c, dr, dc):
                        gap_flag[r][c] = 1
                        break  # Only need one valid direction
    return gap_flag

def save_csv(output_csv_path, gray_img, gap_flag):
    with open(output_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['row', 'column', 'grayscale_value', 'GAP_flag'])
        for r in range(len(gray_img)):
            for c in range(len(gray_img[0])):
                writer.writerow([r, c, gray_img[r][c], gap_flag[r][c]])

def create_highlighted_image(original_img, gap_flag, output_img_path):
    if original_img.mode != 'RGB':
        rgb_img = original_img.convert('RGB')
    else:
        rgb_img = original_img.copy()
    
    pixels = rgb_img.load()
    width, height = rgb_img.size
    
    for r in range(height):
        for c in range(width):
            if gap_flag[r][c] == 1:
                pixels[c, r] = (255, 0, 0)  # Set pixel to red
    
    rgb_img.save(output_img_path)

def process_images(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    image_extensions = ('.png', '.jpg', '.jpeg')
    processed_count = 0
    
    for filename in os.listdir(input_dir):
        if filename.startswith("Li_") and filename.lower().endswith(image_extensions):
            img_path = os.path.join(input_dir, filename)
            try:
                img = Image.open(img_path)
            except Exception as e:
                print(f"Error opening {filename}: {str(e)}")
                continue
            
            # Convert to grayscale and extract pixel values
            gray_img = img.convert('L')
            width, height = gray_img.size
            pixel_data = list(gray_img.getdata())
            gray_2d = [pixel_data[i*width : (i+1)*width] for i in range(height)]
            
            # Identify GAP pixels
            gap_flag = check_gap_conditions(gray_2d)
            
            # Save CSV analysis
            base_name = os.path.splitext(filename)[0]
            csv_filename = f"{base_name}_gap_analysis.csv"
            csv_path = os.path.join(output_dir, csv_filename)
            save_csv(csv_path, gray_2d, gap_flag)
            
            # Create and save highlighted image
            img_filename = f"{base_name}_gap_highlighted.png"
            img_path_out = os.path.join(output_dir, img_filename)
            create_highlighted_image(img, gap_flag, img_path_out)
            
            processed_count += 1
    
    return processed_count

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1"
    
    count = process_images(input_directory, output_directory)
    print(f"Processed {count} images successfully!")
