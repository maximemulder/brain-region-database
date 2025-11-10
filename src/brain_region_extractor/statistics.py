from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class RegionStatistics:
    name: str
    value: int
    voxel_count: int
    mean_intensity: float
    std_intensity: float
    min_intensity: float
    max_intensity: float
    median_intensity: float

    def to_json(self) -> dict[str, Any]:
        return asdict(self)
