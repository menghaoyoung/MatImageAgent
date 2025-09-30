import os
import sys

def check_outputs_exist(output_dir, input_dir):
    # List all Li_*.png/jpg in input_dir
    input_images = [f for f in os.listdir(input_dir) if f.startswith("Li_") and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    success = True
    for img_name in input_images:
        img_base = os.path.splitext(img_name)[0]
        csv_name = f"{img_base}_gap_analysis.csv"
        img_out_name = f"{img_base}_gap_highlight.png"
        csv_path = os.path.join(output_dir, csv_name)
        img_out_path = os.path.join(output_dir, img_out_name)
        if not (os.path.isfile(csv_path) and os.path.isfile(img_out_path)):
            print(f"Missing output for {img_name}:")
            if not os.path.isfile(csv_path):
                print(f"  Missing CSV: {csv_path}")
            if not os.path.isfile(img_out_path):
                print(f"  Missing Highlight Image: {img_out_path}")
            success = False
    return success

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S1\backup9"

    # Run py1.py in the background
    # For safety, check if py1.py exists in current dir
    py1_path = os.path.join(os.getcwd(), "py1.py")
    if not os.path.isfile(py1_path):
        print("py1.py not found in the current directory.")
        sys.exit(1)

    # Use subprocess to run in the background
    import subprocess
    import time

    # Start py1.py
    process = subprocess.Popen(
        [sys.executable, py1_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False
    )

    print("py1.py is running in the background...")

    # Wait for py1.py to finish
    stdout, stderr = process.communicate()

    # Optionally print py1.py output for debugging
    print(stdout.decode())
    if stderr:
        print(stderr.decode())

    # After completion, check outputs
    all_ok = check_outputs_exist(output_directory, input_directory)
    if all_ok:
        print("Calculation successful")
    else:
        print("Calculation incomplete: some outputs are missing.")
