import os
import subprocess
import sys

# Configuration parameters
IMAGE_PATH = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
OUTPUT_DIR = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T2S2\1.0\backup1"
BASE_NAME = os.path.splitext(os.path.basename(IMAGE_PATH))[0]  # "Li_1.0"

# Expected output files
REQUIRED_FILES = [
    f"{BASE_NAME}_grayscale.csv",
    f"{BASE_NAME}_length.txt",
    f"{BASE_NAME}_data.csv",
    f"{BASE_NAME}_plot.tiff"
]

def verify_files():
    """Check if all required output files exist"""
    missing_files = []
    for filename in REQUIRED_FILES:
        if not os.path.exists(os.path.join(OUTPUT_DIR, filename)):
            missing_files.append(filename)
    
    return missing_files

def main():
    # Create output directory if missing
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Run py1.py with resolution=0.9
    try:
        subprocess.run(
            ["python", "py1.py", "-resolution=0.9"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        print(f"Error running py1.py: {e.stderr.decode()}")
        sys.exit(1)
    
    # File verification
    missing = verify_files()
    if not missing:
        print("Calculation successful")
    else:
        print(f"Missing files: {', '.join(missing)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
