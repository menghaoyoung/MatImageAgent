import os
import subprocess
import glob

def run_py1_in_background(re_value):
    # Run py1.py in background with the specified resolution value
    # Use subprocess to capture output if needed
    cmd = ['python', 'py1.py', '-re={}'.format(re_value)]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    # Optionally print output for debugging
    print(stdout.decode())
    if process.returncode != 0:
        print(stderr.decode())
        print("py1.py execution failed.")
        return False
    return True

def check_outputs(output_dir):
    # Check for presence of required output files for each input image
    # They must match pattern: Li_*_gap_analysis.csv, _gap_height.csv, _gap_height.txt, _GAP.png
    found_any = False
    for fname in os.listdir(output_dir):
        if fname.startswith("Li_") and fname.endswith("_gap_analysis.csv"):
            img_basename = fname[:-len("_gap_analysis.csv")]
            # Build expected files
            expected = [
                os.path.join(output_dir, f"{img_basename}_gap_analysis.csv"),
                os.path.join(output_dir, f"{img_basename}_gap_height.csv"),
                os.path.join(output_dir, f"{img_basename}_gap_height.txt"),
                os.path.join(output_dir, f"{img_basename}_GAP.png"),
            ]
            if all(os.path.exists(f) for f in expected):
                found_any = True
            else:
                # If any expected file missing, print for debug
                for f in expected:
                    if not os.path.exists(f):
                        print(f"Missing: {f}")
    return found_any

if __name__ == "__main__":
    # Set re value as required
    re_value = 0.0187
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S2\backup8"

    # 1. Run py1.py in background
    run_py1_in_background(re_value)

    # 2. Check outputs
    if check_outputs(output_dir):
        print("Calculation successful")
    else:
        print("Output files not found or incomplete.")
