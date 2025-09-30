import os
import subprocess
import time

def run_py1_in_background():
    """Run py1.py in background with specified resolution."""
    command = ["python", "py1.py", "-re=0.0187"]
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return process

def verify_output_files(input_dir, output_dir):
    """Check if all required output files exist."""
    input_images = [f for f in os.listdir(input_dir) 
                  if f.startswith("Li_") and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    all_files_exist = True
    missing_files = []
    
    for img in input_images:
        base_name = os.path.splitext(img)[0]
        required_files = [
            f"{base_name}_gap_analysis.csv",
            f"{base_name}_gap_height.csv",
            f"{base_name}_gap_highlight.png",
            f"{base_name}_gap_info.txt"
        ]
        
        for file in required_files:
            file_path = os.path.join(output_dir, file)
            if not os.path.exists(file_path):
                all_files_exist = False
                missing_files.append(file_path)
    
    return all_files_exist, missing_files

if __name__ == "__main__":
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S2\backup8"
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print("Running py1.py in background with re=0.0187...")
    process = run_py1_in_background()
    
    # Wait for process to complete
    stdout, stderr = process.communicate()
    
    if process.returncode != 0:
        print(f"Error in py1.py execution:\n{stderr.decode()}")
    else:
        print("py1.py completed. Verifying output files...")
        success, missing = verify_output_files(input_dir, output_dir)
        
        if success:
            print("Calculation successful")
        else:
            print("Missing files detected:")
            for file in missing:
                print(f"- {file}")
