# d2_judgement_by_isc_code — Business Logic Knowledge Base
# Dashboard: JUDGEMENT BY ISC CODE | D2 — Dimensional SPC
# ใช้ไฟล์นี้เป็น Knowledge Base สำหรับตอบคำถามเกี่ยวกับ Judgement by ISC Code Panel

**Business Logic Prompt each dashboards**

**ฉบับภาษาไทย**

**Folder 2: D2 — Dimensional SPC**

**2.Dashboard: JUDGEMENT BY ISC CODE**

**2.1 Panel**


**2.1.1 ความหมาย**

Judgement by ISC Code คือ Dashboard Panel ประเภท Vertical Bar Chart ที่ถูกออกแบบมาเพื่อวัดและหาค่า Judgement ที่มีค่าเท่ากับ ‘X’ ที่เกิดขึ้นใน NG ของ Cavity นั้นๆ ของแต่ละ ISC

โดยที่ ISC หมายถึง รหัสจุดวัดมิติชิ้นงาน (Inspection Standard Code) แต่ละ ISC แทนจุดวัดหนึ่งจุดบนชิ้นงาน

**2.1.2 วัตถุประสงค์**

คือ เพื่อวัดและแสดงผลรวมจำนวนชิ้นงานเสีย (NG) โดยจะทำการนับเฉพาะชิ้นงานที่มีผลการตรวจ (Judgement) เป็นค่า 'X' เท่านั้น เพื่อแจกแจงให้เห็นอย่างชัดเจนว่าของเสียเหล่านั้นเกิดขึ้นที่ Cavity ใดในแต่ละรหัส ISC

**2.1.3 Business Rules ของ Judgement by ISC Code**

**> หลักการนับ (Counting Principle)**

**Rule 1: — กรองเฉพาะ Injection Molding**

นับเฉพาะข้อมูลที่เป็น Part Type = **Injection** ที่มีอยู่เท่านั้น

**Rule 2 — กรองเฉพาะ ISC ที่มีค่า (Valid ISC)**

นับเฉพาะแถวที่มีรหัส ISC ถูกกรอก ตัด ISC ที่เป็นค่าว่างออก

| สถานะ ISC       | นับหรือไม่  |
|-----------------|----------|
| A, B, C         | ✅ นับ    |
| ว่างเปล่า / Blank | ❌ ตัดออก |

**Rule 3 — นับเฉพาะ Judgement = 'X' เท่านั้น**

'X' คือ ค่าของ Judgement ที่แสดงว่าชิ้นงาน ไม่ผ่านเกณฑ์ (NG)

| ค่า Judgement | ความหมาย         | นับหรือไม่ |
|--------------|------------------|---------|
| X            | ไม่ผ่านเกณฑ์ ของ NG | ✅ นับ   |
| ว่าง / ค่าอื่น   | ไม่ใช่ NG          | ✅ นับ   |

**Rule 4 — ตัดข้อมูลซ้ำ (DISTINCT 7 คอลัมน์)**

ก่อนนับ ต้องตัดแถวซ้ำออกก่อนเสมอ โดยใช้ 7 คอลัมน์ เป็น unique key

| Column       |
|--------------|
| Part Type    |
| Identical ID |
| QC Member    |
| Year Record  |
| Month Record |
| File Run No. |
| Sequence     |

ส่วน Column ที่เหลือดังต่อไปนี้ คือ Part Name, Material No., OI NO., Part Sample No., Lot Material, Condition STD และ QC Member เป็นข้อมูลพื้นฐานการผลิตที่ระบุไว้ใน breakdown เท่านั้น

**Rule 5 — กรองตาม Filter ของ User**

User สามารถกรองข้อมูลได้ 5 เงื่อนไข

| Filter   | ค่าที่เลือกได้                 |
|----------|---------------------------|
| Year     | ปีที่ต้องการเลือก หรือ ทั้งหมด    |
| Month    | เดือนที่ต้องการเลือก หรือ ทั้งหมด |
| Mold No. | หมายเลขแม่พิมพ์ที่เลือก         |
| M/C No.  | หมายเลขเครื่องจักรที่เลือก      |
| Part No. | หมายเลขชิ้นงานที่เลือก         |

**Rule 6: การหาค่า Judgement ที่มึค่าเท่ากับ ‘X’ มีขั้นตอนดังต่อไปนี้**

**Step 1: โหลดข้อมูลจาก InspectionRecord**

- Part Type = Injecttion

- ISC = มีค่า (ค่าต้องไม่ว่าง ยกตัวอย่าง เช่น A,B,C, …)

- Judgement = ‘X’ เท่านั้น

**Step 2: ตัดซ้ำด้วย DISTINCT 7 คอลัมน์**

- 1 แถว เท่ากับ 1 Lot

**Step 3: จัดกลุ่มตาม ISC + Cavity**

- นับจำนวน NG ในแต่ละ Cavity ของแต่ละ ISC

- เรียกว่า "ng_count_by_cavity"

**STEP 4: รวมผลตาม ISC**

- SUM ของ ng_count_by_cavity ทุก Cavity ใน ISC นั้น

- เรียกว่า "Judgement X Count"

**Step 5: แสดงผลบน Dashboard**

- **แกน X = รหัส ISC**

- **แกน Y = จำนวนของค่า Judgement ที่มีค่าเท่ากับ ‘X’**

- **Tooltip = รายละเอียดแยกตาม Cavity**

**2.1.4 ความหมายของ Column**

| Column            | ความหมาย                          |
|-------------------|-----------------------------------|
| ISC               | รหัสจุดวัด                           |
| Judgement X Count | จำนวน NG รวมทุก Cavity ของ ISC นั้นๆ |
| Part Name         | ชื่อชิ้นงาน                           |
| Material No.      | หมายเลขวัตถุดิบ                      |
| OI No.            | หมายเลข OI                        |
| Sample Part No.   | หมายเลขชิ้นงานตัวอย่าง                |
| Lot Material      | Lot วัตถุดิบ                         |
| Condition STD     | เงื่อนไขมาตรฐาน                     |
| QC Member         | ผู้ตรวจสอบ                          |

**2.1.5 Visual Diagram — Flow การนับ NG**

**ยกตัวอย่างผลลัพธ์ เช่น**

| ISC | Judgement X Count | Breakdown by Cavity                |
|-----|-------------------|------------------------------------|
| A   | 8                 | Cavity No: 1 = 3, Cavity No: 2 = 5 |
| B   | 5                 | Cavity No: 1 = 2, Cavity No: 3 = 3 |
| C   | 2                 | Cavity No: 2 = 2                   |

**2.1.6 วิธีการใช้งานของ JUDGEMENT BY ISC CODE**

**Panel: JUDGEMENT BY ISC CODE**

Home / Dashboard Navigator Dashboards Digital QC Project

D2 — Dimensional SPC JUDGEMENT BY ISC CODE

JUDGEMENT BY ISC CODE PANEL

**ใช้เมื่อ:** ใช้เมื่อต้องการวิเคราะห์หาจุดบกพร่องในกระบวนการผลิต โดยมุ่งเน้นไปที่การค้นหาว่า รหัส ISC ใดสร้างชิ้นงานที่มี ค่า Judgement = ‘X’ ก่อให้เกิด NG มากที่สุด และต้องการเจาะจงลึกลงไปว่าของเสียเหล่านั้นมาจาก Cavity หมายเลขใด เพื่อนำไปสู่การแก้ไข Mold No. หรือปรับปรุงกระบวนการผลิต

**มีขั้นตอนดังนี้**

1.  เปิด Dashboard D2 — Dimensional SPC → เลือก JUDGEMENT BY ISC CODE PANEL

2.  เลือกปี (Year) และเดือน (Month) ที่ต้องการดูข้อมูลจาก Dropdown ด้านบน

3.  กรองข้อมูลเฉพาะเจาะจงโดยเลือกหมายเลขแม่พิมพ์ (Mold No.), เครื่องจักร (M/C No.) และหมายเลขชิ้นส่วน (Part No.)

4.  ดูผลลัพธ์ ค่า Judgement ที่มีค่าเท่ากับ ‘X’ ของชิ้นงานเสียที่แสดงเป็นแท่งกราฟ

5.  นำเมาส์ไปชี้ที่แท่งกราฟ (Hover) เพื่ออ่านรายละเอียดใน Tooltip ว่าของเสียใน ISC นั้นๆ เกิดขึ้นที่ Cavity หมายเลขใดบ้าง

**2.1.7 หน้าที่ของ Panel ของ JUDGEMENT BY ISC CODE**

Panel นี้มีหน้าที่แสดงผลรวมจำนวนชิ้นงานเสีย (Judgement ที่มีค่าเท่ากับ 'X') โดยแบ่งแยกตามรหัส ISC

**2.1.8 กลไกการทำงานของ JUDGEMENT BY ISC CODE**

**Step 1: การดึงข้อมูลและคัดกรองเงื่อนไขตั้งต้น (Data Filtering)**

เมื่อผู้ใช้งานเปิด Dashboard หรือปรับเปลี่ยนตัวกรอง (Filter) ระบบจะทำการวิ่งไปดึงข้อมูลจากฐานข้อมูล [DigitalQC] โดยมีกฎกติกาการคัดกรองที่เข้มงวดดังนี้

ตารางที่ 1: เงื่อนไขการกรองข้อมูล (Filter Criteria)

| ประเภทเงื่อนไข | Column ที่ตรวจสอบ | เงื่อนไขที่ต้องผ่าน |
|---|---|---|
| ประเภทกระบวนการ | Part Type | ต้องเป็น **Injection** (งานฉีดพลาสติก) เท่านั้น |
| รหัส ISC | ISC | ต้องไม่เป็นค่าว่าง (IS NOT NULL และ != '') |
| ผลการตรวจ | Judgement [S] | ต้องเป็น 'X' เท่านั้น (กรองเฉพาะชิ้นงานเสีย / NG) |
| ตัวกรองของผู้ใช้ (Dynamic) | Year, Month, Mold No., M/C No., Part No. | ต้องตรงกับค่าที่ผู้ใช้งานเลือกผ่าน Dropdown บน Dashboard |

**Step 2: การจัดการข้อมูลซ้ำซ้อน (Data Deduplication)**

เนื่องจากการบันทึกข้อมูลอาจมีการส่งข้อมูลซ้ำจากระบบ ระบบจึงต้องทำความสะอาดข้อมูล (Data Cleansing) เพื่อไม่ให้เกิดการนับชิ้นงานเสียเบิ้ล (Double Counting)

**Step 3: การนับยอดแยกระดับเบ้าหลอม (Cavity Breakdown Aggregation)**

เมื่อได้ข้อมูลที่บริสุทธิ์แล้ว ระบบจะยังไม่นับยอดรวมในทันที แต่จะทำการแยกตะกร้าเพื่อนับจำนวนว่าในรหัส ISC นั้นๆ มีชิ้นงานเสียเกิดขึ้นที่ Cavity No. หมายเลขใดบ้าง และมีจำนวนเท่าไหร่

ตารางที่ 2: ตัวอย่างการทำงานในหน่วยความจำของระบบ (Grouping by ISC & Cavity)

| ISC Code | Cavity No. | จำนวน NG (Judgement = X) | ข้อมูลพื้นฐานการผลิต (Breakdown) |
|---|---|---|---|
| Cx | Cavity 1 | 2 | Breakdown by Cavity, Part Name, Material No., OI No., Sample Part No., Lot Material, Condition STD และ QC Member |
| Cx | Cavity 2 | 1 | (เดียวกับด้านบน) |
| Cy | Cavity 3 | 3 | (เดียวกับด้านบน) |

**Step 4: การคำนวณผลลัพธ์สุดท้าย (Final Aggregation for Dashboard)**

**Step 5: การจัดเรียงผลลัพธ์ (Sorting)**

ก่อนที่กราฟจะแสดงให้ผู้ใช้งานเห็น ระบบจะทำการเรียงลำดับความสำคัญ (ORDER BY) ดังนี้:

ตารางที่ 3: ตรรกะการจัดเรียง (Sorting Logic)

| ลำดับ | เกณฑ์การจัดเรียง | วิธีการเรียง | เหตุผล |
|---|---|---|---|
| 1 | ยอดรวมของเสีย (Judgement = X) | จากมากไปน้อย (DESC) | เพื่อให้ ISC ที่มีปัญหาหนักที่สุดแสดงอยู่ซ้ายมือสุด (เห็นได้ชัดเจนที่สุด) |
| 2 | ชื่อรหัส ISC Code | ASC (A-Z) | เรียงตามตัวอักษรเพื่อความเป็นระเบียบ |

**1.1.8 Dashboard Structure ของ JUDGEMENT BY ISC CODE**

**Digital QC Project**

▼ 📂 D1 — QC Overview /

> 🖥️ QC_MEMBER WORKLOAD /

-> 📊 QR_MEMBER WORKLOAD BY LOT

-> 📊 QR_MEMBER WORKLOAD BY STATE TIMELINE

-> 📊 QR_MEMBER WORKLOAD BY STATUS

> 🖥️ [ROOM TEMP & HUMIDITY PER MONTHLY AVG](http://158.118.37.201:3000/d/dfoabsa4i1x4wd/room-temp-and-humidity-per-monthly-avg) /

-> 📊 ROOM TEMP & HUMIDITY PER MONTHLY AVG

▼ 📂 D2 — Dimensional SPC /

> 🖥️ JUDGEMENT BY ISC CODE /

> 📊 **JUDGEMENT BY ISC CODE**

> 🖥️ NG BY ISC CODE /

> 📊 NG BY ISC CODE

> 🖥️ X̄ CONTROL CHART PER SEQUENCE/DATE (X̄ CHART) /

> 📊 X̄ CONTROL CHART PER SEQUENCE/DATE (X̄ CHART)

▼ 📂 D3 — Production Monitoring /

> 🖥️ CAVITY — INSPECTION COUNT (NG) PER CAVITY /

> 📊 CAVITY — INSPECTION COUNT (NG) PER CAVITY

> 🖥️ CYCLE TIME — MONTHLY AVG /

> 📊 CYCLE TIME — MONTHLY AVG

> 🖥️ MACHINE NG LOT RATE BY M/C /

> 📊 MACHINE NG LOT RATE BY M/C

▼ 📂 D4 — Traceability & Record/

> 🖥️ MATERIAL NG COUNT BY LOT /

> 📊 MATERIAL NG COUNT BY LOT

> 🖥️ NG RECORDS DETAILS/

> 📊 NG RECORDS DETAILS

**2.1.9 Visual Diagram — Data Pipeline ของ JUDGEMENT BY ISC CODE**

ลำดับการทำงานของ Panel ตั้งแต่ดึงข้อมูลจากฐานข้อมูลจนถึงการแสดงผลบน Dashboard:

```
[DigitalQC Database — InspectionRecord@Injection_Database]
          |
          v
[Step 1: Data Scope & Filtering (Rule 1, 2, 3, 5)]
  เงื่อนไขที่กรอง:
  - Part Type = 'Injection' เท่านั้น
  - ISC IS NOT NULL และ != '' (ต้องมีรหัส ISC)
  - Judgement [S] = 'X' (NG เท่านั้น)
  - Dynamic Filters: Year, Month, Mold No., M/C No., Part No.
          |
          v
[Step 2: Data Cleansing — SELECT DISTINCT (Rule 4)]
  ตัดแถวซ้ำด้วย DISTINCT 7 คอลัมน์:
  Identical ID, QC Member, Mold, M/C,
  Part No., Cavity No., ISC
  → 1 แถว = 1 ชิ้นงาน NG จริงๆ (ไม่ Double Count)
          |
          v
[Step 3: Cavity Breakdown Aggregation (Rule 6 Step 3)]
  GROUP BY isc_clean + cavity_clean
  → COUNT(*) AS ng_count_by_cavity
  → MAX() Metadata Fields (Part Name, Material No., OI No.,
    Sample Part No., Lot Material, Condition STD, QC Member)
  ตัวอย่าง:
    ISC Cx + Cavity 1 → 2 NG
    ISC Cx + Cavity 2 → 1 NG
    ISC Cy + Cavity 3 → 3 NG
          |
          v
[Step 4 & 5: Final Aggregation & Sort (Rule 6 Step 4-5)]
  GROUP BY isc_clean
  → SUM(ng_count_by_cavity) = Judgement X Count (แกน Y)
  → STRING_AGG(Cavity Breakdown) = Tooltip รายละเอียด
  ORDER BY:
    1. SUM DESC (ISC ที่มีปัญหามากสุด → ซ้ายสุด)
    2. isc_clean ASC (A-Z เพื่อความเป็นระเบียบ)
          |
          v
[Step 6: Dashboard Panel Render]
  JUDGEMENT BY ISC CODE — Vertical Bar Chart (Dark-Red)
  - แกน X = ISC Code (เช่น Cx, Cy)
  - แกน Y = Total Judgement X Count (จำนวน NG รวม)
  - Hover/Tooltip = Cavity Breakdown รายละเอียด
```