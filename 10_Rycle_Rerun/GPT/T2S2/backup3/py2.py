import os
import subprocess
import time

# Paths and filenames based on previous step and task
output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T2S2\1.0\backup3"
base_filename = "Li_1.0"
csv_gray = os.path.join(output_dir, f"{base_filename}_gray_values.csv")
txt_length = os.path.join(output_dir, f"{base_filename}_length.txt")
csv_ueq = os.path.join(output_dir, f"{base_filename}_μeq_values.csv")
tiff_ueq = os.path.join(output_dir, f"{base_filename}_μeq_curve.tiff")

# Step 1: Run py1.py in the background with specified resolution
py_script = "py1.py"
cmd = [
    "python", py_script,
    "-resolution=1.08",
    "-image_dir", r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png",
    "-output_dir", output_dir
]

# Launch the process in the background and wait for it to finish
process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
stdout, stderr = process.communicate()

# Step 2: Check if all output files exist
all_exist = True
for f in [csv_gray, txt_length, csv_ueq, tiff_ueq]:
    if not os.path.exists(f):
        all_exist = False

if all_exist:
    print("Calculation successful")
else:
    print("Output files missing. Calculation failed.")

# Note: This program should be run in the directory containing py1.py
