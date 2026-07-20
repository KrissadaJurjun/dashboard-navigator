# สรุปจาก Grafana JSON: d2_xbar_chart

## Dropdown (Variables)
- **spc_month** (query) → Multiple Select
- **spc_year** (query) → Multiple Select
- **spc_mold** (query) → Single Select
- **spc_mc_no** (query) → Single Select
- **spc_part_no** (query) → Single Select
- **spc_isc** (query) → Single Select
- **spc_cavity** (query) → Single Select

## Panel ทั้งหมด

### Panel: Panel Title
- ประเภท Panel: `stat`
- Query (ย่อ): `WITH ng_lot_ids AS (
SELECT DISTINCT [Identical ID]
FROM [DigitalQC].[dbo].[InspectionRecord@Injection_Database]
WHERE UPPER(LTRIM(RTRIM([Judgement [S...`
- Threshold สี:
  - ค่า None → สี green
  - ค่า 80 → สี red

### Panel: Panel Title
- ประเภท Panel: `timeseries`
- Query (ย่อ): `WITH ng_lot_ids AS (
SELECT DISTINCT [Identical ID]
FROM [DigitalQC].[dbo].[InspectionRecord@Injection_Database]
WHERE UPPER(LTRIM(RTRIM([Judgement [S...`
- Threshold สี:
  - ค่า None → สี green
  - ค่า 80 → สี red
- Field '^xbar_val$' → สี: text
- Field '^r_val$' → สี: light-blue
- Field '^ul_val$' → สี: light-green
- Field '^std_val$' → สี: semi-dark-orange
- Field '^ll_val$' → สี: dark-red