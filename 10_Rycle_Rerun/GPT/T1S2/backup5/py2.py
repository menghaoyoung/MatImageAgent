# py2_check_output.py
import os
import sys

def check_all_outputs_exist(output_dir, input_dir):
    # List all images with "Li_" prefix in input_dir and extension .png/.jpg/.jpeg
    image_files = [
        f for f in os.listdir(input_dir)
        if f.startswith("Li_") and f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]
    all_exist = True
    for fname in image_files:
        base = os.path.splitext(fname)[0]
        files_to_check = [
            f"{base}_gap_analysis.csv",
            f"{base}_gap_height.csv",
            f"{base}_result.txt",
            f"{base}_gap_highlighted.png",
        ]
        for out_file in files_to_check:
            out_path = os.path.join(output_dir, out_file)
            if not os.path.exists(out_path):
                print(f"Missing: {out_path}")
                all_exist = False
    return all_exist

if __name__ == "__main__":
    # You may change these paths if needed
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S2\backup5"
    if check_all_outputs_exist(output_dir, input_dir):
        print("Calculation successful")
    else:
        print("Some output files are missing.")
