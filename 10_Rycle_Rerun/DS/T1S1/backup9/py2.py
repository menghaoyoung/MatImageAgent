# run_verification.py
import os
import subprocess
import sys

def main():
    # Path configuration
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1\backup9"
    
    # Run py1.py in background
    cmd = f'start /B python py1.py "{input_dir}"'
    subprocess.run(cmd, shell=True)
    
    # Wait for processing completion
    time.sleep(5)  # Allow time for file operations
    
    # Verify outputs
    success = True
    for fname in os.listdir(input_dir):
        if fname.startswith("Li_") and fname.lower().endswith(('.png', '.jpg', '.jpeg')):
            base = os.path.splitext(fname)[0]
            csv_file = os.path.join(output_dir, f"{base}_gap_analysis.csv")
            img_file = os.path.join(output_dir, f"{base}_gap_highlighted.png")
            
            if not (os.path.exists(csv_file) and os.path.exists(img_file)):
                success = False
                break
    
    print("Calculation successful" if success else "Output verification failed")

if __name__ == "__main__":
    import time
    main()
