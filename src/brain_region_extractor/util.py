import sys
from typing import Never


def print_error_exit(message: str) -> Never:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(-1)


def print_warning(message: str):
    print(f"WARNING: {message}", file=sys.stderr)
