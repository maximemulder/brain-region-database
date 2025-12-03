#!/usr/bin/env python

import argparse
import re

import numpy as np
import pyvista as pv
from geoalchemy2.functions import ST_AsText
from sqlalchemy import select
from sqlalchemy.orm import Session as Database

from brain_region_database.database.engine import get_engine_session
from brain_region_database.database.models import DBScanRegion, DBScanRegionLOD
from brain_region_database.database.queries import try_get_scan_with_file_name
from brain_region_database.util import generate_random_colors, print_error_exit


def visualize_database_scan(db: Database, file_name: str, lod_level: int | None):
    scan = try_get_scan_with_file_name(db, file_name)
    if scan is None:
        return print_error_exit(f"No scan type with file name '{file_name}' found.")

    results: list[str] = list(db.execute(select(DBScanRegion.name, ST_AsText(DBScanRegionLOD.shape))  # type: ignore
        .join(DBScanRegionLOD.region)
        .where(DBScanRegion.scan == scan)
        .where(DBScanRegionLOD.level == lod_level)
    ).all())

    if results == []:
        return print_error_exit(f"No regions found for scan '{scan.file_name}' and LOD level {lod_level}.")

    colors = generate_random_colors(len(results))

    # Convert to PyVista mesh
    plotter = pv.Plotter()
    for (name, surface), color in zip(results, colors):
        mesh = polyhedral_to_pyvista_mesh(surface)
        plotter.add_mesh(mesh, label=name, color=color)  # type: ignore

    plotter.add_legend(  # type: ignore
        bcolor=(0, 0, 0, 0.5),
        face='rectangle',
        loc='upper left',
        size=(0.2, 0.8),
    )

    plotter.show()  # type: ignore


def polyhedral_to_pyvista_mesh(surface_string: str) -> pv.PolyData:
    """
    Convert a PolyhedralSurfaceZ string to a PyVista mesh.
    """

    # Find all polygons.
    polygon_pattern = r'\(\(\((.*?)\)\)\)'
    polygon_matches = re.findall(polygon_pattern, surface_string, re.DOTALL)
    if polygon_matches == []:
        return print_error_exit("No polygons found in polyhedral string.")

    vertices = []
    faces = []
    vertex_offset = 0

    for polygon_string in polygon_matches:
        # Parse the coordinates of this polygon.
        polygon_coords: list[tuple[float, float, float]] = []
        for coords_match in re.finditer(r'(-?\d+\.?\d*)\s+(-?\d+\.?\d*)\s+(-?\d+\.?\d*)', polygon_string):
            x, y, z = map(float, coords_match.groups())
            polygon_coords.append((x, y, z))  # type: ignore

        # For PyVista, we need to create triangular faces
        # Each polygon with n vertices becomes (n-2) triangles

        # Add vertices to global list
        vertices.extend(polygon_coords)  # type: ignore

        # Create triangles using fan triangulation
        n = len(polygon_coords)
        for i in range(1, n - 1):
            # PyVista format: [n, v1, v2, v3, ...] where n=3 for triangle
            faces.extend((  # type: ignore
                3,
                vertex_offset,
                vertex_offset + i,
                vertex_offset + i + 1,
            ))

        vertex_offset += n

    # Convert to numpy arrays
    vertices_array = np.array(vertices)  # type: ignore
    faces_array = np.array(faces, dtype=np.int32)

    return pv.PolyData(vertices_array, faces_array)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Visualize the regions of a scan at a given LOD."
    )

    parser.add_argument('scan',
        help="File name of the scan to analyze")

    parser.add_argument('--lod',
        type=int,
        help=(
            "The level of detail used for visualization, if not present, the native level of detail will be used if"
            " present in the database."
        ))

    args = parser.parse_args()

    db = get_engine_session()

    visualize_database_scan(db, args.scan, args.lod)


if __name__ == '__main__':
    main()
