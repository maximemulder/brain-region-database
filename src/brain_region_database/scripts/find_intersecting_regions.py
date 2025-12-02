import argparse

from geoalchemy2.functions import ST_3DDWithin, ST_3DIntersects
from sqlalchemy import select
from sqlalchemy.orm import Session, aliased

from brain_region_database.database.engine import get_engine
from brain_region_database.database.models import DBScan, DBScanRegion
from brain_region_database.util import print_error_exit


def find_intersecting_regions(db: Session, scan_file_name: str, epsilon: float | None):
    """
    Find all the regions within an epsilon distance of each other. If epsilon is a number, ``
    Find all regions within epsilon distance of each other in a given scan

    Args:
        db_url: Database connection URL
        scan_file_name: Name of the scan file to analyze
        epsilon: Maximum distance threshold (in same units as your spatial data)
        use_3d_intersects: If True, use ST_3DIntersects for exact intersection,
                          else use ST_3DDWithin for distance-based
    """

    scan = db.execute(select(DBScan).where(DBScan.file_name == scan_file_name)).scalar_one_or_none()

    if scan is None:
        return print_error_exit(f"No scan file with name '{scan_file_name} found.")

    print(f"Found scan: '{scan_file_name}' (ID: '{scan.id}')")
    print(f"Epsilon: {epsilon}")

    db_scan_region_a = aliased(DBScanRegion)
    db_scan_region_b = aliased(DBScanRegion)

    query = (
        select(
            db_scan_region_a.id.label('region_a_id'),
            db_scan_region_a.name.label('region_a'),
            db_scan_region_b.id.label('region_b_id'),
            db_scan_region_b.name.label('region_b'),
        )
        .join(DBScanRegion.scan)
        .where(DBScan.id == scan.id)
        .where(db_scan_region_a.id < db_scan_region_b.id)  # Avoid self-comparison and duplicates.
    )

    if epsilon is not None:
        query = query.where(ST_3DDWithin(db_scan_region_a.shape, db_scan_region_b.shape, epsilon))
    else:
        query = query.where(ST_3DIntersects(db_scan_region_a.shape, db_scan_region_b.shape))

    results = db.execute(query).all()

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

    parser.add_argument('--epsilon',
        type=float,
        help="Distance threshold, if present, use 'ST_3DDWithin' to compare regions, if not, use 'ST_3DIntersects'.")

    args = parser.parse_args()

    db = Session(get_engine())

    find_intersecting_regions(db, args.scan, args.epsilon)


if __name__ == "__main__":
    main()
