import os
import subprocess
import time

# File paths and names
output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T2S2\1.0\backup6"
image_filename = "Li_1.0"
gray_csv = os.path.join(output_dir, f"{image_filename}_line_grayscale.csv")
length_txt = os.path.join(output_dir, f"{image_filename}_line_length.txt")
dist_ueq_csv = os.path.join(output_dir, f"{image_filename}_distance_u_eq.csv")
tiff_img = os.path.join(output_dir, f"{image_filename}_u_eq_curve.tiff")
py1_path = "py1.py"

def file_exists(filepath):
    return os.path.isfile(filepath)

def main():
    # Run py1.py with required arguments (background)
    cmd = [
        "python", py1_path,
        "-image_dir", r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png",
        "-output_dir", output_dir,
        "-resolution", "1.08",
        "--start", "152", "29",
        "--end", "135", "92",
        "-u_max", "65535",
        "-u_min", "0"
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Wait for completion (or adjust time as needed)
    process.wait(timeout=180)

    # Give the system a moment for file writing
    time.sleep(2)

    # Check existence of all required output files
    if (
        file_exists(gray_csv) and
        file_exists(length_txt) and
        file_exists(dist_ueq_csv) and
        file_exists(tiff_img)
    ):
        print("Calculation successful")
    else:
        print("Calculation failed")

if __name__ == "__main__":
    main()
