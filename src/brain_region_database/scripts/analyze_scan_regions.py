#!/usr/bin/env python

import argparse
import json
from pathlib import Path

import numpy as np

from brain_region_database.atlas import AtlasRegion, load_atlas_dictionary, print_atlas_regions
from brain_region_database.nifti import NDArray3, NiftiImage, ants_to_nib, get_voxel_size, nib_to_ants, load_nifti_image
from brain_region_database.process.registration import register_nifti
from brain_region_database.process.vectorization import compute_nifti_mask_mesh
from brain_region_database.scan import Point3D, Scan, ScanRegion

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

    parser.add_argument('--output',
        type=Path,
        help="Print the scan information JSON in a file instead of the console.")

    args = parser.parse_args()

    atlas_dictionary_path = Path(args.atlas_dictionary)
    atlas_image_path      = Path(args.atlas_image)
    scan_path             = Path(args.scan)

    atlas_dictionary = load_atlas_dictionary(atlas_dictionary_path)
    atlas_image      = load_nifti_image(atlas_image_path)
    scan_image       = load_nifti_image(scan_path)

    print_atlas_regions(atlas_dictionary)

    atlas_image = ants_to_nib(register_nifti(
        nib_to_ants(atlas_image),
        nib_to_ants(scan_image),
        'nearest',
    ))

    atlas_data: NDArray3[np.float32] = atlas_image.get_fdata()
    scan_data:  NDArray3[np.float32] = scan_image.get_fdata()

    regions: list[ScanRegion] = []

    for region in atlas_dictionary.regions:
        print(f"Processing region '{region.name}' ({region.value})")

        regions.append(collect_region_statistics(atlas_image, region, atlas_data, scan_data))

    scan = Scan(
        file_name=scan_path.name,
        file_size=scan_path.stat().st_size,
        dimensions=f"{scan_data.shape[0]}x{scan_data.shape[1]}x{scan_data.shape[2]}",
        voxel_size=get_voxel_size(scan_image),
        regions=regions
    )

    # Convert the scan object to JSON.
    scan_json = json.dumps(scan.model_dump(), indent=4)

    if args.output:
        print(f"Writing scan information to '{args.output}'.")
        with open(args.output, 'w') as f:
            f.write(scan_json)
    else:
        print(scan_json)



def collect_region_statistics(
    original: NiftiImage,
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

    vertices, faces = compute_nifti_mask_mesh(original, region_mask)

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
        shape=(
            [tuple(row) for row in vertices],
            [tuple(row) for row in faces],
        ),
    )


if __name__ == '__main__':
    main()
