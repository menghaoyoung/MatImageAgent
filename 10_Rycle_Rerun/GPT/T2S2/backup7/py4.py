import os
import sys
import subprocess

def main():
    # Parameters (must match those in py1.py)
    image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
    out_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T2S2\1.0\backup7"
    resolution = "1.08"
    start_point = "152,29"
    end_point = "135,92"
    u_max = "65535"
    u_min = "0"

    filename_base = os.path.splitext(os.path.basename(image_path))[0]
    gray_csv = os.path.join(out_dir, f"{filename_base}_grayvalues.csv")
    length_txt = os.path.join(out_dir, f"{filename_base}_length.txt")
    ueq_csv = os.path.join(out_dir, f"{filename_base}_distance_ueq.csv")
    tiff_img = os.path.join(out_dir, f"{filename_base}_ueq_vs_distance.tiff")

    # Build the command with required arguments for py1.py
    cmd = [
        sys.executable, "py1.py",
        "-image_dir", image_path,
        "-resolution", resolution,
        "-out_dir", out_dir,
        "-u_max", u_max,
        "-u_min", u_min,
        "-start_point", start_point,
        "-end_point", end_point
    ]

    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if stdout:
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
