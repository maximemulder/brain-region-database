## Description

This project is an experimental database and CLI client to store and query regions extracted from brain MRI scans.

As such:
- A
- A
- A
- A

## Requirements

- Python 3.12 or newer.
- PostGIS database.
- Git LFS for the demonstration files.

## Setup

The client reads the database credentials from environment

```
export POSTGIS_HOST=localhost
export POSTGIS_PORT=5432
export POSTGIS_USERNAME=admin
export POSTGIS_PASSWORD=admin
export POSTGIS_DATABASE=brain_db
```

```
docker run --name postgis \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_DB=brain_db \
  -p 5432:5432 \
  -d postgis/postgis
```

```
docker exec -it postgis psql -U $POSTGIS_PASSWORD -d $POSTGIS_DATABASE
```

## How to use

To create the PostGIS database using the aforementioned information:

```
create-database
```

To extract region information from a NIfTI scan:

```
analyze-scan-regions \
  --atlas-image demo/mni_icbm152_CerebrA_tal_nlin_sym_09c.nii \
  --atlas-dictionary demo/CerebrA_LabelDetails.csv \
  --scan ../../COMP5411/demo_587630_V1_t1_001.nii \
  --simplify 2000 \
  --output regions.json
```

To insert region information in the database:

```
insert-scan regions.json
```

## Demonstration files

Demonstration files are located within the `demo` directory.

The [CerebrA brain atlas](https://nist.mni.mcgill.ca/cerebra/), which provides spatial information about the brain regions for an average brain:
- `mni_icbm152_CerebrA_tal_nlin_sym_09c.nii`: The brain atlas volume file, which contains the voxels of each region.
- `CerebrA_LabelDetails.csv`: The brain atlas description file, which contains the description of each region.

## Notes

Things to talk about:

- Coordinate system (everything must be the same !)
- 3D geometry types
- 3D indexes
- Be careful about returning large

## Queries for later

Regions ordered by centroid Z:

```
brain_db=# SELECT
    sr.name AS brain_region,
    AVG(ST_Z(sr.shape)) AS average_z_position,
    COUNT(*) AS region_count
FROM scan_region sr
GROUP BY sr.name
ORDER BY average_z_position DESC;
```

Regions ordered by minimum shape Z:

```
SELECT
    sr.name,
    MIN(ST_ZMin(sr.shape)) as min_shape_z,
    COUNT(*) as region_count
FROM scan_region sr
GROUP BY sr.name
ORDER BY min_shape_z DESC;
```

# TODO:
1. Compare 3D intersection time for single shape
2. Compare single-scan intersection time without index, with index, with SFCGAL
3. Add LOD
4. Randomized scan regions
5. Other queries
