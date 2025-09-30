import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import sys
import io
import argparse
import csv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Parameters (fixed values from task description)
start_point = (152, 29)
end_point = (136, 91)
u_max = 65000
u_min = 0
image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T2S2\1.0\backup2"

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

# Get grayscale values along a line segment
def get_line_grayscale(img, start, end):
    img_array = np.array(img)
    coords = bresenham_line(start[0], start[1], end[0], end[1])
    grays = []
    for x, y in coords:
        if 0 <= y < img_array.shape[0] and 0 <= x < img_array.shape[1]:
            grays.append(img_array[y, x])
        else:
            grays.append(0)
    return coords, np.array(grays)

# Calculate u_eq values from grayscale array
def calculate_μeq(grays, u_min, u_max):
    return u_min + (grays / 255) * u_max

# Plot u_eq curve and save data
def plot_μeq_curve(distances, u_eq, save_path, filename):
    plt.figure(figsize=(10, 6))
    plt.plot(distances, u_eq, 'b-', linewidth=2)
    plt.xlabel("Distance from Start Point (μm)")
    plt.ylabel("Equivalent Value (u_eq)")
    plt.title(f"Material Property Distribution: {filename}")
    plt.grid(True)
    
    # Save plot as TIFF
    plt.savefig(os.path.join(save_path, f"{filename}_plot.tiff"), dpi=300, format='tiff')
    plt.close()
    
    # Save data to CSV
    with open(os.path.join(save_path, f"{filename}_data.csv"), 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Distance (μm)", "u_eq"])
        for d, u in zip(distances, u_eq):
            writer.writerow([f"{d:.4f}", f"{u:.2f}"])

# Main program execution
def main():
    # Parse command-line argument for resolution
    parser = argparse.ArgumentParser()
    parser.add_argument("-resolution", type=float, required=True)
    args = parser.parse_args()
    resolution = args.resolution
    
    # Verify output directory exists
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.splitext(os.path.basename(image_path))[0]
    
    # Process image
    img = Image.open(image_path).convert('L')
    coords, grays = get_line_grayscale(img, start_point, end_point)
    
    # Calculate real-world length
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]
    pixel_length = np.sqrt(dx**2 + dy**2)
    real_length = pixel_length * resolution
    
    # Save grayscale values
    np.savetxt(os.path.join(output_dir, f"{filename}_grays.csv"), grays, fmt='%d', delimiter=',')
    
    # Save length value
    with open(os.path.join(output_dir, f"{filename}_length.txt"), 'w') as f:
        f.write(f"{real_length:.4f}")
    
    # Calculate cumulative distances
    distances = [0.0]
    for i in range(1, len(coords)):
        x1, y1 = coords[i-1]
        x2, y2 = coords[i]
        step = np.sqrt((x2 - x1)**2 + (y2 - y1)**2) * resolution
        distances.append(distances[-1] + step)
    
    # Calculate and plot u_eq
    u_eq = calculate_μeq(grays, u_min, u_max)
    plot_μeq_curve(distances, u_eq, output_dir, filename)

if __name__ == "__main__":
    main()
