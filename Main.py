import streamlit as st
import pandas as pd
import datetime
import sqlite3
import time
from database import get_db_connection, load_css

# ==============================================================================
# 1. ऐप सेटिंग्स और रिफ्रेश सुरक्षा
# ==============================================================================
st.set_page_config(page_title="स्मार्ट स्कूल ERP", page_icon="🏫", layout="wide")
load_css()

# URL से सेशन रिकवरी (रिफ्रेश होने पर)
if not st.session_state.get('logged_in'):
    params = st.query_params
    if "sid" in params:
        sid = params["sid"]
        conn = get_db_connection()
        user = conn.execute("SELECT school_name, role FROM schools WHERE school_id=?", (sid,)).fetchone()
        conn.close()
        if user:
            st.session_state['logged_in'] = True
            st.session_state['school_id'] = sid
            st.session_state['school_name'] = user[0]
            st.session_state['role'] = user[1]

# डिफ़ॉल्ट सेशन स्टेट
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'role' not in st.session_state: st.session_state['role'] = 'user'

# ==============================================================================
# 2. डायनामिक साइडबार नेविगेशन
# ==============================================================================
def show_sidebar_navigation():
    # पेजों की परिभाषा
    p_dash = st.Page("pages/1_📊_डैशबोर्ड.py", title="डैशबोर्ड", icon="📊", default=True)
    p_time = st.Page("pages/2_📅_टाइम_टेबल.py", title="टाइम टेबल", icon="📅")
    p_live = st.Page("pages/3_🏠_लाइव_ट्रेकर.py", title="लाइव ट्रेकर", icon="🏠")
    p_arr  = st.Page("pages/4_📝_अध्यापक_व्यवस्था.py", title="व्यवस्था रजिस्टर", icon="📝")
    p_rep  = st.Page("pages/5_📈_मास्टर_रिपोर्ट.py", title="मास्टर रिपोर्ट्स", icon="📈")
    p_set  = st.Page("pages/6_⚙️_मास्टर_सैटिंग्स.py", title="सेटिंग्स", icon="⚙️")
    p_back = st.Page("pages/7_💾_डेटा_बैकअप.py", title="सर्वर बैकअप", icon="💾")
    p_user = st.Page("pages/8_👥_यूजर_प्रबंधन.py", title="यूजर मैनेजमेंट", icon="👥")

    # रोल आधारित एक्सेस
    if st.session_state.get('role') == 'super_admin':
        pages_dict = {
            "मुख्य कार्य": [p_dash, p_live, p_arr],
            "रिपोर्ट्स एवं सेटिंग्स": [p_time, p_rep, p_set],
            "सिस्टम कंट्रोल": [p_back, p_user] 
        }
    else:
        pages_dict = {
            "विद्यालय प्रबंधन": [p_dash, p_live, p_arr],
            "रिपोर्ट्स एवं सेटिंग्स": [p_time, p_rep, p_set]
        }
    
    pg = st.navigation(pages_dict)
    
    with st.sidebar:
        st.markdown(f"**👤 यूजर:** {st.session_state['school_name']}")
        if st.button("🚪 लॉगआउट करें", use_container_width=True):
            # Clear query parameters properly
            for key in list(st.query_params.keys()):
                del st.query_params[key]
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()
            
    pg.run()

# ==============================================================================
# 3. लॉगिन और रजिस्ट्रेशन UI
# ==============================================================================
def login_ui():
    st.markdown("<style>[data-testid='stSidebar'] {display: none;}</style>", unsafe_allow_html=True)
    st.markdown("<div class='header-box'><h1>🔐 स्मार्ट स्कूल ERP (SaaS)</h1><p>अपनी आसान ID के साथ लॉगिन करें</p></div>", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["🔑 लॉगिन", "🆕 नया विद्यालय रजिस्ट्रेशन"])
    
    with t1:
        with st.form("login_form"):
            l_id = st.text_input("यूजर ID (जैसे: saroth_school):")
            l_pass = st.text_input("पासवर्ड:", type="password")
            if st.form_submit_button("प्रवेश करें", type="primary"):
                conn = get_db_connection()
                user = conn.execute("SELECT school_name, role FROM schools WHERE school_id=? AND password=?", (l_id, l_pass)).fetchone()
                conn.close()
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['school_id'] = l_id
                    st.session_state['school_name'] = user[0]
                    st.session_state['role'] = user[1]
                    st.query_params["sid"] = l_id 
                    st.rerun()
                else:
                    st.error("❌ गलत ID या पासवर्ड।")

    with t2:
        st.write("### 🆕 नया विद्यालय खाता बनाएँ")
        with st.form("reg_form"):
            r_id = st.text_input("अपनी मनपसंद यूजर ID चुनें (Login ID):", placeholder="जैसे: rjschool01 (स्पेस न दें)")
            r_name = st.text_input("विद्यालय का पूरा नाम:")
            r_udise = st.text_input("विद्यालय का U-DISE कोड (केवल रिकॉर्ड के लिए):")
            r_dist = st.text_input("ज़िला (District):")
            r_pass = st.text_input("एक सुरक्षित पासवर्ड बनाएँ:", type="password")
            
            if st.form_submit_button("रजिस्टर करें", type="primary"):
                if r_id and r_name and r_pass:
                    # यूजर आईडी में स्पेस चेक करना
                    if " " in r_id:
                        st.error("❌ यूजर ID में खाली जगह (Space) न दें।")
                    else:
                        conn = get_db_connection()
                        try:
                            # 'schools' टेबल में एंट्री (role: admin)
                            conn.execute("INSERT INTO schools (school_id, school_name, password, district, created_at, role) VALUES (?, ?, ?, ?, ?, ?)",
                                         (r_id, r_name, r_pass, r_dist, str(datetime.date.today()), 'admin'))
                            
                            # डिफ़ॉल्ट सेटिंग्स
                            conn.execute("INSERT OR IGNORE INTO app_settings (school_id, key, value) VALUES (?, 'school_name', ?)", (r_id, r_name))
                            conn.execute("INSERT OR IGNORE INTO app_settings (school_id, key, value) VALUES (?, 'session', '2025-26')", (r_id,))
                            conn.commit()
                            st.success("✅ रजिस्ट्रेशन सफल! अब लॉगिन टैब पर जाकर प्रवेश करें।")
                        except sqlite3.IntegrityError:
                            st.error("❌ यह यूजर ID पहले से किसी और ने ले ली है। कृपया कोई और नाम चुनें।")
                        finally:
                            conn.close()
                else:
                    st.warning("⚠️ कृपया सभी फील्ड्स भरें।")

# ==============================================================================
# 4. मुख्य निष्पादन
# ==============================================================================
try:
    if st.session_state['logged_in']:
        show_sidebar_navigation()
    else:
        login_ui()
except Exception as e:
    st.error(f"❌ एप्लिकेशन में त्रुटि: {str(e)}")
    st.info("कृपया कुछ समय बाद पुनः प्रयास करें या अपने Admin से संपर्क करें।")

st.markdown("<br><hr><center><small>Developed by: <b>Rohitasw Kaswan</b> | SaaS v12.6</small></center>", unsafe_allow_html=True)