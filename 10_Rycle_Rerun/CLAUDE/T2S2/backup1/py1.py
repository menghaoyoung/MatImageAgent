import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import sys
import io
import argparse
import csv
from pathlib import Path
from docx import Document
from docx.shared import Inches

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Core function: Get line grayscale values 
def get_line_grayscale(image_path, start_point, end_point):
    """
    Extract grayscale values along a line segment in an image.
    
    Args:
        image_path: Path to the input image
        start_point: Starting point (x, y) of the line segment
        end_point: Ending point (x, y) of the line segment
        
    Returns:
        tuple: (grayscale_values, line_length)
    """
    # Load the image and convert to grayscale
    img = Image.open(image_path).convert('L')
    img_array = np.array(img)
    
    # Calculate the number of points along the line
    x0, y0 = start_point
    x1, y1 = end_point
    
    # Calculate the Euclidean distance (line length in pixels)
    line_length_pixels = np.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
    
    # Number of points to sample along the line
    num_points = int(line_length_pixels) + 1
    
    # Generate points along the line
    x_points = np.linspace(x0, x1, num_points)
    y_points = np.linspace(y0, y1, num_points)
    
    # Extract grayscale values at each point
    grayscale_values = []
    for i in range(num_points):
        x, y = int(round(x_points[i])), int(round(y_points[i]))
        # Ensure coordinates are within image bounds
        if 0 <= x < img_array.shape[1] and 0 <= y < img_array.shape[0]:
            grayscale_values.append(img_array[y, x])
        else:
            grayscale_values.append(0)  # Default value for out-of-bounds points
    
    return np.array(grayscale_values), line_length_pixels

# Core function: Calculate u_eq
def calculate_μeq(grayscale_values, u_min, u_max) -> np.ndarray:
    """
    Calculate u_eq values from grayscale values.
    
    Args:
        grayscale_values: Array of grayscale values (0-255)
        u_min: Minimum u value
        u_max: Maximum u value
        
    Returns:
        np.ndarray: Array of u_eq values
    """
    return u_min + (grayscale_values / 255) * u_max

# Plot function: Plot u_eq curve
def plot_μeq_curve(distances, u_eq_values, output_path, filename_base):
    """
    Plot u_eq against distance from the start point.
    
    Args:
        distances: Array of distances from the start point
        u_eq_values: Array of u_eq values
        output_path: Directory to save the plot
        filename_base: Base filename for the output file
    """
    plt.figure(figsize=(10, 6))
    plt.plot(distances, u_eq_values, 'b-', linewidth=2)
    plt.xlabel('Distance from Start Point (mm)')
    plt.ylabel('u_eq')
    plt.title('u_eq vs Distance')
    plt.grid(True)
    
    # Save the plot as TIFF
    plt.savefig(os.path.join(output_path, f"{filename_base}_u_eq_plot.tiff"), dpi=300, format='tiff')
    plt.close()

# Main program execution
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process image and calculate u_eq along a line segment.')
    parser.add_argument('-resolution', type=float, default=1.0, help='Image resolution in mm/pixel')
    args = parser.parse_args()
    
    # Input parameters
    image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
    start_point = (152, 29)
    end_point = (136, 91)
    u_max = 65000
    u_min = 0
    resolution = args.resolution  # mm/pixel
    
    # Output directory
    output_path = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T2S2\1.0\backup1"
    os.makedirs(output_path, exist_ok=True)
    
    # Get the base filename without extension
    filename_base = os.path.splitext(os.path.basename(image_path))[0]
    
    # Get grayscale values and line length
    grayscale_values, line_length_pixels = get_line_grayscale(image_path, start_point, end_point)
    
    # Calculate actual line length in mm
    line_length_mm = line_length_pixels * resolution
    
    # Save line length to text file
    with open(os.path.join(output_path, f"{filename_base}_line_length.txt"), 'w') as f:
        f.write(f"Line length: {line_length_mm:.4f} mm\n")
        f.write(f"Start point: {start_point}\n")
        f.write(f"End point: {end_point}\n")
        f.write(f"Resolution: {resolution} mm/pixel\n")
    
    # Save grayscale values to CSV
    with open(os.path.join(output_path, f"{filename_base}_grayscale_values.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Index', 'Grayscale Value (0-255)'])
        for i, value in enumerate(grayscale_values):
            writer.writerow([i, value])
    
    # Calculate u_eq values
    u_eq_values = calculate_μeq(grayscale_values, u_min, u_max)
    
    # Calculate distances from the start point
    num_points = len(grayscale_values)
    distances = np.linspace(0, line_length_mm, num_points)
    
    # Save distance and u_eq values to CSV
    with open(os.path.join(output_path, f"{filename_base}_distance_u_eq.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Distance (mm)', 'u_eq'])
        for i in range(num_points):
            writer.writerow([distances[i], u_eq_values[i]])
    
    # Plot u_eq curve
    plot_μeq_curve(distances, u_eq_values, output_path, filename_base)
    
    print(f"Processing complete for {filename_base}")
    print(f"Line length: {line_length_mm:.4f} mm")
    print(f"Files saved to: {output_path}")

if __name__ == "__main__":
    main()
