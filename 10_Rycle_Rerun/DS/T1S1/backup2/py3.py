import os
import subprocess
import sys
import time

def verify_output_files(output_dir):
    """Check if both CSV and PNG files exist for each processed image."""
    files = os.listdir(output_dir)
    csv_files = [f for f in files if f.endswith('_gap_analysis.csv')]
    png_files = [f for f in files if f.endswith('_gap_highlight.png')]
    
    # Check matching pairs
    missing_files = []
    for csv in csv_files:
        base = csv.replace('_gap_analysis.csv', '')
        if f"{base}_gap_highlight.png" not in png_files:
            missing_files.append(base)
    
    return len(missing_files) == 0

def main():
    # Configure paths
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1\backup2"
    script_path = "py1.py"
    
    # Run py1.py with input directory argument
    print("Starting image processing...")
    result = subprocess.run(
        [sys.executable, script_path, input_dir],
        capture_output=True,
        text=True
    )
    
    # Check execution status
    if result.returncode != 0:
        print(f"Processing failed with error:\n{result.stderr}")
        return
    
    print("Processing completed. Verifying output files...")
    time.sleep(2)  # Allow time for file system updates
    
    # Verify outputs
    if verify_output_files(output_dir):
        print("Calculation successful")
    else:
        print("Error: Missing output files for some images")
        print("Expected files:")
        files = os.listdir(input_dir)
        li_images = [f for f in files if f.startswith("Li_") and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        for img in li_images:
            base = os.path.splitext(img)[0]
            print(f"  - {base}_gap_analysis.csv")
            print(f"  - {base}_gap_highlight.png")

if __name__ == "__main__":
    main()
