###############################################################################
# SMART SCHOOL ERP v12.0 - MASTER REPORTS (MULTI-TENANT SaaS)
# File: pages/5_📈_मास्टर_रिपोर्ट.py
###############################################################################

import streamlit as st
import pandas as pd

# 🌟 बदलाव: DEFAULT_SCHOOL की जगह get_current_school इम्पोर्ट किया गया
from database import get_db_connection, get_unified_class_list, get_short_code, show_print_preview, get_school_info, get_current_school

# 🔒 जादुई सुरक्षा लॉक: यह लाइन लॉगिन हुए स्कूल का ID लेकर उसे DEFAULT_SCHOOL मान लेगी
DEFAULT_SCHOOL = get_current_school()

st.set_page_config(page_title="मास्टर रिपोर्ट", page_icon="📈", layout="wide")

st.markdown("<div style='background: linear-gradient(135deg, #00695c, #004d40); padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 25px; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.15); border-bottom: 4px solid #00251a;'><h1 style='margin: 0; color: white;'>📈 मास्टर रिपोर्ट्स सेंटर</h1><p style='color: #b2dfdb; margin-top: 5px;'>प्रोफेशनल 'गागर में सागर' समय सारणी</p></div>", unsafe_allow_html=True)

conn = get_db_connection()
SCHOOL_NAME, SESSION_YEAR = get_school_info(DEFAULT_SCHOOL)

# ==============================================================================
# 1. इन-पेज सब-मेन्यू (TABS)
# ==============================================================================
tab_master, tab_class, tab_teacher, tab_load, tab_free = st.tabs([
    "📑 गागर में सागर (Pro)", 
    "🏫 कक्षा रिपोर्ट", 
    "👨‍🏫 अध्यापक रिपोर्ट",
    "📊 अध्यापक भार", 
    "🈳 रिक्त कालांश"
])

# ------------------------------------------------------------------------------
# Tab 1: गागर में सागर (ADVANCED COMPACT VIEW)
# ------------------------------------------------------------------------------
with tab_master:
    st.subheader("📑 समेकित समय सारणी (Format: टीचर / विषय / दिन)")
    st.info("💡 **दिन संकेत:** 1=सोम, 2=मंगल, 3=बुध, 4=गुरु, 5=शुक्र, 6=शनि")
    
    df = pd.read_sql_query(f"SELECT * FROM timetable_data WHERE school_id='{DEFAULT_SCHOOL}'", conn)
    slots = pd.read_sql_query(f"SELECT period_name, slot_id FROM time_slots WHERE school_id='{DEFAULT_SCHOOL}' ORDER BY slot_id", conn)
    all_teachers = pd.read_sql_query(f"SELECT Name FROM teachers WHERE school_id='{DEFAULT_SCHOOL}'", conn)['Name'].tolist()
    all_subjects = pd.read_sql_query(f"SELECT name FROM subjects WHERE school_id='{DEFAULT_SCHOOL}'", conn)['name'].tolist()
    
    if df.empty:
        st.warning("⚠️ डेटाबेस खाली है। कृपया पहले टाइम टेबल सेट करें।")
    else:
        # --- STEP 1: अध्यापक शॉर्ट कोड ---
        t_map = {}
        code_counts = {} 
        for t in all_teachers:
            parts = str(t).strip().split()
            if len(parts) >= 2: base_code = (parts[0][0] + parts[1][0]).upper()
            else: base_code = str(t)[:2].upper()
            
            if base_code in code_counts:
                code_counts[base_code] += 1
                final_code = f"{base_code}{code_counts[base_code]}"
            else:
                code_counts[base_code] = 0
                final_code = base_code
            t_map[t] = final_code

        # --- STEP 2: विषय शॉर्ट कोड ---
        s_map = {}
        for s in all_subjects:
            parts = str(s).replace("(", "").replace(")", "").split()
            if len(parts) >= 2: short_sub = parts[0][:2] + "." + parts[1][0]
            else: short_sub = str(s)[:3]
            s_map[s] = short_sub

        # --- STEP 3: दिन मैपिंग ---
        day_to_num = {"सोमवार":1, "मंगलवार":2, "बुधवार":3, "गुरुवार":4, "शुक्रवार":5, "शनिवार":6}
        
        # --- STEP 4: मैट्रिक्स बनाना ---
        classes = get_unified_class_list(DEFAULT_SCHOOL)
        period_names = [p for p in slots['period_name'] if p not in ["प्रार्थना सभा", "मध्यांतर"]]
        
        matrix_data = {p: [] for p in period_names}
        matrix_data['Class'] = classes
        
        for cls in classes:
            for p in period_names:
                cell_data = df[(df['unified_class'] == cls) & (df['period'] == p)]
                if cell_data.empty:
                    matrix_data[p].append("-")
                else:
                    groups = {} 
                    for _, row in cell_data.iterrows():
                        t_code = t_map.get(row['teacher'], "??")
                        s_code = s_map.get(row['subject'], "??")
                        d_num = day_to_num.get(row['day'], 0)
                        
                        key = (t_code, s_code)
                        if key not in groups: groups[key] = []
                        groups[key].append(d_num)
                    
                    cell_html_lines = []
                    for (tc, sc), days_list in groups.items():
                        days_list.sort()
                        ranges = []
                        if not days_list: continue
                        
                        start = end = days_list[0]
                        for i in range(1, len(days_list)):
                            if days_list[i] == end + 1: end = days_list[i]
                            else:
                                ranges.append(f"{start}-{end}" if start != end else f"{start}")
                                start = end = days_list[i]
                        ranges.append(f"{start}-{end}" if start != end else f"{start}")
                        day_str = ",".join(ranges)
                        if day_str == "1-6": day_str = "All"
                        
                        line = f"<b>{tc}</b> <span style='font-size:0.8em'>/{sc}/</span> {day_str}"
                        cell_html_lines.append(line)
                    
                    matrix_data[p].append("<br>".join(cell_html_lines))

        # --- STEP 5: डिस्प्ले और प्रिंट ---
        final_df = pd.DataFrame(matrix_data)
        final_df = final_df.set_index('Class')
        
        st.write("### 📅 मास्टर चार्ट (Pro Preview)")
        
        st.markdown("""
        <style>
            .table-container table { width: 100%; border-collapse: collapse; font-size: 11px; }
            .table-container th { background-color: #2e7d32; color: white; text-align: center; padding: 8px; }
            .table-container td { border: 1px solid #ddd; padding: 4px; text-align: center; vertical-align: middle; line-height: 1.4; }
            .table-container tr:nth-child(even) { background-color: #f9f9f9; }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<div class='table-container'>{final_df.to_html(escape=False)}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        with st.expander("🔍 संकेतों का मतलब (Legend)"):
            c1, c2 = st.columns(2)
            with c1:
                st.write("**👨‍🏫 अध्यापक कोड:**")
                st.write(t_map)
            with c2:
                st.write("**📚 विषय कोड:**")
                st.write(s_map)

        if st.button("🖨️ मास्टर चार्ट प्रिंट करें (Final Print)"):
            html = f"""
            <html>
            <head>
            <style>
                body {{ font-family: sans-serif; }}
                table {{ width: 100%; border-collapse: collapse; font-size: 10px; page-break-inside: auto; }}
                th, td {{ border: 1px solid #000; padding: 4px; text-align: center; vertical-align: middle; }}
                th {{ background-color: #eee; font-weight: bold; height: 25px; }}
                .legend {{ font-size: 9px; margin-top: 10px; display: flex; flex-wrap: wrap; gap: 10px; border-top: 1px solid #ccc; padding-top: 5px; }}
                @page {{ size: landscape; margin: 5mm; }}
            </style>
            </head>
            <body>
                <h3 style="text-align:center;">समेकित समय सारणी - {SCHOOL_NAME}</h3>
                {final_df.to_html(classes='table', escape=False, border=1)}
                <div class="legend">
                    <b>संकेत:</b> (1=सोम, 2=मंगल, 3=बुध, 4=गुरु, 5=शुक्र, 6=शनि)<br>
                    <b>अध्यापक:</b> {", ".join([f"{k}={v}" for k,v in t_map.items()])}
                </div>
            </body>
            </html>
            """
            show_print_preview(html, "समेकित समय सारणी", orientation="landscape", school_id=DEFAULT_SCHOOL)

# ------------------------------------------------------------------------------
# Tab 2: कक्षा-वार रिपोर्ट
# ------------------------------------------------------------------------------
with tab_class:
    st.subheader("🏫 कक्षा-वार टाइम टेबल")
    all_classes = get_unified_class_list(DEFAULT_SCHOOL)
    sel_classes = st.multiselect("कक्षाएं चुनें:", all_classes, default=all_classes[:1] if all_classes else [])
    
    if st.button("🖨️ कक्षा कार्ड प्रिंट करें"):
        if not sel_classes: st.error("कृपया कक्षा चुनें।")
        else:
            full_html = ""
            for cls in sel_classes:
                cls_df = pd.read_sql_query("SELECT * FROM timetable_data WHERE school_id=? AND unified_class=?", conn, params=(DEFAULT_SCHOOL, cls))
                full_html += f"""
                <div style='page-break-inside: avoid; border: 2px solid #333; margin-bottom: 15px; padding: 5px; width: 48%; float: left; margin-right: 1%; box-sizing: border-box;'>
                    <div style='background:#000; color:#fff; text-align:center; font-weight:bold; padding:2px;'>कक्षा: {cls}</div>
                    <table style='width:100%; border-collapse: collapse; margin-top:5px; font-size:10px;'>
                        <tr style='background:#eee;'>
                            <th style='border:1px solid #333;'>कालांश</th>
                            <th style='border:1px solid #333;'>सोम</th>
                            <th style='border:1px solid #333;'>मंगल</th>
                            <th style='border:1px solid #333;'>बुध</th>
                            <th style='border:1px solid #333;'>गुरु</th>
                            <th style='border:1px solid #333;'>शुक्र</th>
                            <th style='border:1px solid #333;'>शनि</th>
                        </tr>
                """
                slot_rows = pd.read_sql_query(f"SELECT period_name FROM time_slots WHERE school_id='{DEFAULT_SCHOOL}' ORDER BY slot_id", conn)
                valid_periods = [p for p in slot_rows['period_name'] if p not in ["प्रार्थना सभा", "मध्यांतर"]]
                for p in valid_periods:
                    full_html += f"<tr><td style='border:1px solid #333; font-weight:bold;'>{p}</td>"
                    for d in ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार"]:
                        cell = cls_df[(cls_df['day'] == d) & (cls_df['period'] == p)]
                        if not cell.empty:
                            t_name = get_short_code(cell.iloc[0]['teacher'], {})
                            sub = cell.iloc[0]['subject'][:6]
                            full_html += f"<td style='border:1px solid #333; text-align:center;'><b>{t_name}</b><br>{sub}</td>"
                        else: full_html += "<td style='border:1px solid #333;'>-</td>"
                    full_html += "</tr>"
                full_html += "</table></div>"
            full_html += "<div style='clear:both;'></div>"
            show_print_preview(full_html, "कक्षा-वार समय सारणी", orientation="portrait", school_id=DEFAULT_SCHOOL)

# ------------------------------------------------------------------------------
# Tab 3: अध्यापक-वार रिपोर्ट
# ------------------------------------------------------------------------------
with tab_teacher:
    st.subheader("👨‍🏫 अध्यापक रिपोर्ट")
    all_teachers = pd.read_sql_query(f"SELECT Name FROM teachers WHERE school_id='{DEFAULT_SCHOOL}'", conn)['Name'].tolist()
    sel_teachers = st.multiselect("अध्यापक चुनें:", all_teachers)
    
    if st.button("🖨️ अध्यापक टाइम टेबल प्रिंट करें"):
        if not sel_teachers: st.error("अध्यापक चुनें।")
        else:
            full_html = ""
            for tch in sel_teachers:
                t_df = pd.read_sql_query("SELECT * FROM timetable_data WHERE school_id=? AND teacher=?", conn, params=(DEFAULT_SCHOOL, tch))
                full_html += f"""
                <div style='page-break-inside: avoid; border: 1px solid #333; margin-bottom: 20px; padding: 10px;'>
                    <h3 style='margin:0 0 5px 0;'>👨‍🏫 {tch}</h3>
                    <table style='width:100%; border-collapse: collapse; font-size:12px;'>
                        <tr style='background:#f0f0f0;'>
                            <th style='border:1px solid #999; padding:4px;'>कालांश</th>
                            <th style='border:1px solid #999; padding:4px;'>सोम</th>
                            <th style='border:1px solid #999; padding:4px;'>मंगल</th>
                            <th style='border:1px solid #999; padding:4px;'>बुध</th>
                            <th style='border:1px solid #999; padding:4px;'>गुरु</th>
                            <th style='border:1px solid #999; padding:4px;'>शुक्र</th>
                            <th style='border:1px solid #999; padding:4px;'>शनि</th>
                        </tr>
                """
                slot_rows = pd.read_sql_query(f"SELECT period_name FROM time_slots WHERE school_id='{DEFAULT_SCHOOL}' ORDER BY slot_id", conn)
                valid_periods = [p for p in slot_rows['period_name'] if p not in ["प्रार्थना सभा", "मध्यांतर"]]
                for p in valid_periods:
                    full_html += f"<tr><td style='border:1px solid #999; padding:4px;'><b>{p}</b></td>"
                    for d in ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार"]:
                        cell = t_df[(t_df['day'] == d) & (t_df['period'] == p)]
                        if not cell.empty:
                            c_name = cell.iloc[0]['unified_class']
                            s_name = cell.iloc[0]['subject']
                            full_html += f"<td style='border:1px solid #999; text-align:center; background:#e8f5e9;'><b>{c_name}</b><br>{s_name}</td>"
                        else: full_html += "<td style='border:1px solid #999; text-align:center;'>-</td>"
                    full_html += "</tr>"
                total_p = len(t_df)
                full_html += f"</table><p style='margin-top:5px;'><b>कुल कालांश: {total_p}</b></p></div>"
            show_print_preview(full_html, "अध्यापक-वार समय सारणी", school_id=DEFAULT_SCHOOL)

# ------------------------------------------------------------------------------
# Tab 4: अध्यापक भार (Workload)
# ------------------------------------------------------------------------------
with tab_load:
    st.subheader("📊 अध्यापक कार्यभार")
    try:
        workload_df = pd.read_sql_query(f"SELECT teacher as 'अध्यापक', COUNT(*) as 'Periods' FROM timetable_data WHERE school_id='{DEFAULT_SCHOOL}' GROUP BY teacher ORDER BY Periods DESC", conn)
        if not workload_df.empty:
            c1, c2 = st.columns([2,1])
            c1.bar_chart(workload_df.set_index('अध्यापक'))
            c2.dataframe(workload_df, use_container_width=True, hide_index=True)
        else: st.info("डेटा उपलब्ध नहीं।")
    except: st.error("Error loading workload.")

# ------------------------------------------------------------------------------
# Tab 5: रिक्त कालांश (Free Periods)
# ------------------------------------------------------------------------------
with tab_free:
    st.subheader("🈳 रिक्त कालांश")
    sel_day_free = st.selectbox("दिन चुनें:", ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार"])
    if st.button("🔍 चेक करें"):
        all_t = pd.read_sql_query(f"SELECT Name FROM teachers WHERE school_id='{DEFAULT_SCHOOL}'", conn)['Name'].tolist()
        slots = pd.read_sql_query(f"SELECT period_name FROM time_slots WHERE school_id='{DEFAULT_SCHOOL}' ORDER BY slot_id", conn)
        valid_p = [p for p in slots['period_name'] if p not in ["प्रार्थना सभा", "मध्यांतर"]]
        res = []
        for p in valid_p:
            busy = pd.read_sql_query("SELECT teacher FROM timetable_data WHERE school_id=? AND day=? AND period=?", conn, params=(DEFAULT_SCHOOL, sel_day_free, p))['teacher'].tolist()
            free = [t for t in all_t if t not in busy]
            res.append({"Period": p, "Free Count": len(free), "Teachers": ", ".join(free)})
        st.dataframe(pd.DataFrame(res), use_container_width=True, hide_index=True)

conn.close()