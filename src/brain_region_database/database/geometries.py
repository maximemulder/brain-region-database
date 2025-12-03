from brain_region_database.scan import Point3D

type Vec3[T] = tuple[T, T, T]
type Vec4[T] = tuple[T, T, T, T]

type Vec3F = Vec3[float]
type Vec4F = Vec3[float]


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


def create_postgis_3d_geometry(vertices: list[Vec3F], faces: list[Vec4[int]]) -> str:
    return polygons_to_surface(close_polygons(get_mesh_polygons(vertices, faces)))


def get_mesh_polygons(vertices: list[Vec3F], faces: list[Vec4[int]]) -> list[Vec3[Vec3F]]:
    polygons: list[Vec3[Vec3F]] = []
    for face in faces:
        face_vertices = (vertices[face[0]], vertices[face[1]], vertices[face[2]])
        polygons.append(face_vertices)

    return polygons


def close_polygons(polygons: list[Vec3[Vec3F]]) -> list[Vec4[Vec3F]]:
    closed_polygons: list[Vec4[Vec3F]] = []
    for polygon in polygons:
        closed_polygons.append((polygon[0], polygon[1], polygon[2], polygon[0]))

    return closed_polygons


def polygons_to_surface(polygons: list[Vec4[Vec3F]]) -> str:
    polygon_strings: list[str] = []
    for polygon in polygons:
        vertex_strings: list[str] = []
        for vertex in polygon:
            vertex_strings.append(" ".join(map(str, vertex)))

        polygon_strings.append(f"(({", ".join(vertex_strings)}))")

    return f"POLYHEDRALSURFACE Z ({", ".join(polygon_strings)})"
