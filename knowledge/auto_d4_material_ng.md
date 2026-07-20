# สรุปจาก Grafana JSON: d4_material_ng

## Dropdown (Variables)
- **year** (query) → Multiple Select
- **month** (query) → Multiple Select
- **mold_no** (query) → Multiple Select

## Panel ทั้งหมด

### Panel: MATERIAL NG RATE COUNT BY LOT
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
[Status]...`
- Threshold สี:
  - ค่า None → สี green
  - ค่า 100 → สี red