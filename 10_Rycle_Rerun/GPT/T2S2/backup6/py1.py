import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import sys
import io
import argparse
import csv

# Ensure UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Parameters (to be used as defaults or overridden by command-line)
DEFAULT_IMAGE_PATH = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
DEFAULT_OUTPUT_DIR = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T2S2\1.0\backup6"
DEFAULT_START_POINT = (152, 29)
DEFAULT_END_POINT = (135, 92)
DEFAULT_RESOLUTION = 1.08  # μm/pixel
DEFAULT_U_MAX = 65535
DEFAULT_U_MIN = 0

def get_line_points(start, end):
    """Bresenham's algorithm to get all pixel coordinates between start and end (inclusive)."""
    x0, y0 = start
    x1, y1 = end
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1

    if dx > dy:
        err = dx // 2
        while x != x1:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
        points.append((x1, y1))
    else:
        err = dy // 2
        while y != y1:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
        points.append((x1, y1))
    return points

# Core function: Get line grayscale values 
def get_line_grayscale(image_path, start_point, end_point):
    # Load image and convert to grayscale
    img = Image.open(image_path)
    gray_img = img.convert('L')
    gray_array = np.array(gray_img)
    # Get points along the line
    points = get_line_points(start_point, end_point)
    # Extract grayscale values
    values = []
    for x, y in points:
        if 0 <= y < gray_array.shape[0] and 0 <= x < gray_array.shape[1]:
            values.append(gray_array[y, x])
        else:
            values.append(np.nan)
    return np.array(values, dtype=np.float32), points

# Core function: Calculate u_eq
def calculate_μeq(gray_values, u_min, u_max):
    gray_values = np.array(gray_values, dtype=np.float32)
    u_eq = u_min + (gray_values / 255.0) * (u_max - u_min)
    return u_eq

# Plot function: Plot u_eq curve
def plot_μeq_curve(distances, u_eq, out_image_path):
    plt.figure(figsize=(8, 5))
    plt.plot(distances, u_eq, color='blue', linewidth=2)
    plt.xlabel('Distance from start point (μm)')
    plt.ylabel('u_eq')
    plt.title('u_eq vs. Distance')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_image_path, dpi=300, format='tiff')
    plt.close()

# Save array to CSV
def save_array_csv(array, out_csv_path, header=None):
    with open(out_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        if header:
            writer.writerow(header)
        for val in array:
            if isinstance(val, (list, tuple, np.ndarray)):
                writer.writerow(val)
            else:
                writer.writerow([val])

# Main program execution
def main():
    parser = argparse.ArgumentParser(description="Extract line grayscale, calculate u_eq, and plot results.")
    parser.add_argument('-image_dir', type=str, default=DEFAULT_IMAGE_PATH, help='Path to input image')
    parser.add_argument('-output_dir', type=str, default=DEFAULT_OUTPUT_DIR, help='Directory for outputs')
    parser.add_argument('-resolution', type=float, default=DEFAULT_RESOLUTION, help='μm per pixel')
    parser.add_argument('-u_max', type=int, default=DEFAULT_U_MAX, help='u_max')
    parser.add_argument('-u_min', type=int, default=DEFAULT_U_MIN, help='u_min')
    parser.add_argument('--start', type=int, nargs=2, default=DEFAULT_START_POINT, help='Start point x y')
    parser.add_argument('--end', type=int, nargs=2, default=DEFAULT_END_POINT, help='End point x y')
    args = parser.parse_args()

    image_path = args.image_dir
    output_dir = args.output_dir
    resolution = args.resolution
    u_max = args.u_max
    u_min = args.u_min
    start_point = tuple(args.start)
    end_point = tuple(args.end)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    image_filename = os.path.splitext(os.path.basename(image_path))[0]

    # 1. Get grayscale values along line
    gray_values, points = get_line_grayscale(image_path, start_point, end_point)
    print(f"Grayscale values along the line: {gray_values}")

    # 2. Save grayscale values as array in CSV
    gray_csv_path = os.path.join(output_dir, f"{image_filename}_line_grayscale.csv")
    save_array_csv(gray_values, gray_csv_path, header=['GrayValue'])

    # 3. Calculate distance for each point
    distances = [np.sqrt((x - start_point[0]) ** 2 + (y - start_point[1]) ** 2) * resolution for x, y in points]
    # Calculate total length
    line_length = np.sum([np.sqrt((points[i][0] - points[i-1][0])**2 + (points[i][1] - points[i-1][1])**2) for i in range(1, len(points))]) * resolution
    print(f"Measured line segment length: {line_length:.3f} μm")

    # 4. Save measured length to txt
    length_txt_path = os.path.join(output_dir, f"{image_filename}_line_length.txt")
    with open(length_txt_path, 'w') as f:
        f.write(f"{line_length:.6f}")

    # 5. Calculate u_eq
    u_eq = calculate_μeq(gray_values, u_min, u_max)
    print(f"u_eq values: {u_eq}")

    # 6. Save distances and u_eq as CSV
    dist_ueq_csv_path = os.path.join(output_dir, f"{image_filename}_distance_u_eq.csv")
    save_array_csv(list(zip(distances, u_eq)), dist_ueq_csv_path, header=['Distance(μm)', 'u_eq'])

    # 7. Plot u_eq against distance and save as TIFF image
    tiff_image_path = os.path.join(output_dir, f"{image_filename}_u_eq_curve.tiff")
    plot_μeq_curve(distances, u_eq, tiff_image_path)
    print(f"Saved results in {output_dir}")

if __name__ == '__main__':
    main()
