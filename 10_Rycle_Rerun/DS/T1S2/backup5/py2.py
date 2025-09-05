import os
import subprocess
import sys

def run_analysis():
    """Run py1.py in the background with re=0.0187 and verify outputs"""
    # Define paths from the task description
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S2\backup5"
    
    # Run the analysis script in the background
    cmd = [sys.executable, "py1.py", "-re=0.0187"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # Check if process completed successfully
    if process.returncode != 0:
        print(f"Error running analysis: {stderr.decode()}")
        return False

    # Verify expected output files exist
    required_files = []
    for filename in os.listdir(r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"):
        if filename.startswith("Li_") and filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            base = os.path.splitext(filename)[0]
            required_files.extend([
                f"{base}_gap_analysis.csv",
                f"{base}_gap_height.csv",
                f"{base}_gap_report.txt",
                f"{base}_gap_highlight.png"
            ])
    
    # Check if all required files exist in output directory
    all_exist = True
    for fname in required_files:
        if not os.path.exists(os.path.join(output_dir, fname)):
            all_exist = False
            break
    
    # Return verification result
    return all_exist

if __name__ == "__main__":
    success = run_analysis()
    if success:
        print("Calculation successful")
    else:
        print("Verification failed - some output files missing")

# NO-RUN-PY
