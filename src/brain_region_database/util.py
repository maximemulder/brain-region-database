import colorsys
import os
import random
import sys
from pathlib import Path
from typing import Never

type Color = tuple[int | float, int | float, int | float]


def print_warning(message: str):
    print(f"WARNING: {message}", file=sys.stderr)


def print_error_exit(message: str) -> Never:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(-1)


def read_environment_variable(name: str) -> str:
    value = os.environ.get(name)
    if value is None:
        return print_error_exit(f"Could not read environment variable '{name}'.")

    return value


def get_full_output_path(output_path: Path, name: str) -> Path:
    if not output_path.parent.is_dir():
        print_error_exit(f"No parent directory found for path '{output_path}'.")

    if output_path.is_dir():
        output_path = output_path / name

    if output_path.exists():
        return print_error_exit(f"File or directory '{output_path}' already exists.")

    return output_path


def generate_random_colors(n: int) -> list[Color]:
    """
    Generate evenly distributed random colors for visualization.
    """

    # Distribute hues evenly around the color wheel.
    hues = [i / n for i in range(n)]

    # Shuffle but maintain some order for better visual separation.
    random.shuffle(hues)

    colors: list[Color] = []

    for hue in hues:
        # Vary saturation and value slightly for a more natural look.
        sat = random.uniform(0.6, 0.8)
        val = random.uniform(0.7, 0.9)

        # Convert HSV to RGB.
        r, g, b = colorsys.hsv_to_rgb(hue, sat, val)

        # Convert to 0-255 range.
        colors.append((int(r * 255), int(g * 255), int(b * 255)))

    return colors
