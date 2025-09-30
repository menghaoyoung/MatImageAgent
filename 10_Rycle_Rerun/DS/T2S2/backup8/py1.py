import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import sys
import argparse

def bresenham_line(start, end):
    """Generate points along a line using Bresenham's algorithm."""
    x0, y0 = start
    x1, y1 = end
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return points

def get_line_grayscale(image, start, end):
    """Extract grayscale values for pixels along a line segment."""
    points = bresenham_line(start, end)
    grayscale_values = []
    for (x, y) in points:
        if 0 <= y < image.shape[0] and 0 <= x < image.shape[1]:
            grayscale_values.append(image[y, x])
        else:
            grayscale_values.append(0)
    return points, np.array(grayscale_values)

def calculate_μeq(gray_values, u_min, u_max):
    """Calculate u_eq from grayscale values using provided formula."""
    return u_min + (gray_values / 255.0) * u_max

def plot_μeq_curve(distances, u_eq, filename):
    """Plot u_eq vs distance and save as TIFF image."""
    plt.figure()
    plt.plot(distances, u_eq, 'b-', linewidth=1.5)
    plt.xlabel("Distance from Start Point (μm)", fontsize=12)
    plt.ylabel("u_eq Value", fontsize=12)
    plt.title("Material Property Variation Along Line Segment", fontsize=14)
    plt.grid(linestyle='--', alpha=0.7)
    plt.savefig(filename, format='tiff', dpi=300)
    plt.close()

def main():
    # Configuration parameters
    start_point = (152, 29)
    end_point = (135, 92)
    u_max = 65535
    u_min = 0
    image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T2S2\1.0\backup8"
    
    # Parse command-line argument for resolution
    parser = argparse.ArgumentParser()
    parser.add_argument("-resolution", type=float, default=1.08)
    args = parser.parse_args()
    resolution = args.resolution
    
    # Load and process image
    img = Image.open(image_path).convert('L')
    img_array = np.array(img)
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    # Create output directory if missing
    os.makedirs(output_dir, exist_ok=True)
    
    # Calculate straight-line length (micrometers)
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]
    length_um = (dx**2 + dy**2)**0.5 * resolution
    
    # Extract grayscale values along line
    points, gray_values = get_line_grayscale(img_array, start_point, end_point)
    
    # Calculate cumulative distances
    distances = [0.0]
    for i in range(1, len(points)):
        step = ((points[i][0]-points[i-1][0])**2 + (points[i][1]-points[i-1][1])**2)**0.5
        distances.append(distances[-1] + step * resolution)
    
    # Compute u_eq values
    u_eq_array = calculate_μeq(gray_values, u_min, u_max)
    
    # Save outputs
    np.savetxt(f"{output_dir}/{base_name}_gray_values.csv", gray_values, fmt='%d')
    with open(f"{output_dir}/{base_name}_length.txt", 'w') as f:
        f.write(f"{length_um:.4f}")
    np.savetxt(f"{output_dir}/{base_name}_u_eq.csv", 
              np.column_stack((distances, u_eq_array)),
              delimiter=',', 
              header="Distance(um),u_eq", 
              fmt='%.6f')
    plot_μeq_curve(distances, u_eq_array, f"{output_dir}/{base_name}_curve.tiff")

if __name__ == "__main__":
    main()
