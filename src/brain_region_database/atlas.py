
import csv
from dataclasses import dataclass
from pathlib import Path

ATLAS_REGION_NAME  = 'Label Name'
ATLAS_REGION_VALUE = 'RH Label'


@dataclass
class AtlasRegion:
    name: str
    value: int


@dataclass
class Atlas:
    headers: list[str]
    rows: list[list[str]]
    regions: list[AtlasRegion]


def load_atlas_dictionary(path: Path) -> Atlas:
    regions = []
    with open(path) as file:
        reader = csv.reader(file)
        headers = next(reader)
        region_name_index  = headers.index(ATLAS_REGION_NAME)
        region_value_index = headers.index(ATLAS_REGION_VALUE)
        rows = list(reader)

    regions = list(map(lambda row: AtlasRegion(row[region_name_index], int(row[region_value_index])), rows))
    return Atlas(headers, rows, regions)


def print_atlas_regions(atlas_dictionary: Atlas):
    print("Atlas regions:")

    for region in atlas_dictionary.regions:
        print(f"- {region.name} ({region.value})")
