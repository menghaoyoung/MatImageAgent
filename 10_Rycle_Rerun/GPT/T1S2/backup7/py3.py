import os
import subprocess
import sys

def check_output_files(output_dir, prefix="Li_"):
    """
    Check in the output_dir for:
     - At least one CSV file ending with _gap_analysis.csv
     - At least one CSV file ending with _gap_height.csv
     - At least one TXT file ending with _gap_stats.txt
     - At least one PNG file ending with _GAP_highlight.png
    All files should correspond to images with the 'Li_' prefix.
    """
    files = os.listdir(output_dir)
    analysis_csv = [f for f in files if f.startswith(prefix) and f.endswith('_gap_analysis.csv')]
    gap_height_csv = [f for f in files if f.startswith(prefix) and f.endswith('_gap_height.csv')]
    stats_txt = [f for f in files if f.startswith(prefix) and f.endswith('_gap_stats.txt')]
    highlight_png = [f for f in files if f.startswith(prefix) and f.endswith('_GAP_highlight.png')]

    return all([analysis_csv, gap_height_csv, stats_txt, highlight_png])

if __name__ == "__main__":
    # Paths
    py1_path = "py1.py"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T1S2\backup6"
    # Run py1.py in background with re=0.0187
    cmd = [
        sys.executable, py1_path,
        "-re", "0.0187",
        "-output_dir", output_dir
    ]
    try:
        print("Running py1.py in background...")
        # Avoid UnicodeDecodeError by not capturing output, or decode as utf-8 with errors='ignore'
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Try decoding output as utf-8, fall back to 'ignore' if needed
        try:
            output = proc.stdout.decode('utf-8')
            error = proc.stderr.decode('utf-8')
        except UnicodeDecodeError:
            output = proc.stdout.decode('utf-8', errors='ignore')
            error = proc.stderr.decode('utf-8', errors='ignore')
        print(output)
        if error:
            print("stderr output from py1.py:")
            print(error)
    except Exception as e:
        print("Error running py1.py:", e)
        exit(1)

    # Check for expected outputs
    if check_output_files(output_dir):
        print("Calculation successful")
    else:
        print("Calculation failed: Some output files are missing.")
