import os
import subprocess
import sys

def verify_outputs():
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T1S2\backup3"
    
    # Check if the output directory exists
    if not os.path.exists(output_directory):
        print("Output directory does not exist.")
        return False
    
    # Get a list of files in the output directory
    files = os.listdir(output_directory)
    
    # Check if there are any files with the expected extensions
    csv_files = [f for f in files if f.endswith("_gap_analysis.csv") or f.endswith("_gap_height.csv")]
    txt_files = [f for f in files if f.endswith("_stats.txt")]
    img_files = [f for f in files if f.endswith("_highlighted.png")]
    
    if csv_files and txt_files and img_files:
        print("Calculation successful")
        return True
    else:
        print("Some output files are missing.")
        print(f"CSV files: {len(csv_files)}")
        print(f"TXT files: {len(txt_files)}")
        print(f"Image files: {len(img_files)}")
        return False

if __name__ == "__main__":
    # Run py1.py with resolution parameter
    try:
        # Make sure to use the correct command line argument format
        subprocess.run([sys.executable, "py1.py", "--resolution=0.0187"], check=True)
        # Verify outputs
        verify_outputs()
    except subprocess.CalledProcessError as e:
        print(f"Error running py1.py: {e}")
