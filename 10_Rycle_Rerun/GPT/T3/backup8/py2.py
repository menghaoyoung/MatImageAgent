import os
import glob

def check_outputs_exist(output_dir, input_dir):
    """
    For each image in input_dir starting with 'Poly_', check that both
    '{name}_gap_analysis.csv' and '{name}_gap_map.png' exist in output_dir.
    """
    input_imgs = [f for f in os.listdir(input_dir)
                  if f.startswith('Poly_') and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not input_imgs:
        print("No Poly_*.png/jpg images found in input directory.")
        return False

    # Check for output files for each input image
    all_exist = True
    for img in input_imgs:
        base = os.path.splitext(img)[0]
        csv_file = os.path.join(output_dir, f"{base}_gap_analysis.csv")
        gap_img = os.path.join(output_dir, f"{base}_gap_map.png")
        if not (os.path.exists(csv_file) and os.path.exists(gap_img)):
            print(f"Missing output for {img}:")
            if not os.path.exists(csv_file):
                print(f"  Missing CSV: {csv_file}")
            if not os.path.exists(gap_img):
                print(f"  Missing gap map image: {gap_img}")
            all_exist = False
    return all_exist

if __name__ == "__main__":
    # These paths should match those used in py1.py
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T3\backup8"

    # Run py1.py in the background (blocking until finished)
    import subprocess
    import sys

    py1_path = os.path.abspath("py1.py")
    if not os.path.exists(py1_path):
        print("py1.py not found in current directory. Exiting.")
        sys.exit(1)

    print("Running py1.py ...")
    proc = subprocess.run(['python', py1_path], capture_output=True, text=True)
    print("py1.py output:")
    print(proc.stdout)
    if proc.returncode != 0:
        print("py1.py exited with error!")
        print(proc.stderr)
        sys.exit(1)

    # Now check for outputs
    if check_outputs_exist(output_dir, input_dir):
        print("Calculation successful")
    else:
        print("Some output files are missing.")
