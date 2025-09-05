import os
import subprocess

def check_files_exist(base_dir, base_name):
    files_needed = [
        f"{base_name}_line_gray.csv",
        f"{base_name}_line_length.txt",
        f"{base_name}_line_u_eq.csv",
        f"{base_name}_u_eq_vs_distance.tiff"
    ]
    all_exist = True
    for fname in files_needed:
        fpath = os.path.join(base_dir, fname)
        if not os.path.exists(fpath):
            print(f"Missing: {fpath}")
            all_exist = False
    return all_exist

def main():
    # Set image base name and output dir per previous step
    image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T2S2\1.0\backup"
    base_name = os.path.splitext(os.path.basename(image_path))[0]

    # 1. Run py1.py in the background for resolution=0.9
    print("Running py1.py with resolution=0.9 ...")
    proc = subprocess.Popen(
        ['python', 'py1.py', '-resolution=0.9'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    stdout, stderr = proc.communicate()
    print("py1.py output:")
    print(stdout)
    if proc.returncode != 0:
        print(f"py1.py failed with error:\n{stderr}")
        return

    # 2. Check if output files exist
    if check_files_exist(output_dir, base_name):
        print("Calculation successful")
    else:
        print("Calculation failed: One or more output files missing.")

if __name__ == "__main__":
    main()
