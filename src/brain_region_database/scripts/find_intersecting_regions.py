import argparse

from geoalchemy2.functions import ST_3DDWithin, ST_3DIntersects
from sqlalchemy import select
from sqlalchemy.orm import Session as Database
from sqlalchemy.orm import aliased

from brain_region_database.database.engine import get_engine_session
from brain_region_database.database.models import DBScan, DBScanRegion, DBScanRegionLOD
from brain_region_database.database.monitor import DatabaseMonitor
from brain_region_database.database.queries import get_scan_regions_lod_with_scan_and_level
from brain_region_database.util import print_error_exit


def find_intersecting_regions(db: Database, scan_file_name: str, lod_level: int | None, epsilon: float | None):
    """
    Find all the regions within an epsilon distance of each other.
    """

    DatabaseMonitor(db)

    scan = db.execute(select(DBScan).where(DBScan.file_name == scan_file_name)).scalar_one_or_none()

    if scan is None:
        return print_error_exit(f"No scan found for file name '{scan_file_name}'.")

    print(f"Found scan: '{scan_file_name}' (ID: {scan.id})")

    if scan.regions == []:
        return print_error_exit(f"No regions found for scan '{scan.file_name}'.")

    print(f"Found {len(scan.regions)} regions for scan '{scan.file_name}'.")

    region_lods = get_scan_regions_lod_with_scan_and_level(db, scan, lod_level)

    if region_lods == []:
        return print_error_exit(f"No regions LOD found for scan '{scan.file_name}' and LOD level {lod_level}.")

    print(f"Found {len(region_lods)} regions LOD for scan '{scan.file_name}' and LOD level {lod_level}.")

    db_scan_region_a = aliased(DBScanRegion)
    db_scan_region_b = aliased(DBScanRegion)
    db_scan_region_lod_a = aliased(DBScanRegionLOD)
    db_scan_region_lod_b = aliased(DBScanRegionLOD)

    results = db.execute(
        select(
            db_scan_region_a.id.label('region_a_id'),
            db_scan_region_a.name.label('region_a'),
            db_scan_region_b.id.label('region_b_id'),
            db_scan_region_b.name.label('region_b'),
        )
        .select_from(DBScan)
        .join(db_scan_region_a, db_scan_region_a.scan_id == DBScan.id)
        .join(db_scan_region_b, db_scan_region_b.scan_id == DBScan.id)
        .join(db_scan_region_lod_a, db_scan_region_lod_a.region_id == db_scan_region_a.id)
        .join(db_scan_region_lod_b, db_scan_region_lod_b.region_id == db_scan_region_b.id)
        .where(
            DBScan.id == scan.id,
            db_scan_region_a.id < db_scan_region_b.id,  # Avoid self-comparison and duplicates.
            db_scan_region_lod_a.level == lod_level,
            db_scan_region_lod_b.level == lod_level,
            ST_3DDWithin(db_scan_region_lod_a.shape, db_scan_region_lod_b.shape, epsilon)
            if epsilon is not None else
            ST_3DIntersects(db_scan_region_lod_a.shape, db_scan_region_lod_b.shape),
        )
    ).all()

    print(f"Found {len(results)} intersecting region pairs:")
    for result in results:
        print(f"  {result.region_a} (ID: {result.region_a_id}) <-> {result.region_b} (ID: {result.region_b_id})")


# Command line interface
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find regions intersecting within a given distance in a brain scan."
    )

    parser.add_argument('scan',
        help="File name of the scan to analyze")

    parser.add_argument('--lod',
        type=int,
        help=(
            "The level of detail used for comparison, if not present, the native level of detail will be used if"
            " present in the database."
        ))

    parser.add_argument('--epsilon',
        type=float,
        help="Distance threshold, if present, use 'ST_3DDWithin' to compare regions, if not, use 'ST_3DIntersects'.")

    args = parser.parse_args()

    db = get_engine_session()

    find_intersecting_regions(db, args.scan, args.lod, args.epsilon)


if __name__ == "__main__":
    main()
