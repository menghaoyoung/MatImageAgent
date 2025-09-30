import os
import subprocess
import sys

def main():
    # Set parameters
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T2S2\1.0\backup4"
    base_name = "Li_1.0"
    expected_files = [
        f"{base_name}_length.txt",
        f"{base_name}_gray_values.csv",
        f"{base_name}_u_eq.csv",
        f"{base_name}_plot.tiff"
    ]

    # Run py1.py with resolution=1.2
    try:
        subprocess.run(
            ["python", "py1.py", "-resolution=1.2"], 
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        print("Error running py1.py")
        sys.exit(1)
    
    # Verify output files
    missing_files = []
    for file in expected_files:
        if not os.path.exists(os.path.join(output_dir, file)):
            missing_files.append(file)
    
    if missing_files:
        print(f"Missing files: {', '.join(missing_files)}")
    else:
        print("Calculation successful")

if __name__ == "__main__":
    main()
