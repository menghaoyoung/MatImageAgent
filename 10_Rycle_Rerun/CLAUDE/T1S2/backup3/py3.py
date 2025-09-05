import os
import subprocess
import sys
import time

def verify_outputs():
    """Verify if the output files from py1.py exist"""
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T1S2\backup3"
    
    # Check if the output directory exists
    if not os.path.exists(output_directory):
        print(f"Output directory {output_directory} does not exist.")
        return False
    
    # Get a list of files in the output directory
    try:
        files = os.listdir(output_directory)
    except Exception as e:
        print(f"Error accessing output directory: {e}")
        return False
    
    # Check if there are any files with the expected extensions
    gap_analysis_csv_files = [f for f in files if f.endswith("_gap_analysis.csv")]
    gap_height_csv_files = [f for f in files if f.endswith("_gap_height.csv")]
    txt_files = [f for f in files if f.endswith("_stats.txt")]
    img_files = [f for f in files if f.endswith("_highlighted.png")]
    
    print(f"Found {len(gap_analysis_csv_files)} gap analysis CSV files")
    print(f"Found {len(gap_height_csv_files)} gap height CSV files")
    print(f"Found {len(txt_files)} TXT files")
    print(f"Found {len(img_files)} highlighted image files")
    
    if gap_analysis_csv_files and gap_height_csv_files and txt_files and img_files:
        return True
    else:
        return False

if __name__ == "__main__":
    # Check if py1.py exists in the current directory
    if not os.path.exists("py1.py"):
        print("Error: py1.py not found in the current directory")
        sys.exit(1)
    
    # Run py1.py with resolution parameter
    print("Running py1.py with resolution 0.0187...")
    start_time = time.time()
    
    try:
        # Use subprocess to run py1.py
        # For argparse, we need to separate the argument name and value
        process = subprocess.run([sys.executable, "py1.py", "-re", "0.0187"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE,
                                 text=True,
                                 check=True)
        
        # Print the output from py1.py
        if process.stdout:
            print("Output from py1.py:")
            print(process.stdout)
        
        # Print any errors
        if process.stderr:
            print("Errors from py1.py:")
            print(process.stderr)
        
        end_time = time.time()
        print(f"py1.py execution completed in {end_time - start_time:.2f} seconds")
        
        # Verify the outputs
        print("Verifying output files...")
        if verify_outputs():
            print("Calculation successful")
        else:
            print("Calculation failed: Some expected output files are missing")
            
    except subprocess.CalledProcessError as e:
        print(f"Error running py1.py: {e}")
        if e.stdout:
            print("Output:")
            print(e.stdout)
        if e.stderr:
            print("Error output:")
            print(e.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
