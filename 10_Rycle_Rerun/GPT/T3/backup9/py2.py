import os
import glob

def check_results(output_dir):
    # Find all GAP analysis CSV and GAP map PNG files in the output directory
    csv_files = glob.glob(os.path.join(output_dir, "Poly_*_gap_analysis.csv"))
    gap_img_files = glob.glob(os.path.join(output_dir, "Poly_*_gap_map.png"))
    clahe_img_files = glob.glob(os.path.join(output_dir, "Poly_*_CLAHE.png"))

    if len(csv_files) > 0 and len(gap_img_files) > 0:
        print("Calculation successful")
        print(f"Found {len(csv_files)} CSV files and {len(gap_img_files)} GAP map images.")
    else:
        print("Calculation failed or output files missing.")

if __name__ == "__main__":
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T3\backup9"
    check_results(output_dir)
