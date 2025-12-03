from geoalchemy2.functions import ST_GeomFromEWKT
from sqlalchemy import select
from sqlalchemy.orm import Session as Database
from sqlalchemy.sql.expression import func

from brain_region_database.database.models import DBScan, DBScanRegion, DBScanRegionLOD
from brain_region_database.scan import Point3D, Scan, ScanRegion


def try_get_scan_with_file_name(db: Database, file_name: str) -> DBScan | None:
    return db.execute(
        select(DBScan).where(DBScan.file_name == file_name)
    ).scalar_one_or_none()


def try_get_scan_region_with_scan_and_name(db: Database, scan: DBScan, name: str) -> DBScanRegion | None:
    return db.execute(
        select(DBScanRegion).where(
            DBScanRegion.scan == scan,
            DBScanRegion.name == name,
        )
    ).scalar_one_or_none()


def try_get_scan_region_lod_with_region_and_level(
    db: Database,
    region: DBScanRegion,
    lod_level: int | None,
) -> DBScanRegionLOD | None:
    return db.execute(
        select(DBScanRegionLOD).where(
            DBScanRegionLOD.region == region,
            DBScanRegionLOD.level  == lod_level,
        )
    ).scalar_one_or_none()


def try_get_largest_scan_lod(db: Database, scan: DBScan) -> int | None:
    return db.execute(
        select(func.max(DBScanRegionLOD.level)).where(
            DBScanRegionLOD.region.scan == scan,
        )
    ).scalar_one_or_none()


def get_scan_regions_lod_with_scan_and_level(
    db: Database,
    scan: DBScan,
    lod_level: int | None,
) -> list[DBScanRegionLOD]:
    return list(db.execute(select(DBScanRegionLOD)
        .join(DBScanRegionLOD.region)
        .where(
            DBScanRegion.scan == scan,
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


def insert_scan_region(db: Database, scan: DBScan, region_data: ScanRegion) -> DBScanRegion:
    db_region = DBScanRegion(
        scan_id=scan.id,
        name=region_data.name,
        value=region_data.value,
        voxel_count=region_data.voxel_count,
        mean_intensity=region_data.mean_intensity,
        std_intensity=region_data.std_intensity,
        min_intensity=region_data.min_intensity,
        max_intensity=region_data.max_intensity,
        median_intensity=region_data.median_intensity,
        centroid=ST_GeomFromEWKT(create_point(region_data.centroid), srid=4326),
    )

    db.add(db_region)
    db.flush()
    return db_region


def insert_scan_region_lod(db: Database, region: DBScanRegion, region_data: ScanRegion) -> DBScanRegionLOD:
    lod = DBScanRegionLOD(
        region_id=region.id,
        level=region_data.lod_level,
        shape=ST_GeomFromEWKT(create_postgis_3d_geometry(region_data.shape[0], region_data.shape[1]), srid=4326)
    )

    db.add(lod)
    db.flush()
    return lod


def create_point(centroid: Point3D) -> str:
    return f"POINT Z({centroid.x} {centroid.y} {centroid.z})"


def create_box(box: tuple[Point3D, Point3D]) -> str:
    min, max = box
    # ruff: noqa
    return f"""POLYHEDRALSURFACE Z (
        (({min.x} {min.y} {min.z}, {max.x} {min.y} {min.z}, {max.x} {max.y} {min.z}, {min.x} {max.y} {min.z}, {min.x} {min.y} {min.z})),
        (({min.x} {min.y} {max.z}, {max.x} {min.y} {max.z}, {max.x} {max.y} {max.z}, {min.x} {max.y} {max.z}, {min.x} {min.y} {max.z})),
        (({min.x} {min.y} {min.z}, {max.x} {min.y} {min.z}, {max.x} {min.y} {max.z}, {min.x} {min.y} {max.z}, {min.x} {min.y} {min.z})),
        (({min.x} {max.y} {min.z}, {max.x} {max.y} {min.z}, {max.x} {max.y} {max.z}, {min.x} {max.y} {max.z}, {min.x} {max.y} {min.z})),
        (({min.x} {min.y} {min.z}, {min.x} {max.y} {min.z}, {min.x} {max.y} {max.z}, {min.x} {min.y} {max.z}, {min.x} {min.y} {min.z})),
        (({max.x} {min.y} {min.z}, {max.x} {max.y} {min.z}, {max.x} {max.y} {max.z}, {max.x} {min.y} {max.z}, {max.x} {min.y} {min.z}))
    )"""


def create_postgis_3d_geometry(
    vertices: list[tuple[float, float, float]],
    faces: list[tuple[int, int, int]],
) -> str:
    """
    Convert vertices and faces to a PostGIS 3D geometry (POLYHEDRALSURFACE).
    """

    def create_polygon_ewkt(face_vertices: list[tuple[float, float, float]])  -> str:
        """Create EWKT for a single polygon from face vertices."""
        # Close the polygon by repeating the first vertex
        coords = ", ".join(f"{x} {y} {z}" for x, y, z in face_vertices)
        coords += f", {face_vertices[0][0]} {face_vertices[0][1]} {face_vertices[0][2]}"
        return f"(({coords}))"

    polygons: list[str] = []
    for face in faces:
        # Get vertices for this face (convert from 0-based to 1-based if needed)
        face_vertices = [vertices[vertex_idx] for vertex_idx in face]
        polygons.append(create_polygon_ewkt(face_vertices))

    polygons_ewkt = ", ".join(polygons)
    return f"POLYHEDRALSURFACE Z ({polygons_ewkt})"
