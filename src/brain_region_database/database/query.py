from geoalchemy2.functions import ST_GeomFromEWKT
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
            centroid=ST_GeomFromEWKT(create_point(region.centroid), srid=4326),
            # bounding_box=WKTElement(create_box(region.bounding_box))
            shape=ST_GeomFromEWKT(create_postgis_3d_geometry(region.shape[0], region.shape[1]), srid=4326),
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
