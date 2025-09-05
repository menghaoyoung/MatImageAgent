import os
import subprocess
import glob
import sys

def run_py1_and_verify():
    # Path to py1.py (assuming it's in the same directory as this script)
    py1_path = "py1.py"
    
    # Output directory where results will be saved
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T1S2\backup6"
    
    # Resolution parameter
    resolution = 0.0187
    
    print(f"Running py1.py with resolution={resolution}...")
    
    # Run py1.py with the resolution parameter
    try:
        # Use the full command that would be used from the command line
        command = [sys.executable, py1_path, "-re", str(resolution)]
        print(f"Executing command: {' '.join(command)}")
        
        # Run the command and capture output
        result = subprocess.run(command, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True,
                               check=False)
        
        # Print the output and error (if any)
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        # Check if the command was successful
        if result.returncode != 0:
            print(f"Error: py1.py exited with code {result.returncode}")
            return False
        
    except Exception as e:
        print(f"Error running py1.py: {e}")
        return False
    
    # Check if the output directory exists
    if not os.path.exists(output_directory):
        print("Output directory does not exist.")
        return False
    
    # Look for CSV files, TXT files, and PNG images
    csv_files = glob.glob(os.path.join(output_directory, "*_gap_analysis.csv"))
    height_csv_files = glob.glob(os.path.join(output_directory, "*_gap_height.csv"))
    txt_files = glob.glob(os.path.join(output_directory, "*_statistics.txt"))
    png_files = glob.glob(os.path.join(output_directory, "*_highlighted.png"))
    
    # Check if files exist
    if csv_files and height_csv_files and txt_files and png_files:
        print("Calculation successful")
        return True
    else:
        print("Some output files are missing.")
        print(f"Found {len(csv_files)} gap analysis CSV files")
        print(f"Found {len(height_csv_files)} gap height CSV files")
        print(f"Found {len(txt_files)} TXT files")
        print(f"Found {len(png_files)} highlighted PNG files")
        return False

if __name__ == "__main__":
    run_py1_and_verify()
