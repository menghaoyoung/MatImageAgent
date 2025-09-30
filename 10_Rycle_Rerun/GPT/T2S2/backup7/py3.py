import os
import sys
import subprocess

def main():
    # Parameters
    image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
    out_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T2S2\1.0\backup7"
    filename_base = os.path.splitext(os.path.basename(image_path))[0]
    # Expected output files
    gray_csv = os.path.join(out_dir, f"{filename_base}_grayvalues.csv")
    length_txt = os.path.join(out_dir, f"{filename_base}_length.txt")
    ueq_csv = os.path.join(out_dir, f"{filename_base}_distance_ueq.csv")
    tiff_img = os.path.join(out_dir, f"{filename_base}_ueq_vs_distance.tiff")

    # Run py1.py in background with resolution=1.08
    cmd = [
        sys.executable, "py1.py"
    ]
    # py1.py in this context uses hardcoded parameters, so direct execution is sufficient.
    # If py1.py required CLI args, you would add them here.

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print(stdout.decode("utf-8"))
        if stderr:
            print(stderr.decode("utf-8"), file=sys.stderr)
    except Exception as e:
        print(f"Error running py1.py: {e}")
        sys.exit(1)

    # Check if all required files exist
    files_exist = all([os.path.exists(f) for f in [gray_csv, length_txt, ueq_csv, tiff_img]])
    if files_exist:
        print("Calculation successful")
    else:
        print("Calculation failed: Some output files are missing.")
        missing = [f for f in [gray_csv, length_txt, ueq_csv, tiff_img] if not os.path.exists(f)]
        print("Missing files:", missing)

if __name__ == '__main__':
    main()
