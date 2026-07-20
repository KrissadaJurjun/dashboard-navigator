# สรุปจาก Grafana JSON: d1_room_temp_humidity_per_monthly_avg

## Dropdown (Variables)
- **rh_month** (query) → Multiple Select
- **rh_year** (query) → Multiple Select
- **rh_mold** (query) → Multiple Select
- **rh_mc_no** (query) → Multiple Select
- **rh_part_no** (query) → Multiple Select

## Panel ทั้งหมด

### Panel: ROOM TEMP  HUMIDITY PER MONTHLY AVG
- ประเภท Panel: `timeseries`
- Query (ย่อ): `WITH NgTime AS (
SELECT
TRY_CONVERT(DATE, [Production Date [S]]]) AS dt,
MAX(CASE WHEN LTRIM(RTRIM(UPPER([Judgement [S]]]))) = 'X'
THEN TRY_CONVERT(TI...`
- Query (ย่อ): `WITH base AS (
SELECT
TRY_CONVERT(DATE, [Production Date [S]]]) AS dt,
TRY_CAST(LTRIM(RTRIM([Room Temp (C)])) AS FLOAT) AS temp_val,
TRY_CAST(LTRIM(RT...`
- Query (ย่อ): `WITH base AS (
SELECT
TRY_CONVERT(DATE, [Production Date [S]]]) AS dt,
TRY_CAST(LTRIM(RTRIM([Room Temp (C)])) AS FLOAT) AS temp_val,
TRY_CAST(LTRIM(RT...`
- Query (ย่อ): `WITH lot_data AS (
SELECT
[Identical ID],
TRY_CONVERT(DATE, [Production Date [S]]]) AS dt,
AVG(TRY_CAST(LTRIM(RTRIM([Room Temp (C)])) AS FLOAT)) AS av...`
- Threshold สี:
  - ค่า None → สี green
  - ค่า 80 → สี red
- Field 'avg_humid_line' → สี: semi-dark-orange
- Field 'avg_temp_line' → สี: dark-blue
- Field 'ng_temp_marker' → สี: dark-red
- Field 'ng_humid_marker' → สี: #821ae5