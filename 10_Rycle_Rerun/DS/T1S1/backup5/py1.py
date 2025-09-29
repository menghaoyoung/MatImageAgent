import os
import csv
from PIL import Image
import numpy as np

def process_images(input_directory):
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1\backup5"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    for filename in os.listdir(input_directory):
        if filename.startswith("Li_") and (filename.lower().endswith('.png') or filename.lower().endswith('.jpg')):
            img_path = os.path.join(input_directory, filename)
            try:
                img = Image.open(img_path)
                gray_img = img.convert('L')
                gray_array = np.array(gray_img)
                
                height, width = gray_array.shape
                condition1_mask = (gray_array >= 5) & (gray_array <= 30)
                
                horizontal_condition2_mask = np.zeros((height, width), dtype=bool)
                for i in range(height):
                    j = 0
                    while j < width:
                        if condition1_mask[i, j]:
                            start_j = j
                            while j < width and condition1_mask[i, j]:
                                j += 1
                            seg_length = j - start_j
                            if seg_length >= 20:
                                horizontal_condition2_mask[i, start_j:j] = True
                        else:
                            j += 1
                
                vertical_condition2_mask = np.zeros((height, width), dtype=bool)
                for j in range(width):
                    i = 0
                    while i < height:
                        if condition1_mask[i, j]:
                            start_i = i
                            while i < height and condition1_mask[i, j]:
                                i += 1
                            seg_length = i - start_i
                            if seg_length >= 20:
                                vertical_condition2_mask[start_i:i, j] = True
                        else:
                            i += 1
                
                adj_cond2_mask = condition1_mask & (horizontal_condition2_mask | vertical_condition2_mask)
                gap_flag = np.zeros((height, width), dtype=np.uint8)
                
                for i in range(height):
                    for j in range(width):
                        if condition1_mask[i, j]:
                            neighbors = []
                            if i > 0: neighbors.append((i-1, j))
                            if i < height-1: neighbors.append((i+1, j))
                            if j > 0: neighbors.append((i, j-1))
                            if j < width-1: neighbors.append((i, j+1))
                            
                            for ni, nj in neighbors:
                                if adj_cond2_mask[ni, nj]:
                                    gap_flag[i, j] = 1
                                    break
                
                base_name = os.path.splitext(filename)[0]
                csv_path = os.path.join(output_directory, f"{base_name}_gap_analysis.csv")
                with open(csv_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['row', 'column', 'gray_value', 'gap_flag'])
                    for i in range(height):
                        for j in range(width):
                            writer.writerow([i, j, gray_array[i, j], gap_flag[i, j]])
                
                if img.mode != 'RGB':
                    out_img = img.convert('RGB')
                else:
                    out_img = img.copy()
                out_pixels = out_img.load()
                for i in range(height):
                    for j in range(width):
                        if gap_flag[i, j] == 1:
                            out_pixels[j, i] = (255, 0, 0)
                
                img_out_path = os.path.join(output_directory, f"{base_name}_gap.png")
                out_img.save(img_out_path)
                print(f"Processed: {filename}")
                
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    process_images(input_directory)
    print("Processed all images!")
