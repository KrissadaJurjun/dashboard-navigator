# สรุปจาก Grafana JSON: d4_ng_records

## Panel ทั้งหมด

### Panel: NG RECORDS DETAILS
- ประเภท Panel: `table`
- Query (ย่อ): `SELECT
REPLACE(LTRIM(RTRIM([Production Date [S]]])), '-', '/') AS [Production Date],
LTRIM(RTRIM([Production Time]))
AS [Production Time],
LTRIM(RTRIM...`
- Threshold สี:
  - ค่า None → สี green
  - ค่า 80 → สี red