import os

def verify_outputs(input_directory, output_directory):
    """
    Check if CSV and highlighted image files exist for each image starting with "Li_"
    in the input_directory. If all exist, print "Calculation successful".
    """
    # List all image filenames with Li_ prefix
    image_files = [f for f in os.listdir(input_directory)
                   if (f.startswith("Li_") and f.lower().endswith(('.png', '.jpg', '.jpeg')))]

    missing_files = []
    for fname in image_files:
        img_name = os.path.splitext(fname)[0]
        csv_path = os.path.join(output_directory, f"{img_name}_gap_analysis.csv")
        img_path = os.path.join(output_directory, f"{img_name}_gap_highlight.png")
        if not os.path.exists(csv_path):
            missing_files.append(csv_path)
        if not os.path.exists(img_path):
            missing_files.append(img_path)

    if not missing_files:
        print("Calculation successful")
    else:
        print("Missing output files:")
        for f in missing_files:
            print(f)

if __name__ == "__main__":
    # These paths must match those in py1.py
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S1\backup7"
    verify_outputs(input_dir, output_dir)
