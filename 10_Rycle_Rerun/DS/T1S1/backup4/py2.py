import subprocess
import os
import time
import sys

def verify_output_files(output_dir):
    """Verify that CSV and highlighted PNG files exist for all Li_ images"""
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    all_files_exist = True
    missing_files = []

    for filename in os.listdir(input_dir):
        if filename.startswith("Li_") and (filename.lower().endswith('.png') or filename.lower().endswith('.jpg')):
            base_name = os.path.splitext(filename)[0]
            csv_file = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
            png_file = os.path.join(output_dir, f"{base_name}_gap_highlighted.png")
            
            if not os.path.exists(csv_file):
                all_files_exist = False
                missing_files.append(csv_file)
            if not os.path.exists(png_file):
                all_files_exist = False
                missing_files.append(png_file)
    
    return all_files_exist, missing_files

if __name__ == "__main__":
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1\backup4"
    
    # Run py1.py in the background
    process = subprocess.Popen(["python", "py1.py"])
    
    # Wait for processing to complete with timeout
    try:
        print("Processing images...")
        process.communicate(timeout=300)  # 5-minute timeout
    except subprocess.TimeoutExpired:
        process.kill()
        print("Processing timed out after 5 minutes")
        sys.exit(1)
    
    # Verify output files
    success, missing = verify_output_files(output_dir)
    if success:
        print("Calculation successful")
    else:
        print(f"Missing {len(missing)} output files:")
        for file in missing:
            print(f"- {file}")
        sys.exit(1)
