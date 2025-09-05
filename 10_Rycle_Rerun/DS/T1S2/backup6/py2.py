import os
import subprocess

# Configuration parameters
re_value = "0.0187"
input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S2\backup6"

# Run py1.py in background with specified resolution
print("Running gap analysis program in background...")
process = subprocess.Popen(["python", "py1.py", f"-re={re_value}"],
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE)
print(f"Process started with PID: {process.pid}")

# Verify outputs after completion
print("Waiting for process to complete...")
stdout, stderr = process.communicate()  # Wait for process to finish

if process.returncode == 0:
    print("Gap analysis completed successfully")
    
    # Check for required output files
    all_files_exist = True
    for filename in os.listdir(input_dir):
        if filename.startswith("Li_") and \
           (filename.lower().endswith('.png') or filename.lower().endswith('.jpg')):
            base_name = os.path.splitext(filename)[0]
            
            # Check for all required output files
            required_files = [
                f"{base_name}_gap_analysis.csv",
                f"{base_name}_gap_height.csv",
                f"{base_name}_gap_highlight.png",
                f"{base_name}_gap_report.txt"
            ]
            
            for file in required_files:
                file_path = os.path.join(output_dir, file)
                if not os.path.exists(file_path):
                    print(f"Missing output file: {file_path}")
                    all_files_exist = False
    
    # Final verification result
    if all_files_exist:
        print("Calculation successful - All output files verified")
    else:
        print("Output verification failed - Some files are missing")
else:
    print(f"Error in gap analysis:\n{stderr.decode()}")
