import os
import sys

def check_outputs(output_directory, input_directory):
    """
    For each 'Poly_' image in input_directory, check if its CSV and _gap_highlight.png exist in output_directory.
    Returns True if all outputs exist, else False.
    """
    # Gather all Poly_ input images (png/jpg/jpeg)
    input_images = [f for f in os.listdir(input_directory)
                    if f.startswith("Poly_") and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not input_images:
        print("No Poly_ images found in the input directory.")
        return False

    all_exist = True
    for img_fname in input_images:
        base = os.path.splitext(img_fname)[0]
        csv_path = os.path.join(output_directory, f"{base}_gap_analysis.csv")
        img_path = os.path.join(output_directory, f"{base}_gap_highlight.png")
        if not (os.path.isfile(csv_path) and os.path.isfile(img_path)):
            print(f"Missing output for {img_fname}:")
            if not os.path.isfile(csv_path):
                print(f" - Missing CSV: {csv_path}")
            if not os.path.isfile(img_path):
                print(f" - Missing highlight image: {img_path}")
            all_exist = False
    return all_exist

if __name__ == "__main__":
    # Paths as specified in the task description
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T3\backup2"

    # Run py1.py in the background
    print("Running py1.py in the background...")
    exit_code = os.system(f'python py1.py')
    if exit_code != 0:
        print("py1.py did not execute successfully.")
        sys.exit(1)

    # Verify output files exist
    success = check_outputs(output_directory, input_directory)
    if success:
        print("Calculation successful")
    else:
        print("Calculation failed: Some output files are missing.")
