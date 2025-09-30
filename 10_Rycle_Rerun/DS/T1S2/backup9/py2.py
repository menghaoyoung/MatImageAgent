import os
import subprocess
import sys
import time

def verify_outputs(output_dir):
    """Verify existence of output files for all processed images"""
    required_suffixes = [
        "_gap_analysis.csv",
        "_gap_height.csv",
        "_gap_highlighted.png",
        "_stats.txt"
    ]
    
    all_files_exist = True
    for img_file in os.listdir(input_dir):
        if not img_file.startswith("Li_"):
            continue
            
        base_name = os.path.splitext(img_file)[0]
        for suffix in required_suffixes:
            file_path = os.path.join(output_dir, f"{base_name}{suffix}")
            if not os.path.exists(file_path):
                print(f"Missing file: {file_path}")
                all_files_exist = False
    
    return all_files_exist

if __name__ == "__main__":
    # Configuration (match paths in py1.py)
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S2\backup9"
    
    # Run py1.py in background
    cmd = [sys.executable, "py1.py", "-re=0.0187"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    print("Processing images in background...")
    time.sleep(2)  # Allow process to start
    
    # Wait for completion with timeout
    try:
        stdout, stderr = process.communicate(timeout=300)
        if process.returncode != 0:
            print(f"Error running py1.py:\n{stderr.decode()}")
            sys.exit(1)
    except subprocess.TimeoutExpired:
        print("Processing timed out after 5 minutes")
        sys.exit(1)
    
    # Verify outputs
    if verify_outputs(output_dir):
        print("Calculation successful")
    else:
        print("Error: Some output files are missing")
        sys.exit(1)
