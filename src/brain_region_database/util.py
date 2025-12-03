import colorsys
import os
import random
import sys
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
