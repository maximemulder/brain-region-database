Commands used to generate the scan regions metata:

```sh
analyze-scan-regions --atlas-image demo/atlases/mni_icbm152_nlin_sym_09c_CerebrA_nifti/mni_icbm152_CerebrA_tal_nlin_sym_09c.nii --atlas-dictionary demo/atlases/mni_icbm152_nlin_sym_09c_CerebrA_nifti/CerebrA_LabelDetails.csv --scan demo/scans/demo_587630_V1_t1_001.nii --simplify 100 --output demo/regions/demo_587630_V1_t1_001_regions_100.json
analyze-scan-regions --atlas-image demo/atlases/mni_icbm152_nlin_sym_09c_CerebrA_nifti/mni_icbm152_CerebrA_tal_nlin_sym_09c.nii --atlas-dictionary demo/atlases/mni_icbm152_nlin_sym_09c_CerebrA_nifti/CerebrA_LabelDetails.csv --scan demo/scans/demo_587630_V1_t1_001.nii --simplify 200 --output demo/regions/demo_587630_V1_t1_001_regions_200.json
analyze-scan-regions --atlas-image demo/atlases/mni_icbm152_nlin_sym_09c_CerebrA_nifti/mni_icbm152_CerebrA_tal_nlin_sym_09c.nii --atlas-dictionary demo/atlases/mni_icbm152_nlin_sym_09c_CerebrA_nifti/CerebrA_LabelDetails.csv --scan demo/scans/demo_587630_V1_t1_001.nii --simplify 500 --output demo/regions/demo_587630_V1_t1_001_regions_500.json
analyze-scan-regions --atlas-image demo/atlases/mni_icbm152_nlin_sym_09c_CerebrA_nifti/mni_icbm152_CerebrA_tal_nlin_sym_09c.nii --atlas-dictionary demo/atlases/mni_icbm152_nlin_sym_09c_CerebrA_nifti/CerebrA_LabelDetails.csv --scan demo/scans/demo_587630_V1_t1_001.nii --simplify 1000 --output demo/regions/demo_587630_V1_t1_001_regions_1000.json
analyze-scan-regions --atlas-image demo/atlases/mni_icbm152_nlin_sym_09c_CerebrA_nifti/mni_icbm152_CerebrA_tal_nlin_sym_09c.nii --atlas-dictionary demo/atlases/mni_icbm152_nlin_sym_09c_CerebrA_nifti/CerebrA_LabelDetails.csv --scan demo/scans/demo_587630_V1_t1_001.nii --simplify 5000 --output demo/regions/demo_587630_V1_t1_001_regions_5000.json
```
