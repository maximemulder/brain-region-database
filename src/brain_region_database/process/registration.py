import ants  # type: ignore
from ants import ANTsImage  # type: ignore


def register_nifti(source: ANTsImage, reference: ANTsImage) -> ANTsImage:
    # Perform registration (SyN for non-linear registration)
    registration = ants.registration(  # type: ignore
        fixed=reference,
        moving=source,
        type_of_transform='SyN',
        interpolator='nearestNeighbor',
    )

    return registration['warpedmovout']  # type: ignore
