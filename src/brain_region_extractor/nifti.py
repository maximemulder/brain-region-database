from pathlib import Path
from typing import Literal

import nibabel as nib
import numpy as np
from nibabel.nifti1 import Nifti1Image
from nibabel.nifti2 import Nifti2Image
from nilearn.datasets import load_mni152_template  # type: ignore
from nilearn.image import resample_img  # type: ignore

from brain_region_extractor.util import print_error_exit

type NiftiImage = Nifti1Image | Nifti2Image

type Interpolation = Literal['nearest', 'continuous']

type VoxelData3D = np.ndarray[tuple[int, int, int], np.dtype[np.float32]]

type VoxelMask3D = np.ndarray[tuple[int, int, int], np.dtype[np.bool_]]


def load_nifti_image(path: Path) -> NiftiImage:
    image = nib.load(path)  # type: ignore
    if not isinstance(image, (Nifti1Image, Nifti2Image)):
        print_error_exit(f"file '{path}' does not contain a NIfTI image")

    return image  # type: ignore


def has_standard_dims(image: NiftiImage) -> bool:
    return has_same_dims(image, load_mni152_template())  # type: ignore


def resample_to_standard_dims(image: NiftiImage, interpolation: Interpolation) -> NiftiImage:
    return resample_to_same_dims(image, load_mni152_template(), interpolation)  # type: ignore


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
