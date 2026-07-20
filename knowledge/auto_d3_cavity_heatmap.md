# สรุปจาก Grafana JSON: d3_cavity_heatmap

## Dropdown (Variables)
- **year** (query) → Multiple Select
- **month** (query) → Multiple Select
- **mold_no** (query) → Single Select
- **mc_no** (query) → Single Select
- **part_no** (query) → Single Select

## Panel ทั้งหมด

### Panel: CAVITY  INSPECTION COUNT (NG) PER CAVITY
- ประเภท Panel: `barchart`
- Query (ย่อ): `WITH unique_records AS (
SELECT DISTINCT
[Part Type],
[Identical ID],
[QC Member],
[Year Record],
[Month Record],
[File Run No.],
[Sequence],
LTRIM(RT...`
- Threshold สี:
  - ค่า None → สี green