import os
import subprocess
import glob
import sys

def run_py1_and_verify():
    """
    Run py1.py with resolution=0.0187 and verify if output files exist.
    Print "Calculation successful" if all files exist.
    """
    # Fixed resolution value as specified in the task
    resolution = 0.0187
    
    # Output directory
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T1S2\backup6"
    
    # Make sure output directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    print(f"Running py1.py with resolution={resolution}...")
    
    try:
        # Run py1.py with the resolution parameter
        cmd = [sys.executable, "py1.py", "-re", str(resolution)]
        print(f"Executing command: {' '.join(cmd)}")
        
        # Execute the command
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Get output
        stdout, stderr = process.communicate()
        
        # Print stdout for debugging
        if stdout:
            print("Output from py1.py:")
            print(stdout)
        
        # Check if there were any errors
        if stderr:
            print("Errors from py1.py:")
            print(stderr)
        
        # Check return code
        if process.returncode != 0:
            print(f"py1.py failed with return code {process.returncode}")
            return False
        
    except Exception as e:
        print(f"Error running py1.py: {e}")
        return False
    
    # Verify output files
    csv_analysis_files = glob.glob(os.path.join(output_directory, "*_gap_analysis.csv"))
    csv_height_files = glob.glob(os.path.join(output_directory, "*_gap_height.csv"))
    txt_files = glob.glob(os.path.join(output_directory, "*_statistics.txt"))
    png_files = glob.glob(os.path.join(output_directory, "*_highlighted.png"))
    
    print(f"Found {len(csv_analysis_files)} gap analysis CSV files")
    print(f"Found {len(csv_height_files)} gap height CSV files")
    print(f"Found {len(txt_files)} TXT files")
    print(f"Found {len(png_files)} highlighted PNG files")
    
    if csv_analysis_files and csv_height_files and txt_files and png_files:
        print("Calculation successful")
        return True
    else:
        print("Some output files are missing")
        return False

if __name__ == "__main__":
    # Run py1.py with fixed resolution value and verify outputs
    run_py1_and_verify()
