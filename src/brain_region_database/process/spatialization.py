from nilearn.image import resample_img  # type: ignore

from brain_region_database.nifti import Interpolation, NiftiImage


def respatialize_nifti(image: NiftiImage, reference: NiftiImage, interpolation: Interpolation) -> NiftiImage:
    """
    Force the moving image into the reference image's coordinate system
    """

    return resample_img(
        image,
        target_affine=reference.affine,  # type: ignore
        target_shape=reference.shape,  # type: ignore
        interpolation=interpolation,
        force_resample=True,
        copy_header=True,
    )
