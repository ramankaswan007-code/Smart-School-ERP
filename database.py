###############################################################################
# SMART SCHOOL ERP v12.0 - FULL SaaS DATABASE ENGINE
# File: database.py
###############################################################################

import sqlite3
import pandas as pd
import datetime
import streamlit as st

# ==============================================================================
# 1. ग्लोबल वेरिएबल्स और कॉन्फ़िगरेशन
# ==============================================================================
DB_FILE = 'school_erp_SaaS_v12.db' 

day_map = {
    "Monday": "सोमवार", "Tuesday": "मंगलवार", "Wednesday": "बुधवार",
    "Thursday": "गुरुवार", "Friday": "शुक्रवार", "Saturday": "शनिवार", "Sunday": "रविवार"
}

period_order = [
    "प्रार्थना सभा", "कालांश 1", "कालांश 2", "कालांश 3", "कालांश 4", 
    "मध्यांतर", "कालांश 5", "कालांश 6", "कालांश 7", "कालांश 8"
]

# ==============================================================================
# 2. मल्टी-टेनेंट सुरक्षा (Security Check)
# ==============================================================================
# database.py के अंदर का संशोधित फंक्शन
def get_current_school():
    """हर पेज पर सेशन को याद रखने और रिफ्रेश होने पर रिकवर करने वाला फंक्शन"""
    
    # 1. पहले चेक करें कि क्या सेशन पहले से एक्टिव है
    if 'logged_in' in st.session_state and st.session_state['logged_in']:
        return st.session_state['school_id']
    
    # 2. अगर रिफ्रेश हुआ है (सेशन खाली है), तो URL (sid) से रिकवर करें
    params = st.query_params
    if "sid" in params:
        sid = params["sid"]
        conn = get_db_connection()
        user = conn.execute("SELECT school_name, role FROM schools WHERE school_id=?", (sid,)).fetchone()
        conn.close()
        
        if user:
            # याददाश्त वापस भरें
            st.session_state['logged_in'] = True
            st.session_state['school_id'] = sid
            st.session_state['school_name'] = user[0]
            st.session_state['role'] = user[1]
            return sid

    # 3. अगर न सेशन है और न URL में आईडी, तब ही एरर दें
    st.error("⚠️ आपका सत्र समाप्त हो गया है! कृपया Main.py पर जाकर लॉगिन करें।")
    st.stop()

# ==============================================================================
# 3. डेटाबेस इंजन और टेबल सेटअप
# ==============================================================================
def get_db_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # 1. स्कूलों की मास्टर टेबल (Role के साथ)
        c.execute('''CREATE TABLE IF NOT EXISTS schools 
                     (school_id TEXT PRIMARY KEY, school_name TEXT, password TEXT, 
                      district TEXT, created_at TEXT, role TEXT)''')
    
        # 2. अन्य सभी डेटा टेबल्स
        c.execute('CREATE TABLE IF NOT EXISTS app_settings (school_id TEXT, key TEXT, value TEXT, PRIMARY KEY(school_id, key))')
        c.execute('CREATE TABLE IF NOT EXISTS teachers (school_id TEXT, Name TEXT, Mobile TEXT, Post TEXT, Subject TEXT, PRIMARY KEY(school_id, Name))')
        c.execute('CREATE TABLE IF NOT EXISTS subjects (school_id TEXT, name TEXT, PRIMARY KEY(school_id, name))')
        c.execute('CREATE TABLE IF NOT EXISTS active_classes (school_id TEXT, class_name TEXT, PRIMARY KEY(school_id, class_name))')
        c.execute('CREATE TABLE IF NOT EXISTS time_slots (school_id TEXT, slot_id INTEGER, period_name TEXT, start_time TEXT, end_time TEXT, PRIMARY KEY(school_id, slot_id))')
        c.execute('CREATE TABLE IF NOT EXISTS timetable_data (school_id TEXT, unified_class TEXT, day TEXT, period TEXT, teacher TEXT, subject TEXT, PRIMARY KEY(school_id, unified_class, day, period))')
        c.execute('CREATE TABLE IF NOT EXISTS subject_mapping (school_id TEXT, class_name TEXT, subject TEXT, teacher TEXT, periods INTEGER, PRIMARY KEY(school_id, class_name, subject))')
        c.execute('CREATE TABLE IF NOT EXISTS absentees (school_id TEXT, date TEXT, teacher_name TEXT, PRIMARY KEY(school_id, date, teacher_name))')
        c.execute('CREATE TABLE IF NOT EXISTS arrangements (school_id TEXT, date TEXT, period TEXT, unified_class TEXT, original_teacher TEXT, assigned_teacher TEXT, PRIMARY KEY(school_id, date, period, unified_class))')
        
        # 🌟 मास्टर लॉगिन का निर्माण (Super Admin और Default School)
        today = str(datetime.date.today())
        master_accounts = [
            ('SAROTH_01', 'रा.उ.मा.वि. सारोठ (ब्यावर)', '1234', 'Beawar', today, 'admin'),
            ('super_admin', 'SaaS Master Admin', 'Ram@245444', 'Headquarters', today, 'super_admin')
        ]
        
        for account in master_accounts:
            c.execute("INSERT OR REPLACE INTO schools VALUES (?, ?, ?, ?, ?, ?)", account)
            
        # डिफ़ॉल्ट स्कूल की बेसिक सेटिंग्स
        c.execute("INSERT OR IGNORE INTO app_settings VALUES ('SAROTH_01', 'school_name', 'राजकीय उच्च माध्यमिक विद्यालय, सारोठ (ब्यावर)')")
        c.execute("INSERT OR IGNORE INTO app_settings VALUES ('SAROTH_01', 'session', '2025-26')")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"⚠️ Database initialization warning: {str(e)}")
        try:
            conn.close()
        except:
            pass

# डेटाबेस स्वतः शुरू करें
try:
    init_db()
except Exception as e:
    print(f"Database init failed: {e}")

# ==============================================================================
# 4. स्मार्ट हेल्पर्स (Utilities)
# ==============================================================================

def get_school_info(school_id):
    conn = get_db_connection()
    try:
        n = pd.read_sql_query("SELECT value FROM app_settings WHERE key='school_name' AND school_id=?", conn, params=(school_id,)).iloc[0,0]
        s = pd.read_sql_query("SELECT value FROM app_settings WHERE key='session' AND school_id=?", conn, params=(school_id,)).iloc[0,0]
        return n, s
    except Exception:
        return "Smart School ERP", "2025-26"
    finally:
        conn.close()

def get_teachers(school_id):
    conn = get_db_connection()
    try:
        return pd.read_sql_query("SELECT Name FROM teachers WHERE school_id=? ORDER BY Name", conn, params=(school_id,))['Name'].tolist()
    finally:
        conn.close()


def get_subjects(school_id):
    conn = get_db_connection()
    try:
        return pd.read_sql_query("SELECT name FROM subjects WHERE school_id=? ORDER BY name", conn, params=(school_id,))['name'].tolist()
    finally:
        conn.close()


def get_time_slots(school_id):
    conn = get_db_connection()
    try:
        return pd.read_sql_query("SELECT slot_id, period_name, start_time, end_time FROM time_slots WHERE school_id=? ORDER BY slot_id", conn, params=(school_id,))
    finally:
        conn.close()


def get_timetable_data(school_id, **filters):
    conn = get_db_connection()
    try:
        base = "SELECT * FROM timetable_data WHERE school_id=?"
        params = [school_id]
        for key, value in filters.items():
            base += f" AND {key}=?"
            params.append(value)
        return pd.read_sql_query(base, conn, params=tuple(params))
    finally:
        conn.close()


def get_active_classes(school_id):
    conn = get_db_connection()
    try:
        return [r[0] for r in conn.execute("SELECT class_name FROM active_classes WHERE school_id=?", (school_id,)).fetchall()]
    finally:
        conn.close()


def safe_sort(lst):
    """कक्षाओं को सही क्रम (1, 2, 10, 11) में लगाने के लिए"""
    try: return sorted([x for x in lst if x], key=lambda x: (int(x.split('-')[0]) if x.split('-')[0].isdigit() else 99, x))
    except: return sorted([str(x) for x in lst if x])

def get_unified_class_list(school_id):
    conn = get_db_connection()
    classes = [r[0] for r in conn.execute("SELECT class_name FROM active_classes WHERE school_id=?", (school_id,)).fetchall()]
    conn.close()
    return safe_sort(classes)

def get_short_code(name, mapping):
    """अध्यापकों के नाम का शॉर्ट कोड (जैसे रोहिताश -> RO) बनाने के लिए"""
    if not name or pd.isna(name): return "-"
    if name in mapping: return mapping[name]
    parts = str(name).strip().split()
    short = "".join([p[0].upper() for p in parts[:2]]) if len(parts) > 1 else str(name)[:2].upper()
    orig, c = short, 1
    while short in mapping.values(): 
        short = f"{orig}{c}"; c += 1
    mapping[name] = short
    return short

def format_day_ranges(day_list):
    """दिनों की लिस्ट को (Som-Shani) फॉर्मेट में बदलने के लिए"""
    if not day_list: return ""
    rev_map = {v: k for k, v in enumerate(["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार"])}
    valid_days = sorted([rev_map[d] for d in day_list if d in rev_map])
    if len(valid_days) == 6: return "All Days"
    if not valid_days: return ""
    ranges = []
    start = end = valid_days[0]
    for i in range(1, len(valid_days)):
        if valid_days[i] == end + 1: end = valid_days[i]
        else:
            ranges.append(f"{start}-{end}" if start != end else f"{start}")
            start = end = valid_days[i]
    ranges.append(f"{start}-{end}" if start != end else f"{start}")
    short_names = ["Som", "Mangal", "Budh", "Guru", "Shukra", "Shani"]
    final_str = []
    for r in ranges:
        if '-' in str(r):
            s, e = map(int, str(r).split('-'))
            final_str.append(f"{short_names[s]}-{short_names[e]}")
        else: final_str.append(short_names[int(r)])
    return ", ".join(final_str)

# ==============================================================================
# 5. UI और प्रिंट इंजन
# ==============================================================================

def load_css():
    st.markdown("""
        <style>
        .stApp { background-color: #fdfdfd !important; color: #1a1a1a !important; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        .stButton>button { width: 100%; border-radius: 6px; font-weight: 600; }
        button[kind="primary"] { background: linear-gradient(135deg, #2e7d32 0%, #1b5e20 100%) !important; color: white !important; border: none !important; }
        .header-box { background: linear-gradient(135deg, #00695c, #004d40); padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 25px; color: white !important; }
        .header-box h1 { color: white !important; margin: 0; font-size: 2.2rem; }
        [data-testid="stSidebar"] { background-color: #f1f8e9; }
        .print-box table { width: 100%; border-collapse: collapse; }
        .print-box th, .print-box td { border: 1px solid #333; padding: 6px; }
        @media print { [data-testid="stSidebar"], header, footer, .no-print { display: none !important; } .print-box { display: block !important; width: 100%; } }
        </style>
    """, unsafe_allow_html=True)

def show_print_preview(html_content, title, orientation="portrait", school_id=None):
    SCHOOL_NAME, SESSION_YEAR = get_school_info(school_id) if school_id else ("School ERP", "2025")
    full_html = f"""
    <div class="print-box">
        <center>
            <h2 style="margin:0; color:black;">{SCHOOL_NAME}</h2>
            <h3 style="margin:5px; color:#333; text-decoration:underline;">{title}</h3>
            <p style="margin:0; font-weight:bold;">सत्र: {SESSION_YEAR}</p>
            <hr style="border-top: 2px solid #000; margin-bottom:15px;">
        </center>
        {html_content}
        <center class="no-print" style="margin-top:20px;">
            <button onclick="window.print()" style="padding:10px 20px; background:#b71c1c; color:white; border:none; border-radius:5px; cursor:pointer;">🖨️ प्रिंट करें (Print)</button>
        </center>
    </div>
    """
    st.components.v1.html(full_html, height=1000, scrolling=True)