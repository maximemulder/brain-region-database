#!/usr/bin/env python

import argparse
from pathlib import Path

import nibabel as nib
import numpy as np
from nibabel.nifti1 import Nifti1Image
from scipy import ndimage  # type: ignore
from scipy.ndimage import label  # type: ignore

from brain_region_database.util import get_full_output_path


def elastic_deform_atlas(atlas_data: np.ndarray, alpha: float = 30, sigma: float = 5, order: float = 0):
    """
    Apply elastic deformation to atlas while preserving integer labels.

    Parameters:
    - atlas_data: 3D numpy array of integer labels
    - alpha: deformation intensity
    - sigma: smoothness of deformation
    - order: interpolation order (0 for nearest-neighbor for labels)
    """

    shape = atlas_data.shape

    # Create random displacement fields
    dx = np.random.randn(*shape) * 2 - 1
    dy = np.random.randn(*shape) * 2 - 1
    dz = np.random.randn(*shape) * 2 - 1

    # Smooth the displacement fields
    dx = ndimage.gaussian_filter(dx, sigma, mode="constant") * alpha  # type: ignore
    dy = ndimage.gaussian_filter(dy, sigma, mode="constant") * alpha  # type: ignore
    dz = ndimage.gaussian_filter(dz, sigma, mode="constant") * alpha  # type: ignore

    # Create coordinate grid
    z, y, x = np.meshgrid(
        np.arange(shape[0]),
        np.arange(shape[1]),
        np.arange(shape[2]),
        indexing='ij',
    )

    # Apply displacement
    indices = (z + dz, y + dy, x + dx)

    # Use nearest-neighbor interpolation to preserve integer labels
    deformed = ndimage.map_coordinates(atlas_data, indices, order=order, mode='nearest')

    return deformed


def postprocess_deformation(deformed_data: np.ndarray, original_data: np.ndarray) -> np.ndarray:
    """
    Clean up holes and islands after deformation.
    """

    processed = deformed_data.copy()
    labels = np.unique(original_data)

    for lab in labels:
        if lab == 0:
            continue

        # Create mask for this label
        mask = processed == lab

        # Remove small islands (connected components)
        labeled_mask, num_features = label(mask)  # type: ignore

        if num_features > 1:
            # Find size of each component
            component_sizes = np.bincount(labeled_mask.ravel())  # type: ignore

            # Keep only largest component
            largest_component = np.argmax(component_sizes[1:]) + 1

            # Remove small islands
            for comp_id in range(1, num_features + 1):  # type: ignore
                if comp_id != largest_component:
                    # Assign these voxels to nearest neighbor label
                    component_mask = labeled_mask == comp_id  # type: ignore

                    # Get coordinates of voxels to reassign
                    coords = np.argwhere(component_mask)  # type: ignore

                    for coord in coords:
                        # Look in immediate neighborhood
                        z, y, x = coord
                        z_slice = slice(max(0, z - 2), min(processed.shape[0], z + 3))
                        y_slice = slice(max(0, y - 2), min(processed.shape[1], y + 3))
                        x_slice = slice(max(0, x - 2), min(processed.shape[2], x + 3))

                        neighborhood = processed[z_slice, y_slice, x_slice]
                        neighbor_labels = neighborhood[neighborhood != 0]

                        if len(neighbor_labels) > 0:
                            # Assign to most common neighbor
                            unique, counts = np.unique(neighbor_labels, return_counts=True)
                            processed[coord[0], coord[1], coord[2]] = unique[np.argmax(counts)]

    return processed


def main() -> None:
    parser = argparse.ArgumentParser(
        prog='patch_scan',
        description="Resize or change the data type of a NIfTI image.",
    )

    parser.add_argument('scan',
        type=Path,
        help="The target NIfTI image.")

    parser.add_argument('--interpolation',
        choices=['nearest', 'continuous'],
        default='continuous',
        help="The interpolation to use in resampling.")

    parser.add_argument('--output',
        required=True,
        type=Path,
        help="The file or directory name for the output NIfTI image.")

    args = parser.parse_args()

    scan_path:   Path = args.scan
    output_path: Path = args.output

    # Load atlas
    scan = nib.load(args.scan)  # type: ignore
    scan_data = scan.get_fdata()  # type: ignore

    warped_data = elastic_deform_atlas(scan_data, alpha=20, sigma=3)  # type: ignore
    warped_data = postprocess_deformation(warped_data, scan_data)  # type: ignore

    scan_image = Nifti1Image(warped_data, scan.affine, scan.header)  # type: ignore

    full_output_path = get_full_output_path(output_path, scan_path.name)
    nib.save(scan_image, full_output_path)  # type: ignore


if __name__ == '__main__':
    main()
