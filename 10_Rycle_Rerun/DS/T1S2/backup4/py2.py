import os
import subprocess
from pathlib import Path

# Configuration
input_dir = Path(r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images")
output_dir = Path(r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S2\backup4")
resolution = 0.0187

# Execute py1.py in background
print(f"Executing py1.py with resolution {resolution}...")
subprocess.run(['python', 'py1.py', f'-re={resolution}'], check=True)

# Verify output files exist
print("Verifying output files...")
all_files_exist = True
for img_file in input_dir.glob("Li_*"):
    if img_file.suffix.lower() not in ('.png', '.jpg', '.jpeg'):
        continue
        
    base_name = img_file.stem
    required_files = [
        output_dir / f"{base_name}_gap_analysis.csv",
        output_dir / f"{base_name}_gap_height.csv",
        output_dir / f"{base_name}_gap_info.txt",
        output_dir / f"{base_name}_gap_highlighted.png"
    ]
    
    for f in required_files:
        if not f.exists():
            print(f"Missing file: {f.name}")
            all_files_exist = False

if all_files_exist:
    print("Calculation successful")
else:
    print("Calculation completed with missing files")
