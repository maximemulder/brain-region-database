from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# SQLAlchemy Models
class Base(DeclarativeBase):
    pass


class Scan(Base):
    __tablename__ = 'scan'

    id         : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_name  : Mapped[str]
    file_size  : Mapped[int]
    dimensions : Mapped[str]
    voxel_size : Mapped[str]

    # Relationships
    regions: Mapped[list['ScanRegion']] = relationship(back_populates='scan')


class ScanRegion(Base):
    __tablename__ = 'scan_region'

    id      : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scan_id : Mapped[int] = mapped_column(ForeignKey('scan.id'))

    # Region atlas properties
    name  :  Mapped[str]
    value : Mapped[int]

    # Region numeric properties
    voxel_count      : Mapped[int]
    mean_intensity   : Mapped[float]
    std_intensity    : Mapped[float]
    min_intensity    : Mapped[float]
    max_intensity    : Mapped[float]
    median_intensity : Mapped[float]

    # Geometric properties
    centroid     : Mapped[str] = mapped_column(Geometry('POINTZ', srid=4326),)
    bounding_box : Mapped[str] = mapped_column(Geometry('POLYHEDRALSURFACEZ', srid=4326))

    # Relationships
    mri_scan: Mapped['Scan'] = relationship(back_populates='regions')
