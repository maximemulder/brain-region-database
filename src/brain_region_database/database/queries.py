from geoalchemy2.functions import ST_GeomFromEWKT
from sqlalchemy import select
from sqlalchemy.orm import Session as Database
from sqlalchemy.sql.expression import func

from brain_region_database.database.geometries import create_point, create_postgis_3d_geometry
from brain_region_database.database.models import DBRegion, DBScan, DBScanRegion, DBScanRegionLOD
from brain_region_database.scan import Scan, ScanRegion


def try_get_scan(db: Database, file_name: str) -> DBScan | None:
    return db.execute(select(DBScan)
        .where(DBScan.file_name == file_name)
    ).scalar_one_or_none()


def try_get_region(db: Database, name: str) -> DBRegion | None:
    return db.execute(select(DBRegion)
        .where(DBRegion.name == name)
    ).scalar_one_or_none()


def try_get_scan_region(db: Database, scan: DBScan, region: DBRegion) -> DBScanRegion | None:
    return db.execute(select(DBScanRegion).where(
        DBScanRegion.scan   == scan,
        DBScanRegion.region == region,
    )).scalar_one_or_none()


def try_get_scan_region_lod(
    db: Database,
    scan: DBScan,
    region: DBRegion,
    lod_level: int | None,
) -> DBScanRegionLOD | None:
    return db.execute(select(DBScanRegionLOD).where(
        DBScanRegionLOD.scan   == scan,
        DBScanRegionLOD.region == region,
        DBScanRegionLOD.level  == lod_level,
    )).scalar_one_or_none()


def try_get_largest_scan_lod(db: Database, scan: DBScan) -> int | None:
    return db.execute(select(func.max(DBScanRegionLOD.level)).where(
        DBScanRegionLOD.scan == scan,
    )).scalar_one_or_none()


def get_scan_regions_lod_with_scan_and_level(
    db: Database,
    scan: DBScan,
    lod_level: int | None,
) -> list[DBScanRegionLOD]:
    return list(db.execute(select(DBScanRegionLOD)
        .join(DBScanRegionLOD.region)
        .where(
            DBScanRegionLOD.scan == scan,
            DBScanRegionLOD.level == lod_level,
        )
    ).scalars().all())


def insert_scan(db: Database, scan_data: Scan) -> DBScan:
    scan = DBScan(
        file_name=scan_data.file_name,
        file_size=scan_data.file_size,
        dimensions=scan_data.dimensions,
        voxel_size=scan_data.voxel_size,
    )

    db.add(scan)
    db.flush()
    return scan


def insert_region(db: Database, region_data: ScanRegion) -> DBRegion:
    region = DBRegion(
        name=region_data.name,
        laterality=None,
        atlas_value=region_data.value,
    )

    db.add(region)
    db.flush()
    return region


def insert_scan_region(db: Database, scan: DBScan, region: DBRegion, region_data: ScanRegion) -> DBScanRegion:
    scan_region = DBScanRegion(
        scan_id=scan.id,
        region_id=region.id,
        voxel_count=region_data.voxel_count,
        mean_intensity=region_data.mean_intensity,
        std_intensity=region_data.std_intensity,
        min_intensity=region_data.min_intensity,
        max_intensity=region_data.max_intensity,
        median_intensity=region_data.median_intensity,
        centroid=ST_GeomFromEWKT(create_point(region_data.centroid), srid=0),
    )

    db.add(scan_region)
    db.flush()
    return scan_region


def insert_scan_region_lod(db: Database, scan: DBScan, region: DBRegion, region_data: ScanRegion) -> DBScanRegionLOD:
    lod = DBScanRegionLOD(
        scan_id=scan.id,
        region_id=region.id,
        level=region_data.lod_level,
        shape=ST_GeomFromEWKT(create_postgis_3d_geometry(region_data.shape[0], region_data.shape[1]), srid=0)
    )

    db.add(lod)
    db.flush()
    return lod
