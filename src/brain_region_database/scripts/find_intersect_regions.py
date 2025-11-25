import argparse

from geoalchemy2.functions import ST_3DDistance, ST_3DDWithin, ST_3DIntersects
from sqlalchemy import text
from sqlalchemy.orm import Session, aliased

from brain_region_database.database.engine import get_engine
from brain_region_database.database.models import DBScan, DBScanRegion


def find_intersection_regions(db, scan_file_name, epsilon, use_3d_intersects=True):
    """
    Find all regions within epsilon distance of each other in a given scan

    Args:
        db_url: Database connection URL
        scan_file_name: Name of the scan file to analyze
        epsilon: Maximum distance threshold (in same units as your spatial data)
        use_3d_intersects: If True, use ST_3DIntersects for exact intersection,
                          else use ST_3DDWithin for distance-based
    """

    try:
        # Get the target scan
        scan = db.query(DBScan).filter(DBScan.file_name == scan_file_name).first()
        if not scan:
            print(f"Scan with file name '{scan_file_name}' not found")
            return []

        print(f"Analyzing scan: {scan_file_name} (ID: {scan.id})")
        print(f"Epsilon: {epsilon}")
        print("-" * 50)

        DBScanRegion2 = aliased(DBScanRegion)

        if use_3d_intersects:

            # Method 1: Exact 3D Intersections (more computationally expensive)
            query = db.query(
                DBScanRegion.name.label('region_a'),
                DBScanRegion.id.label('region_a_id'),
                DBScanRegion2.name.label('region_b'),
                DBScanRegion2.id.label('region_b_id'),
                text('ST_3DDistance(region1.shape, region2.shape) as distance')
            ).select_from(DBScanRegion).join(
                DBScanRegion2,
                DBScanRegion.scan_id == DBScanRegion2.scan_id
            ).filter(
                DBScanRegion.scan_id == scan.id,
                DBScanRegion2.scan_id == scan.id,
                DBScanRegion.id < DBScanRegion2.id,  # Avoid duplicates and self-comparison
                ST_3DIntersects(DBScanRegion.shape, DBScanRegion2.shape)
            )
        else:
            # Method 2: Distance-based within epsilon (more flexible)
            query = db.query(
                DBScanRegion.name.label('region_a'),
                DBScanRegion.id.label('region_a_id'),
                DBScanRegion2.name.label('region_b'),
                DBScanRegion2.id.label('region_b_id'),
                text('ST_3DDistance(region1.shape, region2.shape) as distance')
            ).select_from(DBScanRegion).join(
                DBScanRegion2,
                DBScanRegion.scan_id == DBScanRegion2.scan_id
            ).filter(
                DBScanRegion.scan_id == scan.id,
                DBScanRegion2.scan_id == scan.id,
                DBScanRegion.id < DBScanRegion2.id,
                ST_3DDWithin(DBScanRegion.shape, DBScanRegion2.shape, epsilon)
            )

        results = query.all()

        print(f"Found {len(results)} intersecting region pairs:")
        for result in results:
            print(f"  {result.region_a} (ID: {result.region_a_id}) <-> "
                  f"{result.region_b} (ID: {result.region_b_id}) | "
                  f"Distance: {result.distance:.4f}")

        return results

    except Exception as e:
        print(f"Error: {e}")
        return []


# Alternative implementation using raw SQL for better performance
def find_intersection_regions_sql(db, scan_file_name, epsilon):
    """
    Using raw SQL for potentially better performance with complex 3D operations
    """

    sql = text("""
    WITH scan_regions AS (
        SELECT sr.id, sr.name, sr.shape, sr.centroid
        FROM scan_region sr
        JOIN scan s ON sr.scan_id = s.id
        WHERE s.file_name = :scan_file_name
    )
    SELECT
        a.name as region_a,
        a.id as region_a_id,
        b.name as region_b,
        b.id as region_b_id,
        ST_3DDistance(a.shape, b.shape) as distance,
        ST_3DIntersects(a.shape, b.shape) as exact_intersect
    FROM scan_regions a
    CROSS JOIN scan_regions b
    WHERE a.id < b.id  -- Avoid duplicates and self-comparison
      AND ST_3DDWithin(a.shape, b.shape, :epsilon)
    ORDER BY distance ASC;
    """)

    results = db.execute(sql, {
        'scan_file_name': scan_file_name,
        'epsilon': epsilon
    }).fetchall()

    print(f"Found {len(results)} region pairs within epsilon {epsilon}:")
    for row in results:
        intersect_type = "EXACT" if row.exact_intersect else "NEAR"
        print(f"  {row.region_a} ↔ {row.region_b} | "
                f"Distance: {row.distance:.4f} | {intersect_type}")

    return results


# Advanced version with spatial indexing analysis
def find_intersections_with_performance(db, scan_file_name, epsilon):
    """
    Enhanced version that shows query performance and uses spatial indexes
    """

    # Check if spatial indexes exist
    index_check_sql = text("""
    SELECT indexname, indexdef
    FROM pg_indexes
    WHERE tablename = 'scan_region'
    AND indexdef LIKE '%gist%';
    """)

    print("Checking spatial indexes...")
    indexes = db.execute(index_check_sql).fetchall()
    if indexes:
        print("Spatial indexes found:")
        for idx in indexes:
            print(f"  - {idx.indexname}")
    else:
        print("  No spatial indexes found - consider creating them for better performance")

    # Perform the intersection analysis with EXPLAIN
    explain_sql = text("""
    EXPLAIN ANALYZE
    SELECT
        a.name as region_a,
        b.name as region_b,
        ST_3DDistance(a.shape, b.shape) as distance
    FROM scan_region a
    JOIN scan_region b ON a.scan_id = b.scan_id
    JOIN scan s ON a.scan_id = s.id
    WHERE s.file_name = :scan_file_name
      AND a.id < b.id
      AND ST_3DDWithin(a.shape, b.shape, :epsilon);
    """)

    print(f"\nQuery performance analysis for epsilon={epsilon}:")
    explain_result = db.execute(explain_sql, {
        'scan_file_name': scan_file_name,
        'epsilon': epsilon
    }).fetchall()

    for line in explain_result:
        print(f"  {line[0]}")

    # Now get the actual results
    return find_intersection_regions_sql(db, scan_file_name, epsilon)


# Command line interface
def main():
    parser = argparse.ArgumentParser(description='Find intersecting brain regions in a scan')
    parser.add_argument('scan', help='Scan file name to analyze')
    parser.add_argument('--epsilon', type=float, default=1000.0, help='Distance threshold')
    parser.add_argument('--method', choices=['orm', 'sql', 'performance'], default='sql',
                       help='Query method to use')

    args = parser.parse_args()

    db = Session(get_engine())

    if args.method == 'orm':
        results = find_intersection_regions(db, args.scan, args.epsilon)
    elif args.method == 'sql':
        results = find_intersection_regions_sql(db, args.scan, args.epsilon)
    elif args.method == 'performance':
        results = find_intersections_with_performance(db, args.scan, args.epsilon)

    return results


if __name__ == "__main__":
    main()
