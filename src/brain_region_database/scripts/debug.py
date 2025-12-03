#!/usr/bin/env python

import re

import numpy as np
import pyvista as pv

from brain_region_database.database.conversions import create_postgis_3d_geometry
from brain_region_database.scripts.insert_scan import read_scan_json


def polyhedral_to_pyvista_mesh(surface_string: str) -> pv.PolyData:
    """
    Convert a PolyhedralSurfaceZ string to a PyVista mesh.
    Properly handles vertex deduplication.
    """

    # Find all polygons
    polygon_pattern = r'\(\(\((.*?)\)\)\)'
    polygon_matches = re.findall(polygon_pattern, surface_string, re.DOTALL)
    if not polygon_matches:
        raise ValueError("No polygons found in polyhedral string.")

    # Use a dictionary to deduplicate vertices
    vertex_dict = {}  # maps (x, y, z) -> vertex index
    vertices = []     # list of unique vertices
    faces = []        # list of faces as (3, v1, v2, v3)

    for polygon_string in polygon_matches:
        # Parse coordinates
        polygon_vertices = []
        for coords_match in re.finditer(r'(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)', polygon_string):
            x, y, z = map(float, coords_match.groups())
            polygon_vertices.append((x, y, z))

        # Remove the last vertex if it's a duplicate of the first (polygon closing)
        if len(polygon_vertices) > 1 and polygon_vertices[0] == polygon_vertices[-1]:
            polygon_vertices = polygon_vertices[:-1]

        # For triangular faces, we expect exactly 3 vertices
        if len(polygon_vertices) != 3:
            # If not a triangle, triangulate it
            # For simplicity, we'll assume it's a triangle fan from the first vertex
            for i in range(1, len(polygon_vertices) - 1):
                tri_vertices = [
                    polygon_vertices[0],
                    polygon_vertices[i],
                    polygon_vertices[i + 1]
                ]
                # Create face for this triangle
                face_indices = []
                for vertex in tri_vertices:
                    if vertex not in vertex_dict:
                        vertex_dict[vertex] = len(vertices)
                        vertices.append(vertex)
                    face_indices.append(vertex_dict[vertex])

                faces.extend([3] + face_indices)
        else:
            # It's already a triangle
            face_indices = []
            for vertex in polygon_vertices:
                if vertex not in vertex_dict:
                    vertex_dict[vertex] = len(vertices)
                    vertices.append(vertex)
                face_indices.append(vertex_dict[vertex])

            faces.extend([3] + face_indices)

    if not vertices:
        raise ValueError("No vertices found")

    # Convert to numpy arrays
    vertices_array = np.array(vertices, dtype=np.float64)
    faces_array = np.array(faces, dtype=np.int32)

    return pv.PolyData(vertices_array, faces_array)


with open('demo/regions/demo_587630_V1_t1_001_regions_100.json') as file:
    scan = read_scan_json(file)

region = scan.regions[0]

file_plotter = pv.Plotter()

vertices_array = np.array(region.shape[0], dtype=np.float64)

# PyVista expects faces in format: [n, v1, v2, v3, ...]
# where n is the number of vertices in the face (3 for triangles)
faces_array = np.hstack([
    np.full((len(region.shape[1]), 1), 3),
    np.array(region.shape[1], dtype=np.int32)
]).flatten()

# Add mesh to plotter.
mesh = pv.PolyData(vertices_array, faces_array)
file_plotter.add_mesh(mesh, color='red')  # type: ignore

file_plotter.show()  # type: ignore

db_plotter = pv.Plotter()

surface_string = create_postgis_3d_geometry(region.shape[0], region.shape[1])
mesh = polyhedral_to_pyvista_mesh(surface_string)
db_plotter.add_mesh(mesh, color='red')  # type: ignore

db_plotter.show()  # type: ignore

print(region.shape)
print(surface_string)
