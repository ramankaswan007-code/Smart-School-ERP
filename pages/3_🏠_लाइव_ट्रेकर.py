###############################################################################
# SMART SCHOOL ERP v12.0 - LIVE TRACKER (MULTI-TENANT SaaS)
# File: pages/3_🏠_लाइव_ट्रेकर.py
###############################################################################

import streamlit as st
import pandas as pd
import datetime

# 🌟 बदलाव: DEFAULT_SCHOOL की जगह get_current_school इम्पोर्ट किया गया है
from database import get_db_connection, day_map, get_current_school

# 🔒 जादुई सुरक्षा लॉक: यह लाइन लॉगिन हुए स्कूल का ID लेकर उसे DEFAULT_SCHOOL मान लेगी
DEFAULT_SCHOOL = get_current_school()

st.set_page_config(page_title="लाइव ट्रेकर", page_icon="🏠", layout="wide")

st.markdown("<div style='background: linear-gradient(135deg, #00695c, #004d40); padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 25px; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.15); border-bottom: 4px solid #00251a;'><h1 style='margin: 0; color: white;'>🏠 लाइव क्लास ट्रेकर</h1><p style='color: #b2dfdb; margin-top: 5px;'>रियल-टाइम विद्यालय स्थिति</p></div>", unsafe_allow_html=True)

conn = get_db_connection()

# 1. वर्तमान समय और दिन
now = datetime.datetime.now()
curr_time_str = now.strftime("%H:%M")
curr_day_name = day_map.get(now.strftime("%A"), "Sunday") 

c1, c2, c3 = st.columns(3)
c1.info(f"🕒 समय: **{now.strftime('%I:%M %p')}**")
c2.info(f"📅 दिन: **{curr_day_name}**")

# 2. वर्तमान कालांश (Period) का पता लगाना
all_slots = pd.read_sql_query(f"SELECT * FROM time_slots WHERE school_id='{DEFAULT_SCHOOL}' ORDER BY slot_id", conn)

current_period = None
for i, row in all_slots.iterrows():
    if row['start_time'] <= curr_time_str <= row['end_time']:
        current_period = row['period_name']
        break
        
if not current_period:
    c3.warning("अभी स्कूल समय नहीं है")
    if not all_slots.empty:
        display_period = st.selectbox("मैन्युअल कालांश चुनें (View Mode):", all_slots['period_name'].tolist())
    else:
        display_period = None
        st.error("टाइम स्लॉट्स सेट नहीं हैं।")
else:
    c3.success(f"🔔 वर्तमान: **{current_period}**")
    display_period = current_period

st.markdown("---")

# 3. डेटा निकालना (कौन कहाँ है?)
if curr_day_name == "Sunday":
    st.error("आज रविवार है! (छुट्टी)")
elif display_period:
    st.subheader(f"📍 स्थिति: {display_period}")
    
    # व्यस्त शिक्षक
    busy_df = pd.read_sql_query(
        "SELECT teacher, unified_class, subject FROM timetable_data WHERE school_id=? AND day=? AND period=?", 
        conn, params=(DEFAULT_SCHOOL, curr_day_name, display_period)
    )
    
    # सभी शिक्षक
    all_teachers = pd.read_sql_query(f"SELECT Name FROM teachers WHERE school_id='{DEFAULT_SCHOOL}'", conn)['Name'].tolist()
    
    # फ्री शिक्षक 
    busy_teachers_list = busy_df['teacher'].tolist()
    free_teachers = [t for t in all_teachers if t not in busy_teachers_list]
    
    col_busy, col_free = st.columns([2, 1])
    
    with col_busy:
        st.markdown("### 🔴 कक्षा चल रही है (Ongoing)")
        if not busy_df.empty:
            display_df = busy_df.rename(columns={'teacher': 'अध्यापक', 'unified_class': 'कक्षा', 'subject': 'विषय'})
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("इस कालांश में कोई क्लास नहीं है।")
            
    with col_free:
        st.markdown("### 🟢 फ्री शिक्षक (Available)")
        if free_teachers:
            st.success(f"कुल फ्री: {len(free_teachers)}")
            st.table(pd.DataFrame(free_teachers, columns=["नाम"]))
        else:
            st.warning("कोई भी शिक्षक फ्री नहीं है!")

conn.close()