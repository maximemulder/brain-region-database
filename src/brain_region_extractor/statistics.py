from pydantic import BaseModel


class RegionStatistics(BaseModel):
    name: str
    value: int
    voxel_count: int
    mean_intensity: float
    std_intensity: float
    min_intensity: float
    max_intensity: float
    median_intensity: float
    centroid: tuple[float, float, float]
    bounding_box: tuple[tuple[float, float, float], tuple[float, float, float]]
