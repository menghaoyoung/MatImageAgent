import os
import subprocess

# Configuration
image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T2S2\1.0\backup3"
resolution = 1.2

# Get base filename
base_name = os.path.splitext(os.path.basename(image_path))[0]

# Expected output files
output_files = [
    f"{base_name}_gray_values.csv",
    f"{base_name}_length.txt",
    f"{base_name}_u_eq.csv",
    f"{base_name}_curve.tiff"
]

# Run py1.py with specified parameters
cmd = f'python py1.py -image_dir="{image_path}" -resolution={resolution}'
subprocess.call(cmd, shell=True)

# Verify file existence
all_exist = True
for file in output_files:
    if not os.path.exists(os.path.join(output_dir, file)):
        print(f"Missing file: {file}")
        all_exist = False

# Print final verification result
print("Calculation successful" if all_exist else "Verification failed")
