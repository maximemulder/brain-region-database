import numpy as np
from nibabel.nifti1 import Nifti1Image
from skimage.transform import resize  # type: ignore

from brain_region_database.nifti import Interpolation, NiftiImage


def resize_nifti(nifti: NiftiImage, reference: NiftiImage, interpolation: Interpolation) -> NiftiImage:
    moving_data     = nifti.get_fdata()
    reference_shape = reference.shape[:3]

    match interpolation:
        case 'nearest':
            order = 0
        case 'continuous':
            order = 1

    # Resize the data
    resized_data = resize(  # type: ignore
        moving_data,
        reference_shape,
        order=order,
        mode='constant',
        cval=0,
        anti_aliasing=True
    )

    # Adjust affine for new voxel sizes
    new_affine = nifti.affine.copy()  # type: ignore
    scale_factors = np.array(moving_data.shape) / np.array(reference_shape)
    new_affine[:3, :3] = new_affine[:3, :3] @ np.diag(scale_factors)

    return Nifti1Image(resized_data, new_affine)  # type: ignore
