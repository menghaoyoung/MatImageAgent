import os
import subprocess
import sys

def main():
    # Define paths from the task description
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1\backup3"
    script_path = "py1.py"

    # Run py1.py in the background
    try:
        process = subprocess.Popen(
            [sys.executable, script_path, input_dir],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print(f"Running py1.py in background (PID: {process.pid})...")
        
        # Wait for the process to complete
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Error running py1.py (exit code: {process.returncode})")
            print("Error output:", stderr.decode())
            return
    except Exception as e:
        print(f"Failed to execute py1.py: {str(e)}")
        return

    # Verify output files
    all_files_exist = True
    processed_images = 0
    
    for filename in os.listdir(input_dir):
        if filename.startswith("Li_") and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            base_name = os.path.splitext(filename)[0]
            csv_file = f"{base_name}_gap_analysis.csv"
            png_file = f"{base_name}_gap_highlight.png"
            
            csv_path = os.path.join(output_dir, csv_file)
            png_path = os.path.join(output_dir, png_file)
            
            if not os.path.exists(csv_path):
                print(f"Missing CSV file: {csv_path}")
                all_files_exist = False
                
            if not os.path.exists(png_path):
                print(f"Missing PNG file: {png_path}")
                all_files_exist = False
                
            if os.path.exists(csv_path) and os.path.exists(png_path):
                processed_images += 1

    # Print final verification result
    if all_files_exist:
        print(f"Success: Verified {processed_images} image sets")
        print("Calculation successful")
    else:
        print("Verification failed: Some output files are missing")

if __name__ == "__main__":
    main()
