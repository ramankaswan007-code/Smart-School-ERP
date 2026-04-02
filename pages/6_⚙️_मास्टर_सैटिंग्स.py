###############################################################################
# SMART SCHOOL ERP v18.0 - MASTER SETTINGS WITH BULK MAPPING
# File: pages/6_⚙️_मास्टर_सैटिंग्स.py
###############################################################################

import streamlit as st
import pandas as pd
import time
from database import get_db_connection, get_school_info, get_current_school, get_teachers, get_subjects, get_active_classes, get_time_slots

# 🔒 जादुई सुरक्षा लॉक
DEFAULT_SCHOOL = get_current_school()

st.set_page_config(page_title="मास्टर सैटिंग्स", page_icon="⚙️", layout="wide")

st.markdown("""
    <style>
    .header-box { background: linear-gradient(135deg, #00695c, #004d40); padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 25px; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.15); border-bottom: 4px solid #00251a; }
    .map-box { background: #f1f8e9; padding: 20px; border-radius: 10px; border: 1px solid #c5e1a5; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='header-box'><h1 style='margin: 0; color: white;'>⚙️ मास्टर डेटा सेटिंग्स</h1><p style='color: #b2dfdb; margin-top: 5px;'>विद्यालय प्रोफाइल, अध्यापक, कक्षाएं और स्मार्ट विषय-अध्यापक मैपिंग</p></div>", unsafe_allow_html=True)

conn = get_db_connection()

# 🌟 मैपिंग टेबल को सुरक्षित रूप से बनाना
conn.execute('CREATE TABLE IF NOT EXISTS subject_mapping (school_id TEXT, class_name TEXT, subject TEXT, teacher TEXT, periods INTEGER, PRIMARY KEY(school_id, class_name, subject))')
conn.commit()

# ==============================================================================
# 1. सेटिंग्स टैब्स (6 टैब्स)
# ==============================================================================
tab_sch, tab_t, tab_act_cls, tab_sub, tab_time, tab_map = st.tabs([
    "🏫 प्रोफाइल (Profile)", 
    "👨‍🏫 अध्यापक (Teachers)", 
    "✅ सक्रिय कक्षाएं (Classes)", 
    "📚 विषय (Subjects)", 
    "⏰ समय चक्र (Time Slots)",
    "🔗 विषय-अध्यापक मैपिंग (AI Rules)"
])

# ------------------------------------------------------------------------------
# Tab 1: विद्यालय प्रोफाइल
# ------------------------------------------------------------------------------
with tab_sch:
    st.subheader("🏫 विद्यालय एवं सत्र विवरण")
    curr_name, curr_sess = get_school_info(DEFAULT_SCHOOL)
    
    with st.form("sch_profile_form"):
        c1, c2 = st.columns(2)
        new_name = c1.text_input("विद्यालय का नाम (School Name):", value=curr_name)
        new_sess = c2.text_input("शैक्षणिक सत्र (Session):", value=curr_sess)
        
        if st.form_submit_button("💾 प्रोफाइल अपडेट करें", type="primary"):
            conn.execute("INSERT OR REPLACE INTO app_settings (school_id, key, value) VALUES (?, 'school_name', ?)", (DEFAULT_SCHOOL, new_name))
            conn.execute("INSERT OR REPLACE INTO app_settings (school_id, key, value) VALUES (?, 'session', ?)", (DEFAULT_SCHOOL, new_sess))
            conn.commit()
            st.success("✅ विद्यालय की जानकारी अपडेट हो गई! (रिफ्रेश करें)")
            time.sleep(1); st.rerun()

# ------------------------------------------------------------------------------
# Tab 2: अध्यापक प्रबंधन
# ------------------------------------------------------------------------------
with tab_t:
    st.subheader("👨‍🏫 अध्यापक डेटाबेस")
    
    with st.expander("📥 Excel/CSV से अध्यापक लिस्ट अपलोड करें"):
        st.info("CSV फाइल में ये 4 कॉलम होने चाहिए: `Name`, `Mobile`, `Post`, `Subject`")
        up_file = st.file_uploader("CSV फाइल चुनें:", type=["csv"])
        
        if up_file:
            try:
                idf = pd.read_csv(up_file)
                idf.columns = [c.strip() for c in idf.columns]
                req_cols = ['Name', 'Mobile', 'Post', 'Subject']
                if all(col in idf.columns for col in req_cols):
                    st.dataframe(idf.head(), height=150)
                    if st.button("🚀 डेटाबेस में लोड करें (केवल इस स्कूल का पुराना डेटा हटेगा)", type="primary"):
                        idf['school_id'] = DEFAULT_SCHOOL 
                        conn.execute("DELETE FROM teachers WHERE school_id=?", (DEFAULT_SCHOOL,)) 
                        idf[['school_id'] + req_cols].to_sql('teachers', conn, if_exists='append', index=False)
                        st.success(f"✅ {len(idf)} अध्यापकों का डेटा लोड हो गया!")
                        time.sleep(1); st.rerun()
                else:
                    st.error(f"❌ फाइल में सही कॉलम नहीं मिले। आवश्यक: {req_cols}")
            except Exception as e: st.error(f"Error: {e}")
    
    st.markdown("---")
    st.write("🔻 **मौजूदा अध्यापक सूची (यहाँ सीधे एडिट या डिलीट करें):**")
    t_df = pd.read_sql_query("SELECT Name, Mobile, Post, Subject FROM teachers WHERE school_id=?", conn, params=(DEFAULT_SCHOOL,))
    
    edited_t = st.data_editor(
        t_df, 
        num_rows="dynamic", 
        use_container_width=True,
        key="teacher_editor_main",
        column_config={
            "Name": st.column_config.TextColumn("अध्यापक का नाम", required=True),
            "Mobile": st.column_config.TextColumn("मोबाइल"),
            "Post": st.column_config.TextColumn("पद (Post)"),
            "Subject": st.column_config.TextColumn("मूल विषय")
        }
    )
    
    if st.button("💾 अध्यापक सूची सुरक्षित करें", key="save_teachers", type="primary"):
        try:
            clean_t = edited_t.dropna(subset=['Name']).copy()
            clean_t['school_id'] = DEFAULT_SCHOOL
            if not clean_t.empty:
                conn.execute("DELETE FROM teachers WHERE school_id=?", (DEFAULT_SCHOOL,))
                clean_t[['school_id', 'Name', 'Mobile', 'Post', 'Subject']].to_sql('teachers', conn, if_exists='append', index=False)
                conn.commit()
                st.success("✅ अध्यापक सूची अपडेट हो गई!")
                time.sleep(1); st.rerun()
        except Exception as e: st.error(f"Error: {e}")

# ------------------------------------------------------------------------------
# Tab 3: सक्रिय कक्षा प्रबंधन
# ------------------------------------------------------------------------------
with tab_act_cls:
    st.subheader("✅ सक्रिय कक्षा प्रबंधन")
    st.info("💡 **टिप:** जो कक्षाएं स्कूल में नहीं हैं उन्हें सेलेक्ट करके Delete (Trash Icon) दबाएं। नई कक्षा जोड़ने के लिए नीचे '+' दबाएं।")
    
    with st.expander("⚡ नई कक्षाएं जनरेट करें (Class Generator)", expanded=False):
        if st.button("🚀 1-Click: 1 से 12 तक की डिफ़ॉल्ट कक्षाएं सेट करें", type="primary"):
            classes = [(DEFAULT_SCHOOL, str(i)) for i in range(1, 11)]
            classes += [(DEFAULT_SCHOOL, "11-Arts"), (DEFAULT_SCHOOL, "11-Sci"), (DEFAULT_SCHOOL, "11-Comm")]
            classes += [(DEFAULT_SCHOOL, "12-Arts"), (DEFAULT_SCHOOL, "12-Sci"), (DEFAULT_SCHOOL, "12-Comm")]
            conn.executemany("INSERT OR IGNORE INTO active_classes (school_id, class_name) VALUES (?, ?)", classes)
            conn.commit()
            st.success("✅ 1 से 12 तक कक्षाएं जनरेट हो गईं!"); time.sleep(1); st.rerun()
            
        st.markdown("---")
        st.write("👉 **कस्टम कक्षाएं (सेक्शन के साथ) बनाएं:**")
        gc1, gc2 = st.columns(2)
        sel_nums = gc1.multiselect("कक्षा (1-12):", [str(i) for i in range(1, 13)])
        sel_secs = gc2.multiselect("सेक्शन (A-F):", ["A", "B", "C", "D", "E"])
        
        if st.button("⚡ कस्टम कक्षाएं जोड़ें", type="secondary"):
            new_cls = []
            for n in sel_nums:
                for s in sel_secs:
                    if n in ['11', '12']:
                        new_cls.append((DEFAULT_SCHOOL, f"{n}-{s}-Arts"))
                        new_cls.append((DEFAULT_SCHOOL, f"{n}-{s}-Science"))
                    else:
                        new_cls.append((DEFAULT_SCHOOL, f"{n}-{s}"))
            
            if new_cls:
                conn.executemany("INSERT OR IGNORE INTO active_classes (school_id, class_name) VALUES (?, ?)", new_cls)
                conn.commit()
                st.success(f"✅ {len(new_cls)} कक्षाएं जोड़ी गईं!"); time.sleep(1); st.rerun()

    st.write("🔻 **वर्तमान सक्रिय कक्षाएं:**")
    curr_active = pd.DataFrame({'class_name': get_active_classes(DEFAULT_SCHOOL)})
    
    edited_cls = st.data_editor(
        curr_active, 
        num_rows="dynamic", 
        use_container_width=True, 
        key="active_cls_editor",
        column_config={"class_name": st.column_config.TextColumn("कक्षा का नाम", required=True)}
    )
    
    if st.button("💾 कक्षा सूची अपडेट करें", type="primary"):
        try:
            conn.execute("DELETE FROM active_classes WHERE school_id=?", (DEFAULT_SCHOOL,))
            clean_c = edited_cls.dropna(subset=['class_name']).copy()
            clean_c['school_id'] = DEFAULT_SCHOOL
            clean_c[['school_id', 'class_name']].to_sql('active_classes', conn, if_exists='append', index=False)
            conn.commit()
            st.success("✅ कक्षा सूची अपडेट हो गई!")
            time.sleep(1); st.rerun()
        except Exception as e: st.error(f"Error: {e}")

# ------------------------------------------------------------------------------
# Tab 4: विषय सूची
# ------------------------------------------------------------------------------
with tab_sub:
    st.subheader("📚 विषय डेटाबेस")
    
    if st.button("⚡ डिफ़ॉल्ट विषय (Primary to Senior) लोड करें", type="secondary"):
        subs = ["हिन्दी", "अंग्रेजी", "गणित", "विज्ञान", "सामाजिक विज्ञान", "संस्कृत", "तृतीय भाषा (उर्दू)", "शारीरिक शिक्षा", "कला शिक्षा", "सूचना प्रौद्योगिकी", "पर्यावरण अध्ययन", "राजनीति विज्ञान", "इतिहास", "भूगोल", "भौतिक विज्ञान", "रसायन विज्ञान", "जीव विज्ञान", "लेखाशास्त्र"]
        data = [(DEFAULT_SCHOOL, s) for s in subs]
        conn.executemany("INSERT OR IGNORE INTO subjects (school_id, name) VALUES (?, ?)", data)
        conn.commit()
        st.success("✅ डिफ़ॉल्ट विषय लोड कर दिए गए हैं!"); time.sleep(1); st.rerun()

    s_df = pd.DataFrame({'name': get_subjects(DEFAULT_SCHOOL)})
    if s_df.empty:
        s_df = pd.DataFrame(columns=["name"])
        st.warning("सूची खाली है। कृपया विषय जोड़ें या ऊपर से डिफ़ॉल्ट लोड करें।")

    edited_s = st.data_editor(
        s_df, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={"name": st.column_config.TextColumn("विषय का नाम", required=True)}
    )
    
    if st.button("💾 विषय अपडेट करें", type="primary"):
        clean_s = edited_s.dropna(subset=['name']).copy()
        clean_s['school_id'] = DEFAULT_SCHOOL
        conn.execute("DELETE FROM subjects WHERE school_id=?", (DEFAULT_SCHOOL,))
        clean_s[['school_id', 'name']].to_sql('subjects', conn, if_exists='append', index=False)
        conn.commit()
        st.success("✅ विषय सेव हो गए!"); time.sleep(1); st.rerun()

# ------------------------------------------------------------------------------
# Tab 5: समय चक्र
# ------------------------------------------------------------------------------
with tab_time:
    st.subheader("⏰ समय चक्र (Time Slots)")
    
    st.write("👉 **क्विक सेटअप (राजस्थान शिविरा पंचांग):**")
    c_sum, c_win = st.columns(2)
    
    def apply_time(mode):
        if mode == "Summer":
            slots = [(0,"प्रार्थना सभा","07:30","07:50"),(1,"कालांश 1","07:50","08:30"),(2,"कालांश 2","08:30","09:10"),(3,"कालांश 3","09:10","09:50"),(4,"कालांश 4","09:50","10:30"),(5,"मध्यांतर","10:30","11:00"),(6,"कालांश 5","11:00","11:30"),(7,"कालांश 6","11:30","12:00"),(8,"कालांश 7","12:00","12:30"),(9,"कालांश 8","12:30","13:00")]
        else:
            slots = [(0,"प्रार्थना सभा","10:00","10:25"),(1,"कालांश 1","10:25","11:05"),(2,"कालांश 2","11:05","11:45"),(3,"कालांश 3","11:45","12:25"),(4,"कालांश 4","12:25","13:05"),(5,"मध्यांतर","13:05","13:35"),(6,"कालांश 5","13:35","14:10"),(7,"कालांश 6","14:10","14:45"),(8,"कालांश 7","14:45","15:20"),(9,"कालांश 8","15:20","16:00")]
        conn.execute("DELETE FROM time_slots WHERE school_id=?", (DEFAULT_SCHOOL,))
        data = [(DEFAULT_SCHOOL, s[0], s[1], s[2], s[3]) for s in slots]
        conn.executemany("INSERT INTO time_slots VALUES (?, ?, ?, ?, ?)", data)
        conn.commit()
        st.success(f"✅ {mode} समय लागू कर दिया गया है!")

    if c_sum.button("☀️ ग्रीष्मकालीन (7:30 - 1:00)", use_container_width=True):
        apply_time("Summer"); time.sleep(1); st.rerun()
    if c_win.button("❄️ शीतकालीन (10:00 - 4:00)", use_container_width=True):
        apply_time("Winter"); time.sleep(1); st.rerun()

    st.markdown("---")
    ts_df = get_time_slots(DEFAULT_SCHOOL)
    
    edited_ts = st.data_editor(
        ts_df, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "slot_id": st.column_config.NumberColumn("क्रम", required=True, format="%d"),
            "period_name": st.column_config.TextColumn("कालांश", required=True),
            "start_time": st.column_config.TextColumn("शुरू"),
            "end_time": st.column_config.TextColumn("समाप्त")
        }
    )
    
    if st.button("💾 समय चक्र सुरक्षित करें", type="primary"):
        clean_ts = edited_ts.copy()
        clean_ts['school_id'] = DEFAULT_SCHOOL
        conn.execute("DELETE FROM time_slots WHERE school_id=?", (DEFAULT_SCHOOL,))
        clean_ts[['school_id', 'slot_id', 'period_name', 'start_time', 'end_time']].to_sql('time_slots', conn, if_exists='append', index=False)
        conn.commit(); st.success("✅ समय चक्र सुरक्षित!"); time.sleep(1); st.rerun()

# ------------------------------------------------------------------------------
# 🌟 Tab 6: विषय-अध्यापक मैपिंग (अब स्मार्ट 'मल्टी-सेलेक्ट' के साथ)
# ------------------------------------------------------------------------------
with tab_map:
    st.markdown("<div class='map-box'><h3>🔗 स्मार्ट विषय-अध्यापक मैपिंग (AI Rules)</h3><p>एक ही बार में कई कक्षाओं को चुनें और अध्यापक असाइन करें। (उदा: कक्षा 1 से 5 तक पर्यावरण के लिए एक ही अध्यापक)</p></div>", unsafe_allow_html=True)
    
    t_list = sorted(get_teachers(DEFAULT_SCHOOL))
    s_list = sorted(get_subjects(DEFAULT_SCHOOL))
    c_list = sorted(get_active_classes(DEFAULT_SCHOOL))
    
    if not (t_list and s_list and c_list):
        st.warning("⚠️ मैपिंग शुरू करने से पहले कृपया कक्षाएं, विषय और अध्यापक जोड़ें।")
    else:
        with st.form("add_mapping_form"):
            st.write("👉 **नया वर्कलोड (बल्क) असाइन करें:**")
            
            # 🌟 बदलाव: यहाँ multiselect का उपयोग किया गया है
            sel_classes = st.multiselect("🏫 कक्षाएं चुनें (एक या एक से अधिक):", c_list, placeholder="कक्षाएं चुनें... (उदा: 1, 2, 3)")
            
            col1, col2, col3 = st.columns([2, 2, 1])
            sel_sub = col1.selectbox("📚 विषय:", s_list)
            sel_teach = col2.selectbox("👨‍🏫 अध्यापक:", t_list)
            sel_periods = col3.number_input("⏱️ प्रति सप्ताह कालांश:", min_value=1, max_value=12, value=6)
            
            if st.form_submit_button("🚀 एक क्लिक में नियम लागू करें", type="primary"):
                if not sel_classes:
                    st.error("❌ कृपया कम से कम एक कक्षा चुनें!")
                else:
                    # चयनित सभी कक्षाओं के लिए डेटाबेस में एंट्री
                    new_mappings = [(DEFAULT_SCHOOL, c, sel_sub, sel_teach, sel_periods) for c in sel_classes]
                    conn.executemany("INSERT OR REPLACE INTO subject_mapping VALUES (?, ?, ?, ?, ?)", new_mappings)
                    conn.commit()
                    
                    class_str = ", ".join(sel_classes)
                    st.toast("✅ मैपिंग सफलतापूर्वक लागू हो गई!")
                    st.success(f"🎉 शानदार! **{sel_teach}** को **{class_str}** में **{sel_sub}** पढ़ाने के लिए सेट कर दिया गया है।")
                    time.sleep(1.5); st.rerun()
                
        st.markdown("---")
        st.write(f"🔻 **वर्तमान मैपिंग सूची:**")
        map_df = pd.read_sql_query("SELECT teacher as 'अध्यापक', subject as 'विषय', class_name as 'कक्षा', periods as 'कालांश' FROM subject_mapping WHERE school_id=? ORDER BY teacher, class_name", conn, params=(DEFAULT_SCHOOL,))
        
        if not map_df.empty:
            st.dataframe(map_df, use_container_width=True, hide_index=True)
            if st.button("🗑️ सभी मैपिंग रीसेट करें", type="secondary"):
                conn.execute("DELETE FROM subject_mapping WHERE school_id=?", (DEFAULT_SCHOOL,))
                conn.commit(); st.rerun()
        else:
            st.info("अभी कोई मैपिंग नहीं की गई है।")

conn.close()