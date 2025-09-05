import os
import subprocess
import time

def run_and_verify():
    # Define the output directory
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T2S2\1.0\backup1"
    
    # Get the base filename of the image
    image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
    filename_base = os.path.splitext(os.path.basename(image_path))[0]
    
    # Expected output files
    expected_files = [
        f"{filename_base}_line_length.txt",
        f"{filename_base}_grayscale_values.csv",
        f"{filename_base}_distance_u_eq.csv",
        f"{filename_base}_u_eq_plot.tiff"
    ]
    
    # Run py1.py with resolution 0.9
    print("Running py1.py with resolution 0.9...")
    try:
        subprocess.run(["python", "py1.py", "-resolution=0.9"], check=True)
        
        # Wait a moment to ensure files are written
        time.sleep(2)
        
        # Verify that all expected files exist
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

if __name__ == "__main__":
    run_and_verify()
