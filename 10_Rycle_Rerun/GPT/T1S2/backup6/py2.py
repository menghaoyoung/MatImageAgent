import os
import subprocess
import sys

def run_py1():
    # Path to py1.py
    py1_path = os.path.abspath("py1.py")
    # Set the command; background run (no wait)
    cmd = [sys.executable, py1_path, "-re=0.0187"]
    try:
        # Run in background, suppress output
        # For windows, creationflags to hide window
        creationflags = 0
        if os.name == 'nt':
            creationflags = subprocess.CREATE_NO_WINDOW

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=creationflags
        )
        # Wait for completion
        proc.wait(timeout=600)
        out, err = proc.communicate()
        if proc.returncode != 0:
            print(f"py1.py failed: {err.decode(errors='ignore')}")
            return False
        return True
    except Exception as e:
        print(f"Error running py1.py: {e}")
        return False

def check_outputs():
    # Output directory
    outdir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S2\backup7"
    if not os.path.isdir(outdir):
        return False
    found_csv = found_txt = found_img = False
    for fname in os.listdir(outdir):
        if fname.endswith("_gap_analysis.csv"):
            found_csv = True
        if fname.endswith("_gap_height.csv"):
            found_csv = True
        if fname.endswith("_gap_result.txt"):
            found_txt = True
        if fname.endswith("GAP_highlighted.png"):
            found_img = True
    return found_csv and found_txt and found_img

if __name__ == "__main__":
    # Step 1: Run py1.py
    success = run_py1()
    if not success:
        print("Calculation failed")
        sys.exit(1)
    # Step 2: Check output files
    if check_outputs():
        print("Calculation successful")
    else:
        print("Calculation failed: Output files not found")
