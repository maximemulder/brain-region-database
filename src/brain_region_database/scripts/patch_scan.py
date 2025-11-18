#!/usr/bin/env python

import argparse
from pathlib import Path

import ants  # type: ignore
import nibabel as nib
import numpy as np
from nibabel.nifti1 import Nifti1Image

from brain_region_database.nifti import load_nifti_image
from brain_region_database.process.orientation import reorient_nifti
from brain_region_database.process.registration import register_nifti
from brain_region_database.process.size import resize_nifti
from brain_region_database.process.spatialization import respatialize_nifti
from brain_region_database.util import print_error_exit


def main() -> None:
    parser = argparse.ArgumentParser(
        prog='patch_scan',
        description="Resize or change the data type of a NIfTI image.",
    )

    parser.add_argument('scan',
        type=Path,
        help="The target NIfTI image.")

    parser.add_argument('--type',
        choices=['uint8', 'int8', 'int16', 'float32', 'float64'],
        help="Change the image NIfTI data type.")

    parser.add_argument('--register',
        action='store_true',
        help="Register the image.")

    parser.add_argument('--respatialize',
        action='store_true',
        help="Respatialize the image.")

    parser.add_argument('--reorient',
        action='store_true',
        help="Reorient the image.")

    parser.add_argument('--resize',
        action='store_true',
        help="Resize the image.")

    parser.add_argument('--interpolation',
        choices=['nearest', 'continuous'],
        default='continuous',
        help="The interpolation to use in resampling.")

    parser.add_argument('--reference',
        type=Path,
        help="The reference NIfTI image against which to resize or reorient the image.")

    parser.add_argument('--output',
        required=True,
        type=Path,
        help="The file or directory name for the output NIfTI image.")

    args = parser.parse_args()

    scan_path   = args.scan
    output_path = args.output

    if args.register:
        if args.reference is None:
            return print_error_exit("A reference image is needed to perform registration.")

        if args.respatialize or args.reorient or args.resize:
            return print_error_exit(
                "Registration should not be used simultaneously with respatialization, reorientation, or resizing."
            )

        scan_image      = ants.image_read(str(args.scan))  # type: ignore
        reference_image = ants.image_read(str(args.reference))  # type: ignore

        print("Registering image...")

        scan_image = register_nifti(scan_image, reference_image)  # type: ignore
        output_path = get_full_output_path(args.output, scan_path.name)
        ants.image_write(scan_image, str(output_path))  # type: ignore
        args.scan = output_path

    if args.reference is not None:
        reference_image = load_nifti_image(args.reference)
    else:
        reference_image = None

    scan_image = load_nifti_image(scan_path)

    if args.respatialize:
        if reference_image is None:
            return print_error_exit("A reference image is needed to perform respatialization.")

        print("Respatializing image...")

        scan_image = respatialize_nifti(scan_image, reference_image, args.interpolation)

    if args.reorient:
        if reference_image is None:
            return print_error_exit("A reference image is needed to perform reorientation.")

        print("Reorienting image...")

        scan_image = reorient_nifti(scan_image, reference_image, args.interpolation)

    if args.resize:
        if reference_image is None:
            return print_error_exit("A reference image is needed to perform resizing.")

        print("Resizing image...")

        scan_image = resize_nifti(scan_image, reference_image, args.interpolation)

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

    nib.save(scan_image, get_full_output_path(output_path, scan_path.name))  # type: ignore

    print("Success!")


def get_full_output_path(output_path: Path, name: Path) -> Path:
    if not output_path.parent.is_dir():
        print_error_exit(f"No parent directory found for path '{output_path}'.")

    if output_path.is_dir():
        output_path = output_path / name

    if output_path.exists():
        return print_error_exit(f"File or directory '{output_path}' already exists.")

    return output_path


if __name__ == '__main__':
    main()
