import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import csv
import argparse

# Constants and parameters
image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T2S2\1.0\backup"
start_point = (152, 29)
end_point = (136, 91)
u_max = 65000
u_min = 0

def parse_args():
    parser = argparse.ArgumentParser(description="Line grayscale extraction and u_eq calculation")
    parser.add_argument('-resolution', type=float, default=0.8, help='Pixel resolution (μm/pixel)')
    return parser.parse_args()

# Core function: Get line grayscale values
def get_line_grayscale(img, start, end):
    # Bresenham's line algorithm for integer pixel coordinates
    x0, y0 = start
    x1, y1 = end
    x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
    points = []
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        points.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy
    # Get grayscale value at each point
    gray_values = []
    for (x, y) in points:
        pixel_value = img.getpixel((x, y))
        if isinstance(pixel_value, tuple):  # If RGB, convert to grayscale
            pixel_value = int(round(0.299 * pixel_value[0] + 0.587 * pixel_value[1] + 0.114 * pixel_value[2]))
        gray_values.append(pixel_value)
    return np.array(gray_values), points

# Core function: Calculate u_eq
def calculate_μeq(gray_values, u_min, u_max):
    gray_values = np.asarray(gray_values)
    u_eq = u_min + (gray_values / 255.0) * (u_max - u_min)
    return u_eq

# Plot function: Plot u_eq curve
def plot_μeq_curve(u_eq, distances, out_tiff_path):
    plt.figure(figsize=(8, 5))
    plt.plot(distances, u_eq, label='u_eq vs. distance', color='navy')
    plt.xlabel('Distance from start point (μm)')
    plt.ylabel('u_eq')
    plt.title('u_eq along line segment')
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_tiff_path, format='tiff')
    plt.close()

# Main program execution
def main():
    args = parse_args()
    resolution = args.resolution  # μm/pixel

    # Load image and convert to grayscale if needed
    img = Image.open(image_path)
    img_gray = img.convert('L')

    # Get grayscale values along the line
    gray_values, points = get_line_grayscale(img_gray, start_point, end_point)
    print(f"Grayscale values along the line: {gray_values}")

    # Calculate Euclidean distance in pixels
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]
    pixel_length = np.sqrt(dx**2 + dy**2)
    segment_length = pixel_length * resolution  # in μm
    print(f"Segment pixel length: {pixel_length}")
    print(f"Segment physical length: {segment_length:.2f} μm")

    # Calculate distances along the line (for plotting)
    x_vals = np.array([p[0] for p in points])
    y_vals = np.array([p[1] for p in points])
    distances = np.sqrt((x_vals - x_vals[0])**2 + (y_vals - y_vals[0])**2) * resolution

    # Save grayscale values to CSV
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    csv_path = os.path.join(output_dir, f"{base_name}_line_gray.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['index', 'x', 'y', 'gray_value'])
        for idx, ((x, y), gv) in enumerate(zip(points, gray_values)):
            writer.writerow([idx, x, y, gv])

    print(f"Grayscale values saved to {csv_path}")

    # Save measured segment length to text file
    length_txt_path = os.path.join(output_dir, f"{base_name}_line_length.txt")
    with open(length_txt_path, 'w') as f:
        f.write(f"Line segment length: {segment_length:.2f} μm\n")
        f.write(f"Pixel length: {pixel_length:.2f} pixels\n")
        f.write(f"Resolution: {resolution} μm/pixel\n")
    print(f"Segment length saved to {length_txt_path}")

    # Calculate u_eq
    u_eq = calculate_μeq(gray_values, u_min, u_max)
    print(f"u_eq values: {u_eq}")

    # Save u_eq values to CSV
    ueq_csv_path = os.path.join(output_dir, f"{base_name}_line_u_eq.csv")
    with open(ueq_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['distance_um', 'u_eq'])
        for dist, val in zip(distances, u_eq):
            writer.writerow([dist, val])
    print(f"u_eq values saved to {ueq_csv_path}")

    # Plot and save u_eq curve
    tiff_path = os.path.join(output_dir, f"{base_name}_u_eq_vs_distance.tiff")
    plot_μeq_curve(u_eq, distances, tiff_path)
    print(f"u_eq curve plot saved to {tiff_path}")

if __name__ == "__main__":
    main()
