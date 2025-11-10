import os
import sys
from typing import Never


def print_error_exit(message: str) -> Never:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(-1)


def print_warning(message: str):
    print(f"WARNING: {message}", file=sys.stderr)


def read_environment_variable(name: str) -> str:
    value = os.environ.get(name)
    if value is None:
        return print_error_exit(f"Could not read environment variable '{name}'.")

    return value
