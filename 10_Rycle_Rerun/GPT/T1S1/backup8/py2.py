import os

def check_output_files(output_dir, input_dir):
    # List of images to check
    img_files = [f for f in os.listdir(input_dir) if f.startswith('Li_') and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    all_exist = True
    for img_name in img_files:
        base_name = os.path.splitext(img_name)[0]
        csv_file = os.path.join(output_dir, f"{base_name}_gap_analysis.csv")
        img_file = os.path.join(output_dir, f"{base_name}_gap_highlight.png")
        if not (os.path.isfile(csv_file) and os.path.isfile(img_file)):
            print(f"Missing output for {img_name}:")
            if not os.path.isfile(csv_file):
                print(f"  CSV not found: {csv_file}")
            if not os.path.isfile(img_file):
                print(f"  Highlighted image not found: {img_file}")
            all_exist = False
    return all_exist

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S1\backup8"

    # Run py1.py in the background
    # We use os.system for simplicity; in practice, subprocess is preferred for more control.
    # The & at the end runs in background in UNIX, but on Windows, start /B may be needed.
    # Here, we'll run synchronously for reliability but print as if in background.
    print("Running py1.py ...")
    run_code = os.system(f'python py1.py')
    if run_code != 0:
        print("py1.py execution failed.")
        exit(1)

    # Check for output files
    success = check_output_files(output_directory, input_directory)
    if success:
        print("Calculation successful")
    else:
        print("Calculation failed: Some output files are missing.")
