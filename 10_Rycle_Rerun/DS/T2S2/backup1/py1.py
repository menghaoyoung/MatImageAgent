import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import sys
import io
import math
import argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Bresenham's line algorithm to get pixel coordinates
def bresenham_line(start, end):
    x0, y0 = start
    x1, y1 = end
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    line_pixels = []
    
    while True:
        line_pixels.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return line_pixels

# Get grayscale values along the line segment
def get_line_grayscale(image_array, start, end):
    points = bresenham_line(start, end)
    gray_values = []
    for (x, y) in points:
        if 0 <= y < image_array.shape[0] and 0 <= x < image_array.shape[1]:
            gray_values.append(image_array[y, x])
        else:
            gray_values.append(0)
    return gray_values, points

# Calculate equivalent values (u_eq)
def calculate_ueq(gray_values, u_min, u_max):
    gray_array = np.array(gray_values, dtype=np.float64)
    u_eq = u_min + (gray_array / 255.0) * u_max
    return u_eq

# Plot u_eq vs distance and save results
def plot_ueq_curve(distances, u_eq, base_filename, output_dir):
    plt.figure(figsize=(10, 6))
    plt.plot(distances, u_eq, 'b-', linewidth=2)
    plt.xlabel("Distance from Start Point (Physical Units)")
    plt.ylabel("u_eq Values")
    plt.title(f"u_eq Distribution along Line Segment: {base_filename}")
    plt.grid(True)
    
    plot_path = os.path.join(output_dir, f"{base_filename}_plot.tiff")
    plt.savefig(plot_path, format='tiff', dpi=300)
    plt.close()
    
    data_path = os.path.join(output_dir, f"{base_filename}_data.csv")
    np.savetxt(data_path, np.column_stack((distances, u_eq)), 
               delimiter=',', header='distance,u_eq', comments='', fmt='%.6f')

# Main program execution
def main():
    parser = argparse.ArgumentParser(description='Process image line profile.')
    parser.add_argument('-resolution', type=float, required=True, help='Physical dimension per pixel (e.g., 0.9)')
    args = parser.parse_args()
    
    # Fixed parameters
    start_point = (152, 29)
    end_point = (136, 91)
    u_min = 0
    u_max = 65000
    image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
    output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T2S2\1.0\backup1"
    
    # Create output directory if missing
    os.makedirs(output_dir, exist_ok=True)
    base_filename = os.path.splitext(os.path.basename(image_path))[0]
    
    # Load and process image
    img = Image.open(image_path).convert('L')
    img_array = np.array(img)
    
    # Calculate physical length of segment
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]
    pixel_length = math.sqrt(dx**2 + dy**2)
    physical_length = pixel_length * args.resolution
    with open(os.path.join(output_dir, f"{base_filename}_length.txt"), 'w') as f:
        f.write(f"{physical_length:.6f}")

    # Get grayscale values and distances
    gray_values, points = get_line_grayscale(img_array, start_point, end_point)
    distances = [args.resolution * math.sqrt((x-start_point[0])**2 + (y-start_point[1])**2) 
                 for (x, y) in points]
    
    # Save raw grayscale values
    gray_path = os.path.join(output_dir, f"{base_filename}_grayscale.csv")
    np.savetxt(gray_path, gray_values, delimiter=',', fmt='%d')
    
    # Calculate and save u_eq results
    u_eq = calculate_ueq(gray_values, u_min, u_max)
    plot_ueq_curve(distances, u_eq, base_filename, output_dir)

if __name__ == "__main__":
    main()
