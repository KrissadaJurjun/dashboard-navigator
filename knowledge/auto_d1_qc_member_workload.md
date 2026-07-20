# สรุปจาก Grafana JSON: d1_qc_member_workload

## Dropdown (Variables)
- **part_type** (query) → Multiple Select
- **year** (query) → Multiple Select
- **month** (query) → Multiple Select

## Panel ทั้งหมด

### Panel: QR_MEMBER WORKLOAD BY NG
- ประเภท Panel: `barchart`
- Query (ย่อ): `WITH distinct_lots AS (
SELECT DISTINCT
LTRIM(RTRIM([Part Type]))
AS Part_Type,
LTRIM(RTRIM([Identical ID])) AS Identical_ID,
LTRIM(RTRIM([QC Member])...`
- Threshold สี:
  - ค่า None → สี green
  - ค่า 80 → สี red
- Field 'OK Lots' → สี: green
- Field 'NG Lots' → สี: dark-red
- Field 'Blank Lots' → สี: text

### Panel: QR_MEMBER WORKLOAD BY STATE TIMELINE
- ประเภท Panel: `barchart`
- Query (ย่อ): `WITH distinct_lots AS (
SELECT
LTRIM(RTRIM([Part Type]))
AS Part_Type,
LTRIM(RTRIM([Identical ID])) AS Identical_ID,
LTRIM(RTRIM([QC Member]))
AS QC_M...`
- Threshold สี:
  - ค่า None → สี green
- Field 'S (Start)' → สี: dark-green
- Field 'S+E (Start+End)' → สี: dark-blue
- Field 'M (Middle)' → สี: dark-purple
- Field 'E (End)' → สี: dark-red

### Panel: QR_MEMBER WORKLOAD BY LOT
- ประเภท Panel: `barchart`
- Query (ย่อ): `WITH distinct_lots AS (
SELECT DISTINCT
[Part Type],
[Identical ID],
[QC Member],
[Year Record],
[Month Record],
[File Run No.],
[Sequence]
FROM [Digi...`
- Threshold สี:
  - ค่า 0 → สี green
  - ค่า 80 → สี red