import os
import sys

def verify_outputs():
    input_directory = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_directory = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T1S1\backup9"
    
    # Get all Li_ image files that were processed
    image_files = [
        "Li_0.125.png", "Li_0.25.png", "Li_0.375.png", "Li_0.5.png", 
        "Li_0.625.png", "Li_0.75.png", "Li_0.875.png", "Li_0.png", 
        "Li_1.125.png", "Li_1.25.png", "Li_1.png"
    ]
    
    all_files_exist = True
    
    # Check if each expected output file exists
    for img_file in image_files:
        base_name = os.path.splitext(img_file)[0]
        
        # Check for CSV file
        csv_path = os.path.join(output_directory, f"{base_name}_gap_analysis.csv")
        if not os.path.exists(csv_path):
            print(f"Missing CSV file: {csv_path}")
            all_files_exist = False
        
        # Check for highlighted PNG file
        png_path = os.path.join(output_directory, f"{base_name}_gap_highlighted.png")
        if not os.path.exists(png_path):
            print(f"Missing PNG file: {png_path}")
            all_files_exist = False
    
    if all_files_exist:
        print("Calculation successful")
        return True
    else:
        print("Some output files are missing")
        return False

if __name__ == "__main__":
    verify_outputs()
