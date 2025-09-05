import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import sys
import io
import csv
import argparse
import math
from docx import Document
from docx.shared import Inches

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Core function: Get line grayscale values 
def get_line_grayscale(image_path, start_point, end_point, resolution):
    """
    Extract grayscale values along a line segment from start_point to end_point.
    
    Args:
        image_path: Path to the input image
        start_point: (x, y) coordinates of the start point
        end_point: (x, y) coordinates of the end point
        resolution: Spatial resolution in units/pixel
        
    Returns:
        distances: Array of distances from start point
        gray_values: Array of grayscale values along the line
        line_length: Physical length of the line segment
    """
    # Load the image
    img = Image.open(image_path).convert('L')  # Convert to grayscale
    img_array = np.array(img)
    
    # Calculate the number of points on the line
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]
    num_points = int(np.ceil(np.sqrt(dx**2 + dy**2)))
    
    # Generate points along the line
    x_points = np.linspace(start_point[0], end_point[0], num_points)
    y_points = np.linspace(start_point[1], end_point[1], num_points)
    
    # Extract grayscale values along the line
    gray_values = []
    for i in range(num_points):
        x, y = int(round(x_points[i])), int(round(y_points[i]))
        # Ensure coordinates are within image bounds
        if 0 <= x < img_array.shape[1] and 0 <= y < img_array.shape[0]:
            gray_values.append(img_array[y, x])
        else:
            gray_values.append(0)  # Default value for out-of-bounds points
    
    # Calculate physical distances
    distances = np.linspace(0, np.sqrt(dx**2 + dy**2) * resolution, num_points)
    line_length = distances[-1]
    
    return distances, np.array(gray_values), line_length

# Core function: Calculate u_eq
def calculate_μeq(gray_values, u_min, u_max) -> np.ndarray:
    """
    Calculate u_eq using the formula: u_eq = u_min + (gray_values / 255) * u_max
    
    Args:
        gray_values: Array of grayscale values
        u_min: Minimum u value
        u_max: Maximum u value
        
    Returns:
        u_eq: Array of calculated u_eq values
    """
    return u_min + (gray_values / 255.0) * (u_max - u_min)

# Plot function: Plot u_eq curve
def plot_μeq_curve(distances, u_eq, output_path):
    """
    Plot u_eq against distance and save to a file
    
    Args:
        distances: Array of distances from start point
        u_eq: Array of calculated u_eq values
        output_path: Path to save the plot
    """
    plt.figure(figsize=(10, 6))
    plt.plot(distances, u_eq, 'b-', linewidth=2)
    plt.xlabel('Distance (units)')
    plt.ylabel('u_eq')
    plt.title('u_eq vs Distance')
    plt.grid(True)
    plt.savefig(output_path, dpi=300, format='tiff')
    plt.close()

# Main program execution
def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Process image and calculate u_eq')
    parser.add_argument('-resolution', type=float, default=1.0, help='Spatial resolution in units/pixel')
    args = parser.parse_args()
    
    # Set parameters
    image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
    start_point = (152, 29)
    end_point = (136, 91)
    u_max = 65000
    u_min = 0
    resolution = args.resolution
    
    # Create output directory
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\CLAUDE\T2S2\1.0\backup2"
    os.makedirs(output_dir, exist_ok=True)
    
    # Get base filename without extension
    base_filename = os.path.splitext(os.path.basename(image_path))[0]
    
    # Get grayscale values along the line
    distances, gray_values, line_length = get_line_grayscale(image_path, start_point, end_point, resolution)
    
    # Save grayscale values to CSV
    gray_csv_path = os.path.join(output_dir, f"{base_filename}_gray_values.csv")
    with open(gray_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Distance', 'GrayValue'])
        for i in range(len(distances)):
            writer.writerow([distances[i], gray_values[i]])
    
    # Save line length to text file
    length_txt_path = os.path.join(output_dir, f"{base_filename}_line_length.txt")
    with open(length_txt_path, 'w') as txtfile:
        txtfile.write(f"Line segment length: {line_length:.2f} units\n")
        txtfile.write(f"Start point: {start_point}\n")
        txtfile.write(f"End point: {end_point}\n")
        txtfile.write(f"Resolution: {resolution} units/pixel\n")
    
    # Calculate u_eq
    u_eq = calculate_μeq(gray_values, u_min, u_max)
    
    # Save u_eq values to CSV
    ueq_csv_path = os.path.join(output_dir, f"{base_filename}_ueq_values.csv")
    with open(ueq_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Distance', 'u_eq'])
        for i in range(len(distances)):
            writer.writerow([distances[i], u_eq[i]])
    
    # Plot u_eq curve
    plot_path = os.path.join(output_dir, f"{base_filename}_ueq_plot.tiff")
    plot_μeq_curve(distances, u_eq, plot_path)
    
    print(f"Processing complete for {base_filename}")
    print(f"Line length: {line_length:.2f} units")
    print(f"Output files saved to {output_dir}")

if __name__ == "__main__":
    main()
