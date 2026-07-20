# สรุปจาก Grafana JSON: d3_cycle_time

## Dropdown (Variables)
- **ct_mc_no** (query) → Multiple Select
- **ct_month** (query) → Multiple Select
- **ct_year** (query) → Multiple Select
- **ct_mold** (query) → Multiple Select
- **ct_part_no** (query) → Multiple Select

## Panel ทั้งหมด

### Panel: CYCLE TIME - MONTHLY AVG
- ประเภท Panel: `timeseries`
- Query (ย่อ): `WITH NgLots AS (
SELECT
TRY_CONVERT(DATE, [Production Date [S]]]) AS prod_date,
TRY_CAST(LTRIM(RTRIM([Cycle Time (sec)])) AS FLOAT) AS ct_sec,
LTRIM(R...`
- Query (ย่อ): `WITH base AS (
SELECT
-- ✅ ใช้ TRY_CONVERT แทน CAST → ป้องกัน out-of-range error
TRY_CONVERT(DATE, [Production Date [S]]]) AS prod_date,
[Judgement [S...`
- Threshold สี:
  - ค่า None → สี green
  - ค่า 80 → สี red