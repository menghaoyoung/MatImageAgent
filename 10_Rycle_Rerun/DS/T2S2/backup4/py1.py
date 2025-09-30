import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import sys
import io
import argparse
import csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Bresenham's line algorithm to get points along a line
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

# Core function: Get line grayscale values
def get_line_grayscale(img_array, start, end):
    line_points = bresenham_line(start, end)
    gray_values = []
    for point in line_points:
        x, y = point
        gray_values.append(img_array[y, x])
    return gray_values, line_points

# Core function: Calculate u_eq
def calculate_ueq(gray_values, u_min, u_max):
    gray_array = np.array(gray_values, dtype=np.float32)
    ueq = u_min + (gray_array / 255.0) * u_max
    return ueq

# Plot function: Plot u_eq curve
def plot_ueq_curve(distances, ueq, output_path):
    plt.figure()
    plt.plot(distances, ueq, 'b-', linewidth=2)
    plt.xlabel('Distance from start point (units)')
    plt.ylabel('u_eq')
    plt.title('Equivalent Displacement (u_eq) along Line Segment')
    plt.grid(True)
    plt.savefig(output_path, format='tiff', dpi=300)
    plt.close()

# Calculate cumulative distances from start point
def calculate_distances(points, resolution):
    distances = [0.0]
    cumulative = 0.0
    for i in range(1, len(points)):
        x1, y1 = points[i-1]
        x2, y2 = points[i]
        step_dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2) * resolution
        cumulative += step_dist
        distances.append(cumulative)
    return np.array(distances)

# Main program execution
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-resolution', type=float, required=True)
    args = parser.parse_args()
    
    # Fixed parameters
    start_point = (152, 29)
    end_point = (136, 91)
    u_max = 65000
    u_min = 0
    
    # Hardcoded paths (single quotes to avoid escape issues)
    image_path = r'C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png'
    output_dir = r'C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T2S2\1.0\backup4'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate base filename from input image
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    
    # Process image
    img = Image.open(image_path).convert('L')
    img_array = np.array(img)
    
    # Get grayscale values along line
    gray_values, line_points = get_line_grayscale(img_array, start_point, end_point)
    
    # Calculate segment length
    pixel_distance = np.sqrt((end_point[0]-start_point[0])**2 + (end_point[1]-start_point[1])**2)
    segment_length = pixel_distance * args.resolution
    length_file = os.path.join(output_dir, f"{base_name}_length.txt")
    with open(length_file, 'w') as f:
        f.write(f"{segment_length:.4f}")
    
    # Save grayscale values
    gray_file = os.path.join(output_dir, f"{base_name}_gray_values.csv")
    with open(gray_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Gray_value'])
        for val in gray_values:
            writer.writerow([val])
    
    # Calculate u_eq
    ueq_array = calculate_ueq(gray_values, u_min, u_max)
    
    # Calculate distances
    distances = calculate_distances(line_points, args.resolution)
    
    # Save distance and u_eq
    data_file = os.path.join(output_dir, f"{base_name}_u_eq.csv")
    with open(data_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Distance', 'u_eq'])
        for d, u in zip(distances, ueq_array):
            writer.writerow([f"{d:.4f}", f"{u:.2f}"])
    
    # Plot and save
    plot_file = os.path.join(output_dir, f"{base_name}_plot.tiff")
    plot_ueq_curve(distances, ueq_array, plot_file)

if __name__ == "__main__":
    main()
