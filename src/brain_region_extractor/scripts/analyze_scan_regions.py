#!/usr/bin/env python

import argparse
import json
from pathlib import Path

import numpy as np

from brain_region_extractor.atlas import AtlasRegion, load_atlas_dictionary, print_atlas_regions
from brain_region_extractor.nifti import NDArray3, has_same_dims, resample_to_same_dims, load_nifti_image
from brain_region_extractor.scan import Point3D, ScanRegion

# ruff: noqa
# analyze-scan-regions --atlas-image ../atlases/mni_icbm152_nlin_sym_09c_CerebrA_nifti/mni_icbm152_CerebrA_tal_nlin_sym_09c.nii --atlas-dictionary ../atlases/mni_icbm152_nlin_sym_09c_CerebrA_nifti/CerebrA_LabelDetails.csv --scan ../../COMP5411/demo_587630_V1_t1_001.nii


def main() -> None:
    parser = argparse.ArgumentParser(
        prog='extract_brain_regions',
        description="Extract regions information of a NIfTI file using a brain atlas.",
    )

    parser.add_argument('--atlas-dictionary',
        required=True,
        help="The brain atlas CSV dictionary.")

    parser.add_argument('--atlas-image',
        required=True,
        help="The brain atlas NIfTI image.")

    parser.add_argument('--scan',
        required=True,
        help="The brain scan NIfTI image.")

    args = parser.parse_args()

    atlas_dictionary_path = Path(args.atlas_dictionary)
    atlas_image_path      = Path(args.atlas_image)
    scan_path             = Path(args.scan)

    atlas_dictionary = load_atlas_dictionary(atlas_dictionary_path)
    atlas_image      = load_nifti_image(atlas_image_path)
    scan_image       = load_nifti_image(scan_path)

    print_atlas_regions(atlas_dictionary)

    if not has_same_dims(atlas_image, scan_image):
        print("Resampling the atlas to the scan dimensions.")
        atlas_image = resample_to_same_dims(atlas_image, scan_image, 'nearest')
    else:
        print("Atlas is already in the scan dimensions.")

    atlas_data: NDArray3[np.float32] = atlas_image.get_fdata()
    scan_data:  NDArray3[np.float32] = scan_image.get_fdata()

    # Dictionary to store region statistics
    regions_statistics: dict[str, ScanRegion] = {}

    for region in atlas_dictionary.regions:
        print(f"Processing region '{region.name}' ({region.value})")

        regions_statistics[region.name] = collect_region_statistics(region, atlas_data, scan_data)

    print(json.dumps({region_name: region_statistics.model_dump() for region_name, region_statistics in regions_statistics.items()}, indent=4))


def collect_region_statistics(
    region: AtlasRegion,
    atlas_data: NDArray3[np.float32],
    scan_data: NDArray3[np.float32],
) -> ScanRegion:
    # Create the mask of the region.
    region_mask = (atlas_data == region.value)

    # Get coordinates of the region
    region_coordinates = np.argwhere(region_mask)

    # Apply the region mask to the scan data.
    region_scan_data = scan_data[region_mask]

    # Compute centroid.
    centroid = np.mean(region_coordinates, axis=0)

    # Compute bounding box.
    min_bounding_box = np.min(region_coordinates, axis=0).astype(int)
    max_bounding_box = np.max(region_coordinates, axis=0).astype(int)

    return ScanRegion(
        name=region.name,
        value=region.value,
        voxel_count=np.sum(region_mask).item(),
        mean_intensity=np.mean(region_scan_data).item(),
        std_intensity=np.std(region_scan_data).item(),
        min_intensity=np.min(region_scan_data).item(),
        max_intensity=np.max(region_scan_data).item(),
        median_intensity=np.median(region_scan_data).item(),
        centroid=Point3D.from_array(centroid),
        bounding_box=(
            Point3D.from_array(min_bounding_box),
            Point3D.from_array(max_bounding_box),
        ),
    )


if __name__ == '__main__':
    main()
