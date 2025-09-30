import os
import subprocess
import sys

def main():
    # Parameters and paths
    image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T2S2\1.0\backup9"
    script_path = "py1.py"
    resolution = "1.08"

    # Run py1.py in the background with required arguments
    cmd = [
        sys.executable, script_path,
        "-image_dir", image_path,
        "-out_dir", output_dir,
        "-resolution", resolution
    ]
    # Run process and wait for completion
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # Output files to check
    img_filename = os.path.splitext(os.path.basename(image_path))[0]
    csv_gray = os.path.join(output_dir, f"{img_filename}_line_gray.csv")
    txt_len = os.path.join(output_dir, f"{img_filename}_line_length.txt")
    csv_u_eq = os.path.join(output_dir, f"{img_filename}_distance_u_eq.csv")
    tiff_plot = os.path.join(output_dir, f"{img_filename}_u_eq_curve.tiff")

    # Check if all files exist
    all_exist = True
    output_files = [csv_gray, txt_len, csv_u_eq, tiff_plot]
    for f in output_files:
        if not os.path.exists(f):
            all_exist = False
            print(f"Missing: {f}")

    if all_exist:
        print("Calculation successful")

if __name__ == '__main__':
    main()
