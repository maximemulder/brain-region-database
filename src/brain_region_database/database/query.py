from geoalchemy2 import WKTElement
from sqlalchemy import select
from sqlalchemy.orm import Session

from brain_region_database.database.models import DBScan, DBScanRegion
from brain_region_database.scan import Point3D, Scan


def select_scan(db: Session, file_name: str) -> DBScan | None:
    return db.execute(
        select(DBScan).where(DBScan.file_name == file_name)
    ).scalar_one_or_none()


def insert_scan(db: Session, scan: Scan) -> DBScan:
    # Insert the main scan record.
    db_scan = DBScan(
        file_name=scan.file_name,
        file_size=scan.file_size,
        dimensions=scan.dimensions,
        voxel_size=scan.voxel_size,
    )

    db.add(db_scan)
    db.flush()

    # Insert the scan region records.
    for region in scan.regions:
        db.add(DBScanRegion(
            scan_id=db_scan.id,
            name=region.name,
            value=region.value,
            voxel_count=region.voxel_count,
            mean_intensity=region.mean_intensity,
            std_intensity=region.std_intensity,
            min_intensity=region.min_intensity,
            max_intensity=region.max_intensity,
            median_intensity=region.median_intensity,
            centroid=WKTElement(create_point(region.centroid), srid=4326),
            bounding_box=WKTElement(create_box(region.bounding_box))
        ))

    db.commit()
    db.refresh(db_scan)
    return db_scan


def create_point(centroid: Point3D) -> str:
    return f"POINT Z({centroid.x} {centroid.y} {centroid.z})"


def create_box(bounding_box: tuple[Point3D, Point3D]) -> str:
    min, max = bounding_box
    # ruff: noqa
    return f"""POLYHEDRALSURFACE Z (
        (({min.x} {min.y} {min.z}, {max.x} {min.y} {min.z}, {max.x} {max.y} {min.z}, {min.x} {max.y} {min.z}, {min.x} {min.y} {min.z})),
        (({min.x} {min.y} {max.z}, {max.x} {min.y} {max.z}, {max.x} {max.y} {max.z}, {min.x} {max.y} {max.z}, {min.x} {min.y} {max.z})),
        (({min.x} {min.y} {min.z}, {max.x} {min.y} {min.z}, {max.x} {min.y} {max.z}, {min.x} {min.y} {max.z}, {min.x} {min.y} {min.z})),
        (({min.x} {max.y} {min.z}, {max.x} {max.y} {min.z}, {max.x} {max.y} {max.z}, {min.x} {max.y} {max.z}, {min.x} {max.y} {min.z})),
        (({min.x} {min.y} {min.z}, {min.x} {max.y} {min.z}, {min.x} {max.y} {max.z}, {min.x} {min.y} {max.z}, {min.x} {min.y} {min.z})),
        (({max.x} {min.y} {min.z}, {max.x} {max.y} {min.z}, {max.x} {max.y} {max.z}, {max.x} {min.y} {max.z}, {max.x} {min.y} {min.z}))
    )"""
