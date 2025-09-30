import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import sys
import io
import argparse
import math
import csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Bresenham's line algorithm for pixel-perfect line coordinates
def bresenham_line(start, end):
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

# Get grayscale values along line segment
def get_line_grayscale(image_array, start, end):
    points = bresenham_line(start, end)
    gray_values = []
    for x, y in points:
        if 0 <= y < image_array.shape[0] and 0 <= x < image_array.shape[1]:
            gray_values.append(image_array[y, x])
        else:
            gray_values.append(0)  # Default to 0 for out-of-bound points
    return gray_values, points

# Calculate u_eq values from grayscale array
def calculate_ueq(gray_values, u_min, u_max):
    gray_arr = np.array(gray_values, dtype=np.float32)
    return u_min + (gray_arr / 255.0) * u_max

# Plot u_eq vs distance and save as TIFF
def plot_ueq_curve(distances, ueq, output_path):
    plt.figure(figsize=(10, 6))
    plt.plot(distances, ueq, 'b-', linewidth=2)
    plt.xlabel('Distance from Start Point (μm)')
    plt.ylabel('u_eq Value')
    plt.title('Equivalent Magnetic Potential Distribution')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(output_path, format='tiff', dpi=300, bbox_inches='tight')
    plt.close()

# Main program execution
def main():
    # Fixed parameters from [Parameters] section
    start_point = (152, 29)
    end_point = (135, 92)
    u_max = 65535
    u_min = 0
    image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T2S2\1.0\backup5"
    
    # Parse command line argument for resolution with default value
    parser = argparse.ArgumentParser()
    parser.add_argument('-resolution', type=float, default=1.08,
                        help='Resolution value in micrometers per pixel')
    args = parser.parse_args()
    resolution = args.resolution

    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)
    
    # Process image
    img = Image.open(image_path).convert('L')  # Convert to grayscale
    img_array = np.array(img)
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    # Get grayscale values and calculate segment length
    gray_values, points = get_line_grayscale(img_array, start_point, end_point)
    length_pixels = math.sqrt((end_point[0] - start_point[0])**2 + 
                             (end_point[1] - start_point[1])**2)
    length_um = length_pixels * resolution
    
    # Save grayscale values to CSV
    gray_csv = os.path.join(output_dir, f"{base_name}_gray_values.csv")
    with open(gray_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Gray_value'])
        for value in gray_values:
            writer.writerow([value])
    
    # Save segment length to text file
    length_txt = os.path.join(output_dir, f"{base_name}_length.txt")
    with open(length_txt, 'w') as f:
        f.write(f"{length_um:.4f}")
    
    # Calculate u_eq values
    ueq = calculate_ueq(gray_values, u_min, u_max)
    
    # Calculate distances from start point
    distances = []
    for i, (x, y) in enumerate(points):
        d_pixels = math.sqrt((x - start_point[0])**2 + (y - start_point[1])**2)
        distances.append(d_pixels * resolution)
    
    # Save distance and u_eq to CSV
    dist_ueq_csv = os.path.join(output_dir, f"{base_name}_distance_ueq.csv")
    with open(dist_ueq_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Distance_um', 'u_eq'])
        for d, u in zip(distances, ueq):
            writer.writerow([f"{d:.4f}", f"{u:.1f}"])
    
    # Generate and save plot
    plot_path = os.path.join(output_dir, f"{base_name}_ueq_curve.tiff")
    plot_ueq_curve(distances, ueq, plot_path)

if __name__ == "__main__":
    main()
