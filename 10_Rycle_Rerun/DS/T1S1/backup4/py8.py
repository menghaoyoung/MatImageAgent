import os
import subprocess
import sys
import time

def run_py1_background():
    """Run py1.py in the background and verify output files"""
    # Configuration with explicit paths
    base_dir = r"C:\Users\admin\Desktop\Python_proj"
    py1_script = os.path.join(base_dir, "py1.py")
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1\backup4"
    
    # Verify py1.py exists before execution
    if not os.path.exists(py1_script):
        print(f"Error: py1.py not found at {py1_script}")
        return False
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Run py1.py in the background
    print("Starting GAP pixel analysis...")
    try:
        # Use absolute path for py1.py
        process = subprocess.Popen(
            [sys.executable, py1_script, input_dir],
            cwd=base_dir  # Set working directory
        )
        
        # Wait for process to complete with timeout
        print("Processing images (this may take several minutes)...")
        timeout = 600  # 10 minutes timeout
        start_time = time.time()
        interval = 5  # Check every 5 seconds
        
        while True:
            retcode = process.poll()  # Check if process has finished
            if retcode is not None:
                break  # Process completed
            elif time.time() - start_time > timeout:
                process.terminate()
                raise TimeoutError("Processing timed out after 10 minutes")
            time.sleep(interval)
        
        # Check exit status
        if retcode != 0:
            raise RuntimeError(f"py1.py exited with code {retcode}")
            
        print("Image processing completed successfully")
        return True
        
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        return False

def verify_output_files():
    """Verify that all required output files exist"""
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1\backup4"
    
    # Get list of input images
    input_images = []
    for f in os.listdir(input_dir):
        if f.startswith('Li_') and f.lower().endswith(('.png', '.jpg')):
            input_images.append(f)
    
    # Check for each input image
    missing_files = []
    
    for img_file in input_images:
        base_name = os.path.splitext(img_file)[0]
        csv_file = f"{base_name}_gap_analysis.csv"
        png_file = f"{base_name}_gap_highlighted.png"
        
        csv_path = os.path.join(output_dir, csv_file)
        png_path = os.path.join(output_dir, png_file)
        
        if not os.path.exists(csv_path):
            missing_files.append(csv_path)
        if not os.path.exists(png_path):
            missing_files.append(png_path)
    
    return missing_files

def main():
    """Main execution function"""
    # Run the processing
    success = run_py1_background()
    
    if not success:
        print("Processing failed. Output verification aborted.")
        return
    
    # Verify output files
    missing_files = verify_output_files()
    
    if not missing_files:
        print("Calculation successful")
    else:
        print(f"Error: {len(missing_files)} output files missing:")
        for file in missing_files:
            print(f" - {os.path.basename(file)}")
        print("Please check processing logs for errors")

if __name__ == "__main__":
    main()
