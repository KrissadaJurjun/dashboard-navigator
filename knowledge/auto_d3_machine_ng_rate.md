# สรุปจาก Grafana JSON: d3_machine_ng_rate

## Dropdown (Variables)
- **month** (query) → Multiple Select
- **year** (query) → Multiple Select

## Panel ทั้งหมด

### Panel: MACHINE NG LOT RATE BY M/C
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