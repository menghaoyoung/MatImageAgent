import os
import subprocess
import sys

def main():
    # Define output directory and expected files
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T2S2\1.0\backup5"
    base_filename = "Li_1.0"
    expected_files = [
        f"{base_filename}_gray_values.csv",
        f"{base_filename}_length.txt",
        f"{base_filename}_distance_ueq.csv",
        f"{base_filename}_ueq_curve.tiff"
    ]
    
    # Run py1.py with resolution=1.08 in background
    try:
        cmd = [sys.executable, "py1.py", "-resolution=1.08"]
        subprocess.run(cmd, check=True, capture_output=True)
        print("py1.py executed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error running py1.py: {e.stderr.decode()}")
        return
    
    # Verify all expected files exist
    all_files_exist = True
    for file in expected_files:
        file_path = os.path.join(output_dir, file)
        if not os.path.exists(file_path):
            print(f"Missing file: {file}")
            all_files_exist = False
    
    # Print final status
    if all_files_exist:
        print("Calculation successful")
    else:
        print("Calculation incomplete - missing output files")

if __name__ == "__main__":
    main()
