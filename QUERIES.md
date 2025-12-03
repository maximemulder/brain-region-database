# Find interseting regions

Command: `find-intersecting-regions demo_587630_V1_t1_001.nii --lod X --distance 1`

## No bounding box

### 100 faces

- Timings: 14s, 14s,15s
- Average: 14s

### 200 faces

- Timings: 49s, 51s, 54s
- Average: 48s

### 500 faces

- Timings: 297s, 290s, 300s
- Average: 296s

### 1000 faces

- Timings: 1179s, 1210s, 1242s
- Average: 1210s

## 2D bounding box

### 100 faces

- Timings: 7s, 7s, 7s
- Average: 7s

### 200 faces

- Timings: 25s, 25s, 25s
- Average: 25s

### 500 faces

- Timings: 153s, 175s, 191s
- Average: 173s

### 1000 faces

- Timings: 659s, 611s, 645s
- Average: 638s

## 3D bounding box

### 100 faces

- Timings: 5s, 5s, 5s
- Average: 5s

### 200 faces

- Timings: 17s, 18s, 18s
- Average: 18s

### 500 faces

- Timings: 112s, 120s, 123s
- Average: 118s

### 1000 faces

- Timings: 470s, 447s, 444s
- Average: 454s
