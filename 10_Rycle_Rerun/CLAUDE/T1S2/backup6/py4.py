import os
import subprocess
import glob
import sys

def verify_outputs():
    """Verify if the output files from py1.py exist"""
    # Define output directory
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T1S2\backup6"
    
    # Check if the directory exists
    if not os.path.exists(output_directory):
        print(f"Output directory does not exist: {output_directory}")
        return False
    
    # Look for output files
    csv_analysis_files = glob.glob(os.path.join(output_directory, "*_gap_analysis.csv"))
    csv_height_files = glob.glob(os.path.join(output_directory, "*_gap_height.csv"))
    txt_files = glob.glob(os.path.join(output_directory, "*_statistics.txt"))
    png_files = glob.glob(os.path.join(output_directory, "*_highlighted.png"))
    
    # Print what we found
    print(f"Found {len(csv_analysis_files)} gap analysis CSV files")
    print(f"Found {len(csv_height_files)} gap height CSV files")
    print(f"Found {len(txt_files)} TXT files")
    print(f"Found {len(png_files)} highlighted PNG files")
    
    # Check if all types of files exist
    if csv_analysis_files and csv_height_files and txt_files and png_files:
        return True
    else:
        return False

def run_py1():
    """Run py1.py with resolution parameter"""
    resolution = 0.0187
    
    try:
        # Run py1.py with the resolution parameter
        print(f"Running py1.py with resolution={resolution}...")
        
        # Construct the command
        command = [sys.executable, "py1.py", "-re", str(resolution)]
        
        # Run the command
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Get output and error
        stdout, stderr = process.communicate()
        
        # Check if the command was successful
        if process.returncode != 0:
            print(f"Error running py1.py. Return code: {process.returncode}")
            print(f"Error message: {stderr}")
            return False
        
        print("py1.py executed successfully")
        return True
        
    except Exception as e:
        print(f"Exception while running py1.py: {str(e)}")
        return False

if __name__ == "__main__":
    # Run py1.py
    if run_py1():
        # Verify outputs
        if verify_outputs():
            print("Calculation successful")
        else:
            print("Calculation completed but some output files are missing")
    else:
        print("Failed to run py1.py")
