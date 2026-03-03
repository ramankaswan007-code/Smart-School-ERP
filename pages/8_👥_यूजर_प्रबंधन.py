###############################################################################
# SMART SCHOOL ERP v12.0 - USER MANAGEMENT (SUPER ADMIN ONLY)
# File: pages/8_👥_यूजर_प्रबंधन.py
###############################################################################

import streamlit as st
import pandas as pd
import time
from database import get_db_connection, get_current_school

# 1. पेज कॉन्फ़िगरेशन
st.set_page_config(page_title="यूजर प्रबंधन", page_icon="👥", layout="wide")

# 🔒 सुरक्षा जाँच: केवल Super Admin ही इसे देख सके
if st.session_state.get('role') != 'super_admin':
    st.error("🚫 **Access Denied:** यह पेज केवल सॉफ़्टवेयर निर्माता (Super Admin) के लिए है।")
    st.stop()

st.markdown("<div style='background: linear-gradient(135deg, #1565c0, #0d47a1); padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 25px; color: white;'><h1 style='margin: 0; color: white;'>👥 यूजर (स्कूल) प्रबंधन केंद्र</h1><p style='color: #bbdefb; margin-top: 5px;'>सभी पंजीकृत विद्यालयों का नियंत्रण और सहायता</p></div>", unsafe_allow_html=True)

conn = get_db_connection()

# टैब्स बनाना
tab_list, tab_reset, tab_danger = st.tabs(["📋 पंजीकृत विद्यालय सूची", "🔑 पासवर्ड रीसेट", "⚠️ डेंजर ज़ोन"])

# ------------------------------------------------------------------------------
# Tab 1: विद्यालय सूची (View All Schools)
# ------------------------------------------------------------------------------
with tab_list:
    st.subheader("पंजीकृत विद्यालयों का डेटा")
    query = "SELECT school_id, school_name, district, created_at, role FROM schools WHERE role != 'super_admin'"
    df_schools = pd.read_sql_query(query, conn)
    
    if not df_schools.empty:
        st.dataframe(df_schools, use_container_width=True, hide_index=True)
        st.info(f"कुल पंजीकृत विद्यालय: **{len(df_schools)}**")
    else:
        st.warning("अभी तक कोई विद्यालय पंजीकृत नहीं हुआ है।")

# ------------------------------------------------------------------------------
# Tab 2: पासवर्ड रीसेट (Password Reset)
# ------------------------------------------------------------------------------
with tab_reset:
    st.subheader("🔑 पासवर्ड रीसेट सहायता")
    st.write("यदि कोई स्कूल अपना पासवर्ड भूल गया है, तो आप यहाँ से नया पासवर्ड सेट कर सकते हैं।")
    
    all_school_ids = pd.read_sql_query("SELECT school_id FROM schools WHERE role != 'super_admin'", conn)['school_id'].tolist()
    
    if all_school_ids:
        with st.form("reset_pass_form"):
            target_id = st.selectbox("विद्यालय चुनें (Select School ID):", all_school_ids)
            new_password = st.text_input("नया पासवर्ड बनाएँ (New Password):", placeholder="उदा: school@123")
            
            if st.form_submit_button("💾 पासवर्ड अपडेट करें", type="primary"):
                if new_password:
                    conn.execute("UPDATE schools SET password=? WHERE school_id=?", (new_password, target_id))
                    conn.commit()
                    st.success(f"✅ विद्यालय **{target_id}** का पासवर्ड सफलतापूर्वक बदल दिया गया है!")
                else:
                    st.error("⚠️ कृपया नया पासवर्ड दर्ज करें।")
    else:
        st.info("रीसेट करने के लिए कोई विद्यालय उपलब्ध नहीं है।")

# ------------------------------------------------------------------------------
# Tab 3: डेंजर ज़ोन (Danger Zone)
# ------------------------------------------------------------------------------
with tab_danger:
    st.subheader("⚠️ विद्यालय अकाउंट हटाएँ")
    st.warning("सावधानी: विद्यालय हटाने से उसका सारा डेटा (टीचर, टाइम-टेबल, सेटिंग्स) हमेशा के लिए मिट जाएगा।")
    
    if all_school_ids:
        delete_id = st.selectbox("हटाने के लिए विद्यालय चुनें:", ["-- चुनें --"] + all_school_ids)
        confirm_del = st.checkbox(f"मैं पुष्टि करता हूँ कि मुझे '{delete_id}' का सारा डेटा डिलीट करना है।")
        
        if st.button("🔥 विद्यालय को पूरी तरह हटाएँ", type="secondary", disabled=not confirm_del):
            if delete_id != "-- चुनें --":
                # सभी टेबल्स से डेटा साफ़ करना (SaaS Clean-up)
                tables = ['schools', 'app_settings', 'teachers', 'subjects', 'active_classes', 'time_slots', 'timetable_data', 'arrangements']
                for table in tables:
                    conn.execute(f"DELETE FROM {table} WHERE school_id=?", (delete_id,))
                
                conn.commit()
                st.success(f"🗑️ विद्यालय {delete_id} और उसका सारा डेटा डिलीट कर दिया गया है।")
                time.sleep(1)
                st.rerun()

conn.close()