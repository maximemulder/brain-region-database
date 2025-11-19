## Requirements

- Python 3.12 or newer.
- PostGIS database.
- Git LFS for the demonstration files.

## Setup

```
docker run --name postgis \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=admin \
  -e POSTGRES_DB=brain_db \
  -p 5432:5432 \
  -d postgis/postgis
```

```
export POSTGIS_HOST=localhost
export POSTGIS_PORT=5432
export POSTGIS_USERNAME=admin
export POSTGIS_PASSWORD=admin
export POSTGIS_DATABASE=brain_db
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
