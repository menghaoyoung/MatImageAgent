import os
import glob
import subprocess

def verify_outputs():
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T1S2\backup1"
    
    # Check if directory exists
    if not os.path.exists(output_dir):
        print("Output directory does not exist!")
        return False
    
    # Look for analysis files
    analysis_files = glob.glob(os.path.join(output_dir, "*_gap_analysis.csv"))
    height_files = glob.glob(os.path.join(output_dir, "*_gap_height.csv"))
    stat_files = glob.glob(os.path.join(output_dir, "*_stats.txt"))
    image_files = glob.glob(os.path.join(output_dir, "*_highlighted.png"))
    
    # Check if files exist
    if analysis_files and height_files and stat_files and image_files:
        print("Calculation successful")
        return True
    else:
        print("Some output files are missing!")
        print(f"Analysis CSVs: {len(analysis_files)}")
        print(f"Height CSVs: {len(height_files)}")
        print(f"Stat TXTs: {len(stat_files)}")
        print(f"Highlighted Images: {len(image_files)}")
        return False

if __name__ == "__main__":
    # First run the analysis script with resolution 0.0187
    print("Running analysis with resolution = 0.0187...")
    
    # Properly format the command with the resolution parameter
    try:
        # Make sure to pass the argument correctly
        result = subprocess.run(["python", "py1.py", "-re", "0.0187"], 
                               check=True, 
                               capture_output=True, 
                               text=True)
        print("Analysis script output:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("Error running analysis script:")
        print(e.stderr)
        exit(1)
    
    # Then verify the outputs
    verify_outputs()
