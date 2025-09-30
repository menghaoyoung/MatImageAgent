import os
import sys

def check_outputs_exist(output_dir, input_dir):
    # List all Li_*.png/jpg in input_dir
    input_images = [f for f in os.listdir(input_dir) if f.startswith("Li_") and f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    success = True
    for img_name in input_images:
        img_base = os.path.splitext(img_name)[0]
        csv_name = f"{img_base}_gap_analysis.csv"
        img_out_name = f"{img_base}_gap_highlight.png"
        csv_path = os.path.join(output_dir, csv_name)
        img_out_path = os.path.join(output_dir, img_out_name)
        if not (os.path.isfile(csv_path) and os.path.isfile(img_out_path)):
            print(f"Missing output for {img_name}:")
            if not os.path.isfile(csv_path):
                print(f"  Missing CSV: {csv_path}")
            if not os.path.isfile(img_out_path):
                print(f"  Missing Highlight Image: {img_out_path}")
            success = False
    return success

def safe_print_bytes(b):
    """
    Print subprocess output in a way that avoids UnicodeDecodeError/EncodeError
    by decoding with 'utf-8' and 'replace', then re-encoding to the console encoding,
    again with 'replace'.
    """
    if not b:
        return
    try:
        # Use the preferred console encoding
        enc = sys.stdout.encoding or "utf-8"
        txt = b.decode('utf-8', errors='replace')
        print(txt.encode(enc, errors='replace').decode(enc, errors='replace'))
    except Exception:
        # Fallback: print just the raw bytes in repr form
        print(repr(b))

if __name__ == "__main__":
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S1\backup9"

    # Check for py1.py
    py1_path = os.path.join(os.getcwd(), "py1.py")
    if not os.path.isfile(py1_path):
        print("py1.py not found in the current directory.")
        sys.exit(1)

    # Run py1.py
    import subprocess

    print("Running py1.py ...")
    process = subprocess.Popen(
        [sys.executable, py1_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=False
    )
    stdout, stderr = process.communicate()

    # Print output safely
    safe_print_bytes(stdout)
    if stderr:
        safe_print_bytes(stderr)

    # Check if all outputs exist
    all_ok = check_outputs_exist(output_directory, input_directory)
    if all_ok:
        print("Calculation successful")
    else:
        print("Calculation incomplete: some outputs are missing.")
