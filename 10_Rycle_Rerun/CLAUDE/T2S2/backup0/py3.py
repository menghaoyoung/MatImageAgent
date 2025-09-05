import os
import subprocess
import sys
import time

def run_and_verify():
    """
    Run py1.py with resolution=0.9 and verify if output files exist
    """
    # Set the resolution
    resolution = 0.9
    
    # Define the output directory
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T2S2\1.0\backup"
    os.makedirs(output_dir, exist_ok=True)
    
    # Define the image path to extract the base filename
    image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
    base_filename = os.path.splitext(os.path.basename(image_path))[0]
    
    # Expected output files
    expected_files = [
        f"{base_filename}_grayscale_values.csv",
        f"{base_filename}_line_length.txt",
        f"{base_filename}_u_eq_values.csv",
        f"{base_filename}_u_eq_curve.tiff"
    ]
    
    # Check if py1.py exists in the current directory
    if not os.path.exists("py1.py"):
        print("Error: py1.py not found in the current directory")
        return
    
    # Run py1.py with the specified resolution
    try:
        print(f"Running py1.py with resolution={resolution}...")
        
        # Run the command with proper argument format
        cmd = ["python", "py1.py", "-resolution", str(resolution)]
        process = subprocess.Popen(cmd, 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  text=True)
        
        # Wait for the process to complete
        stdout, stderr = process.communicate()
        
        # Check return code
        if process.returncode != 0:
            print(f"Error running py1.py: {stderr}")
            return
        
        print(f"py1.py execution completed with output:\n{stdout}")
        
        # Give some time for file system operations to complete
        time.sleep(1)
        
        # Check if all expected files exist
        missing_files = []
        for file in expected_files:
            file_path = os.path.join(output_dir, file)
            if not os.path.exists(file_path):
                missing_files.append(file)
        
        if missing_files:
            print(f"The following expected files are missing: {', '.join(missing_files)}")
        else:
            print("Calculation successful")
            
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    run_and_verify()
