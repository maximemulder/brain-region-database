from pathlib import Path
from typing import Any, Literal

import nibabel as nib
import numpy as np
from nibabel.nifti1 import Nifti1Image
from nibabel.nifti2 import Nifti2Image
from nilearn.image import resample_img  # type: ignore

from brain_region_database.util import print_error_exit

type NiftiImage = Nifti1Image | Nifti2Image

type Interpolation = Literal['nearest', 'continuous']

type NDArray3[T: Any] = np.ndarray[tuple[int, int, int], np.dtype[T]]


def load_nifti_image(path: Path) -> NiftiImage:
    image = nib.load(path)  # type: ignore
    if not isinstance(image, (Nifti1Image, Nifti2Image)):
        print_error_exit(f"file '{path}' does not contain a NIfTI image")

    return image  # type: ignore


def has_same_dims(image: NiftiImage, template: NiftiImage) -> bool:
    return np.allclose(image.affine, template.affine) and image.shape == template.shape  # type: ignore


def resample_to_same_dims(image: NiftiImage, template: NiftiImage, interpolation: Interpolation) -> NiftiImage:
    return resample_img(
        image,
        target_affine=template.affine,  # type: ignore
        target_shape=template.shape,  # type: ignore
        interpolation=interpolation,
        force_resample=True,
        copy_header=True,
    )  # type: ignore


def get_voxel_size(image: NiftiImage) -> str:
    """Extract voxel size from NIfTI image header and format as string."""
    try:
        # Get the affine matrix or header information
        header = image.header
        # Typical NIfTI voxel size is in the pixdim field
        voxel_dims = header.get_zooms()  # This gets (x, y, z) voxel dimensions # type: ignore

        if len(voxel_dims) >= 3:  # type: ignore
            return f"{voxel_dims[0]:.2f}x{voxel_dims[1]:.2f}x{voxel_dims[2]:.2f}mm"
        else:
            return "1.00x1.00x1.00mm"  # Default fallback

    except (AttributeError, IndexError):
        # Fallback if voxel size can't be determined
        return "1.00x1.00x1.00mm"
