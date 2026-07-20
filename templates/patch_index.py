#!/usr/bin/env python3
"""
patch_index.py — เพิ่ม Language Guard override handler ใน index.html
วางไฟล์นี้ใน templates/ แล้วรัน: python patch_index.py
"""
from pathlib import Path

f = Path("index.html")
if not f.exists():
    print("❌ ไม่พบ index.html — ตรวจสอบว่ารันจาก templates/ folder")
    exit(1)

html = f.read_text(encoding="utf-8")

# ── Patch 1: เพิ่ม override handler ก่อน data.chunk ──────────────────────
OLD1 = "                    if (data.chunk) { full+=data.chunk; sc.innerHTML=full.replace(/\\*\\*(.*?)\\*\\*/g,'<strong>$1</strong>').replace(/\\n/g,'<br>'); c.scrollTop=c.scrollHeight; }"

NEW1 = """                    // ✅ Language Guard: server ส่ง Thai มาแทน non-Thai response
                    if (data.override) {
                        full = data.content;
                        sc.innerHTML = full
                            .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
                            .replace(/\\n/g, '<br>');
                        c.scrollTop = c.scrollHeight;
                        continue;
                    }
                    if (data.chunk) { full+=data.chunk; sc.innerHTML=full.replace(/\\*\\*(.*?)\\*\\*/g,'<strong>$1</strong>').replace(/\\n/g,'<br>'); c.scrollTop=c.scrollHeight; }"""

if OLD1 in html:
    html = html.replace(OLD1, NEW1)
    print("✅ Patch 1 สำเร็จ: เพิ่ม override handler แล้ว")
else:
    print("⚠️  Patch 1: ไม่พบ target — ลอง fallback pattern")
    # Fallback: ค้นหา pattern สั้นกว่า
    import re
    pattern = r"(if \(data\.chunk\) \{)"
    if re.search(pattern, html):
        FALLBACK_INSERT = """// ✅ Language Guard override
                    if (data.override) {
                        full = data.content;
                        sc.innerHTML = full.replace(/\\*\\*(.*?)\\*\\*/g,'<strong>$1</strong>').replace(/\\n/g,'<br>');
                        c.scrollTop = c.scrollHeight;
                        continue;
                    }
                    """
        html = re.sub(pattern, FALLBACK_INSERT + r"\1", html, count=1)
        print("✅ Patch 1 Fallback สำเร็จ")
    else:
        print("❌ ไม่พบ data.chunk — กรุณาแก้ด้วยมือ (ดูคำแนะนำ)")

f.write_text(html, encoding="utf-8")
print("\n✅ index.html แก้ไขสำเร็จ — Restart server แล้วทดสอบครับ")
print("คำสั่ง: cd .. && uvicorn main:app --reload --host 0.0.0.0 --port 8000")