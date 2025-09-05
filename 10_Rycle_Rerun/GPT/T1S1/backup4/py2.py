import os
import sys
import glob

def check_outputs_exist(output_dir, input_dir):
    # Find all "Li_*.png" or "Li_*.jpg" images in the input dir
    input_images = []
    for ext in ('*.png', '*.jpg', '*.jpeg'):
        input_images.extend(glob.glob(os.path.join(input_dir, 'Li_' + ext)))

    success = True
    for img_path in input_images:
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        csv_name = f"{base_name}_gap_analysis.csv"
        out_img_name = f"{base_name}_gap_highlight.png"
        csv_path = os.path.join(output_dir, csv_name)
        out_img_path = os.path.join(output_dir, out_img_name)

        if not (os.path.isfile(csv_path) and os.path.isfile(out_img_path)):
            print(f"Missing output for {base_name}:")
            if not os.path.isfile(csv_path):
                print(f"  Missing CSV: {csv_path}")
            if not os.path.isfile(out_img_path):
                print(f"  Missing PNG: {out_img_path}")
            success = False
    return success

if __name__ == "__main__":
    # Directories as specified
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S1\backup4"
    # You can run py1.py here in the background if required (simulate that step if needed)
    # For this task, just check and print result
    if check_outputs_exist(output_dir, input_dir):
        print("Calculation successful")
    else:
        print("Calculation failed or incomplete")
