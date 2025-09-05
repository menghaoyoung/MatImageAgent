import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import sys
import io
import argparse
import csv
import math

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Core function: Get line grayscale values
def get_line_grayscale(image_path, start_point, end_point):
    """
    Extract grayscale values along a line segment in an image.
    
    Args:
        image_path: Path to the input image
        start_point: Starting point coordinates (x, y)
        end_point: Ending point coordinates (x, y)
        
    Returns:
        tuple: (grayscale_values, line_length_pixels)
    """
    # Load the image
    try:
        img = Image.open(image_path).convert('L')  # Convert to grayscale
        img_array = np.array(img)
    except Exception as e:
        print(f"Error opening image: {e}")
        sys.exit(1)
    
    # Calculate number of points on the line
    x0, y0 = start_point
    x1, y1 = end_point
    
    # Calculate Euclidean distance (pixels)
    line_length_pixels = math.sqrt((x1 - x0)**2 + (y1 - y0)**2)
    
    # Number of points to sample (use the ceiling of the distance to ensure adequate sampling)
    num_points = int(math.ceil(line_length_pixels)) + 1
    
    # Generate points along the line
    x_points = np.linspace(x0, x1, num_points, dtype=int)
    y_points = np.linspace(y0, y1, num_points, dtype=int)
    
    # Extract grayscale values
    grayscale_values = img_array[y_points, x_points]
    
    return grayscale_values, line_length_pixels

# Core function: Calculate u_eq
def calculate_μeq(grayscale_values, u_min, u_max) -> np.ndarray:
    """
    Calculate u_eq values from grayscale values.
    
    Args:
        grayscale_values: Array of grayscale values (0-255)
        u_min: Minimum u value
        u_max: Maximum u value
        
    Returns:
        np.ndarray: Array of calculated u_eq values
    """
    # Apply the formula: u_eq = u_min + (gray_values / 255) * u_max
    μeq_values = u_min + (grayscale_values / 255.0) * u_max
    
    return μeq_values

# Plot function: Plot u_eq curve
def plot_μeq_curve(distances, μeq_values, output_path, title):
    """
    Plot u_eq values against distance and save the plot.
    
    Args:
        distances: Array of distances from start point
        μeq_values: Array of u_eq values
        output_path: Path to save the plot
        title: Title for the plot
    """
    plt.figure(figsize=(10, 6))
    plt.plot(distances, μeq_values, 'b-', linewidth=2)
    plt.grid(True)
    plt.xlabel('Distance from Start Point (μm)')
    plt.ylabel('μeq (Arbitrary Units)')
    plt.title(title)
    
    # Save plot as TIFF
    plt.savefig(output_path, format='tiff', dpi=300)
    plt.close()

# Main program execution
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process image and calculate u_eq values.')
    parser.add_argument('-resolution', type=float, required=True, help='Image resolution in μm per pixel')
    args = parser.parse_args()
    
    # Input parameters
    image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
    start_point = (152, 29)
    end_point = (136, 91)
    u_max = 65000
    u_min = 0
    resolution = args.resolution
    
    # Create output directory
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T2S2\1.0\backup2"
    os.makedirs(output_dir, exist_ok=True)
    
    # Extract filename without extension
    image_filename = os.path.splitext(os.path.basename(image_path))[0]
    
    # Step 1: Get grayscale values along the line
    grayscale_values, line_length_pixels = get_line_grayscale(image_path, start_point, end_point)
    
    # Calculate real-world line length based on resolution
    line_length_real = line_length_pixels * resolution
    
    # Save grayscale values to CSV
    grayscale_csv_path = os.path.join(output_dir, f"{image_filename}_grayscale_values.csv")
    with open(grayscale_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Index', 'Grayscale Value (0-255)'])
        for i, value in enumerate(grayscale_values):
            writer.writerow([i, value])
    
    # Save line length to text file
    length_txt_path = os.path.join(output_dir, f"{image_filename}_line_length.txt")
    with open(length_txt_path, 'w') as txtfile:
        txtfile.write(f"Line segment from {start_point} to {end_point}:\n")
        txtfile.write(f"Length in pixels: {line_length_pixels:.2f}\n")
        txtfile.write(f"Length in μm (resolution={resolution} μm/pixel): {line_length_real:.2f} μm\n")
    
    # Step 2: Calculate u_eq values
    μeq_values = calculate_μeq(grayscale_values, u_min, u_max)
    
    # Calculate distances from start point
    num_points = len(grayscale_values)
    distances = np.linspace(0, line_length_real, num_points)
    
    # Save u_eq values and distances to CSV
    ueq_csv_path = os.path.join(output_dir, f"{image_filename}_ueq_values.csv")
    with open(ueq_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Distance (μm)', 'μeq Value'])
        for dist, ueq in zip(distances, μeq_values):
            writer.writerow([dist, ueq])
    
    # Step 3: Plot u_eq curve
    plot_title = f"μeq vs Distance for {image_filename} (Resolution: {resolution} μm/pixel)"
    plot_path = os.path.join(output_dir, f"{image_filename}_ueq_curve.tiff")
    plot_μeq_curve(distances, μeq_values, plot_path, plot_title)
    
    print(f"Processing complete for {image_filename}")
    print(f"Line length: {line_length_real:.2f} μm")
    print(f"Files saved to {output_dir}")

if __name__ == "__main__":
    main()
