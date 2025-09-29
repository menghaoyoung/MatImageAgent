import os
import subprocess
import sys
import time

def run_py1_background():
    """Run py1.py in the background and verify output files"""
    # Configuration
    input_dir = r"C:\Users\admin\Desktop\Python_proj\distance_analysis_new\Images"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T1S1\backup4"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Run py1.py in the background
    print("Starting GAP pixel analysis...")
    try:
        # Use Popen to run in background
        process = subprocess.Popen([sys.executable, "py1.py", input_dir])
        
        # Wait for process to complete with timeout
        print("Processing images (this may take several minutes)...")
        timeout = 600  # 10 minutes timeout
        start_time = time.time()
        
        while True:
            retcode = process.poll()  # Check if process has finished
            if retcode is not None:
                break  # Process completed
            elif time.time() - start_time > timeout:
                process.terminate()
                raise TimeoutError("Processing timed out after 10 minutes")
            time.sleep(5)  # Check every 5 seconds
        
        # Check exit status
        if retcode != 0:
            raise RuntimeError(f"py1.py exited with code {retcode}")
            
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        return False
    
    print("Image processing completed successfully")
    return True

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
        
        # Check CSV
        if not os.path.exists(os.path.join(output_dir, csv_file)):
            missing_files.append(csv_file)
        
        # Check PNG
        if not os.path.exists(os.path.join(output_dir, png_file)):
            missing_files.append(png_file)
    
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
            print(f" - {file}")
        print("Please check processing logs for errors")

if __name__ == "__main__":
    main()
