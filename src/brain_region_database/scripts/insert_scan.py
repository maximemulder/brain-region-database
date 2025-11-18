#!/usr/bin/env python

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO

from sqlalchemy.orm import Session

from brain_region_database.database.engine import get_engine
from brain_region_database.database.query import insert_scan, select_scan
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
        '--file',
        type=Path,
        help='JSON file containing the scan data. If not provided, read from the standard input.'
    )

    args = parser.parse_args()

    if args.file:
        if not args.file.exists():
            print_error_exit(f"File '{args.file}' not found.")

        with open(args.file) as file:
            scan = read_scan_json(file)
    else:
        scan = read_scan_json(sys.stdin)

    print(f"Loaded scan: {scan.file_name}")
    print(f"Number of regions: {len(scan.regions)}")

    db = Session(get_engine())

    if select_scan(db, scan.file_name) is not None:
        print_error_exit(f"Scan '{scan.file_name}' is already inserted in the database.")

    print("Inserting scan into database...")

    db_scan = insert_scan(db, scan)

    print(f"Successfully inserted scan with ID: {db_scan.id}")


if __name__ == '__main__':
    main()
