import os
import glob

def check_output_files(output_dir):
    # Find all output CSVs and highlighted PNGs
    csv_files = glob.glob(os.path.join(output_dir, "Li_*_gap_analysis.csv"))
    png_files = glob.glob(os.path.join(output_dir, "Li_*_gap_highlight.png"))
    # Check that at least one of each exists
    if len(csv_files) > 0 and len(png_files) > 0:
        print("Calculation successful")
    else:
        print("Calculation failed: Some output files are missing.")
    print(f"CSV files found: {csv_files}")
    print(f"PNG files found: {png_files}")

if __name__ == "__main__":
    # This path should match the output path from py1.py
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S1\backup3"
    check_output_files(output_directory)
