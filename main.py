"""
Dashboard Navigator — main.py
============================
หน้าที่ของไฟล์นี้: Infrastructure + Routing เท่านั้น

ไม่มีเนื้อหา Dashboard ใดๆ ในนี้
ไม่มีกฎการตอบใดๆ ในนี้

กฎทั้งหมด → knowledge/ai_rules.md
ข้อมูล Dashboard → knowledge/*.md
"""
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import httpx, json, os, uuid, re
from datetime import datetime
from pathlib import Path

app = FastAPI(title="Dashboard Navigator")

if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ── ค่า config (ปรับ model ตรงนี้เท่านั้น) ────────────────────────────────
OLLAMA_URL    = "http://localhost:11434/api/chat"
OLLAMA_MODEL  = "qwen2.5:7b"   # เปลี่ยน model ตรงนี้   # เปลี่ยน model ตรงนี้
KNOWLEDGE_DIR = Path("knowledge")
MEMORY_DIR    = Path("memory")
MEMORY_DIR.mkdir(exist_ok=True)

# ── Ollama options (ปรับ speed/quality ตรงนี้) ────────────────────────────
MAIN_OPTIONS = {
    "temperature":    0.3,
    "num_predict":    400,   # 3b รับได้มากกว่า → ตอบครบทั้ง 3 Panel
    "repeat_penalty": 1.1,
    "stop":           ["</s>", "\n\n\n\n"],
    "num_ctx":        1024,   # เพิ่มจาก 2048 → 4096 เพื่อรองรับ ai_rules.md
    "num_thread":     4,
}
RETRY_OPTIONS = {
    "temperature": 0.3,
    "num_predict": 400,
    "stop":        ["</s>", "\n\n\n\n"],
    "num_ctx":     1024,
    "num_thread":  4,
}

DASHBOARDS = [
    {
        "id": "d1", "name": "D1 — QC Overview",
        "description": "ภาพรวมคุณภาพการผลิตทั้งหมด สถานะ OK/NG, Workload, Cavity Heatmap",
        "url": "http://158.118.37.201:3000/dashboards/f/efq9jvhpz78xsb/",
        "icon": "📊", "color_class": "blue",
        "tags": ["overview", "NG", "OK", "cavity"],
        "sub_dashboards": [
            {"name": "QC Member Workload",               "url": "http://158.118.37.201:3000/d/ffnekdrm4tyiod/qc-member-workload",                           "icon": "👥"},
            {"name": "Room Temp & Humidity Monthly Avg", "url": "http://158.118.37.201:3000/d/dfoabsa4i1x4wd/room-temp-and-humidity-per-monthly-avg",         "icon": "🌡️"}
        ]
    },
    {
        "id": "d2", "name": "D2 — Dimensional SPC",
        "description": "ควบคุมคุณภาพเชิงสถิติ X̄/R Chart, UCL/LCL",
        "url": "http://158.118.37.201:3000/dashboards/f/dfq9jwmklx5oge/",
        "icon": "📈", "color_class": "purple",
        "tags": ["SPC", "XBar", "control chart", "UCL", "LCL"],
        "sub_dashboards": [
            {"name": "Judgement by ISC Code",              "url": "http://158.118.37.201:3000/d/afpgumpthc6bkc/judgement-by-isc-code",                           "icon": "⚖️"},
            {"name": "NG by ISC Code (filtered by part)",  "url": "http://158.118.37.201:3000/d/bfnh4fdmncao0f/ng-by-isc-code-filtered-by-part",                 "icon": "❌"},
            {"name": "X̄ Control Chart per Sequence/Date", "url": "http://158.118.37.201:3000/d/ffogyujv8lhj4f/xcc84-control-chart-per-sequence-date-xcc84-chart","icon": "📉"}
        ]
    },
    {
        "id": "d3", "name": "D3 — Production Monitoring",
        "description": "ติดตามการผลิต Cycle Time, Room Temperature, Humidity",
        "url": "http://158.118.37.201:3000/dashboards/f/ffq9jxqm1bsw0a/",
        "icon": "🏭", "color_class": "green",
        "tags": ["production", "cycle time", "temperature", "humidity"],
        "sub_dashboards": [
            {"name": "Cavity — Inspection Count (NG) per Cavity", "url": "http://158.118.37.201:3000/d/ffnl12r6hv474f/cavity-e28094-inspection-count-ng-per-cavity","icon": "🔲"},
            {"name": "Cycle Time — Monthly Avg",                  "url": "http://158.118.37.201:3000/d/bfnhn1lewqzuoe/cycle-time-e28094-monthly-avg",             "icon": "⏱️"},
            {"name": "Machine NG Lot Rate by M/C",                "url": "http://158.118.37.201:3000/d/bfovawrjiuh34e/machine-ng-lot-rate-by-m-c",               "icon": "⚙️"}
        ]
    },
    {
        "id": "d4", "name": "D4 — Traceability & Record",
        "description": "ย้อนรอยข้อมูล ค้นหา Lot, ISC Code, NG Records",
        "url": "http://158.118.37.201:3000/dashboards/f/bfq9jz9t122v4b/",
        "icon": "🔍", "color_class": "amber",
        "tags": ["traceability", "ISC", "lot", "record"],
        "sub_dashboards": [
            {"name": "Material NG Count by Lot", "url": "http://158.118.37.201:3000/d/bfo3tygy944cga/material-ng-count-by-lot", "icon": "📦"},
            {"name": "NG Records Details",       "url": "http://158.118.37.201:3000/d/efo6c6m2269kwe/ng-records-details",       "icon": "📋"}
        ]
    },
]


# ════════════════════════════════════════════════════════════════
# ROUTING CONFIG — ไฟล์ไหนตอบคำถามอะไร
# ════════════════════════════════════════════════════════════════

# คำถามประเภทไหน → section headers ที่ต้องโหลดจากไฟล์ .md
# (ต้องตรงกับชื่อ header ใน .md files)
SECTION_HEADERS_MAP = {
    "วิธีอ่านผลลัพธ์": ["วิธีอ่านผลลัพธ์", "ความหมายของสี"],
    "วิธีการใช้งาน":   ["วิธีการใช้งาน"],
    "วัตถุประสงค์":    ["วัตถุประสงค์", "ความสำคัญ"],
    "Business Rule":  ["business rules", "กลไก"],
    "เปรียบเทียบ":    ["วัตถุประสงค์"],
    "ตัวอย่างข้อมูล": ["ตัวอย่าง"],
    "ภาพรวม":         ["วัตถุประสงค์"],
}

# keyword → ไฟล์ knowledge ที่ต้องโหลด
KNOWLEDGE_MAP = {
    "d1_workload": {
        "triggers": [
            "qc member workload","qc_member workload","workload","ภาระงาน",
            "by lot","by state","by status","qc member","panel workload",
            "กี่ panel","3 panel","panel ทั้ง",
            "ความหมายของสี","สีใน","สีของ","สีแต่ละ",
            "สีเขียว","สีแดง","สีส้ม","สีเหลือง",
            "วิธีอ่าน","หลักการอ่าน","อ่าน dashboard","อ่านผลลัพธ์",
            "วิธีใช้","วิธีการใช้","วัตถุประสงค์","กลไก","business rule",
        ],
        "files":          ["d1_qc_member_workload.md"],
        "panel_specific": True,
    },
    "d1_temp": {
        "triggers": ["room temp","อุณหภูมิ","ความชื้น","humidity","ห้องผลิต","monthly avg"],
        "files":    ["d1_room_temp_humidity_per_monthly_avg.md"],
    },
    "d2_spc": {
        "triggers": ["spc","xbar","x-bar","ucl","lcl","isc","judgement","control chart","d2"],
        "files":    ["d2_spc.md","auto_d2_judgement_isc.md","auto_d2_ng_isc.md","auto_d2_xbar_chart.md"],
    },
    "d3_prod": {
        "triggers": ["cavity","cycle time","machine","d3","การผลิต","heatmap"],
        "files":    ["d3_production.md","auto_d3_cavity_heatmap.md","auto_d3_cycle_time.md","auto_d3_machine_ng_rate.md"],
    },
    "d4_trace": {
        "triggers": ["traceability","ng record","material ng","ย้อนรอย","d4"],
        "files":    ["d4_traceability.md","auto_d4_material_ng.md","auto_d4_ng_records.md"],
    },
}

# Question type classifiers — trigger keywords เท่านั้น ไม่มีเนื้อหา
QUESTION_TYPES = [
    ("วิธีอ่านผลลัพธ์", [
        "วิธีอ่าน","วิธีการอ่าน","อ่านผล","อ่านกราฟ","แปลผล",
        "หลักการอ่าน","การอ่าน dashboard","อ่าน dashboard",
        "อ่านผลลัพธ์","อธิบายหลักการ","หลักการ",
        "ความหมายของสี","สีหมาย","สีแปล","สีในกราฟ","สีแสดง",
        "สีเขียว","สีแดง","สีส้ม","สีเหลือง","ตารางสี",
    ]),
    ("วิธีการใช้งาน", [
        "วิธีใช้","วิธีการใช้","วิธีใช้งาน","วิธีการใช้งาน",
        "บอกวิธี","ทำยังไง","เริ่มต้นใช้","การใช้งาน",
    ]),
    ("วัตถุประสงค์", [
        "คืออะไร","ความหมาย","วัตถุประสงค์","จุดประสงค์",
        "ทำอะไร","ความสำคัญ","ประโยชน์","มีไว้เพื่อ",
        "กี่ panel","3 panel","panel ทั้ง",
    ]),
    ("Business Rule", [
        "business rule","กลไก","หลักการ","rule","เงื่อนไข",
        "การกรอง","กรอง","distinct","นับ lot","จำนวน lot",
    ]),
    ("เปรียบเทียบ", [
        "ต่างกัน","ต่างจาก","เปรียบเทียบ","แตกต่าง","vs","เทียบกัน",
        "by lot กับ","by status กับ",
    ]),
    ("ตัวอย่างข้อมูล", [
        "ยกตัวอย่าง","ตัวอย่าง","แสดงตาราง","ข้อมูลจริง","ตัวเลข",
    ]),
]


# ════════════════════════════════════════════════════════════════
# UTILITIES — ฟังก์ชันช่วยเหลือ ไม่มีเนื้อหา Dashboard
# ════════════════════════════════════════════════════════════════

def normalize(text: str) -> str:
    return re.sub(r"[_\s]+", " ", text.strip().lower())

def clean_response(text: str) -> str:
    """ลบอักขระจีน/ญี่ปุ่น/เกาหลีออก"""
    ZH = {"如下":"ดังนี้","以下":"ดังต่อไปนี้","例如":"ตัวอย่างเช่น",
           "因此":"ดังนั้น","其中":"โดย","所有":"ทั้งหมด","方法":"วิธี"}
    for zh, th in ZH.items():
        text = text.replace(zh, th)
    text = re.sub(r'[\u4E00-\u9FFF\u3400-\u4DBF\u3040-\u309F\u30A0-\u30FF\uAC00-\uD7AF]+','',text)
    return re.sub(r'  +',' ', re.sub(r'\n{4,}','\n\n\n',text)).strip()

def strip_sql(text: str) -> str:
    """ตัด SQL code blocks ออก เก็บ Business Logic"""
    text = re.sub(r'```(?:sql|python|mermaid|json|bash)[^`]*```','',text,flags=re.DOTALL)
    text = re.sub(r'```[^`]*```','',text,flags=re.DOTALL)
    sql_kws = ['SELECT ','FROM ','WHERE ','JOIN ','GROUP BY','ORDER BY',
               'WITH ','HAVING ','UNION ','LEFT JOIN','INNER JOIN','CAST(']
    lines = [l for l in text.split('\n')
             if not any(l.strip().upper().startswith(k) for k in sql_kws)]
    return re.sub(r'\n{4,}','\n\n\n','\n'.join(lines)).strip()


# ════════════════════════════════════════════════════════════════
# KNOWLEDGE LOADER — โหลดไฟล์ .md
# ════════════════════════════════════════════════════════════════

def load_ai_rules() -> str:
    """โหลดกฎทั้งหมดจาก ai_rules.md"""
    fp = KNOWLEDGE_DIR / "ai_rules.md"
    if fp.exists():
        content = fp.read_text(encoding="utf-8")
        print(f"[Rules] ✅ โหลด ai_rules.md: {len(content)} chars")
        return content
    print("[Rules] ⚠️ ไม่พบ ai_rules.md — ใช้ default")
    return ""  # ไม่มี ai_rules.md → ใช้ prompt ว่าง (AI จะพึ่ง training ของ model)

def load_section(filepath: Path, section_headers: list, max_chars: int = 1500) -> str:
    """โหลดเฉพาะ section ที่ตรงกับ headers จากไฟล์ .md
    หยุดที่ # header เท่านั้น ไม่หยุดที่ **bold**
    """
    if not filepath.exists():
        return ""
    clean = strip_sql(filepath.read_text(encoding="utf-8"))
    lines = clean.split('\n')
    blocks, current, active = [], [], False
    for line in lines:
        ll = line.lower().strip()
        is_section_hdr = line.startswith('#')
        is_target      = is_section_hdr and any(h.lower() in ll for h in section_headers)
        if is_section_hdr:
            if is_target:
                if current and active:
                    blocks.append('\n'.join(current))
                current, active = [line], True
            elif active and current:
                blocks.append('\n'.join(current))
                current, active = [], False
        elif active:
            current.append(line)
    if current and active:
        blocks.append('\n'.join(current))
    if blocks:
        out = '\n\n'.join(blocks)
        print(f"[KB] {filepath.name}: {len(blocks)} section(s), {len(out)} chars")
        return out[:max_chars]
    return clean[:max_chars]

def load_file(filepath: Path, max_chars: int = 1500) -> str:
    if not filepath.exists(): return ""
    return strip_sql(filepath.read_text(encoding="utf-8"))[:max_chars]


# ════════════════════════════════════════════════════════════════
# QUESTION ROUTER — จัดการคำถาม
# ════════════════════════════════════════════════════════════════

def classify(question: str) -> tuple[str, list]:
    """จัดประเภทคำถาม → คืน (type, section_headers)"""
    q = normalize(question)
    for q_type, triggers in QUESTION_TYPES:
        if any(normalize(t) in q for t in triggers):
            headers = SECTION_HEADERS_MAP.get(q_type, SECTION_HEADERS_MAP["ภาพรวม"])
            print(f"[Classify] type='{q_type}'")
            return q_type, headers
    return "ภาพรวม", SECTION_HEADERS_MAP["ภาพรวม"]

def detect_panel(q: str) -> str | None:
    """ตรวจ Panel จากคำถาม
    คืน "ALL" เมื่อถาม 'ทั้ง 3 panel'
    คืน Panel name เมื่อระบุ panel ชัดเจน
    คืน None เมื่อไม่แน่ใจ
    """
    # ถามทั้ง 3 panel พร้อมกัน
    if any(k in q for k in ["ทั้ง 3", "ทั้งสาม", "ทั้ง3", "3 panel", "ทุก panel", "ทั้งหมด"]):
        return "ALL"
    # ระบุ Panel เฉพาะ
    if "by lot" in q and "state" not in q and "status" not in q:
        return "QC MEMBER WORKLOAD BY LOT"
    if "by lot" in q:
        return "QC MEMBER WORKLOAD BY LOT"
    if "by state" in q or "state timeline" in q:
        return "QC MEMBER WORKLOAD BY STATE TIMELINE"
    if "by status" in q:
        return "QC MEMBER WORKLOAD BY STATUS"
    return None

def get_context(question: str) -> str:
    """
    Router บริสุทธิ์:
    คำถาม → knowledge group → Panel → section → context
    ไม่มีเนื้อหา Dashboard ในนี้
    """
    q = normalize(question)
    q_type, headers = classify(question)
    panel = detect_panel(q)

    # หา knowledge group
    matched = None
    for group, cfg in KNOWLEDGE_MAP.items():
        if any(normalize(t) in q for t in cfg["triggers"]):
            matched = group
            break

    if not matched:
        fp = KNOWLEDGE_DIR / "overview.md"
        return f"=== overview ===\n{load_file(fp, 2000)}" if fp.exists() else "ไม่พบข้อมูล"

    cfg = KNOWLEDGE_MAP[matched]
    print(f"[Router] group='{matched}' | panel={panel} | type={q_type}")

    # ── โหลด 3 Panel พร้อมกัน (เมื่อถาม "ทั้ง 3 panel") ──────────────
    if panel == "ALL" and cfg.get("panel_specific"):
        all_panels  = ["BY LOT", "BY STATE TIMELINE", "BY STATUS"]
        all_sections = []
        for fname in cfg["files"]:
            fp = KNOWLEDGE_DIR / fname
            if not fp.exists(): continue
            for p in all_panels:
                ph = [f"{h} ({p})" for h in headers]
                s  = load_section(fp, ph, max_chars=900)
                if s:
                    all_sections.append(f"--- {p} ---\n{s}")
        if all_sections:
            print(f"[Router] ALL panels | {len(all_sections)} sections")
            return f"=== d1_workload | ALL ===\n" + "\n\n".join(all_sections)

    # ── โหลดเฉพาะ Panel ที่ถาม ────────────────────────────────────────
    if panel and panel != "ALL" and cfg.get("panel_specific"):
        use_headers = [f"{h} ({panel})" for h in headers]
        chars       = 1800 if q_type == "วิธีอ่านผลลัพธ์" else 1200
    else:
        use_headers = headers
        chars       = 1200

    # ── Multi-panel: ถาม "ทั้ง 3 panel" ────────────────────────────────
    if (panel is None and cfg.get("panel_specific") and
            any(k in q for k in ["ทั้ง 3","ทุก panel","ทั้งหมด","3 panel","แต่ละ panel"])):
        parts = []
        chars = 1200 if q_type == "วิธีอ่านผลลัพธ์" else 800
        for fname in cfg["files"]:
            fp = KNOWLEDGE_DIR / fname
            if not fp.exists(): continue
            for ptag in ["BY LOT","BY STATE TIMELINE","BY STATUS"]:
                ph = [f"{h} ({ptag})" for h in headers]
                sec = load_section(fp, ph, max_chars=chars)
                if sec: parts.append(f"--- {ptag} ---\n{sec}")
        if parts:
            print(f"[Router] MULTI-PANEL: {len(parts)} sections")
            return "=== d1_workload | ALL PANELS ===\n\n" + "\n\n".join(parts)

        # โหลดไฟล์แรกที่มี
    for fname in cfg["files"]:
        fp = KNOWLEDGE_DIR / fname
        if fp.exists():
            section = load_section(fp, use_headers, max_chars=chars)
            if section:
                label = f"{matched}" + (f" | {panel}" if panel else "")
                return f"=== {label} ===\n{section}"

    return f"ไม่พบข้อมูล {matched}"


# ════════════════════════════════════════════════════════════════
# PROMPT BUILDER — รวม ai_rules + context
# ════════════════════════════════════════════════════════════════

def build_prompt(context: str, q_type: str) -> tuple[str, str]:
    """คืน (system_prompt, kb_context) แยกกัน
    system = กฎ
    kb_context = ข้อมูลส่งใน user message เพื่อให้ model focus
    """
    rules = load_ai_rules()
    system = f"{rules}\n\n## Q_TYPE: {q_type}"
    return system, context


# ════════════════════════════════════════════════════════════════
# LANGUAGE GUARD
# ════════════════════════════════════════════════════════════════

def is_non_thai(text: str) -> bool:
    thai    = len(re.findall(r'[\u0E00-\u0E7F]', text))
    chinese = len(re.findall(r'[\u4E00-\u9FFF]', text))
    total   = len(re.findall(r'[a-zA-Z\u0E00-\u0E7F\u4E00-\u9FFF]', text))
    if total == 0: return False
    if chinese > 0: return True
    return (thai / total) < 0.4

def is_repetitive(new_resp: str, last_ai: str) -> bool:
    if not last_ai or len(new_resp) < 20: return False
    n = normalize(new_resp[:100])
    l = normalize(last_ai[:100])
    common = sum(1 for a, b in zip(n, l) if a == b)
    return (common / max(len(n), len(l), 1)) > 0.6


# ════════════════════════════════════════════════════════════════
# SESSION / MEMORY
# ════════════════════════════════════════════════════════════════

def session_path(sid: str) -> Path:
    return MEMORY_DIR / f"{sid}.md"

def parse_ts(line: str) -> str | None:
    parts = line.split(" | ", 1)
    return parts[1].strip() if len(parts) == 2 and parts[1].strip() else None

def load_session(sid: str) -> dict:
    path = session_path(sid)
    if not path.exists():
        return {"id": sid, "title": "New Chat", "messages": [], "is_starred": False}
    lines      = path.read_text(encoding="utf-8").split("\n")
    raw        = lines[0].replace("# ", "").strip() if lines else "New Chat"
    is_starred = raw.startswith("⭐")
    title      = raw.replace("⭐", "").strip()
    messages, role, buf, ts = [], None, [], None
    for ln in lines[2:]:
        if ln.startswith("## 👤 User"):
            if role: messages.append({"role":role,"content":"\n".join(buf).strip(),"timestamp":ts})
            role, buf, ts = "user", [], parse_ts(ln)
        elif ln.startswith("## 🤖 Assistant"):
            if role: messages.append({"role":role,"content":"\n".join(buf).strip(),"timestamp":ts})
            role, buf, ts = "assistant", [], parse_ts(ln)
        elif role: buf.append(ln)
    if role and buf:
        messages.append({"role":role,"content":"\n".join(buf).strip(),"timestamp":ts})
    return {"id":sid,"title":title,"messages":messages,"is_starred":is_starred}

def save_session(sid: str, title: str, messages: list, is_starred: bool = False):
    prefix = "⭐ " if is_starred else ""
    lines  = [f"# {prefix}{title}", ""]
    for m in messages:
        ts = m.get("timestamp") or datetime.now().isoformat()
        lines.append(f"## 👤 User | {ts}" if m["role"]=="user" else f"## 🤖 Assistant | {ts}")
        lines.append(m["content"])
        lines.append("")
    session_path(sid).write_text("\n".join(lines), encoding="utf-8")

def list_sessions() -> list:
    out = []
    for f in MEMORY_DIR.glob("*.md"):
        fl = f.read_text(encoding="utf-8").split("\n")[0].replace("# ","").strip()
        mt = datetime.fromtimestamp(os.path.getmtime(f))
        out.append({"id":f.stem,"title":fl.replace("⭐","").strip(),
                    "is_starred":fl.startswith("⭐"),
                    "updated_at":mt.strftime("%d/%m/%Y %H:%M"),
                    "mtime_raw":os.path.getmtime(f)})
    out.sort(key=lambda x: (not x["is_starred"],-x["mtime_raw"]))
    return out


# ════════════════════════════════════════════════════════════════
# API MODELS
# ════════════════════════════════════════════════════════════════

class ChatRequest(BaseModel):
    session_id: str; message: str; timestamp: str = ""
class NewSessionRequest(BaseModel):
    title: str = "New Chat"
class RenameSessionRequest(BaseModel):
    title: str
class StarSessionRequest(BaseModel):
    is_starred: bool
class TruncateRequest(BaseModel):
    keep_count: int


# ════════════════════════════════════════════════════════════════
# ROUTES
# ════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request":request,"dashboards":DASHBOARDS})

@app.get("/api/sessions")
async def get_sessions(): return list_sessions()

@app.post("/api/sessions")
async def create_session(req: NewSessionRequest):
    sid = str(uuid.uuid4())[:8]
    save_session(sid, req.title, [])
    return {"id":sid,"title":req.title,"is_starred":False}

@app.get("/api/sessions/{sid}")
async def get_session(sid: str): return load_session(sid)

@app.put("/api/sessions/{sid}/rename")
async def rename_session(sid: str, req: RenameSessionRequest):
    s = load_session(sid)
    save_session(sid, req.title, s["messages"], s["is_starred"])
    return {"ok":True,"title":req.title}

@app.put("/api/sessions/{sid}/star")
async def toggle_star(sid: str, req: StarSessionRequest):
    s = load_session(sid)
    save_session(sid, s["title"], s["messages"], req.is_starred)
    return {"ok":True,"is_starred":req.is_starred}

@app.put("/api/sessions/{sid}/truncate")
async def truncate_session(sid: str, req: TruncateRequest):
    s = load_session(sid)
    save_session(sid, s["title"], s["messages"][:req.keep_count], s["is_starred"])
    return {"ok":True}

@app.delete("/api/sessions/{sid}")
async def delete_session(sid: str):
    p = session_path(sid)
    if p.exists(): p.unlink()
    return {"ok":True}


# ════════════════════════════════════════════════════════════════
# CHAT ENDPOINT
# ════════════════════════════════════════════════════════════════

@app.post("/api/chat")
async def chat(req: ChatRequest):
    session  = load_session(req.session_id)
    context  = get_context(req.message)
    q_type, _ = classify(req.message)
    system_prompt, kb_context = build_prompt(context, q_type)

    msgs = [{"role":"system","content":system_prompt}]
    hist    = session["messages"]
    last_ai = next((m["content"] for m in reversed(hist) if m["role"]=="assistant"), "")

    recent = hist[-2:] if len(hist) >= 2 else hist
    for m in recent:
        if m.get("content","").strip():
            msgs.append({"role":m["role"],"content":m["content"]})

    # ตรวจว่าถาม multi-panel → เพิ่ม num_predict
    q_low = req.message.lower()
    is_multi = any(k in q_low for k in ["ทั้ง 3","ทุก panel","ทั้งหมด","3 panel","ทั้งสาม","แต่ละ panel"])
    dynamic_options = {**MAIN_OPTIONS}
    if is_multi:
        dynamic_options["num_predict"] = 700  # เพิ่มจาก 400 → 700 สำหรับ 3 panels
        print(f"[Chat] multi-panel → num_predict=700")

    # แนบ KB context ใน user message → model focus กับ KB มากขึ้น
    user_content = (
        f"ข้อมูลอ้างอิงจาก Knowledge Base:\n{kb_context}\n\n"
        f"---\n"
        f"คำถาม: {req.message}\n"
        f"ตอบโดยใช้เฉพาะข้อมูลด้านบนเท่านั้น"
    )
    msgs.append({"role":"user","content":user_content})

    is_first = len(session["messages"]) == 0
    user_ts  = req.timestamp or datetime.now().isoformat()

    async def stream():
        full = ""
        try:
            async with httpx.AsyncClient(timeout=60.0, trust_env=False) as client:
                async with client.stream("POST", OLLAMA_URL, json={
                    "model":OLLAMA_MODEL,"messages":msgs,
                    "stream":True,"options":dynamic_options,
                }) as resp:
                    print(f"[Ollama] {OLLAMA_MODEL} | {resp.status_code}")
                    async for line in resp.aiter_lines():
                        if not line: continue
                        try:
                            d = json.loads(line)
                            if "message" in d and "content" in d["message"]:
                                chunk = clean_response(d["message"]["content"])
                                full += chunk
                                yield f"data: {json.dumps({'chunk':chunk})}\n\n"

                            if d.get("done"):
                                ai_ts    = datetime.now().isoformat()
                                override = False

                                if is_non_thai(full):
                                    print("[LANG GUARD] non-Thai → retry")
                                    try:
                                        async with httpx.AsyncClient(timeout=45.0, trust_env=False) as rc:
                                            rr = await rc.post(OLLAMA_URL, json={
                                                "model":OLLAMA_MODEL,
                                                "messages":[
                                                    {"role":"system","content":system_prompt},
                                                    {"role":"user","content":user_content},
                                                ],
                                                "stream":False,"options":RETRY_OPTIONS,
                                            })
                                            full = clean_response(rr.json().get("message",{}).get("content","") or full)
                                    except Exception as e:
                                        print(f"[LANG GUARD] error: {e}")
                                    if is_non_thai(full):
                                        full = ""  # ai_rules.md จะจัดการกรณีไม่มีข้อมูล
                                    override = True

                                elif is_repetitive(full, last_ai):
                                    print("[REPEAT GUARD] → retry")
                                    try:
                                        async with httpx.AsyncClient(timeout=45.0, trust_env=False) as rc:
                                            rr = await rc.post(OLLAMA_URL, json={
                                                "model":OLLAMA_MODEL,
                                                "messages":[
                                                    {"role":"system","content":system_prompt},
                                                    {"role":"user","content":user_content},
                                                ],
                                                "stream":False,"options":RETRY_OPTIONS,
                                            })
                                            full = clean_response(rr.json().get("message",{}).get("content","") or full)
                                    except Exception as e:
                                        print(f"[REPEAT GUARD] error: {e}")
                                    override = True

                                if override:
                                    yield f"data: {json.dumps({'override':True,'content':full})}\n\n"

                                new_msgs = session["messages"] + [
                                    {"role":"user",     "content":req.message,"timestamp":user_ts},
                                    {"role":"assistant","content":full,       "timestamp":ai_ts},
                                ]
                                title = session["title"]
                                if is_first or title == "New Chat":
                                    title = req.message[:50]+("..." if len(req.message)>50 else "")
                                save_session(req.session_id, title, new_msgs, session["is_starred"])
                                yield f"data: {json.dumps({'done':True,'title':title,'ai_timestamp':ai_ts})}\n\n"

                        except json.JSONDecodeError: pass

        except Exception as e:
            print(f"[ERROR] {type(e).__name__}: {e}")
            yield f"data: {json.dumps({'chunk':f'❌ เชื่อมต่อ Ollama ไม่ได้: {e}'})}\n\n"
            yield f"data: {json.dumps({'done':True,'title':'Error','ai_timestamp':datetime.now().isoformat()})}\n\n"

    return StreamingResponse(stream(), media_type="text/event-stream")


@app.post("/api/reload-knowledge")
async def reload_knowledge():
    return {"ok":True,"files":len(list(KNOWLEDGE_DIR.glob("*.md")))}