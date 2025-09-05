import os
import subprocess
import sys

def run_calculation():
    # Define the resolution
    resolution = 0.9
    
    # Define the output directory
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T2S2\1.0\backup"
    
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
    
    # Run py1.py with the specified resolution
    try:
        # Fix: Ensure the resolution argument is properly formatted
        cmd = [sys.executable, 'py1.py', f'-resolution={resolution}']
        print(f"Executing command: {' '.join(cmd)}")
        
        subprocess.run(cmd, check=True)
        print(f"Executed py1.py with resolution={resolution}")
        
        # Check if all expected files exist
        all_files_exist = True
        for file in expected_files:
            file_path = os.path.join(output_dir, file)
            if not os.path.exists(file_path):
                print(f"Missing file: {file}")
                all_files_exist = False
        
        if all_files_exist:
            print("Calculation successful")
        else:
            print("Some output files are missing")
            
    except subprocess.CalledProcessError as e:
        print(f"Error running py1.py: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    run_calculation()
