import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import csv
import tifffile
import sys
import io

# Ensure utf-8 output for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Parameters (can be overridden by CLI)
DEFAULT_IMAGE_PATH = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
DEFAULT_OUTPUT_DIR = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T2S2\1.0\backup5"
DEFAULT_START_POINT = (152, 29)
DEFAULT_END_POINT = (135, 92)
DEFAULT_U_MAX = 65535
DEFAULT_U_MIN = 0

def parse_args():
    parser = argparse.ArgumentParser(description="Line profile extraction and u_eq calculation from image.")
    parser.add_argument('-image_dir', type=str, default=DEFAULT_IMAGE_PATH,
                        help='Path to input image file.')
    parser.add_argument('-output_dir', type=str, default=DEFAULT_OUTPUT_DIR,
                        help='Directory to save output files.')
    parser.add_argument('-start', type=int, nargs=2, default=DEFAULT_START_POINT,
                        help='Start point (x y) of line segment.')
    parser.add_argument('-end', type=int, nargs=2, default=DEFAULT_END_POINT,
                        help='End point (x y) of line segment.')
    parser.add_argument('-resolution', type=float, required=True,
                        help='Image resolution in microns per pixel.')
    parser.add_argument('-u_max', type=int, default=DEFAULT_U_MAX,
                        help='Maximum u_eq value.')
    parser.add_argument('-u_min', type=int, default=DEFAULT_U_MIN,
                        help='Minimum u_eq value.')
    args = parser.parse_args()
    return args

# Bresenham's line algorithm to get all pixel coordinates between two points
def get_line_pixels(start, end):
    x0, y0 = start
    x1, y1 = end
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1
    if dx > dy:
        err = dx / 2.0
        while x != x1:
            points.append( (x, y) )
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
        points.append( (x, y) )
    else:
        err = dy / 2.0
        while y != y1:
            points.append( (x, y) )
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
        points.append( (x, y) )
    return points

# Core function: Get line grayscale values
def get_line_grayscale(image, start, end):
    points = get_line_pixels(start, end)
    gray_values = []
    for (x, y) in points:
        # Image uses (x,y) but numpy is [y][x]
        gray = image[y, x]
        gray_values.append(gray)
    gray_values = np.array(gray_values, dtype=np.uint8)
    return points, gray_values

# Core function: Calculate u_eq
def calculate_μeq(gray_values, u_min, u_max):
    u_eq = u_min + (gray_values.astype(np.float64) / 255.0) * (u_max - u_min)
    return u_eq

# Plot function: Plot u_eq curve
def plot_μeq_curve(distances, u_eq, output_path_tiff):
    plt.figure(figsize=(8, 5), dpi=100)
    plt.plot(distances, u_eq, color='b', linewidth=2)
    plt.xlabel('Distance from Start Point (μm)')
    plt.ylabel('u_eq')
    plt.title('u_eq vs Distance')
    plt.tight_layout()
    # Save as TIFF
    plt.savefig(output_path_tiff, format='tiff')
    plt.close()

def main():
    args = parse_args()
    image_path = args.image_dir
    output_dir = args.output_dir
    start_point = tuple(args.start)
    end_point = tuple(args.end)
    resolution = args.resolution
    u_max = args.u_max
    u_min = args.u_min

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get base filename without extension
    base_filename = os.path.splitext(os.path.basename(image_path))[0]

    print(f"Reading image: {image_path}")
    img = Image.open(image_path).convert('L')  # Convert to grayscale
    img_np = np.array(img)
    print(f"Image shape: {img_np.shape}")

    print(f"Extracting line from {start_point} to {end_point}")
    line_points, gray_values = get_line_grayscale(img_np, start_point, end_point)
    print(f"Total points along line: {len(line_points)}")

    # Save grayscale values to CSV
    gray_csv_path = os.path.join(output_dir, f"{base_filename}_line_gray.csv")
    with open(gray_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['X', 'Y', 'GrayValue'])
        for (x, y), g in zip(line_points, gray_values):
            writer.writerow([x, y, int(g)])
    print(f"Grayscale values saved to: {gray_csv_path}")

    # Calculate length of the line segment (in microns)
    pixel_length = np.sqrt( (start_point[0]-end_point[0])**2 + (start_point[1]-end_point[1])**2 )
    length_microns = pixel_length * resolution
    length_txt_path = os.path.join(output_dir, f"{base_filename}_line_length.txt")
    with open(length_txt_path, 'w') as f:
        f.write(f"Line segment length: {length_microns:.4f} μm\n")
    print(f"Line length saved to: {length_txt_path}")

    # Calculate distance along the line (from start point, in microns)
    distances = np.arange(len(line_points)) * resolution

    # Calculate u_eq
    u_eq = calculate_μeq(gray_values, u_min, u_max)

    # Save distance and u_eq to CSV
    ueq_csv_path = os.path.join(output_dir, f"{base_filename}_line_ueq.csv")
    with open(ueq_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Distance(um)', 'u_eq'])
        for d, u in zip(distances, u_eq):
            writer.writerow([f"{d:.4f}", f"{u:.4f}"])
    print(f"u_eq and distances saved to: {ueq_csv_path}")

    # Plot and save u_eq curve as TIFF
    tiff_path = os.path.join(output_dir, f"{base_filename}_ueq_curve.tiff")
    plot_μeq_curve(distances, u_eq, tiff_path)
    print(f"u_eq vs distance plot saved as TIFF to: {tiff_path}")

if __name__ == '__main__':
    main()
