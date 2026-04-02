###############################################################################
# SMART SCHOOL ERP v17.0 - AI AUTO-PILOT TIMETABLE GENERATOR
# File: pages/2_📅_टाइम_टेबल.py
###############################################################################

import streamlit as st
import pandas as pd
import time
from database import get_db_connection, safe_sort, get_unified_class_list, get_current_school, get_teachers, get_subjects, get_time_slots, get_timetable_data

# 🔒 सुरक्षा लॉक
DEFAULT_SCHOOL = get_current_school()

st.set_page_config(page_title="स्मार्ट टाइम टेबल एडिटर", page_icon="📅", layout="wide")

st.markdown("""
    <style>
    .header-box { background: linear-gradient(135deg, #00695c, #004d40); padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 20px; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.15); border-bottom: 4px solid #00251a; }
    .status-bar { background: #e8f5e9; padding: 12px; border-radius: 8px; border-left: 6px solid #2e7d32; margin-bottom: 10px; font-size: 16px; font-weight: bold;}
    .workload-bar { background: #fff3e0; padding: 10px; border-radius: 8px; border-left: 6px solid #e65100; margin-bottom: 20px; font-size: 15px; color: #d84315;}
    .break-row { background: #e0f2f1; color: #004d40; text-align: center; padding: 8px; border-radius: 5px; font-weight: bold; margin: 5px 0; border: 1px dashed #00695c; }
    .ai-box { background: linear-gradient(135deg, #6a1b9a, #4a148c); padding: 15px; border-radius: 10px; color: white; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='header-box'><h1 style='margin: 0; color: white;'>📅 स्मार्ट टाइम-टेबल मैट्रिक्स (AI Assisted)</h1><p style='color: #b2dfdb; margin-top: 5px;'>टकराव-मुक्त मैनुअल एडिटिंग या AI की मदद से 1-क्लिक जनरेशन</p></div>", unsafe_allow_html=True)

conn = get_db_connection()

# --- मास्टर डेटा ---
all_teachers = safe_sort(get_teachers(DEFAULT_SCHOOL))
all_subjects = safe_sort(get_subjects(DEFAULT_SCHOOL))
all_classes = get_unified_class_list(DEFAULT_SCHOOL)
all_tt_data = get_timetable_data(DEFAULT_SCHOOL)

if 'tool_teacher' not in st.session_state: st.session_state.tool_teacher = None
if 'tool_subject' not in st.session_state: st.session_state.tool_subject = None
if 'tool_class' not in st.session_state: st.session_state.tool_class = None

# ==============================================================================
# 🤖 STEP 0: AI AUTO-PILOT (जादुई जनरेटर)
# ==============================================================================
with st.expander("✨ 🤖 AI ऑटो-पायलट (1-Click Timetable Generator)", expanded=False):
    st.markdown("<div class='ai-box'><h3>✨ जादुई टाइम-टेबल जनरेटर</h3><p>मास्टर सेटिंग्स में दी गई 'विषय-अध्यापक मैपिंग' के आधार पर सिस्टम पूरे स्कूल का टाइम-टेबल खुद बना देगा।</p></div>", unsafe_allow_html=True)
    
    mapping_data = pd.read_sql_query("SELECT * FROM subject_mapping WHERE school_id=?", conn, params=(DEFAULT_SCHOOL,))
    
    if mapping_data.empty:
        st.warning("⚠️ **मैपिंग डेटा नहीं मिला!** कृपया पहले 'मास्टर सेटिंग्स' -> 'विषय-अध्यापक मैपिंग' में जाकर तय करें कि कौन सा अध्यापक कौनसी कक्षा में पढ़ाएगा।")
    else:
        st.success(f"📊 सिस्टम को {len(mapping_data)} मैपिंग नियम (Rules) मिल गए हैं।")
        if st.button("🚀 AI ऑटो-जनरेट शुरू करें (पुराना टाइम-टेबल रीसेट हो जाएगा)", type="primary"):
            with st.spinner("🧠 AI टाइम-टेबल बना रहा है... कृपया प्रतीक्षा करें (टकराव से बचते हुए)..."):
                # 1. डेटा साफ़ करें
                conn.execute("DELETE FROM timetable_data WHERE school_id=?", (DEFAULT_SCHOOL,))
                
                slots = [row['period_name'] for _, row in get_time_slots(DEFAULT_SCHOOL).iterrows() if row['period_name'] not in ('प्रार्थना सभा', 'मध्यांतर')]
                days = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार"]
                
                # 2. इन-मेमोरी ट्रैकर (तेज़ जनरेशन के लिए)
                teacher_schedule = set()
                class_schedule = set()
                new_tt_records = []
                
                # 3. एल्गोरिदम लॉजिक
                for _, row in mapping_data.iterrows():
                    cls, sub, tch, req_p = row['class_name'], row['subject'], row['teacher'], int(row['periods'])
                    assigned = 0
                    
                    # राउंड 1: हर दिन 1 कालांश देने की कोशिश (समान वितरण के लिए)
                    for d in days:
                        if assigned >= req_p: break
                        for p in slots:
                            if (d, p, tch) not in teacher_schedule and (d, p, cls) not in class_schedule:
                                new_tt_records.append((DEFAULT_SCHOOL, cls, d, p, tch, sub))
                                teacher_schedule.add((d, p, tch))
                                class_schedule.add((d, p, cls))
                                assigned += 1
                                break # एक दिन में एक हो गया, अगले दिन चलें
                                
                    # राउंड 2: अगर कुछ पीरियड बच गए हों (जैसे 6 से ज्यादा पीरियड हों)
                    if assigned < req_p:
                        for d in days:
                            if assigned >= req_p: break
                            for p in slots:
                                if assigned >= req_p: break
                                if (d, p, tch) not in teacher_schedule and (d, p, cls) not in class_schedule:
                                    new_tt_records.append((DEFAULT_SCHOOL, cls, d, p, tch, sub))
                                    teacher_schedule.add((d, p, tch))
                                    class_schedule.add((d, p, cls))
                                    assigned += 1
                
                # 4. डेटाबेस में सुरक्षित करना
                if new_tt_records:
                    conn.executemany("INSERT INTO timetable_data VALUES (?,?,?,?,?,?)", new_tt_records)
                    conn.commit()
                    st.balloons()
                    st.success("🎉 जादुई रूप से टाइम-टेबल तैयार हो गया! आप नीचे इसकी समीक्षा कर सकते हैं।")
                    time.sleep(2)
                    st.rerun()

st.markdown("---")

# ==============================================================================
# STEP 1: सिलेक्शन मोड (MANUAL EDITOR)
# ==============================================================================
c_mode, c_select = st.columns([1, 2])
with c_mode: editor_mode = st.radio("1️⃣ एडिटिंग मोड:", ["🏫 कक्षा-वार (Class-wise)", "👨‍🏫 अध्यापक-वार (Teacher-wise)"], horizontal=True)
with c_select:
    if "कक्षा" in editor_mode: main_selection = st.selectbox("2️⃣ कक्षा चुनें:", all_classes) if all_classes else None
    else: main_selection = st.selectbox("2️⃣ अध्यापक चुनें:", all_teachers) if all_teachers else None

st.markdown("---")

if main_selection:
    # ==============================================================================
    # STEP 2: पेंट-ब्रश टूल्स (क्या भरना है?)
    # ==============================================================================
    st.markdown("### 🖌️ 3️⃣ अपना 'पेंट-ब्रश' तैयार करें (मैनुअल सुधार के लिए)")
    
    t_tool = st.session_state.tool_teacher if "कक्षा" in editor_mode else st.session_state.tool_class
    s_tool = st.session_state.tool_subject

    # 🌟 लाइव वर्कलोड ट्रैकर 🌟
    workload_msg = ""
    if "कक्षा" in editor_mode and st.session_state.tool_teacher:
        t_count = len(all_tt_data[all_tt_data['teacher'] == st.session_state.tool_teacher])
        workload_msg = f"📊 **वर्कलोड ट्रैकर:** {st.session_state.tool_teacher} को अब तक पूरे सप्ताह में **{t_count}** कालांश दिए जा चुके हैं।"
    elif "अध्यापक" in editor_mode and main_selection:
        t_count = len(all_tt_data[all_tt_data['teacher'] == main_selection])
        workload_msg = f"📊 **वर्कलोड ट्रैकर:** {main_selection} को अब तक पूरे सप्ताह में **{t_count}** कालांश दिए जा चुके हैं।"

    tool_msg = f"वर्तमान टूल: "
    if s_tool == "ERASER": tool_msg += "🗑️ **मिटाने वाला (Eraser Mode)** - जिसे मिटाना है उस पर क्लिक करें।"
    elif t_tool and s_tool: tool_msg += f"✅ **{t_tool}** को **{s_tool}** पढ़ाने के लिए सेट किया गया है।"
    else: tool_msg += "❌ **खाली** (कृपया नीचे से विषय और अध्यापक चुनें)"

    st.markdown(f"<div class='status-bar'>{tool_msg}</div>", unsafe_allow_html=True)
    if workload_msg: st.markdown(f"<div class='workload-bar'>{workload_msg}</div>", unsafe_allow_html=True)

    col_tl, col_tr = st.columns(2)
    with col_tl:
        with st.container(border=True):
            if "कक्षा" in editor_mode:
                st.write("**👨‍🏫 अध्यापक चुनें:**")
                t_cols = st.columns(3)
                for i, t in enumerate(all_teachers):
                    is_act = (st.session_state.tool_teacher == t)
                    if t_cols[i % 3].button(t, key=f"t_{i}", type="primary" if is_act else "secondary", use_container_width=True):
                        st.session_state.tool_teacher = t; st.rerun()
            else:
                st.write("**🏫 कक्षा चुनें:**")
                c_cols = st.columns(3)
                for i, c in enumerate(all_classes):
                    is_act = (st.session_state.tool_class == c)
                    if c_cols[i % 3].button(c, key=f"c_{i}", type="primary" if is_act else "secondary", use_container_width=True):
                        st.session_state.tool_class = c; st.rerun()

    with col_tr:
        with st.container(border=True):
            st.write("**📚 विषय चुनें:**")
            s_cols = st.columns(3)
            for i, s in enumerate(all_subjects):
                is_act = (st.session_state.tool_subject == s)
                if s_cols[i % 3].button(s, key=f"s_{i}", type="primary" if is_act else "secondary", use_container_width=True):
                    st.session_state.tool_subject = s; st.rerun()
            st.markdown("---")
            if st.button("🗑️ इरेज़र (Eraser Mode) चालू करें", type="primary" if s_tool == "ERASER" else "secondary", use_container_width=True):
                st.session_state.tool_subject = "ERASER"; st.rerun()

    st.markdown("---")

    # ==============================================================================
    # STEP 3: वीकली मैट्रिक्स (Smart Highlighting के साथ)
    # ==============================================================================
    st.markdown(f"### 🗓️ 4️⃣ साप्ताहिक शेड्यूल: <span style='color:#2e7d32'>{main_selection}</span>", unsafe_allow_html=True)

    all_slots = get_time_slots(DEFAULT_SCHOOL)['period_name'].tolist()
    if "कक्षा" in editor_mode: curr_data = all_tt_data[all_tt_data['unified_class'] == main_selection]
    else: curr_data = all_tt_data[all_tt_data['teacher'] == main_selection]

    days = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार"]
    short_days = ["सोम", "मंगल", "बुध", "गुरु", "शुक्र", "शनि"]

    h_cols = st.columns([1.5, 1, 1, 1, 1, 1, 1])
    h_cols[0].markdown("<h5 style='text-align:center;'>⏱️ कालांश</h5>", unsafe_allow_html=True)
    for i, d in enumerate(short_days): h_cols[i+1].markdown(f"<h5 style='text-align:center;'>{d}</h5>", unsafe_allow_html=True)

    for p_name in all_slots:
        if p_name in ["प्रार्थना सभा", "मध्यांतर"]:
            st.markdown(f"<div class='break-row'>☕ {p_name}</div>", unsafe_allow_html=True)
            continue

        r_cols = st.columns([1.5, 1, 1, 1, 1, 1, 1])
        
        if r_cols[0].button(f"⚡ {p_name}\n(सभी 6 दिन)", key=f"all_{p_name}", type="primary", use_container_width=True):
            if s_tool == "ERASER":
                remove_col = 'unified_class' if 'कक्षा' in editor_mode else 'teacher'
                conn.execute(f"DELETE FROM timetable_data WHERE school_id=? AND period=? AND {remove_col}=?", (DEFAULT_SCHOOL, p_name, main_selection))
                conn.commit(); st.rerun()
            elif t_tool and s_tool:
                for d in days:
                    conn.execute("INSERT OR REPLACE INTO timetable_data VALUES (?,?,?,?,?,?)", (DEFAULT_SCHOOL, main_selection if "कक्षा" in editor_mode else t_tool, d, p_name, t_tool if "कक्षा" in editor_mode else main_selection, s_tool))
                conn.commit(); st.balloons(); st.rerun()

        for i, d in enumerate(days):
            match = curr_data[(curr_data['period'] == p_name) & (curr_data['day'] == d)]
            btn_txt = "➕ खाली"
            is_disabled = False
            
            # 🌟 स्मार्ट लॉकिंग 🌟
            if "कक्षा" in editor_mode and t_tool and s_tool != "ERASER":
                conflict = all_tt_data[(all_tt_data['day'] == d) & (all_tt_data['period'] == p_name) & (all_tt_data['teacher'] == t_tool) & (all_tt_data['unified_class'] != main_selection)]
                if not conflict.empty: btn_txt = f"🔴 व्यस्त\n({conflict.iloc[0]['unified_class']})"; is_disabled = True
            elif "अध्यापक" in editor_mode and t_tool and s_tool != "ERASER":
                conflict = all_tt_data[(all_tt_data['day'] == d) & (all_tt_data['period'] == p_name) & (all_tt_data['unified_class'] == t_tool) & (all_tt_data['teacher'] != main_selection)]
                if not conflict.empty: btn_txt = f"🔴 व्यस्त\n({conflict.iloc[0]['teacher']})"; is_disabled = True

            if not match.empty:
                assigned_name = match.iloc[0]['teacher'] if "कक्षा" in editor_mode else match.iloc[0]['unified_class']
                btn_txt = f"✅ {assigned_name}\n({match.iloc[0]['subject']})"
                is_disabled = False 
            elif not is_disabled and t_tool and s_tool != "ERASER":
                btn_txt = "🟢 फ्री (क्लिक करें)"
                
            if r_cols[i+1].button(btn_txt, key=f"c_{p_name}_{d}", disabled=is_disabled, use_container_width=True):
                if s_tool == "ERASER":
                    remove_col = 'unified_class' if 'कक्षा' in editor_mode else 'teacher'
                    conn.execute(f"DELETE FROM timetable_data WHERE school_id=? AND day=? AND period=? AND {remove_col}=?", (DEFAULT_SCHOOL, d, p_name, main_selection))
                elif t_tool and s_tool:
                    conn.execute("INSERT OR REPLACE INTO timetable_data VALUES (?,?,?,?,?,?)", (DEFAULT_SCHOOL, main_selection if "कक्षा" in editor_mode else t_tool, d, p_name, t_tool if "कक्षा" in editor_mode else main_selection, s_tool))
                conn.commit(); st.rerun()

conn.close()