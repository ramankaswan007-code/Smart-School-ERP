###############################################################################
# SMART SCHOOL ERP v12.0 - ARRANGEMENT SYSTEM (MULTI-TENANT SaaS)
# File: pages/4_📝_अध्यापक_व्यवस्था.py
###############################################################################

import streamlit as st
import pandas as pd
import datetime
import urllib.parse

# 🌟 बदलाव: DEFAULT_SCHOOL की जगह get_current_school इम्पोर्ट किया गया है
from database import get_db_connection, day_map, show_print_preview, get_school_info, get_current_school

# 🔒 जादुई सुरक्षा लॉक: यह लाइन लॉगिन हुए स्कूल का ID लेकर उसे DEFAULT_SCHOOL मान लेगी
DEFAULT_SCHOOL = get_current_school()

# 1. पेज कॉन्फ़िगरेशन
st.set_page_config(page_title="अध्यापक व्यवस्था", page_icon="📝", layout="wide")

# 2. मुख्य हेडर
st.markdown("<div style='background: linear-gradient(135deg, #00695c, #004d40); padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 25px; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.15); border-bottom: 4px solid #00251a;'><h1 style='margin: 0; color: white;'>📝 स्मार्ट व्यवस्थापन रजिस्टर</h1><p style='color: #b2dfdb; margin-top: 5px;'>समेकित सूचना प्रणाली (Consolidated Alerts)</p></div>", unsafe_allow_html=True)

conn = get_db_connection()
SCHOOL_NAME, _ = get_school_info(DEFAULT_SCHOOL) # 🌟 स्कूल का डायनामिक नाम

# --- A. इनपुट सेक्शन ---
c_date, c_absent = st.columns([1, 2])
arrange_date = c_date.date_input("तारीख (Date):", datetime.date.today())
target_day = day_map.get(arrange_date.strftime("%A"), "Sunday")

# 🌟 बदलाव: केवल वर्तमान स्कूल के अध्यापक
all_teachers = pd.read_sql_query(f"SELECT Name FROM teachers WHERE school_id='{DEFAULT_SCHOOL}'", conn)['Name'].tolist()
absent_teachers = c_absent.multiselect("अनुपस्थित शिक्षक चुनें:", all_teachers)

if target_day == "Sunday":
    st.error("रविवार को व्यवस्था नहीं लगाई जा सकती।")
elif not absent_teachers:
    st.info("👈 कृपया व्यवस्था लगाने के लिए पहले अनुपस्थित शिक्षकों को चुनें।")
else:
    st.markdown("---")
    st.subheader("🛠️ व्यवस्था लगाएं (Assign Substitution)")
    
    arrangement_data = [] # डेटा इकट्ठा करने के लिए लिस्ट
    
    # --- B. लूप: हर अनुपस्थित शिक्षक के लिए ---
    for ab_t in absent_teachers:
        st.markdown(f"**👤 {ab_t} की कक्षाएं:**")
        
        # उस दिन की उनकी कक्षाएं
        classes_to_cover = pd.read_sql_query(
            "SELECT period, unified_class, subject FROM timetable_data WHERE school_id=? AND day=? AND teacher=?", 
            conn, params=(DEFAULT_SCHOOL, target_day, ab_t)
        )
        
        if classes_to_cover.empty:
            st.caption("आज इनकी कोई कक्षा नहीं है।")
            continue
        
        # हर पीरियड के लिए व्यवस्था
        for idx, row in classes_to_cover.iterrows():
            p = row['period']
            cls = row['unified_class']
            sub = row['subject']
            
            # व्यस्त और फ्री शिक्षक ढूँढना
            busy_in_period = pd.read_sql_query("SELECT teacher FROM timetable_data WHERE school_id=? AND day=? AND period=?", conn, params=(DEFAULT_SCHOOL, target_day, p))['teacher'].tolist()
            possible_subs = [t for t in all_teachers if t not in busy_in_period and t not in absent_teachers]
            
            # UI लेआउट (Row)
            c1, c2 = st.columns([2, 2])
            c1.write(f"🔴 **{p}** - {cls} ({sub})")
            
            # ड्रापडाउन और पिछला डेटा
            key_str = f"arr_{ab_t}_{p}_{cls}"
            existing = pd.read_sql_query("SELECT assigned_teacher FROM arrangements WHERE school_id=? AND date=? AND period=? AND unified_class=?", conn, params=(DEFAULT_SCHOOL, str(arrange_date), p, cls))
            
            def_idx = 0
            if not existing.empty and existing.iloc[0]['assigned_teacher'] in possible_subs:
                def_idx = possible_subs.index(existing.iloc[0]['assigned_teacher']) + 1
            
            selected_sub = c2.selectbox("व्यवस्थापक चुनें:", ["-- चुनें --"] + possible_subs, index=def_idx, key=key_str, label_visibility="collapsed")
            
            # डेटा कलेक्ट करें (अगर चुना गया है)
            if selected_sub != "-- चुनें --":
                arrangement_data.append({
                    "Original": ab_t,
                    "Period": p,
                    "Class": cls,
                    "Subject": sub,
                    "New Teacher": selected_sub
                })
        st.write("") # Spacer

    st.markdown("---")

    # --- C. फाइनल ड्राफ्ट और व्हाट्सएप सेक्शन ---
    if arrangement_data:
        df_arr = pd.DataFrame(arrangement_data)
        
        # 1. फाइनल लिस्ट दिखाएं
        st.subheader("📋 फाइनल ड्राफ्ट (Final List)")
        st.dataframe(df_arr, use_container_width=True)
        
        # सेव बटन
        c_save, c_print = st.columns(2)
        if c_save.button("💾 रजिस्टर में सेव करें", type="primary"):
            for item in arrangement_data:
                conn.execute("INSERT OR REPLACE INTO arrangements (school_id, date, period, unified_class, original_teacher, assigned_teacher) VALUES (?,?,?,?,?,?)",
                    (DEFAULT_SCHOOL, str(arrange_date), item['Period'], item['Class'], item['Original'], item['New Teacher']))
            conn.commit()
            st.success("✅ डेटा सेव हो गया!")
            
        if c_print.button("🖨️ प्रिंट प्रिव्यू (Print)"):
            html_table = f"""
            <h3 style="text-align:center;">अध्यापक व्यवस्था रजिस्टर - {arrange_date.strftime('%d-%m-%Y')}</h3>
            <table style="width:100%; border-collapse: collapse; font-family: Arial; font-size: 14px;">
                <tr style="background:#eee;">
                    <th style="border:1px solid #000; padding:8px;">कालांश</th>
                    <th style="border:1px solid #000; padding:8px;">कक्षा</th>
                    <th style="border:1px solid #000; padding:8px;">अनुपस्थित</th>
                    <th style="border:1px solid #000; padding:8px;">व्यवस्थापक</th>
                    <th style="border:1px solid #000; padding:8px;">हस्ताक्षर</th>
                </tr>
            """
            for item in arrangement_data:
                html_table += f"""
                    <tr>
                        <td style="border:1px solid #000; padding:8px; text-align:center;">{item['Period']}</td>
                        <td style="border:1px solid #000; padding:8px; text-align:center;">{item['Class']}</td>
                        <td style="border:1px solid #000; padding:8px;">{item['Original']}</td>
                        <td style="border:1px solid #000; padding:8px; font-weight:bold;">{item['New Teacher']}</td>
                        <td style="border:1px solid #000; padding:8px;"></td>
                    </tr>
                """
            html_table += "</table>"
            show_print_preview(html_table, f"Arrangement_{arrange_date}", school_id=DEFAULT_SCHOOL)

        st.markdown("---")
        
        # 2. व्हाट्सएप सेक्शन (CONSOLIDATED)
        st.subheader("📢 व्हाट्सएप सूचना केंद्र")
        st.info("यहाँ से शिक्षकों को उनकी **सभी व्यवस्थाओं** की जानकारी एक ही मैसेज में भेजें।")
        
        tab_individual, tab_group = st.tabs(["👤 व्यक्तिगत संदेश (Individual)", "🏫 स्टाफ ग्रुप संदेश (Group)"])
        
        # --- TAB 1: एक शिक्षक को एक ही मैसेज (Consolidated) ---
        with tab_individual:
            grouped = df_arr.groupby('New Teacher')
            cols = st.columns(3)
            idx = 0
            
            for teacher_name, group_df in grouped:
                mob_row = pd.read_sql_query("SELECT Mobile FROM teachers WHERE school_id=? AND Name=?", conn, params=(DEFAULT_SCHOOL, teacher_name))
                mobile_no = ""
                if not mob_row.empty and mob_row.iloc[0]['Mobile']:
                    mobile_no = ''.join(filter(str.isdigit, str(mob_row.iloc[0]['Mobile'])))
                
                msg_lines = [f"*{SCHOOL_NAME}*"]
                msg_lines.append(f"📅 दिनांक: {arrange_date.strftime('%d-%m-%Y')}\n")
                msg_lines.append(f"नमस्ते *{teacher_name}* जी,")
                msg_lines.append(f"आज आपकी व्यवस्था (Substitution) निम्न कक्षाओं में है:\n")
                
                for _, row in group_df.iterrows():
                    msg_lines.append(f"🔹 *{row['Period']}*: {row['Class']} ({row['Subject']})")
                    msg_lines.append(f"   (मूल: {row['Original']})")
                
                msg_lines.append(f"\nकृपया समय पर कक्षा लें।\n- प्रभारी")
                final_msg = "\n".join(msg_lines)
                
                if len(mobile_no) >= 10:
                    link = f"https://wa.me/91{mobile_no[-10:]}?text={urllib.parse.quote(final_msg)}"
                    btn_label = f"💬 {teacher_name} ({len(group_df)})"
                    
                    with cols[idx % 3]:
                        st.markdown(f"""
                            <a href="{link}" target="_blank" style="text-decoration:none;">
                                <div style="background:#25D366; color:white; padding:10px; border-radius:5px; text-align:center; font-weight:bold; margin-bottom:10px; box-shadow:0 2px 4px rgba(0,0,0,0.2);">
                                    {btn_label}
                                </div>
                            </a>
                        """, unsafe_allow_html=True)
                else:
                    with cols[idx % 3]:
                        st.warning(f"{teacher_name} (No Mobile)")
                
                idx += 1

        # --- TAB 2: पूरे स्टाफ ग्रुप के लिए एक लिस्ट ---
        with tab_group:
            st.write("नीचे दी गई लिस्ट को **Copy** करें और स्कूल के व्हाट्सएप ग्रुप में पेस्ट करें।")
            
            group_msg = [f"*🏫 {SCHOOL_NAME} - व्यवस्था रजिस्टर*"]
            group_msg.append(f"📅 दिनांक: {arrange_date.strftime('%d-%m-%Y')}\n")
            group_msg.append("आज अनुपस्थित शिक्षकों के स्थान पर निम्न व्यवस्था रहेगी:\n")
            
            for _, row in df_arr.iterrows():
                group_msg.append(f"📌 *{row['Period']}* | {row['Class']} | {row['New Teacher']}")
                group_msg.append(f"   ({row['Original']} के स्थान पर)\n")
            
            group_msg.append("\n- आज्ञा से प्रधानाचार्य")
            full_text = "\n".join(group_msg)
            
            st.code(full_text, language="text")
            
            group_link = f"https://wa.me/?text={urllib.parse.quote(full_text)}"
            st.markdown(f"""
                <a href="{group_link}" target="_blank">
                    <button style="background:#128C7E; color:white; border:none; padding:10px 20px; border-radius:5px; font-weight:bold; cursor:pointer;">
                        🚀 WhatsApp पर शेयर करें (Share to Group)
                    </button>
                </a>
            """, unsafe_allow_html=True)

conn.close()