import numpy as np
from pydantic import BaseModel


class Point3D(BaseModel):
    x: float
    y: float
    z: float

    @staticmethod
    def from_array(array: np.ndarray) -> 'Point3D':
        return Point3D(
            x=array[0].item(),
            y=array[1].item(),
            z=array[2].item(),
        )


class ScanRegion(BaseModel):
    name: str
    value: int
    voxel_count: int
    mean_intensity: float
    std_intensity: float
    min_intensity: float
    max_intensity: float
    median_intensity: float
    centroid: Point3D
    bounding_box: tuple[Point3D, Point3D]
    shape: tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]


class Scan(BaseModel):
    file_name: str
    file_size: int
    dimensions: str
    voxel_size: str
    regions: list[ScanRegion]
