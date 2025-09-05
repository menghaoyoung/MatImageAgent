import os
import subprocess
import sys

def verify_outputs():
    # Define paths
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T2S2\1.0\backup2"
    image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
    base_filename = os.path.splitext(os.path.basename(image_path))[0]
    
    # Expected output files
    gray_csv = os.path.join(output_dir, f"{base_filename}_gray_values.csv")
    ueq_csv = os.path.join(output_dir, f"{base_filename}_ueq_values.csv")
    length_txt = os.path.join(output_dir, f"{base_filename}_line_length.txt")
    plot_file = os.path.join(output_dir, f"{base_filename}_ueq_plot.tiff")
    
    # Run py1.py with resolution 1.2
    try:
        print("Running py1.py with resolution=1.2...")
        result = subprocess.run(["python", "py1.py", "-resolution=1.2"], 
                               capture_output=True, text=True, check=True)
        print(result.stdout)
        
        # Check if output files exist
        files_to_check = {
            "Grayscale values CSV": gray_csv,
            "u_eq values CSV": ueq_csv,
            "Line length text file": length_txt,
            "u_eq plot TIFF": plot_file
        }
        
        all_files_exist = True
        for file_desc, file_path in files_to_check.items():
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"✓ {file_desc} exists ({file_size} bytes): {file_path}")
            else:
                print(f"✗ {file_desc} does not exist: {file_path}")
                all_files_exist = False
        
        if all_files_exist:
            print("Calculation successful")
            return True
        else:
            print("Some output files are missing")
            return False
    
    except subprocess.CalledProcessError as e:
        print(f"Error running py1.py: {e}")
        print(f"Standard output: {e.stdout}")
        print(f"Standard error: {e.stderr}")
        return False

if __name__ == "__main__":
    verify_outputs()
