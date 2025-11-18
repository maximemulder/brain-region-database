#!/usr/bin/env python

import argparse
from pathlib import Path

import nibabel as nib
from nibabel.nifti1 import Nifti1Image

from brain_region_database.atlas import load_atlas_dictionary, print_atlas_regions
from brain_region_database.nifti import has_same_dims, load_nifti_image, resample_to_same_dims
from brain_region_database.util import print_error_exit

# ruff: noqa
# extract-scan-regions --atlas-image ../atlases/mni_icbm152_nlin_sym_09c_CerebrA_nifti/mni_icbm152_CerebrA_tal_nlin_sym_09c.nii --atlas-dictionary ../atlases/mni_icbm152_nlin_sym_09c_CerebrA_nifti/CerebrA_LabelDetails.csv --scan ../../COMP5411/demo_587630_V1_t1_001.nii

def main() -> None:
    parser = argparse.ArgumentParser(
        prog='extract_scan_regions',
        description="Extract the different regions of a NIfTI file using a brain atlas.",
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

    parser.add_argument('--output-dir',
        required=True,
        help="The output directory in which to write the region files.")

    args = parser.parse_args()

    atlas_dictionary = load_atlas_dictionary(Path(args.atlas_dictionary))
    atlas_image      = load_nifti_image(Path(args.atlas_image))
    scan_image       = load_nifti_image(Path(args.scan))
    output_dir_path  = Path(args.output_dir)

    print_atlas_regions(atlas_dictionary)

    if not has_same_dims(scan_image, atlas_image):
        print("Resampling atlas to the image space.")
        atlas_image = resample_to_same_dims(atlas_image, scan_image, 'nearest')
    else:
        print("Atlas is already in the image space.")

    if not output_dir_path.exists():
        if not output_dir_path.parent.exists():
            print_error_exit(f"Parent directory '{output_dir_path.parent}' does not exist.")
        output_dir_path.mkdir(exist_ok=True)
    else:
        if not output_dir_path.is_dir():
            print_error_exit(f"Path '{output_dir_path}' exists but is not a directory.")

    atlas_data = atlas_image.get_fdata()
    scan_data  = scan_image.get_fdata()

    for region in atlas_dictionary.regions:
        print(f"Processing region '{region.name}' ({region.value})")

        # Create the mask for this region.
        region_mask = (atlas_data == region.value)

        # Apply the mask to the scan data.
        region_data = scan_data * region_mask

        # Create a new NIfTI image with the region data.
        region_nifti = Nifti1Image(region_data, scan_image.affine, scan_image.header)  # type: ignore

        # Save the region as a NIfTI file.
        region_path = output_dir_path / f"{region.name}.nii"
        nib.save(region_nifti, region_path)  # type: ignore

    print("Success!")


if __name__ == '__main__':
    main()
