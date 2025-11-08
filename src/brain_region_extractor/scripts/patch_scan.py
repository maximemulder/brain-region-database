#!/usr/bin/env python

import argparse
from pathlib import Path

import nibabel as nib
import numpy as np
from nibabel.nifti1 import Nifti1Image

from brain_region_extractor.nifti import has_same_dims, load_nifti_image, resample_to_same_dims
from brain_region_extractor.util import print_error_exit


def main() -> None:
    parser = argparse.ArgumentParser(
        prog='patch_scan',
        description="Resize or change the data type of a NIfTI image.",
    )

    parser.add_argument('--scan',
        required=True,
        help="The brain scan NIfTI image.")

    parser.add_argument('--resize',
        help="Resize the NIfTI image to the NIfTI template dimensions.")

    parser.add_argument('--interpolation',
        choices=['nearest', 'continuous'],
        help="Resize interpolation.")

    parser.add_argument('--type',
        choices=['uint8', 'int8', 'int16', 'float32', 'float64'],
        help="Change the NIfTI data type.")

    parser.add_argument('--output',
        required=True,
        help="The file or directory name for the output NIfTI image.")

    args = parser.parse_args()

    scan_path   = Path(args.scan)
    output_path = Path(args.output)
    scan_image  = load_nifti_image(scan_path)

    if args.resize is not None:
        if args.interpolation is None:
            print_error_exit("--interpolation is required when --resize is used.")

        template_image = load_nifti_image(Path(args.resize))
        if not has_same_dims(scan_image, template_image):
            print("Resampling image to the template space...")
            scan_image = resample_to_same_dims(scan_image, template_image, args.interpolation)
        else:
            print("Image is already in the template space.")

    if args.type:
        current_type = scan_image.get_fdata().dtype
        target_type = getattr(np, args.type)

        if current_type != target_type:
            print(f"Converting image from {current_type} to {args.type}...")
            data = scan_image.get_fdata().astype(target_type)  # type: ignore
            scan_image = Nifti1Image(data, scan_image.affine, scan_image.header)  # type: ignore
            scan_image.header.set_data_dtype(target_type)  # type: ignore
        else:
            print(f"Image already uses the '{target_type}' data type. No conversion needed.")

    if not output_path.parent.is_dir():
        print_error_exit(f"No parent directory found for path '{output_path}'.")

    if output_path.is_dir():
        output_path = output_path / scan_path.name

    if output_path.exists():
        print_error_exit(f"File or directory '{output_path}' already exists.")

    nib.save(scan_image, output_path)  # type: ignore

    print("Success!")


if __name__ == '__main__':
    main()
