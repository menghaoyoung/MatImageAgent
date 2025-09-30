import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import sys
import io
import argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Fixed parameters
start_point = (152, 29)
end_point = (135, 92)
u_max = 65535
u_min = 0
image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T2S2\1.0\backup7"

def get_line_points(start, end):
    """Generate integer coordinates along a straight line using Bresenham's algorithm."""
    x0, y0 = start
    x1, y1 = end
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    points = []
    
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

def get_line_grayscale(img_array, points):
    """Extract grayscale values along a line segment."""
    gray_values = []
    for (x, y) in points:
        gray_values.append(img_array[y, x])
    return np.array(gray_values)

def calculate_ueq(gray_values):
    """Calculate equivalent displacement (u_eq) from grayscale values."""
    return u_min + (gray_values / 255.0) * u_max

def plot_ueq_curve(distances, ueq, output_file):
    """Plot u_eq versus distance and save as TIFF."""
    plt.figure(figsize=(10, 6))
    plt.plot(distances, ueq, 'b-', linewidth=2)
    plt.xlabel('Distance from Start Point (μm)', fontsize=12)
    plt.ylabel('u_eq', fontsize=12)
    plt.title('Displacement Profile Along the Line Segment', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.savefig(output_file, format='tiff', dpi=300)
    plt.close()

def main():
    # Parse command-line arguments for resolution
    parser = argparse.ArgumentParser(description='Process image line profile.')
    parser.add_argument('-resolution', type=float, default=1.08, 
                        help='Image resolution in μm/pixel (default: 1.08)')
    args = parser.parse_args()
    resolution = args.resolution
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Load and process image
    img = Image.open(image_path).convert('L')
    img_array = np.array(img)
    base_filename = os.path.splitext(os.path.basename(image_path))[0]
    
    # Generate line points and get grayscale values
    line_points = get_line_points(start_point, end_point)
    gray_values = get_line_grayscale(img_array, line_points)
    
    # Calculate geometric properties
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]
    segment_length_px = np.sqrt(dx**2 + dy**2)
    segment_length_um = segment_length_px * resolution
    
    # Save grayscale values
    gray_csv = os.path.join(output_dir, f"{base_filename}_grayscale.csv")
    np.savetxt(gray_csv, gray_values, delimiter=',', fmt='%d')
    
    # Save segment length
    length_txt = os.path.join(output_dir, f"{base_filename}_length.txt")
    with open(length_txt, 'w') as f:
        f.write(f"{segment_length_um:.4f}")
    
    # Calculate u_eq values
    ueq_values = calculate_ueq(gray_values)
    
    # Calculate cumulative distances
    distances = []
    for i, (x, y) in enumerate(line_points):
        px = x - start_point[0]
        py = y - start_point[1]
        dist_px = np.sqrt(px**2 + py**2)
        distances.append(dist_px * resolution)
    distances = np.array(distances)
    
    # Save plot and results
    plot_tiff = os.path.join(output_dir, f"{base_filename}_plot.tiff")
    plot_ueq_curve(distances, ueq_values, plot_tiff)
    
    results_csv = os.path.join(output_dir, f"{base_filename}_results.csv")
    np.savetxt(results_csv, np.column_stack((distances, ueq_values)), 
               delimiter=',', header='Distance(um),u_eq', comments='', 
               fmt='%.4f,%.2f')

if __name__ == '__main__':
    main()
