import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import argparse
import csv

# ========== PARAMETERS ==========
# Constants
u_max = 65535
u_min = 0

# Default values (can be overridden by arguments)
start_point = (152, 29)
end_point = (135, 92)

# Default image path (can be overridden by arguments)
default_image_path = r"C:\Users\admin\Desktop\Python_proj\datas\T2_IMGS\Li_1.0.png"
default_out_dir = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\GPT\T2S2\1.0\backup9"

# ========== UTILITY FUNCTIONS ==========

def get_line_pixels(start, end):
    """
    Bresenham's line algorithm to get all pixel coordinates on a line segment from start to end (inclusive).
    Returns a list of (x, y) tuples.
    """
    x1, y1 = start
    x2, y2 = end
    points = []

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    x, y = x1, y1

    sx = -1 if x1 > x2 else 1
    sy = -1 if y1 > y2 else 1

    if dx > dy:
        err = dx // 2
        while x != x2:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy // 2
        while y != y2:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    points.append((x2, y2))
    return points

def get_line_grayscale(img, start, end):
    """
    For an image, get the grayscale values (0-255) along the line segment defined by start and end points.
    Returns: np.ndarray of grayscale values along the line, list of pixel coordinates [(x, y), ...]
    """
    pixels = get_line_pixels(start, end)
    gray_values = []
    for x, y in pixels:
        # Ensure within image bounds
        if 0 <= x < img.width and 0 <= y < img.height:
            val = img.getpixel((x, y))
            if isinstance(val, tuple):  # RGB or RGBA
                # Convert to grayscale
                val = int(0.299 * val[0] + 0.587 * val[1] + 0.114 * val[2])
            gray_values.append(val)
        else:
            gray_values.append(0)  # Out of bounds, set to 0
    return np.array(gray_values, dtype=np.uint8), pixels

def calculate_μeq(gray_values, u_min, u_max):
    """
    Calculate μ_eq using the formula: u_eq = u_min + (gray_values / 255) * u_max
    Returns: np.ndarray of μ_eq values
    """
    gray_values = np.array(gray_values, dtype=np.float64)
    u_eq = u_min + (gray_values / 255.0) * (u_max - u_min)
    return u_eq

def plot_μeq_curve(distances, u_eq, out_path, title='μ_eq vs. Distance'):
    """
    Plots μ_eq vs. distance and saves as a TIFF image.
    """
    plt.figure(figsize=(8,5))
    plt.plot(distances, u_eq, 'b-', linewidth=2)
    plt.xlabel('Distance from start (μm)', fontsize=14)
    plt.ylabel('μ_eq', fontsize=14)
    plt.title(title, fontsize=16)
    plt.tight_layout()
    plt.grid(True)
    plt.savefig(out_path, dpi=300, format='tiff')
    plt.close()
    print(f"μ_eq curve saved: {out_path}")

# ========== MAIN PROGRAM ==========

def main():
    parser = argparse.ArgumentParser(description="Extract line grayscale and μ_eq from image.")
    parser.add_argument('-image_dir', type=str, default=default_image_path, help='Input image path')
    parser.add_argument('-out_dir', type=str, default=default_out_dir, help='Output files directory')
    parser.add_argument('-resolution', type=float, default=1.08, help='Resolution (μm/pixel)')
    parser.add_argument('-u_max', type=int, default=u_max, help='u_max value')
    parser.add_argument('-u_min', type=int, default=u_min, help='u_min value')
    parser.add_argument('--start', type=int, nargs=2, default=list(start_point), help='Start point (x y)')
    parser.add_argument('--end', type=int, nargs=2, default=list(end_point), help='End point (x y)')
    args = parser.parse_args()

    img_path = args.image_dir
    out_dir = args.out_dir
    resolution = args.resolution
    u_max_val = args.u_max
    u_min_val = args.u_min
    start = tuple(args.start)
    end = tuple(args.end)

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    img_filename = os.path.splitext(os.path.basename(img_path))[0]
    # Output filenames
    csv_gray_path = os.path.join(out_dir, f"{img_filename}_line_gray.csv")
    txt_len_path = os.path.join(out_dir, f"{img_filename}_line_length.txt")
    csv_u_eq_path = os.path.join(out_dir, f"{img_filename}_distance_u_eq.csv")
    tiff_plot_path = os.path.join(out_dir, f"{img_filename}_u_eq_curve.tiff")

    # 1. Load image
    img = Image.open(img_path)
    img_gray = img.convert('L')

    # 2. Get gray values along the line
    gray_values, line_pixels = get_line_grayscale(img_gray, start, end)
    print(f"Extracted {len(gray_values)} grayscale values along line from {start} to {end}.")

    # 3. Save grayscale values as a CSV
    with open(csv_gray_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['x', 'y', 'gray_value'])
        for (x, y), g in zip(line_pixels, gray_values):
            writer.writerow([x, y, g])
    print(f"Grayscale values saved: {csv_gray_path}")

    # 4. Calculate line segment length (in μm)
    dx = (end[0] - start[0])
    dy = (end[1] - start[1])
    pixel_length = np.sqrt(dx ** 2 + dy ** 2)
    real_length = pixel_length * resolution
    # Save to text file
    with open(txt_len_path, 'w') as f:
        f.write(f"Line length (pixels): {pixel_length:.4f}\n")
        f.write(f"Resolution (μm/pixel): {resolution}\n")
        f.write(f"Line length (μm): {real_length:.4f}\n")
    print(f"Line segment length saved: {txt_len_path} ({real_length:.4f} μm)")

    # 5. Calculate u_eq
    u_eq = calculate_μeq(gray_values, u_min_val, u_max_val)
    print(f"u_eq calculated for {len(u_eq)} points.")

    # 6. Calculate distance from start for each point (in μm)
    x0, y0 = start
    distances = []
    for (x, y) in line_pixels:
        dist = np.sqrt((x - x0) ** 2 + (y - y0) ** 2) * resolution
        distances.append(dist)
    distances = np.array(distances, dtype=np.float64)

    # 7. Save distances and u_eq to CSV
    with open(csv_u_eq_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['distance_um', 'u_eq'])
        for d, u in zip(distances, u_eq):
            writer.writerow([d, u])
    print(f"Distance and u_eq saved: {csv_u_eq_path}")

    # 8. Plot u_eq vs. distance and save as TIFF
    plot_μeq_curve(distances, u_eq, tiff_plot_path, 
                   title=f"μ_eq vs Distance for {img_filename}")

    print("All steps completed.")

if __name__ == '__main__':
    main()
