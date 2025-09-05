import os
import subprocess
import time

# Output directory and expected files
output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T2S2\1.0\backup4"
image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
image_filename = os.path.splitext(os.path.basename(image_path))[0]

# Expected output files
expected_files = [
    f"{image_filename}_gray_values.csv",
    f"{image_filename}_line_length.txt",
    f"{image_filename}_distance_u_eq.csv",
    f"{image_filename}_u_eq_curve.tiff"
]
expected_paths = [os.path.join(output_dir, fname) for fname in expected_files]

def run_py1():
    # Run py1.py in the background with the required argument
    command = ["python", "py1.py", "-resolution=1.08"]
    subprocess.Popen(command)
    # Give some time for the process to finish (depends on image size, increase if needed)
    time.sleep(10)

def check_outputs():
    # Check if all expected files exist
    all_exist = True
    for path in expected_paths:
        if not os.path.exists(path):
            print(f"Missing output: {path}")
            all_exist = False
    if all_exist:
        print("Calculation successful")
    else:
        print("Calculation failed (some files missing)")

if __name__ == "__main__":
    run_py1()
    check_outputs()
