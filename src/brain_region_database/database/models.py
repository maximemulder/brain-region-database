from typing import Literal

from geoalchemy2 import Geometry
from sqlalchemy import ForeignKey, ForeignKeyConstraint, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column, relationship

type Laterality = Literal['L', 'R']


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


class DBRegion(Base):
    __tablename__ = 'region'

    id          : Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    name        : Mapped[str]
    laterality  : Mapped[Laterality | None]
    atlas_value : Mapped[int]

    # Relationships
    scans: Mapped[list['DBScanRegion']] = relationship(init=False, back_populates='region')


class DBScanRegion(Base):
    __tablename__ = 'scan_region'
    __table_args__ = (
        Index('idx_scan_region_scan_id_region_id', 'scan_id', 'region_id', unique=True),
    )

    # Keys
    id        : Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    scan_id   : Mapped[int] = mapped_column(ForeignKey('scan.id'), index=True)
    region_id : Mapped[int] = mapped_column(ForeignKey('region.id'), index=True)

    # Numeric properties
    voxel_count      : Mapped[int]
    mean_intensity   : Mapped[float]
    std_intensity    : Mapped[float]
    min_intensity    : Mapped[float]
    max_intensity    : Mapped[float]
    median_intensity : Mapped[float]

    # Geometric properties
    centroid: Mapped[Geometry] = mapped_column(Geometry('POINTZ', srid=0, use_N_D_index=True))

    # Relationships
    scan   : Mapped['DBScan']   = relationship(init=False, back_populates='regions')
    region : Mapped['DBRegion'] = relationship(init=False, back_populates='scans')


class DBScanRegionLOD(Base):
    __tablename__ = 'scan_region_lod'
    __table_args__ = (
        Index('idx_scan_region_lod_scan_id_region_id_lod', 'scan_id', 'region_id', 'level', unique=True),
        ForeignKeyConstraint(
            ['scan_id', 'region_id'],
            ['scan_region.scan_id', 'scan_region.region_id']
        ),
    )

    # Keys
    id        : Mapped[int] = mapped_column(init=False, primary_key=True, autoincrement=True)
    scan_id   : Mapped[int] = mapped_column(ForeignKey('scan.id'), index=True)
    region_id : Mapped[int] = mapped_column(ForeignKey('region.id'), index=True)
    level     : Mapped[int | None]

    # Geometric properties
    shape: Mapped[Geometry] = mapped_column(Geometry('POLYHEDRALSURFACEZ', srid=0, use_N_D_index=True))

    # Relationships
    scan   : Mapped['DBScan']   = relationship(init=False)
    region : Mapped['DBRegion'] = relationship(init=False)
