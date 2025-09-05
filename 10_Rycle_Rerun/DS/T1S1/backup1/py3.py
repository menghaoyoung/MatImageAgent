# py2.py: Execute py1.py and verify output files
import os
import sys
import subprocess
import time

def verify_output_files(output_dir):
    """Verify existence of CSV and image files for each input image"""
    input_images = [
        f for f in os.listdir(input_dir) 
        if f.startswith("Li_") and f.lower().endswith(('.png', '.jpg', '.jpeg'))
    ]
    
    all_files_exist = True
    for img_file in input_images:
        base_name = os.path.splitext(img_file)[0]
        csv_file = f"{base_name}_gap_analysis.csv"
        png_file = f"{base_name}_gap_highlighted.png"
        
        csv_path = os.path.join(output_dir, csv_file)
        png_path = os.path.join(output_dir, png_file)
        
        if not os.path.exists(csv_path):
            print(f"Missing CSV file: {csv_path}")
            all_files_exist = False
        if not os.path.exists(png_path):
            print(f"Missing image file: {png_path}")
            all_files_exist = False
    
    return all_files_exist

if __name__ == "__main__":
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1"

    # Execute py1.py in the background
    print("Starting image processing with py1.py...")
    process = subprocess.Popen([sys.executable, "py1.py"])
    
    # Monitor process with timeout
    timeout = 300  # 5 minutes
    start_time = time.time()
    while process.poll() is None:
        if time.time() - start_time > timeout:
            print("Processing timed out!")
            process.terminate()
            sys.exit(1)
        time.sleep(5)
    
    # Verify outputs exist
    print("Verifying output files...")
    if verify_output_files(output_dir):
        print("Calculation successful")
    else:
        print("Error: Some output files are missing")
        sys.exit(1)
