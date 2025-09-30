import os
import subprocess

# Configuration - same as previous step
input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S2\backup7"

def verify_output_files():
    """Check existence of required output files for all processed images"""
    # Get all input images with Li_ prefix
    input_images = [f for f in os.listdir(input_dir) 
                   if f.startswith("Li_") and f.lower().endswith(('.png', '.jpg'))]
    
    missing_files = []
    
    # Check outputs for each image
    for img in input_images:
        base_name = os.path.splitext(img)[0]
        required_files = [
            f"{base_name}_gap_analysis.csv",
            f"{base_name}_gap_height.csv",
            f"{base_name}_info.txt",
            f"{base_name}_gap_highlight.png"
        ]
        
        # Verify each required file exists
        for f in required_files:
            if not os.path.exists(os.path.join(output_dir, f)):
                missing_files.append(f"Missing: {f} for {img}")
    
    return missing_files

if __name__ == "__main__":
    # Run py1.py with specified resolution
    result = subprocess.run(
        ["python", "py1.py", "-re=0.0187"],
        capture_output=True,
        text=True
    )
    
    # Check process exit status
    if result.returncode != 0:
        print(f"Execution failed with error:\n{result.stderr}")
    else:
        # Verify output files
        missing = verify_output_files()
        if not missing:
            print("Calculation successful")
        else:
            print("Missing output files:")
            for item in missing:
                print(f"- {item}")
