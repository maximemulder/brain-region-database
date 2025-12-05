#!/usr/bin/env python

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO

import numpy as np
import pyvista as pv

from brain_region_database.scan import Scan
from brain_region_database.util import generate_random_colors, print_error_exit


def read_scan_json(text: TextIO) -> Scan:
    print("Loading scan data...")
    scan_data = json.load(text)
    return Scan(**scan_data)


def visualize_file_regions(scan_data: Scan):
    print(f"Loaded scan: {scan_data.file_name}")
    print(f"Number of regions: {len(scan_data.regions)}")

    colors = generate_random_colors(len(scan_data.regions))

    plotter = pv.Plotter()

    for region_data, color in zip(scan_data.regions, colors):
        vertices_array = np.array(region_data.shape[0], dtype=np.float64)

        # PyVista expects faces in format: [n, v1, v2, v3, ...]
        # where n is the number of vertices in the face (3 for triangles)
        faces_array = np.hstack([
            np.full((len(region_data.shape[1]), 1), 3),
            np.array(region_data.shape[1], dtype=np.int32)
        ]).flatten()

        # Add mesh to plotter.
        mesh = pv.PolyData(vertices_array, faces_array)
        plotter.add_mesh(mesh, label=region_data.name, color=color)  # type: ignore

    plotter.add_legend(  # type: ignore
        bcolor=(0, 0, 0, 0.5),
        face='rectangle',
        loc='upper left',
        size=(0.2, 0.8),
    )

    plotter.show()  # type: ignore


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Insert a scan JSON into the database.'
    )

    parser.add_argument(
        'file',
        type=Path,
        help='JSON file containing the scan data. If not provided, read from the standard input.'
    )

    args = parser.parse_args()

    if args.file:
        if not args.file.exists():
            print_error_exit(f"File '{args.file}' not found.")

        with open(args.file) as file:
            scan_data = read_scan_json(file)
    else:
        scan_data = read_scan_json(sys.stdin)

    visualize_file_regions(scan_data)


if __name__ == '__main__':
    main()
