import os
import sys

def check_outputs(output_dir):
    """
    Check if output CSV and PNG files exist for each processed image.
    """
    # List all files in the output directory
    files = os.listdir(output_dir)
    csv_files = [f for f in files if f.endswith('_gap_analysis.csv')]
    png_files = [f for f in files if f.endswith('_GAP_map.png')]

    if len(csv_files) == 0 or len(png_files) == 0:
        print("Output files not found. Calculation failed.")
        return

    # Optionally, print the found files
    print("Found CSV files:")
    for f in csv_files:
        print(f"  {f}")
    print("Found GAP map images:")
    for f in png_files:
        print(f"  {f}")

    print("Calculation successful")

if __name__ == "__main__":
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T3\backup4"
    check_outputs(output_directory)
