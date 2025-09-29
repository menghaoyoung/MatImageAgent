import os
import subprocess
import time

def verify_outputs():
    # Path configurations
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1\backup5"
    
    # Get all input image names
    input_files = [f for f in os.listdir(input_dir) 
                  if f.startswith("Li_") and f.lower().endswith(('.png', '.jpg'))]
    
    # Expected output filenames
    expected_csvs = {f"{os.path.splitext(f)[0]}_gap_analysis.csv" for f in input_files}
    expected_imgs = {f"{os.path.splitext(f)[0]}_gap.png" for f in input_files}
    
    # Run py1.py as subprocess
    process = subprocess.Popen(['python', 'py1.py'], stdout=subprocess.PIPE)
    time.sleep(5)  # Allow time for processing
    
    # Check output directory contents
    existing_files = set(os.listdir(output_dir))
    
    # Validate outputs
    csv_missing = expected_csvs - existing_files
    img_missing = expected_imgs - existing_files
    
    # Final verification
    if not csv_missing and not img_missing:
        print("Calculation successful")
    else:
        print(f"Missing CSV files: {csv_missing}" if csv_missing else "")
        print(f"Missing images: {img_missing}" if img_missing else "")

if __name__ == "__main__":
    verify_outputs()
