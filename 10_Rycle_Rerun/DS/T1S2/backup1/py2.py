import os
import subprocess
import sys

def run_py1_and_verify():
    """Run py1.py with specified resolution and verify output files."""
    # Define parameters
    resolution = 0.0187
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S2\backup1"
    
    # Run py1.py in background
    cmd = f'python py1.py -re={resolution}'
    subprocess.run(cmd, shell=True, check=True)
    
    # Verify outputs for each image
    all_files_exist = True
    for filename in os.listdir(input_dir):
        if filename.startswith("Li_") and (filename.lower().endswith(('.png', '.jpg'))):
            base_name = os.path.splitext(filename)[0]
            
            # Check required output files
            required_files = [
                f"{base_name}_gap_analysis.csv",
                f"{base_name}_gap_height.csv",
                f"{base_name}_gap_highlight.png",
                f"{base_name}_gap_info.txt"
            ]
            
            # Verify existence
            for f in required_files:
                if not os.path.exists(os.path.join(output_dir, f)):
                    print(f"Missing file: {f}")
                    all_files_exist = False
    
    # Final verification
    if all_files_exist:
        print("Calculation successful")
    else:
        print("Output verification failed")

if __name__ == "__main__":
    run_py1_and_verify()
