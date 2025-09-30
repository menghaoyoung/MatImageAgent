import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import argparse
import csv
import tifffile

# Parameters (will be overwritten by args if provided)
start_point = (152, 29)
end_point = (135, 92)
u_max = 65535
u_min = 0

def get_line_points(start, end):
    """
    Bresenham's line algorithm. Returns all the pixel coordinates along a line.
    """
    x0, y0 = start
    x1, y1 = end
    points = []
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy
    return points

def get_line_grayscale(img, line_points):
    """
    Extract grayscale values from the image along the line defined by line_points.
    """
    # Ensure image is grayscale
    if img.mode != 'L':
        img = img.convert('L')
    pixels = img.load()
    grayscale_values = [pixels[x, y] for (x, y) in line_points]
    return grayscale_values

def calculate_u_eq(gray_values, u_min, u_max):
    """
    Calculate u_eq for each grayscale value.
    """
    gray_arr = np.array(gray_values, dtype=np.float64)
    u_eq = u_min + (gray_arr / 255.0) * (u_max - u_min)
    return u_eq

def plot_u_eq_curve(distances, u_eq, out_tiff_path):
    """
    Plot u_eq vs. distance from start point, save as TIFF.
    """
    plt.figure(figsize=(8, 5))
    plt.plot(distances, u_eq, color='blue', linewidth=2)
    plt.xlabel('Distance from start point (μm)')
    plt.ylabel('u_eq')
    plt.title('u_eq vs. Distance')
    plt.tight_layout()
    # Save as TIFF
    plt.savefig(out_tiff_path, format='tiff')
    plt.close()

def main():
    parser = argparse.ArgumentParser(description='Extract grayscale values and calculate u_eq along a line segment in an image.')
    parser.add_argument('-image_dir', type=str, required=True, help='Path to input image')
    parser.add_argument('-resolution', type=float, required=True, help='Pixel size in μm/pixel')
    parser.add_argument('-out_dir', type=str, required=True, help='Directory to save output files')
    parser.add_argument('-u_max', type=int, default=65535, help='Maximum u value')
    parser.add_argument('-u_min', type=int, default=0, help='Minimum u value')
    parser.add_argument('-start_point', type=str, default="152,29", help='Start point as x,y')
    parser.add_argument('-end_point', type=str, default="135,92", help='End point as x,y')

    args = parser.parse_args()

    img_path = args.image_dir
    resolution = args.resolution
    out_dir = args.out_dir
    u_max = args.u_max
    u_min = args.u_min
    start_point = tuple(map(int, args.start_point.split(',')))
    end_point = tuple(map(int, args.end_point.split(',')))

    os.makedirs(out_dir, exist_ok=True)
    filename_base = os.path.splitext(os.path.basename(img_path))[0]

    print(f"Loading image from {img_path} ...")
    img = Image.open(img_path)

    # Get all points along the line
    line_points = get_line_points(start_point, end_point)
    print(f"Number of points along the line: {len(line_points)}")

    # Get grayscale values along the line
    grayscale_values = get_line_grayscale(img, line_points)
    print("First 10 grayscale values along the line:", grayscale_values[:10])

    # Save grayscale values to CSV
    gray_csv_path = os.path.join(out_dir, f"{filename_base}_grayvalues.csv")
    with open(gray_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Index', 'X', 'Y', 'GrayValue'])
        for idx, ((x, y), g) in enumerate(zip(line_points, grayscale_values)):
            writer.writerow([idx, x, y, g])
    print(f"Grayscale values saved to {gray_csv_path}")

    # Calculate physical length of the segment
    dx = (end_point[0] - start_point[0])
    dy = (end_point[1] - start_point[1])
    pixel_length = np.sqrt(dx**2 + dy**2)
    physical_length = pixel_length * resolution
    length_txt_path = os.path.join(out_dir, f"{filename_base}_length.txt")
    with open(length_txt_path, 'w') as f:
        f.write(f"{physical_length}\n")
    print(f"Measured line segment length: {physical_length:.3f} μm (saved to {length_txt_path})")

    # Calculate distances for each point
    distances = [np.sqrt((x - start_point[0])**2 + (y - start_point[1])**2) * resolution for (x, y) in line_points]

    # Calculate u_eq
    u_eq = calculate_u_eq(grayscale_values, u_min, u_max)
    print("First 10 u_eq values:", u_eq[:10])

    # Save distances and u_eq to CSV
    ueq_csv_path = os.path.join(out_dir, f"{filename_base}_distance_ueq.csv")
    with open(ueq_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Index', 'Distance_μm', 'u_eq'])
        for idx, (d, u) in enumerate(zip(distances, u_eq)):
            writer.writerow([idx, d, u])
    print(f"Distances and u_eq values saved to {ueq_csv_path}")

    # Plot u_eq vs distance and save as TIFF
    tiff_path = os.path.join(out_dir, f"{filename_base}_ueq_vs_distance.tiff")
    plot_u_eq_curve(distances, u_eq, tiff_path)
    print(f"u_eq vs. distance plot saved as TIFF: {tiff_path}")

if __name__ == '__main__':
    main()
