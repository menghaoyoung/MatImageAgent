import os
import subprocess
import time

# Define the expected output directory and base filename
output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T2S2\1.0\backup5"
image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
base_filename = os.path.splitext(os.path.basename(image_path))[0]

# Output files to check
expected_files = [
    f"{base_filename}_line_gray.csv",
    f"{base_filename}_line_length.txt",
    f"{base_filename}_line_ueq.csv",
    f"{base_filename}_ueq_curve.tiff"
]
expected_files = [os.path.join(output_dir, f) for f in expected_files]

# Build command to run py1.py with appropriate arguments
run_cmd = [
    "python", "py1.py",
    "-image_dir", image_path,
    "-output_dir", output_dir,
    "-start", "152", "29",
    "-end", "135", "92",
    "-resolution", "1.08",
    "-u_max", "65535",
    "-u_min", "0"
]

# Run py1.py in the background and wait for it to finish
process = subprocess.Popen(run_cmd)
process.wait(timeout=60)  # Wait up to 60 seconds

# Allow a short wait for file writing
time.sleep(2)

files_exist = all([os.path.exists(f) for f in expected_files])

if files_exist:
    print("Calculation successful")
else:
    print("Calculation failed: Some output files are missing.")
