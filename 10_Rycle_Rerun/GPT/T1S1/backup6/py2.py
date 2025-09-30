import os

# Output directory and naming rules must match py1.py
OUTPUT_DIRECTORY = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S1\backup6"

def check_results_exist(output_dir):
    """
    Check if there are any _gap_analysis.csv and _GAP_highlight.png files in the output directory.
    """
    if not os.path.exists(output_dir):
        print("Output directory does not exist.")
        return False

    files = os.listdir(output_dir)
    csv_files = [f for f in files if f.endswith('_gap_analysis.csv')]
    png_files = [f for f in files if f.endswith('_GAP_highlight.png')]
    if csv_files and png_files:
        return True
    else:
        return False

if __name__ == "__main__":
    # Run py1.py in the background
    ret = os.system("python py1.py")
    # Wait for process to complete before checking (os.system is blocking)
    if check_results_exist(OUTPUT_DIRECTORY):
        print("Calculation successful")
    else:
        print("Calculation failed or output files are missing.")
