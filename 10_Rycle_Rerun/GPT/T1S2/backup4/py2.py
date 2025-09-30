import os
import subprocess

# Set paths as specified
input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S2\backup4"

def run_py1_and_verify(re_value=0.0187):
    # Step 1: Run py1.py in the background
    print("Running py1.py in the background...")
    run_cmd = f'python py1.py -re={re_value}'
    # Run in background and wait for completion
    process = subprocess.Popen(run_cmd, shell=True)
    process.wait()

    # Step 2: Check output directory for required files
    files = os.listdir(output_directory)
    found_gap_csv = False
    found_height_csv = False
    found_stats_txt = False
    found_highlight_img = False

    for f in files:
        if f.startswith("Li_") and f.endswith("_gap_analysis.csv"):
            found_gap_csv = True
        elif f.startswith("Li_") and f.endswith("_gap_height.csv"):
            found_height_csv = True
        elif f.startswith("Li_") and f.endswith("_gap_height_stats.txt"):
            found_stats_txt = True
        elif f.startswith("Li_") and f.endswith("_gap_highlight.png"):
            found_highlight_img = True

    # Step 3: Print result
    if all([found_gap_csv, found_height_csv, found_stats_txt, found_highlight_img]):
        print("Calculation successful")
    else:
        print("Calculation failed")
        if not found_gap_csv:
            print("Missing gap analysis CSV file.")
        if not found_height_csv:
            print("Missing gap height CSV file.")
        if not found_stats_txt:
            print("Missing stats TXT file.")
        if not found_highlight_img:
            print("Missing highlighted PNG image.")

if __name__ == "__main__":
    run_py1_and_verify(re_value=0.0187)
