# Find interseting regions

```sql
SELECT
    scan_region_1.id AS region_b_id,
    scan_region_1.name AS region_a,
    scan_region_2.id AS region_b_id,
    scan_region_2.name AS region_b
FROM scan_region JOIN scan ON
    scan.id = scan_region.scan_id,
    scan_region AS scan_region_1,
    scan_region AS scan_region_2
WHERE
    scan.id = %(id_1)s AND
    scan_region_1.id < scan_region_2.id AND
    ST_3DIntersects(scan_region_1.shape, scan_region_2.shape)
```

```sql
SELECT
    scan_region_1.id AS region_a_id,
    scan_region_1.name AS region_a,
    scan_region_2.id AS region_b_id,
    scan_region_2.name AS region_b
FROM
    scan_region AS scan_region_1
    JOIN scan_region AS scan_region_2
    ON scan_region_1.scan_id = scan_region_2.scan_id
WHERE
    scan_region_1.scan_id = %(scan_id_1)s
    AND scan_region_2.scan_id = %(scan_id_2)s
    AND scan_region_1.id < scan_region_2.id
    AND ST_3DDWithin(scan_region_1.shape, scan_region_2.shape, %(ST_3DDWithin_1)s)
```

```
2025-12-03 01:11:28,068 INFO sqlalchemy.engine.Engine SELECT scan_region_1.id AS region_a_id, scan_region_1.name AS region_a, scan_region_2.id AS region_b_id, scan_region_2.name AS region_b
FROM scan_region AS scan_region_1 JOIN scan_region AS scan_region_2 ON scan_region_1.scan_id = scan_region_2.scan_id
WHERE scan_region_1.scan_id = %(scan_id_1)s AND scan_region_2.scan_id = %(scan_id_2)s AND scan_region_1.id < scan_region_2.id AND ST_3DDWithin(scan_region_1.shape, scan_region_2.shape, %(ST_3DDWithin_1)s)
2025-12-03 01:11:28,068 INFO sqlalchemy.engine.Engine [generated in 0.00011s] {'scan_id_1': 1, 'scan_id_2': 1, 'ST_3DDWithin_1': 1.0}
Found 78 intersecting region pairs:
  Caudal Anterior Cingulate (ID: 1) <-> Rostral Anterior Cingulate (ID: 24)
  Caudal Anterior Cingulate (ID: 1) <-> Superior Frontal (ID: 26)
  Caudal Middle Frontal (ID: 2) <-> Precentral (ID: 22)
  Caudal Middle Frontal (ID: 2) <-> Rostral Middle Frontal (ID: 25)
  Caudal Middle Frontal (ID: 2) <-> Superior Frontal (ID: 26)
  Cuneus (ID: 3) <-> Pericalcarine (ID: 19)
  Cuneus (ID: 3) <-> Precuneus (ID: 23)
  Entorhinal (ID: 4) <-> Fusiform (ID: 5)
  Entorhinal (ID: 4) <-> Hippocampus (ID: 44)
  Entorhinal (ID: 4) <-> Amygdala (ID: 45)
  Pars Orbitalis (ID: 17) <-> Pars Triangularis (ID: 18)
  Fusiform (ID: 5) <-> Parahippocampal (ID: 14)
  Fusiform (ID: 5) <-> Cerebellum Gray Matter (ID: 38)
  Inferior Parietal (ID: 6) <-> Lateral Occipital (ID: 9)
  Inferior Parietal (ID: 6) <-> Middle Temporal (ID: 13)
  Inferior Parietal (ID: 6) <-> Superior Parietal (ID: 27)
  Inferior Parietal (ID: 6) <-> Supramarginal (ID: 29)
  Inferior temporal (ID: 7) <-> Middle Temporal (ID: 13)
  Isthmus Cingulate (ID: 8) <-> Posterior Cingulate (ID: 21)
  Isthmus Cingulate (ID: 8) <-> Precuneus (ID: 23)
  Lateral Occipital (ID: 9) <-> Middle Temporal (ID: 13)
  Lateral Occipital (ID: 9) <-> Pericalcarine (ID: 19)
  Lateral Orbitofrontal (ID: 10) <-> Medial Orbitofrontal (ID: 12)
  Lingual (ID: 11) <-> Pericalcarine (ID: 19)
  Medial Orbitofrontal (ID: 12) <-> Rostral Anterior Cingulate (ID: 24)
  Medial Orbitofrontal (ID: 12) <-> Optic Chiasm (ID: 35)
  Middle Temporal (ID: 13) <-> Superior Temporal (ID: 28)
  Paracentral (ID: 15) <-> Posterior Cingulate (ID: 21)
  Paracentral (ID: 15) <-> Superior Frontal (ID: 26)
  Pars Opercularis (ID: 16) <-> Pars Triangularis (ID: 18)
  Pars Opercularis (ID: 16) <-> Rostral Middle Frontal (ID: 25)
  Pars Opercularis (ID: 16) <-> Insula (ID: 31)
  Pars Triangularis (ID: 18) <-> Rostral Middle Frontal (ID: 25)
  Postcentral (ID: 20) <-> Precentral (ID: 22)
  Postcentral (ID: 20) <-> Superior Parietal (ID: 27)
  Postcentral (ID: 20) <-> Supramarginal (ID: 29)
  Posterior Cingulate (ID: 21) <-> Precuneus (ID: 23)
  Posterior Cingulate (ID: 21) <-> Superior Frontal (ID: 26)
  Precentral (ID: 22) <-> Superior Frontal (ID: 26)
  Precuneus (ID: 23) <-> Superior Parietal (ID: 27)
  Rostral Anterior Cingulate (ID: 24) <-> Superior Frontal (ID: 26)
  Rostral Middle Frontal (ID: 25) <-> Superior Frontal (ID: 26)
  Brainstem (ID: 32) <-> Fourth Ventricle (ID: 34)
  Brainstem (ID: 32) <-> Cerebellum Gray Matter (ID: 38)
  Brainstem (ID: 32) <-> Cerebellum White Matter (ID: 39)
  Brainstem (ID: 32) <-> Thalamus (ID: 40)
  Brainstem (ID: 32) <-> Ventral Diencephalon (ID: 47)
  Third Ventricle (ID: 33) <-> Optic Chiasm (ID: 35)
  Third Ventricle (ID: 33) <-> Thalamus (ID: 40)
  Third Ventricle (ID: 33) <-> Ventral Diencephalon (ID: 47)
  Superior Temporal (ID: 28) <-> Transverse Temporal (ID: 30)
  Transverse Temporal (ID: 30) <-> Insula (ID: 31)
  Fourth Ventricle (ID: 34) <-> Cerebellum White Matter (ID: 39)
  Fourth Ventricle (ID: 34) <-> Vermal lobules I-V (ID: 49)
  Fourth Ventricle (ID: 34) <-> Vermal lobules VIII-X (ID: 51)
  Optic Chiasm (ID: 35) <-> Ventral Diencephalon (ID: 47)
  Optic Chiasm (ID: 35) <-> Basal Forebrain (ID: 48)
  Lateral Ventricle (ID: 36) <-> Thalamus (ID: 40)
  Lateral Ventricle (ID: 36) <-> Caudate (ID: 41)
  Lateral Ventricle (ID: 36) <-> Hippocampus (ID: 44)
  Inferior Lateral Ventricle (ID: 37) <-> Hippocampus (ID: 44)
  Inferior Lateral Ventricle (ID: 37) <-> Amygdala (ID: 45)
  Inferior Lateral Ventricle (ID: 37) <-> Ventral Diencephalon (ID: 47)
  Putamen (ID: 42) <-> Pallidum (ID: 43)
  Putamen (ID: 42) <-> Accumbens Area (ID: 46)
  Cerebellum Gray Matter (ID: 38) <-> Cerebellum White Matter (ID: 39)
  Cerebellum Gray Matter (ID: 38) <-> Vermal lobules I-V (ID: 49)
  Cerebellum Gray Matter (ID: 38) <-> Vermal lobules VI-VII (ID: 50)
  Cerebellum Gray Matter (ID: 38) <-> Vermal lobules VIII-X (ID: 51)
  Cerebellum White Matter (ID: 39) <-> Vermal lobules VIII-X (ID: 51)
  Thalamus (ID: 40) <-> Caudate (ID: 41)
  Thalamus (ID: 40) <-> Ventral Diencephalon (ID: 47)
  Caudate (ID: 41) <-> Accumbens Area (ID: 46)
  Hippocampus (ID: 44) <-> Amygdala (ID: 45)
  Accumbens Area (ID: 46) <-> Basal Forebrain (ID: 48)
  Ventral Diencephalon (ID: 47) <-> Basal Forebrain (ID: 48)
  Vermal lobules I-V (ID: 49) <-> Vermal lobules VI-VII (ID: 50)
  Vermal lobules VI-VII (ID: 50) <-> Vermal lobules VIII-X (ID: 51)
```
