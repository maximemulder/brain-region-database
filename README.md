## Description

This project is an experimental database and CLI client to store and query regions extracted from brain MRI scans.

## Installation

### Requirements

- Python 3.12 or newer
- PostGIS database
- (optional) Git LFS for the demonstration files
- (optional) Docker to containerize the database

### Database

The client connects to the database by reading its credentials from the following environment variables, these are required to run any script that interacts with the database.

```sh
export POSTGIS_HOST=localhost
export POSTGIS_PORT=5432
export POSTGIS_USERNAME=admin
export POSTGIS_PASSWORD=admin
export POSTGIS_DATABASE=brain_db
```

The PostGIS database can be a local installation, or use a Docker container such as with the following command:

```sh
docker run --name postgis \
  -e POSTGRES_USER=$POSTGIS_USERNAME \
  -e POSTGRES_PASSWORD=$POSTGIS_USERNAME \
  -e POSTGRES_DB=$POSTGIS_DATABASE \
  -p $POSTGIS_PORT:5432 \
  -d postgis/postgis
```

If PostGIS is used in Docker, the following command can be used to access its SQL REPL:

```sh
docker exec -it postgis psql -U $POSTGIS_PASSWORD -d $POSTGIS_DATABASE
```

### Client

The client is a Python package that can be installed in a Python virtual environment, to create and activate a Python virtual environment, use the following command:

```sh
python -m venv .venv
source .venv/bin/activate.sh
```

Then, to install the client and its dependencies in the virtual environment, use the following command in the project root directory:

```sh
pip install -e .
```

With the database and the client both set up, the project can be used.

## Scripts

All the project scripts are accessible as simple commands in the project Python virtual environment.

### Create database

To create or reset the database using the environment credentials, use the following command:

```sh
create-database
```

Note that the environment variable:

```sh
export POSTGIS_DEBUG=true
```

Can be set to output debug information including the queries sent to the database.

### Extract regions information

To extract region the regions information from a NIfTI scan into a JSON file, use the following command:

```sh
extract-scan-regions \
  --atlas-image demo/atlases/mni_icbm152_CerebrA_tal_nlin_sym_09c.nii \
  --atlas-dictionary demo/atlases/CerebrA_LabelDetails.csv \
  --scan demo/scans/demo_587630_V1_t1_001.nii \
  --lod 200 \
  --output regions.json
```

- The `atlas-image` and `atlas-dictionary` arguments describe the brain region names and shapes. Ideally these should be adapted to the scan.
- The `scan` argument is the MRI file from which to extract regions information from.
- (recommended) The `lod` argument is the LOD (level-of-detail) to which to simplify the region shapes to. More precisely, it is the maximum number of faces that each region shape should have.
- The `output` argument is the output JSON file to create.

### Insert regions

The following command can be used to insert a scan regions information from a JSON in the database.

```sh
insert-scan demo/regions/demo_587630_V1_t1_001_regions_200.json
```

Some extracted regions are provided already extracted as part of the repository in the `demo/regions` directory.

### Find intersecting regions

The following command can be used to query the pairs of intersecting regions within a scan:

```sh
find-intersecting-regions demo_587630_V1_t1_001.nii \
  --lod 200 \
  --box 3d \
  --intersect \
  --distance 1.5
```

- The first argument is the file name of the scan whose region are queried (just the name when it was inserted, not the full path).
- (recommended) The `lod` argument is the level of details of the regions that were inserted. Note that a single scan can have regions inserted at several LODs.
- (optional) The `box` argument instructs to intersect the regions bounding boxes. Possible values are `2d` and `3d`.
- (optional) The `intersect` argument instructs to intersects the regions using `ST_3DIntersects`.
- (optional) The `distance` argument instructs to intersects the regions using `ST_3DDistance` and a distance.

Optional arguments can be used cumulatively.

Other scripts are available in the `src/brain_region_database/scripts` directory.

## Example SQL queries

### Find scans with region in an area

The following query can be used to find all scans whose hippocampus is located within the (0, 0, 0) (200, 200, 200) coordinates:

```sql
SELECT s.file_name
FROM scan_region sr
  JOIN region r ON sr.region_id = r.id
  JOIN scan s ON sr.scan_id = s.id
WHERE sr.centroid &&& ST_3DMakeBox(
    ST_MakePoint(0, 0, 0),
    ST_MakePoint(200, 200, 200)
  ) AND
  r.name = 'Hippocampus';
```

### Order regions by volume

The following query that uses SFCGAL can be used to order all regions within a scan by bounding box volume:

```sql
SELECT
  r.name as region_name,
  CG_Volume(srl.shape::box3d) as region_volume
FROM scan_region_lod srl
  JOIN region r ON srl.region_id = r.id
  JOIN scan s ON srl.scan_id = s.id
WHERE srl.level = 200
  AND s.file_name = 'demo_587630_V1_t1_001.nii'
ORDER BY CG_Volume(srl.shape::box3d) DESC;
```

SFCGAL can be enabled using the following command (works in Docker, untested in local database):

```sql
CREATE EXTENSION IF NOT EXISTS postgis_sfcgal;
```

## Demonstration files

Demonstration files are located within the `demo` directory.

The [CerebrA brain atlas](https://nist.mni.mcgill.ca/cerebra/), which provides spatial information about the brain regions for an average brain:
- `mni_icbm152_CerebrA_tal_nlin_sym_09c.nii`: The brain atlas volume file, which contains the voxels of each region.
- `CerebrA_LabelDetails.csv`: The brain atlas description file, which contains the description of each region.

The demonstration scan comes from the [LORIS demonstration database](https://demo.loris.ca/).
