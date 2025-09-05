#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import sys
import io
import csv
import math
import argparse

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Bresenham's line algorithm implementation
def bresenham_line(start, end):
    """Generate line coordinates using Bresenham's algorithm"""
    x0, y0 = start
    x1, y1 = end
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

# Core function: Get line grayscale values
def get_line_grayscale(image, start, end):
    """Extract grayscale values along a specified line segment"""
    line_points = bresenham_line(start, end)
    gray_values = []
    for (x, y) in line_points:
        # Ensure points are within image boundaries
        if 0 <= y < image.shape[0] and 0 <= x < image.shape[1]:
            gray_values.append(int(image[y, x]))
    return np.array(gray_values), line_points

# Core function: Calculate u_eq
def calculate_μeq(gray_values, u_min, u_max):
    """Calculate equivalent values using grayscale conversion formula"""
    return u_min + (gray_values / 255.0) * u_max

# Plot function: Plot u_eq curve
def plot_μeq_curve(distances, u_eq, output_path, image_name):
    """Generate and save u_eq curve plot"""
    plt.figure(figsize=(10, 6))
    plt.plot(distances, u_eq, 'b-', linewidth=2)
    plt.xlabel('Distance from Start Point (units)', fontsize=12)
    plt.ylabel('u_eq Value', fontsize=12)
    plt.title(f'u_eq Distribution along Line Segment\n{image_name}', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # Save as TIFF
    output_file = os.path.join(output_path, f"{image_name}_ueq_curve.tiff")
    plt.savefig(output_file, format='tiff', dpi=300)
    plt.close()
    return output_file

# Main program execution
def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Process image line segments')
    parser.add_argument('--image_dir', type=str, required=True, help='Path to input image')
    parser.add_argument('--resolution', type=float, required=True, help='Resolution value')
    args = parser.parse_args()
    
    # Hardcoded parameters from [Parameters]
    start_point = (152, 29)
    end_point = (136, 91)
    u_max = 65000
    u_min = 0
    
    # Output directory
    output_path = r"C:\Users\admin\Desktop\Python_proj\ALL_RESULT\DS\T2S2\1.0\backup"
    os.makedirs(output_path, exist_ok=True)
    
    # Extract image name for output files
    image_name = os.path.splitext(os.path.basename(args.image_dir))[0]
    
    try:
        # Load and process image
        img = Image.open(args.image_dir)
        if img.mode != 'L':
            img = img.convert('L')
        img_array = np.array(img)
        
        # Get grayscale values along the line
        gray_values, points = get_line_grayscale(img_array, start_point, end_point)
        
        # Calculate segment length in physical units
        dx = start_point[0] - end_point[0]
        dy = start_point[1] - end_point[1]
        pixel_length = math.sqrt(dx**2 + dy**2)
        phys_length = pixel_length * args.resolution
        
        # Save grayscale values to CSV
        csv_file = os.path.join(output_path, f"{image_name}_gray_values.csv")
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Gray Value'])
            for val in gray_values:
                writer.writerow([int(val)])
        
        # Save physical length to text file
        length_file = os.path.join(output_path, f"{image_name}_length.txt")
        with open(length_file, 'w') as f:
            f.write(f"{phys_length:.4f}")
        
        # Calculate u_eq values
        u_eq = calculate_μeq(gray_values, u_min, u_max)
        
        # Generate distance array (cumulative physical distance)
        distances = np.linspace(0, phys_length, len(u_eq))
        
        # Generate and save plot
        plot_file = plot_μeq_curve(distances, u_eq, output_path, image_name)
        
        # Print success messages
        print(f"Processed image: {args.image_dir}")
        print(f"Grayscale values saved to: {csv_file}")
        print(f"Physical length saved to: {length_file}")
        print(f"u_eq curve saved to: {plot_file}")
        print(f"Line segment length: {phys_length:.4f} units")
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
