import os
import subprocess
import sys
import argparse

def verify_files(output_dir, base_name):
    """Check if all required output files exist"""
    required_files = [
        f"{base_name}_grayscale.csv",
        f"{base_name}_length.txt",
        f"{base_name}_data.csv",
        f"{base_name}_plot.tiff"
    ]
    
    missing = []
    for filename in required_files:
        if not os.path.exists(os.path.join(output_dir, filename)):
            missing.append(os.path.join(output_dir, filename))
    
    return missing

def main():
    # Configuration parameters
    IMAGE_PATH = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
    OUTPUT_DIR = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T2S2\1.0\backup1"
    BASE_NAME = os.path.splitext(os.path.basename(IMAGE_PATH))[0]  # "Li_1.0"
    
    parser = argparse.ArgumentParser(description='Run and verify image processing pipeline')
    parser.add_argument('-resolution', type=float, default=0.9, help='Physical dimension per pixel')
    args = parser.parse_args()

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print("Starting image processing pipeline...")
    print(f"Resolution: {args.resolution}")
    print(f"Output directory: {OUTPUT_DIR}")
    
    # Run py1.py with specified resolution
    try:
        result = subprocess.run(
            ["python", "py1.py", f"-resolution={args.resolution}"],
            capture_output=True,
            text=True,
            check=True
        )
        print("py1.py executed successfully")
        print("Output from py1.py:")
        print(result.stdout)
        
        if result.stderr:
            print("Errors from py1.py:")
            print(result.stderr)
    
    except subprocess.CalledProcessError as e:
        print(f"Error running py1.py: {e.stderr}")
        print("Troubleshooting steps:")
        print("1. Verify py1.py exists in current directory")
        print("2. Check image path in py1.py matches actual location")
        print("3. Ensure required libraries are installed (Pillow, numpy, matplotlib)")
        sys.exit(1)
    
    except FileNotFoundError:
        print("Error: py1.py not found in current directory")
        sys.exit(1)
    
    # Verify output files
    missing = verify_files(OUTPUT_DIR, BASE_NAME)
    
    if not missing:
        print("Calculation successful")
        print("Generated files:")
        for fname in os.listdir(OUTPUT_DIR):
            if fname.startswith(BASE_NAME):
                print(f" - {os.path.join(OUTPUT_DIR, fname)}")
    else:
        print("Error: Missing output files:")
        for f in missing:
            print(f" - {f}")
        
        print("\nTroubleshooting recommendations:")
        print("1. Check py1.py logic for file creation")
        print("2. Verify write permissions in output directory")
        print("3. Ensure image processing functions handle coordinates correctly")
        print("4. Confirm matplotlib backend supports TIFF export")
        sys.exit(1)

if __name__ == "__main__":
    main()
