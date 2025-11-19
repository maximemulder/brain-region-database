import numpy as np
import trimesh
from skimage import measure

from brain_region_database.nifti import NiftiImage, Zooms


def compute_nifti_mask_mesh(
    original: NiftiImage,
    data: np.ndarray,
    simplify: bool = False,
    decimate_factor: float = 0.5,
) -> tuple[np.ndarray, np.ndarray]:
    header = original.header
    zooms  = header.get_zooms()

    verts, faces = extract_surface_marching_cubes(data, zooms, original.affine)

    if simplify and len(faces) > 10000:
        verts, faces = simplify_mesh(verts, faces, decimate_factor)

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

    verts, faces, normals, values = measure.marching_cubes(
        mask.astype(float),
        level=level,
        spacing=zooms,
        allow_degenerate=False
    )

    verts = apply_affine_transform(verts, affine)

    return verts, faces


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
    factor: float = 0.5
) -> tuple[np.ndarray, np.ndarray]:
    """
    Simplify mesh to reduce polygon count while preserving shape.
    """

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    target_faces = int(len(faces) * factor)

    simplified = mesh.simplify_quadric_decimation(target_faces)

    return simplified.vertices, simplified.faces
