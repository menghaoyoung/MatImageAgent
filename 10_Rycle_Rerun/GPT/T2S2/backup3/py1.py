import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import csv

# Parameters (can be overridden by arguments)
start_point = (152, 29)
end_point = (135, 92)
u_max = 65535
u_min = 0

# Input/output paths
image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T2S2\1.0\backup3"

def get_line_points(start, end):
    """Bresenham's Line Algorithm to get all points along a line."""
    x1, y1 = start
    x2, y2 = end
    points = []
    dx = abs(x2 - x1)
    dy = -abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx + dy
    while True:
        points.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x1 += sx
        if e2 <= dx:
            err += dx
            y1 += sy
    return points

def get_line_grayscale(img: np.ndarray, start, end):
    points = get_line_points(start, end)
    gray_values = []
    for (x, y) in points:
        gray_values.append(img[y, x])  # Note: numpy array is [row, col] = [y, x]
    return np.array(gray_values), points

def calculate_μeq(gray_values: np.ndarray, u_min, u_max) -> np.ndarray:
    return u_min + (gray_values.astype(np.float32) / 255) * (u_max - u_min)

def plot_μeq_curve(distances, μeq, filename):
    plt.figure(figsize=(7, 5))
    plt.plot(distances, μeq, '-o', markersize=2)
    plt.xlabel('Distance from start (μm)')
    plt.ylabel(r'$u_{eq}$')
    plt.title(r'$u_{eq}$ vs. Distance')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename, format='tiff', dpi=300)
    plt.close()

def save_csv(filename, header, rows):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

def save_length_txt(filename, length):
    with open(filename, 'w') as f:
        f.write(f'Line segment length: {length:.2f} μm\n')

def main():
    parser = argparse.ArgumentParser(description='Process image line grayscale and calculate μeq.')
    parser.add_argument('-image_dir', type=str, default=image_path, help='Path to input image')
    parser.add_argument('-resolution', type=float, default=1.08, help='Image resolution in μm/pixel')
    parser.add_argument('-u_max', type=int, default=u_max, help='Maximum u_eq')
    parser.add_argument('-u_min', type=int, default=u_min, help='Minimum u_eq')
    parser.add_argument('-output_dir', type=str, default=output_dir, help='Output directory')
    parser.add_argument('-start_point', type=int, nargs=2, default=start_point, help='Start point (x y)')
    parser.add_argument('-end_point', type=int, nargs=2, default=end_point, help='End point (x y)')
    args = parser.parse_args()

    # Prepare output names
    img_filename = os.path.splitext(os.path.basename(args.image_dir))[0]
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
    gray_csv = os.path.join(args.output_dir, f"{img_filename}_gray_values.csv")
    length_txt = os.path.join(args.output_dir, f"{img_filename}_length.txt")
    μeq_tiff = os.path.join(args.output_dir, f"{img_filename}_μeq_curve.tiff")
    μeq_csv = os.path.join(args.output_dir, f"{img_filename}_μeq_values.csv")

    # Load image and convert to grayscale if needed
    img = Image.open(args.image_dir)
    if img.mode != 'L':
        img = img.convert('L')
    img_np = np.array(img)

    # Get grayscale values along the line
    gray_values, points = get_line_grayscale(img_np, tuple(args.start_point), tuple(args.end_point))
    print(f"Grayscale values along the line: {gray_values}")

    # Calculate physical distance for each point
    xs, ys = zip(*points)
    distances = [0.0]
    for i in range(1, len(points)):
        dx = xs[i] - xs[i-1]
        dy = ys[i] - ys[i-1]
        pixel_dist = (dx**2 + dy**2)**0.5
        distances.append(distances[-1] + pixel_dist * args.resolution)
    total_length = distances[-1]
    print(f"Line segment length: {total_length:.2f} μm")

    # Save grayscale values to CSV
    gray_rows = [['x', 'y', 'gray_value']]
    for (x, y), g in zip(points, gray_values):
        gray_rows.append([x, y, g])
    save_csv(gray_csv, gray_rows[0], gray_rows[1:])
    print(f"Saved grayscale values to {gray_csv}")

    # Save length to txt
    save_length_txt(length_txt, total_length)
    print(f"Saved length to {length_txt}")

    # Calculate μeq
    μeq = calculate_μeq(gray_values, args.u_min, args.u_max)
    print(f"Calculated μeq: {μeq}")

    # Save distance and μeq to CSV
    μeq_rows = [['distance_μm', 'μeq']]
    for d, u in zip(distances, μeq):
        μeq_rows.append([d, u])
    save_csv(μeq_csv, μeq_rows[0], μeq_rows[1:])
    print(f"Saved μeq and distances to {μeq_csv}")

    # Plot μeq vs distance and save as TIFF
    plot_μeq_curve(distances, μeq, μeq_tiff)
    print(f"Saved μeq curve plot to {μeq_tiff}")

if __name__ == '__main__':
    main()
