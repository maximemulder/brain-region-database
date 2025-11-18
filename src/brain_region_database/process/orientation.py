import numpy as np
from nibabel.nifti1 import Nifti1Image
from scipy.ndimage import map_coordinates  # type: ignore

from brain_region_database.nifti import Interpolation, NiftiImage


def reorient_nifti(image: NiftiImage, reference: NiftiImage, interpolation: Interpolation) -> NiftiImage:
    match interpolation:
        case 'nearest':
            order = 0
        case 'continuous':
            order = 1

    # Get the affine matrices and data
    image_affine     = image.affine  # type: ignore
    reference_affine = reference.affine  # type: ignore
    image_data = image.get_fdata()

    # Get reference image shape
    reference_shape = reference.shape

    # Create coordinate grid in reference space
    i, j, k = np.mgrid[:reference_shape[0], :reference_shape[1], :reference_shape[2]]

    # Convert reference coordinates to world coordinates
    world_coords = np.dot(reference_affine, np.vstack([i.ravel(), j.ravel(), k.ravel(), np.ones(i.size)]))  # type: ignore

    # Convert world coordinates to moving image coordinates
    moving_coords = np.dot(np.linalg.inv(image_affine), world_coords)  # type: ignore

    # Extract the physical coordinates (remove homogeneous coordinate)
    moving_coords_physical = moving_coords[:3]

    # Reshape for interpolation
    coords_array = moving_coords_physical.reshape(3, *reference_shape)

    # Apply interpolation
    reoriented_data = map_coordinates(image_data, coords_array, order=order, mode='constant', cval=0.0)  # type: ignore

    # Create a new NIfTI image with the reoriented data and reference affine
    reoriented_img = Nifti1Image(reoriented_data, reference_affine, header=reference.header)  # type: ignore

    return reoriented_img
