import os
import subprocess
import time

def run_py1_and_verify():
    # Paths and parameters
    images_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S2"
    re_value = 0.0187

    # Run py1.py in the background
    cmd = f'python py1.py -re={re_value}'
    print("Running py1.py in the background...")
    proc = subprocess.Popen(cmd, shell=True)
    proc.wait()  # Wait for completion

    # Allow a brief moment for files to flush/save
    time.sleep(1)

    # Check for expected output files
    success = False
    if os.path.exists(output_dir) and os.path.isdir(output_dir):
        files = os.listdir(output_dir)
        csv_files = [f for f in files if f.endswith('_gap_analysis.csv')]
        txt_files = [f for f in files if f.endswith('_gap_stat.txt')]
        img_files = [f for f in files if f.endswith('_gap_highlight.png')]
        if csv_files and txt_files and img_files:
            success = True

    if success:
        print("Calculation successful")
    else:
        print("Output files not found or incomplete.")

if __name__ == "__main__":
    run_py1_and_verify()
