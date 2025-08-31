import os
import glob

def check_outputs(output_dir):
    csv_files = glob.glob(os.path.join(output_dir, "*_gap_analysis.csv"))
    img_files = glob.glob(os.path.join(output_dir, "*_gap_highlight.png"))
    if csv_files and img_files:
        print("Calculation successful")
        return True
    else:
        print("Output files not found. Calculation not successful.")
        return False

if __name__ == "__main__":
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T3\backup7"
    check_outputs(output_directory)
