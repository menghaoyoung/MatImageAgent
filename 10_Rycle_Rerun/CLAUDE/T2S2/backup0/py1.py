import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import sys
import io
import argparse
import csv
from docx import Document
from docx.shared import Inches
import math

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Core function: Get line grayscale values
def get_line_grayscale(image_path, start_point, end_point, resolution):
    """
    Extract grayscale values along a line segment from start_point to end_point.
    
    Args:
        image_path: Path to the input image
        start_point: Starting point (x, y) of the line segment
        end_point: Ending point (x, y) of the line segment
        resolution: Resolution of the line segment (points per pixel)
        
    Returns:
        grayscale_values: Array of grayscale values along the line segment
        line_length: Length of the line segment in pixels
    """
    # Open the image and convert to grayscale
    image = Image.open(image_path).convert('L')
    img_array = np.array(image)
    
    # Calculate the distance between start and end points
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]
    line_length = math.sqrt(dx**2 + dy**2)
    
    # Calculate the number of points to sample based on resolution
    num_points = int(line_length / resolution) + 1
    
    # Generate points along the line
    x_points = np.linspace(start_point[0], end_point[0], num_points)
    y_points = np.linspace(start_point[1], end_point[1], num_points)
    
    # Extract grayscale values at each point
    grayscale_values = []
    for x, y in zip(x_points, y_points):
        # Round to nearest integer for pixel coordinates
        x_int, y_int = int(round(x)), int(round(y))
        
        # Ensure coordinates are within image bounds
        if 0 <= x_int < img_array.shape[1] and 0 <= y_int < img_array.shape[0]:
            grayscale_values.append(img_array[y_int, x_int])
        else:
            grayscale_values.append(0)  # Default value for out-of-bounds points
    
    return np.array(grayscale_values), line_length

# Core function: Calculate u_eq
def calculate_μeq(grayscale_values, u_min, u_max) -> np.ndarray:
    """
    Calculate u_eq using the formula: u_eq = u_min + (gray_values / 255) * u_max
    
    Args:
        grayscale_values: Array of grayscale values
        u_min: Minimum u value
        u_max: Maximum u value
        
    Returns:
        u_eq: Array of calculated u_eq values
    """
    return u_min + (grayscale_values / 255) * u_max

# Plot function: Plot u_eq curve
def plot_μeq_curve(u_eq_values, line_length, resolution, output_path):
    """
    Plot u_eq against distance from the start point
    
    Args:
        u_eq_values: Array of u_eq values
        line_length: Length of the line segment
        resolution: Resolution used for sampling
        output_path: Path to save the plot
    """
    # Calculate distance array
    num_points = len(u_eq_values)
    distances = np.linspace(0, line_length, num_points)
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(distances, u_eq_values, 'b-', linewidth=2)
    plt.xlabel('Distance from Start Point (pixels)')
    plt.ylabel('u_eq')
    plt.title('u_eq vs. Distance')
    plt.grid(True)
    
    # Save the plot
    plt.savefig(output_path, format='tiff', dpi=300)
    plt.close()

# Main program execution
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Calculate and plot u_eq values along a line segment')
    parser.add_argument('-resolution', type=float, required=True, help='Resolution for line sampling')
    args = parser.parse_args()
    
    # Parameters
    image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
    start_point = (152, 29)
    end_point = (136, 91)
    u_max = 65000
    u_min = 0
    resolution = args.resolution
    
    # Create output directory
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T2S2\1.0\backup"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get the base filename without extension
    base_filename = os.path.splitext(os.path.basename(image_path))[0]
    
    # Get grayscale values along the line segment
    grayscale_values, line_length = get_line_grayscale(image_path, start_point, end_point, resolution)
    
    # Save grayscale values to CSV
    csv_path = os.path.join(output_dir, f"{base_filename}_grayscale_values.csv")
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Point', 'Grayscale Value'])
        for i, value in enumerate(grayscale_values):
            writer.writerow([i, value])
    
    # Save line length to text file
    length_path = os.path.join(output_dir, f"{base_filename}_line_length.txt")
    with open(length_path, 'w') as f:
        f.write(f"Line segment length: {line_length} pixels\n")
        f.write(f"Resolution: {resolution}\n")
        f.write(f"Number of points: {len(grayscale_values)}\n")
    
    # Calculate u_eq values
    u_eq_values = calculate_μeq(grayscale_values, u_min, u_max)
    
    # Save u_eq values to CSV
    u_eq_csv_path = os.path.join(output_dir, f"{base_filename}_u_eq_values.csv")
    with open(u_eq_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Point', 'u_eq Value'])
        for i, value in enumerate(u_eq_values):
            writer.writerow([i, value])
    
    # Plot u_eq curve
    plot_path = os.path.join(output_dir, f"{base_filename}_u_eq_curve.tiff")
    plot_μeq_curve(u_eq_values, line_length, resolution, plot_path)
    
    print(f"Processing complete for {base_filename}")
    print(f"Line segment length: {line_length} pixels")
    print(f"Grayscale values saved to: {csv_path}")
    print(f"Line length saved to: {length_path}")
    print(f"u_eq values saved to: {u_eq_csv_path}")
    print(f"u_eq curve plot saved to: {plot_path}")

if __name__ == "__main__":
    main()
