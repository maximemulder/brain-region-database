#!/usr/bin/env python

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO

from brain_region_database.database.engine import get_engine_session
from brain_region_database.database.models import DBScanRegion
from brain_region_database.database.queries import (
    insert_scan,
    insert_scan_region,
    insert_scan_region_lod,
    try_get_scan_region_lod_with_region_and_level,
    try_get_scan_region_with_scan_and_name,
    try_get_scan_with_name,
)
from brain_region_database.scan import Scan
from brain_region_database.util import print_error_exit


def read_scan_json(text: TextIO) -> Scan:
    print("Loading scan data...")
    scan_data = json.load(text)
    return Scan(**scan_data)


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

    print(f"Loaded scan: {scan_data.file_name}")
    print(f"Number of regions: {len(scan_data.regions)}")

    db = get_engine_session()

    scan = try_get_scan_with_name(db, scan_data.file_name)
    if scan is not None:
        print(f"Scan '{scan.file_name}' already present in the database.")
    else:
        print("Inserting scan into the database...")
        scan = insert_scan(db, scan_data)
        print(f"Successfully inserted scan with ID: {scan.id}")

    regions: list[DBScanRegion] = []
    for region_data in scan_data.regions:
        region = try_get_scan_region_with_scan_and_name(db, scan, region_data.name)
        if region is not None:
            print(f"Region '{region.name}' already present in the database for that scan.")
        else:
            print("Inserting scan region into the database...")
            region = insert_scan_region(db, scan, region_data)
            print(f"Successfully inserted scan region with ID: {region.id}")

        regions.append(region)

    for region, region_data in zip(regions, scan_data.regions):
        lod = try_get_scan_region_lod_with_region_and_level(db, region, region_data.lod_level)
        if lod is not None:
            print(f"Region LOD '{lod.region.name}' ('{lod.level}') already present in the database for that scan.")
        else:
            print("Inserting scan region LOD into the database...")
            lod = insert_scan_region_lod(db, region, region_data)
            print(f"Successfully inserted scan region LOD with ID: {lod.id}")

    db.commit()


if __name__ == '__main__':
    main()
