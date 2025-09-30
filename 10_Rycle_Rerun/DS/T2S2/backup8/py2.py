import os
import subprocess
import sys

# Configuration parameters
output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T2S2\1.0\backup8"
image_name = "Li_1.0"
expected_files = [
    f"{image_name}_gray_values.csv",
    f"{image_name}_length.txt",
    f"{image_name}_u_eq.csv",
    f"{image_name}_curve.tiff"
]

def verify_outputs():
    """Check if all expected output files exist"""
    missing = [f for f in expected_files if not os.path.exists(os.path.join(output_dir, f))]
    return len(missing) == 0

if __name__ == "__main__":
    # Run py1.py with specified resolution
    cmd = [sys.executable, "py1.py", "-resolution=1.08"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Verify outputs and print result
    if verify_outputs():
        print("Calculation successful")
    else:
        print("Error: Missing output files")
        print(result.stderr)
