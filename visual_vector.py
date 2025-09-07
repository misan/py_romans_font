import sys
import math
import random
import glob
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from collections import namedtuple

from romans_font import Romans

from shapely.geometry import Polygon, MultiPolygon, Point
from shapely.ops import nearest_points
import numpy as np


def most_inland_point(polygon_points, step=0.1):
    """
    Finds the most inland point of a polygon and the diameter of the largest circle
    that can fit inside it using negative buffers and distance-to-boundary check.
    This is an approximation method.
    """
    polygon = Polygon(polygon_points)
    if not polygon.is_valid:
        polygon = polygon.buffer(0)

    if polygon.is_empty:
        return (0, 0), 0

    min_x, min_y, max_x, max_y = polygon.bounds
    max_possible_radius = max(max_x - min_x, max_y - min_y) / 2.0
    last_valid_shrunken_polygon = polygon

    for r in np.arange(step, max_possible_radius + step, step):
        shrunken = polygon.buffer(-r)
        if shrunken.is_empty:
            break
        if isinstance(shrunken, MultiPolygon):
            shrunken = max(shrunken.geoms, key=lambda p: p.area)
        last_valid_shrunken_polygon = shrunken

    inland_point = last_valid_shrunken_polygon.representative_point()
    nearest = nearest_points(inland_point, polygon.boundary)[1]
    radius = inland_point.distance(nearest)

    return (inland_point.x, inland_point.y), radius * 2


def get_polygon_bbox(points):
    """Calculates the bounding box of a polygon."""
    if not points:
        return 0, 0, 0, 0
    min_x = min(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_x = max(p[0] for p in points)
    max_y = max(p[1] for p in points)
    return min_x, min_y, max_x, max_y


def parse_problem_file(file_path):
    """
    Parses the problem file to extract original piece geometries, their initial
    bounding boxes, and the bin dimensions.
    """
    original_pieces_data = {}
    with open(file_path, 'r') as f:
        lines = f.readlines()

    BinDimension = namedtuple('BinDimension', ['width', 'height'])
    bin_width, bin_height = map(float, lines[0].strip().split())
    bin_dimension = BinDimension(width=bin_width, height=bin_height)

    piece_id_counter = 1
    for line in lines[2:]:
        line = line.strip()
        if not line:
            continue
        
        points_str = line.split(' ')
        vertices = []
        for point_str in points_str:
            try:
                x_str, y_str = point_str.split(',')
                vertices.append((float(x_str), float(y_str)))
            except ValueError:
                continue
        
        if vertices:
            min_x, min_y, max_x, max_y = get_polygon_bbox(vertices)
            # The rotation pivot is the center of the piece's initial bounding box.
            pivot_x = min_x + (max_x - min_x) / 2
            pivot_y = min_y + (max_y - min_y) / 2
            original_pieces_data[piece_id_counter] = (vertices, (pivot_x, pivot_y))
            piece_id_counter += 1
            
    return bin_dimension, original_pieces_data


def parse_bin_files():
    """
    Parses all Bin-*.txt files in the current directory to get placement data.
    """
    bins_data = []
    # Glob for files and sort them numerically based on the number in the filename.
    # This correctly handles cases like Bin-1.txt, Bin-2.txt, Bin-10.txt.
    bin_files = sorted(
        glob.glob('Bin-*.txt'),
        key=lambda f: int(os.path.basename(f).replace('Bin-', '').replace('.txt', ''))
    )

    for bin_file in bin_files:
        try:
            bin_number = int(os.path.basename(bin_file).replace('Bin-', '').replace('.txt', ''))
        except ValueError:
            continue  # Skip if file name is not in the expected format

        placed_pieces = []
        with open(bin_file, 'r') as f:
            lines = f.readlines()
        
        # First line is number of pieces, we can skip it.
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split()
            if len(parts) < 3:
                continue
            
            piece_id = int(parts[0])
            rotation = float(parts[1])
            x_str, y_str = parts[2].split(',')
            x = float(x_str)
            y = float(y_str)
            
            placed_pieces.append({'id': piece_id, 'rotation': rotation, 'x': x, 'y': y})
        
        if placed_pieces:
            bins_data.append({'number': bin_number, 'placed_pieces': placed_pieces})
    
    return bins_data


def rotate_point(point, angle_degrees, center):
    """
    Rotates a point around a given center.
    """
    # Reverting to the original angle inversion, as it is necessary for the
    # visualization to correctly interpret the rotation from the packing output.
    angle_degrees = 360 - angle_degrees
    angle_rad = math.radians(angle_degrees)
    cos_theta = math.cos(angle_rad)
    sin_theta = math.sin(angle_rad)
    
    x, y = point
    cx, cy = center
    
    new_x = cos_theta * (x - cx) - sin_theta * (y - cy) + cx
    new_y = sin_theta * (x - cx) + cos_theta * (y - cy) + cy
    
    return new_x, new_y

def create_packing_visual_pdf(bins_data, bin_dimension, original_pieces_data, file_name="nesting_visualization_from_files.pdf"):
    """
    Creates a PDF visualizing the nesting result by reading placement from files.
    """
    c = canvas.Canvas(file_name, pagesize=(bin_dimension.width + 50, bin_dimension.height + 50))
    font = Romans()
    
    # Define pastel colors with 60% opacity (alpha=0.6)
    pastel_colors = [
        colors.Color(0.9569, 0.7608, 0.7608, alpha=0.6),  # Light Pink
        colors.Color(0.7608, 0.9569, 0.7608, alpha=0.6),  # Light Green
        colors.Color(0.7608, 0.7608, 0.9569, alpha=0.6),  # Light Blue
        colors.Color(0.9569, 0.9569, 0.7608, alpha=0.6),  # Light Yellow
        colors.Color(0.9569, 0.7608, 0.9569, alpha=0.6),  # Light Purple
        colors.Color(0.7608, 0.9569, 0.9569, alpha=0.6),  # Light Cyan
        colors.Color(0.9569, 0.8471, 0.7608, alpha=0.6),  # Light Peach
        colors.Color(0.8471, 0.9569, 0.7608, alpha=0.6),  # Light Mint
        colors.Color(0.7608, 0.8471, 0.9569, alpha=0.6),  # Light Lavender
        colors.Color(0.9569, 0.7608, 0.8471, alpha=0.6),  # Light Coral
        colors.Color(1.0, 0.627, 0.478, alpha=0.6),       # Light Salmon
        colors.Color(0.686, 0.933, 0.933, alpha=0.6),       # Pale Turquoise
        colors.Color(0.941, 0.902, 0.549, alpha=0.6),       # Khaki
        colors.Color(0.847, 0.749, 0.847, alpha=0.6),       # Thistle
        colors.Color(0.596, 0.984, 0.596, alpha=0.6),       # Pale Green
        colors.Color(0.69, 0.769, 0.871, alpha=0.6),        # Light Steel Blue
        colors.Color(1.0, 0.894, 0.71, alpha=0.6),         # Moccasin
        colors.Color(0.69, 0.878, 0.902, alpha=0.6),        # Powder Blue
        colors.Color(0.98, 0.98, 0.824, alpha=0.6),        # Light Goldenrod Yellow
        colors.Color(0.855, 0.439, 0.839, alpha=0.6),       # Orchid
    ]
    # Expand the palette to handle complex layouts with many adjacent pieces, reducing color reuse.
    pastel_colors.extend([
        colors.Color(0.933, 0.823, 0.933, alpha=0.6),      # Plum
        colors.Color(0.96, 0.80, 0.69, alpha=0.6),         # Light Tan
        colors.Color(0.529, 0.808, 0.922, alpha=0.6),      # Sky Blue
        colors.Color(0.87, 0.95, 0.7, alpha=0.6),          # Light Lime
        colors.Color(1.0, 0.75, 0.79, alpha=0.6),          # Pink
        colors.Color(0.8, 0.9, 0.9, alpha=0.6),            # Light Teal
        colors.Color(0.9, 0.9, 0.8, alpha=0.6),            # Beige
        colors.Color(1.0, 0.84, 0.0, alpha=0.6),           # Gold
        colors.Color(0.74, 0.83, 0.9, alpha=0.6),          # Light Periwinkle
        colors.Color(0.9, 0.7, 0.7, alpha=0.6),            # Dusty Rose
    ])
    for bin_info in bins_data:
        print(f"Drawing Bin {bin_info['number']}...")
        c.setPageSize((bin_dimension.width + 50, bin_dimension.height + 50))
        c.setStrokeColor(colors.lightgrey)
        c.translate(25, 48)
        c.rect(0, 0, bin_dimension.width, bin_dimension.height)
        
        # --- Pre-computation for coloring ---
        all_final_vertices = []
        all_polygons = []
        for piece_info in bin_info['placed_pieces']:
            piece_id = piece_info['id']
            if piece_id not in original_pieces_data:
                all_final_vertices.append(None)
                all_polygons.append(None)
                continue

            # --- Transformation Logic ---
            original_vertices, rotation_pivot = original_pieces_data[piece_id]
            rotation_angle = piece_info['rotation']
            rotated_vertices = [rotate_point(p, rotation_angle, rotation_pivot) for p in original_vertices]
            final_placed_x = piece_info['x']
            final_placed_y = piece_info['y']
            rotated_min_x, rotated_min_y, _, _ = get_polygon_bbox(rotated_vertices)
            translation_x = final_placed_x - rotated_min_x
            translation_y = final_placed_y - rotated_min_y
            final_vertices = [(p[0] + translation_x, p[1] + translation_y) for p in rotated_vertices]
            
            all_final_vertices.append(final_vertices)
            polygon = Polygon(final_vertices)
            if not polygon.is_valid:
                polygon = polygon.buffer(0)
            all_polygons.append(polygon)

        # --- Adjacency Graph and Coloring ---
        num_pieces = len(all_polygons)
        adjacency_list = [[] for _ in range(num_pieces)]
        for i in range(num_pieces):
            if all_polygons[i] is None or all_polygons[i].is_empty:
                continue
            for j in range(i + 1, num_pieces):
                if all_polygons[j] is None or all_polygons[j].is_empty:
                    continue
                # Use distance check with a small tolerance to find adjacent pieces.
                # This is more robust than buffer().intersects() for floating point inaccuracies.
                # Increased tolerance to catch pieces that are visually close but not perfectly touching.
                if all_polygons[i].distance(all_polygons[j]) < 1.0:
                    adjacency_list[i].append(j)
                    adjacency_list[j].append(i)

        # --- Degree-based Greedy Coloring ---
        # A more sophisticated greedy coloring. By coloring the nodes with the highest
        # degree (most neighbors) first, we are more likely to find an optimal coloring
        # and avoid running out of palette colors for complex layouts. This approach is
        # deterministic and generally more effective than a random-order coloring.
        piece_to_color_map = {}  # Maps piece index to a reportlab color object

        # Calculate the degree of each piece (number of neighbors)
        degrees = [(i, len(adj)) for i, adj in enumerate(adjacency_list)]
        # Sort pieces by degree in descending order
        sorted_piece_indices = [i for i, degree in sorted(degrees, key=lambda x: x[1], reverse=True)]

        for i in sorted_piece_indices:
            # Get the actual color objects of already-colored neighbors
            neighbor_colors = {piece_to_color_map.get(neighbor) for neighbor in adjacency_list[i] if neighbor in piece_to_color_map}

            # Find colors from the palette that are not used by neighbors
            available_colors = [c for c in pastel_colors if c not in neighbor_colors]

            if not available_colors:
                # This case occurs if a piece is adjacent to more pieces than there are available colors.
                # We must reuse a color. We'll pick one at random and print a warning.
                print(f"  - Warning: Could not find a unique color for a piece (index {i}). The palette might be too small for this complex layout. Assigning a random color.")
                chosen_color = random.choice(pastel_colors)
            else:
                # From the non-clashing colors, pick one at random to ensure better color distribution
                # and avoid the "fewer colors" look of a purely deterministic choice.
                chosen_color = random.choice(available_colors)
            piece_to_color_map[i] = chosen_color

        # --- Drawing Loop ---
        for i, piece_info in enumerate(bin_info['placed_pieces']):
            final_vertices = all_final_vertices[i]
            piece_id = piece_info['id']
            if final_vertices is None:
                print(f"  - Warning: Could not find original geometry for Piece ID: {piece_id}")
                continue

            # --- Drawing Logic ---
            p = c.beginPath()
            p.moveTo(final_vertices[0][0], final_vertices[0][1])
            for point in final_vertices[1:]:
                p.lineTo(point[0], point[1])
            p.close()
            
            # Assign color based on our new mapping.
            if i in piece_to_color_map:
                c.setFillColor(piece_to_color_map[i])
            else:
                # Fallback for any piece that wasn't colored (should not happen with current logic)
                c.setFillColor(colors.grey)
            c.setStrokeColor(colors.darkgrey)
            c.setLineWidth(1)
            c.drawPath(p, fill=1, stroke=1)

            final_centroid, size = most_inland_point(final_vertices, 10)
            c.setFillColor(colors.black)
            
            text = str(piece_id)
            font.scale = size / 80
            text_width = font.get_string_length(text)
            paths = font.get_string(text)
            c.setStrokeColor(colors.black)
            c.setLineWidth(1)
            x_offset = final_centroid[0] - text_width / 2
            y_offset = final_centroid[1] - 10 * font.scale

            for path in paths:
                p = c.beginPath()
                p.moveTo(path[0][0] + x_offset, path[0][1] + y_offset)
                for point in path[1:]:
                    p.lineTo(point[0] + x_offset, point[1] + y_offset)
                c.drawPath(p)

        c.showPage()

    print(f"\nSaving PDF to {file_name}...")
    c.save()
    print("PDF saved successfully.")


def main():
    print("--- Visualizing Nesting from Bin Files ---")
    
    if len(sys.argv) < 2:
        print("Usage: python visual_vector.py <original_problem_file>")
        print("Example: python visual_vector.py samples/S266.txt")
        sys.exit(1)
        
    input_file = sys.argv[1]
        
    try:
        bin_dimension, original_pieces_data = parse_problem_file(input_file)
    except FileNotFoundError:
        print(f"Error: Original problem file not found at '{input_file}'")
        sys.exit(1)

    print(f"Loaded {len(original_pieces_data)} original piece geometries from {input_file}.")
    print(f"Bin dimensions: {bin_dimension.width}x{bin_dimension.height}")

    print("\nSearching for packing result files (Bin-*.txt)...")
    bins_data = parse_bin_files()
    if not bins_data:
        print("\n[ERROR] No packing data found. Cannot generate PDF.")
        print("Reason: No files matching 'Bin-*.txt' were found, or the files were empty/malformed.")
        print(f"Please ensure that the packing result files (e.g., 'Bin-1.txt') are present in the current working directory: {os.getcwd()}")
        sys.exit(1)
    print(f"Found and parsed {len(bins_data)} bin result file(s).")

    output_filename = "nesting_visualization_from_files.pdf"
    create_packing_visual_pdf(bins_data, bin_dimension, original_pieces_data, file_name=output_filename)


if __name__ == "__main__":
    main()