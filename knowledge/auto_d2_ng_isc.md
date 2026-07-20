# สรุปจาก Grafana JSON: d2_ng_isc

## Dropdown (Variables)
- **month** (query) → Multiple Select
- **year** (query) → Multiple Select
- **mold_no** (query) → Single Select
- **mc_no** (query) → Single Select
- **part_no** (query) → Single Select

## Panel ทั้งหมด

### Panel: NG BY ISC CODE (filtered by part)
- ประเภท Panel: `barchart`
- Query (ย่อ): `WITH unique_lots AS (
SELECT DISTINCT
[Part Type],
[Identical ID],
[QC Member],
[Year Record],
[Month Record],
[File Run No.],
[Sequence],
[Mold No.],...`
- Threshold สี:
  - ค่า 0 → สี green