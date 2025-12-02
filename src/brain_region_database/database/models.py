from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column, relationship


# SQLAlchemy Models
class Base(DeclarativeBase, MappedAsDataclass):
    pass


class DBScan(Base):
    __tablename__ = 'scan'

    id         : Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    file_name  : Mapped[str] = mapped_column(index=True, unique=True)
    file_size  : Mapped[int]
    dimensions : Mapped[str]
    voxel_size : Mapped[str]

    # Relationships
    regions: Mapped[list['DBScanRegion']] = relationship(init=False, back_populates='scan')


class DBScanRegion(Base):
    __tablename__ = 'scan_region'
    # __table_args__ = (
    #     # Regular index for non-geometric columns
    #     Index('idx_scan_region_scan_id_name', 'scan_id', 'name'),
    #     # Spatial indexes for geometric columns
    #     Index('idx_scan_region_centroid', 'centroid', postgresql_using='gist'),
    #     Index('idx_scan_region_shape', 'shape', postgresql_using='gist'),
    # )

    id      : Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    scan_id : Mapped[int] = mapped_column(ForeignKey('scan.id'))

    # Region atlas properties
    name  : Mapped[str] = mapped_column(index=True)
    value : Mapped[int]

    # Region numeric properties
    voxel_count      : Mapped[int]
    mean_intensity   : Mapped[float]
    std_intensity    : Mapped[float]
    min_intensity    : Mapped[float]
    max_intensity    : Mapped[float]
    median_intensity : Mapped[float]

    # Geometric properties
    centroid : Mapped[Geometry] = mapped_column(Geometry('POINTZ', srid=4326))
    shape    : Mapped[Geometry] = mapped_column(Geometry('POLYHEDRALSURFACEZ', srid=4326))

    # Relationships
    scan: Mapped['DBScan'] = relationship(init=False, back_populates='regions')
