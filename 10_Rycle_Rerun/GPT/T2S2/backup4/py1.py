import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import argparse
import csv
import tifffile

# Parameters (as specified)
start_point = (152, 29)
end_point = (135, 92)
u_max = 65535
u_min = 0

# Input/output paths
image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
output_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T2S2\1.0\backup4"

def get_line_points(start, end):
    """Bresenham's Line Algorithm for pixel coordinates between two points."""
    x0, y0 = start
    x1, y1 = end
    points = []
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1
    swapped = False
    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0
        swapped = True
    dx = x1 - x0
    dy = abs(y1 - y0)
    error = int(dx / 2)
    ystep = 1 if y0 < y1 else -1
    y = y0
    for x in range(x0, x1 + 1):
        coord = (y, x) if steep else (x, y)
        points.append(coord)
        error -= dy
        if error < 0:
            y += ystep
            error += dx
    if swapped:
        points.reverse()
    return points

def get_line_grayscale(image, start, end):
    points = get_line_points(start, end)
    gray_values = []
    for x, y in points:
        gray = image[y, x]  # Note y, x due to numpy image indexing
        gray_values.append(gray)
    gray_values = np.array(gray_values)
    return gray_values, points

def calculate_distance_between_points(start, end, resolution):
    # Euclidean distance in pixels
    dist_px = np.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
    dist_um = dist_px * resolution
    return dist_um, dist_px

def calculate_μeq(gray_values, u_min, u_max):
    # gray_values: numpy array, 0~255
    u_eq = u_min + (gray_values / 255) * (u_max - u_min)
    return u_eq

def plot_μeq_curve(distances, u_eq, tiff_path):
    plt.figure(figsize=(8,5))
    plt.plot(distances, u_eq, marker='o', linestyle='-')
    plt.xlabel('Distance from Start (μm)')
    plt.ylabel('u_eq')
    plt.title('u_eq vs. Distance')
    plt.tight_layout()
    # Save as TIFF
    plt.savefig(tiff_path, format='tiff')
    plt.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-resolution', type=float, default=1.08, help='Image resolution (μm/pixel)')
    args = parser.parse_args()
    resolution = args.resolution

    # Read image
    img = Image.open(image_path).convert('L')  # grayscale
    img_np = np.array(img)
    print(f"Loaded image shape: {img_np.shape}")

    # Get grayscale values along the line
    gray_values, points = get_line_grayscale(img_np, start_point, end_point)
    print(f"Extracted {len(gray_values)} grayscale values along the line.")

    # Save grayscale values as CSV
    image_filename = os.path.splitext(os.path.basename(image_path))[0]
    gray_csv_path = os.path.join(output_dir, f"{image_filename}_gray_values.csv")
    os.makedirs(output_dir, exist_ok=True)
    with open(gray_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Index', 'X', 'Y', 'GrayValue'])
        for idx, ((x, y), gray) in enumerate(zip(points, gray_values)):
            writer.writerow([idx, x, y, gray])
    print(f"Saved grayscale values to {gray_csv_path}")

    # Calculate and save line segment length
    length_um, length_px = calculate_distance_between_points(start_point, end_point, resolution)
    length_txt_path = os.path.join(output_dir, f"{image_filename}_line_length.txt")
    with open(length_txt_path, 'w') as f:
        f.write(f"Line segment length: {length_um:.3f} μm ({length_px:.2f} px)\n")
    print(f"Saved line segment length to {length_txt_path}")

    # Calculate u_eq
    u_eq = calculate_μeq(gray_values, u_min, u_max)
    print(f"Calculated u_eq for all points.")

    # Calculate distances from start_point for each point
    points_arr = np.array(points)
    distances_px = np.sqrt((points_arr[:,0]-start_point[0])**2 + (points_arr[:,1]-start_point[1])**2)
    distances_um = distances_px * resolution

    # Save u_eq and distances as CSV
    ueq_csv_path = os.path.join(output_dir, f"{image_filename}_distance_u_eq.csv")
    with open(ueq_csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Index', 'Distance_um', 'u_eq'])
        for idx, (d, u) in enumerate(zip(distances_um, u_eq)):
            writer.writerow([idx, d, u])
    print(f"Saved u_eq and distances to {ueq_csv_path}")

    # Plot and save u_eq curve as TIFF
    tiff_path = os.path.join(output_dir, f"{image_filename}_u_eq_curve.tiff")
    plot_μeq_curve(distances_um, u_eq, tiff_path)
    print(f"Saved u_eq curve to {tiff_path}")

if __name__ == "__main__":
    main()
