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
