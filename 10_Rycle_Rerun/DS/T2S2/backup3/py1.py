import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import sys
import io
import argparse
import math

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Bresenham's line algorithm to get pixel coordinates
def bresenham_line(x0, y0, x1, y1):
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
    x0, y0 = start
    x1, y1 = end
    points = bresenham_line(x0, y0, x1, y1)
    gray_values = []
    for (x, y) in points:
        gray_values.append(img_array[y, x])
    
    cum_dist = [0.0]
    for i in range(1, len(points)):
        x_prev, y_prev = points[i-1]
        x_curr, y_curr = points[i]
        d_pixel = math.sqrt((x_curr - x_prev)**2 + (y_curr - y_prev)**2)
        cum_dist.append(cum_dist[-1] + d_pixel)
    
    return gray_values, np.array(cum_dist)

# Core function: Calculate u_eq
def calculate_μeq(gray_values, u_min, u_max):
    normalized_gray = np.array(gray_values, dtype=float) / 255.0
    u_eq = u_min + normalized_gray * u_max
    return u_eq

# Plot function: Plot u_eq curve
def plot_μeq_curve(distances, u_eq, filename):
    plt.figure(figsize=(10, 6))
    plt.plot(distances, u_eq, 'b-', linewidth=2)
    plt.xlabel('Distance from Start Point (mm)')
    plt.ylabel('Equivalent Displacement (u_eq)')
    plt.title('Displacement Variation Along Measurement Line')
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(filename, format='tiff', dpi=300)
    plt.close()

# Main program execution
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-image_dir', type=str, required=True, help='Path to input image')
    parser.add_argument('-resolution', type=float, required=True, help='Image resolution (mm/pixel)')
    args = parser.parse_args()
    
    # Fixed parameters
    start_point = (152, 29)
    end_point = (136, 91)
    u_max = 65000
    u_min = 0
    
    # Output directory
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T2S2\1.0\backup3"
    os.makedirs(output_dir, exist_ok=True)
    
    # Process image
    img = Image.open(args.image_dir).convert('L')
    img_array = np.array(img)
    base_name = os.path.splitext(os.path.basename(args.image_dir))[0]
    
    # Get grayscale values and cumulative distances
    gray_values, cum_pixel_dist = get_line_grayscale(img_array, start_point, end_point)
    cum_real_dist = cum_pixel_dist * args.resolution
    
    # Calculate line length (Euclidean distance between endpoints)
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]
    line_length = math.sqrt(dx**2 + dy**2) * args.resolution
    
    # Save outputs
    gray_csv = os.path.join(output_dir, f"{base_name}_gray_values.csv")
    np.savetxt(gray_csv, gray_values, fmt='%d', delimiter=',')
    
    len_txt = os.path.join(output_dir, f"{base_name}_length.txt")
    with open(len_txt, 'w') as f:
        f.write(f"{line_length:.4f}")
    
    u_eq = calculate_μeq(gray_values, u_min, u_max)
    ueq_csv = os.path.join(output_dir, f"{base_name}_u_eq.csv")
    np.savetxt(ueq_csv, np.column_stack((cum_real_dist, u_eq)), 
               delimiter=',', header="Distance (mm),u_eq", comments='')
    
    plot_file = os.path.join(output_dir, f"{base_name}_curve.tiff")
    plot_μeq_curve(cum_real_dist, u_eq, plot_file)

if __name__ == '__main__':
    main()
