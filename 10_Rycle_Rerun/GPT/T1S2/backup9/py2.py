import os
import subprocess

def run_py1_and_check():
    # Define paths
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S2\backup9"
    re = 0.0187

    # Run py1.py in the background
    cmd = [
        "python", "py1.py",
        "-re={}".format(re),
        "--input={}".format(input_dir),
        "--output={}".format(output_dir)
    ]
    print("Running py1.py in background...")
    proc = subprocess.Popen(cmd)
    proc.wait()  # Wait for process to finish

    # Now check for existence of output files
    exist_flag = False
    found_csv = False
    found_gapheight = False
    found_txt = False
    found_img = False
    # Scan output directory for expected files
    if os.path.exists(output_dir):
        for fname in os.listdir(output_dir):
            # Check for per-pixel CSV
            if fname.startswith("Li_") and fname.endswith("_gap_analysis.csv"):
                found_csv = True
            # Check for gap height CSV
            if fname.startswith("Li_") and fname.endswith("_gap_height.csv"):
                found_gapheight = True
            # Check for TXT summary
            if fname.startswith("Li_") and fname.endswith("_gap_height.txt"):
                found_txt = True
            # Check for highlighted images
            if fname.startswith("Li_") and fname.endswith("_gap_highlighted.png"):
                found_img = True

    if found_csv and found_gapheight and found_txt and found_img:
        print("Calculation successful")
    else:
        print("Output files missing or incomplete!")

if __name__ == "__main__":
    run_py1_and_check()
