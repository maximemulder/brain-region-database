import numpy as np
import trimesh
import trimesh.repair
from skimage import measure

from brain_region_database.nifti import NiftiImage, Zooms


def compute_nifti_mask_mesh(
    original: NiftiImage,
    data: np.ndarray,
    faces_limit: int | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Compte the 3D mesh of a NIfTI mask, simplifying according to the given parameters if desired.
    """

    header = original.header
    zooms  = header.get_zooms()  # type: ignore

    print("  Computing region mesh...")
    verts, faces = extract_surface_marching_cubes(data, zooms, original.affine)  # type: ignore

    print(f"  Region has {len(faces)} faces")
    print("  Cleaning mesh...")
    verts, faces = clean_mesh(verts, faces)

    if faces_limit is not None and len(faces) > faces_limit:
        print(f"  Simplifying region mesh to {faces_limit} faces...")
        verts, faces = simplify_mesh(verts, faces, faces_limit)
        print("  Cleaning mesh...")
        verts, faces = clean_mesh(verts, faces)

    return verts, faces


def extract_surface_marching_cubes(
    mask: np.ndarray,
    zooms: Zooms,
    affine: np.ndarray,
    level: float = 0.5
) -> tuple[np.ndarray, np.ndarray]:
    """
    Extract surface using marching cubes with proper coordinate transformation.
    """

    verts, faces, _, _ = measure.marching_cubes(  # type: ignore
        mask.astype(float),
        level=level,
        spacing=zooms,
        allow_degenerate=False
    )

    verts = apply_affine_transform(verts, affine)  # type: ignore

    return verts, faces  # type: ignore


def apply_affine_transform(vertices: np.ndarray, affine: np.ndarray) -> np.ndarray:
    """
    Apply NIfTI affine transform to convert voxel coordinates to world coordinates.
    """

    ones = np.ones((vertices.shape[0], 1))

    verts_homogeneous = np.hstack([vertices, ones])

    verts_transformed = (affine @ verts_homogeneous.T).T

    return verts_transformed[:, :3]


def simplify_mesh(
    vertices: np.ndarray,
    faces: np.ndarray,
    faces_limit: int,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Simplify a mesh by reducing the polygon count while trying to preserve its shape.
    """

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    simplified = mesh.simplify_quadric_decimation(face_count=faces_limit)

    return simplified.vertices, simplified.faces


def clean_mesh(
    vertices: np.ndarray,
    faces: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    Clean mesh and ensure consistent face orientation.
    """

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    print(f"    Original: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

    # 1. Remove duplicate vertices
    mesh.merge_vertices()
    mesh.remove_unreferenced_vertices()

    # 2. Fix face orientation
    trimesh.repair.fix_normals(mesh)
    trimesh.repair.fix_winding(mesh)

    # 3. Try to make watertight
    if not mesh.is_watertight:
        print("    Mesh is not watertight, attempting to fix...")
        trimesh.repair.fill_holes(mesh)
        mesh.fill_holes()

    # 4. Fix any inversion
    trimesh.repair.fix_inversion(mesh)

    print(f"    Cleaned: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

    return mesh.vertices, mesh.faces
