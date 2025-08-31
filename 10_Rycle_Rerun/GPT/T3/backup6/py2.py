import os
import sys

def check_outputs():
    # Path where CLAHE PNGs, GAP map PNGs, and CSVs should be saved
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T3\backup6"
    if not os.path.exists(output_dir):
        print(f"Output directory does not exist: {output_dir}")
        sys.exit(1)
    # List all outputs - look for _gap_analysis.csv and _gap_map.png
    files = os.listdir(output_dir)
    csv_files = [f for f in files if f.startswith('Poly_') and f.endswith('_gap_analysis.csv')]
    map_files = [f for f in files if f.startswith('Poly_') and f.endswith('_gap_map.png')]
    if len(csv_files) > 0 and len(map_files) > 0:
        print("Calculation successful")
        print(f"Found {len(csv_files)} CSV files and {len(map_files)} GAP map images.")
    else:
        print("Calculation failed: Missing output GAP map images or CSV files.")
        print(f"Found {len(csv_files)} CSV files and {len(map_files)} GAP map images.")

if __name__ == "__main__":
    # Run py1.py in the background
    import subprocess
    print("Running py1.py in the background...")
    # You may adjust the path to py1.py as needed
    py1_path = os.path.abspath("py1.py")
    result = subprocess.run([sys.executable, py1_path], capture_output=True, text=True)
    print("py1.py output:")
    print(result.stdout)
    print("Checking for output files...")
    check_outputs()
