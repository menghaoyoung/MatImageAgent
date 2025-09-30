import os
import subprocess
import time

# Configuration parameters
INPUT_DIR = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
OUTPUT_DIR = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S2\backup2"
RE_VALUE = 0.0187

def verify_output_files():
    """Verify existence of required output files for all processed images"""
    # Get list of input images
    input_images = [f for f in os.listdir(INPUT_DIR) 
                   if f.startswith('Li_') and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    all_files_exist = True
    
    for img_file in input_images:
        base_name = os.path.splitext(img_file)[0]
        required_files = [
            f"{base_name}_gap_analysis.csv",
            f"{base_name}_gap_height.csv",
            f"{base_name}_gap_report.txt",
            f"{base_name}_gap_highlighted.png"
        ]
        
        # Check each required file
        for file_name in required_files:
            file_path = os.path.join(OUTPUT_DIR, file_name)
            if not os.path.exists(file_path):
                print(f"Missing file: {file_path}")
                all_files_exist = False
    
    return all_files_exist

def main():
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Run py1.py in the background
    print("Starting image processing in background...")
    process = subprocess.Popen(["python", "py1.py", f"-re={RE_VALUE}"])
    
    # Wait for processing to complete with timeout
    try:
        print("Waiting for processing to complete...")
        process.communicate(timeout=300)  # 5-minute timeout
    except subprocess.TimeoutExpired:
        print("Processing timed out after 5 minutes")
        process.kill()
        print("Calculation failed")
        return

    # Verify output files
    print("Verifying output files...")
    if verify_output_files():
        print("Calculation successful")
    else:
        print("Calculation failed - missing output files")

if __name__ == "__main__":
    main()
