###############################################################################
# SMART SCHOOL ERP v12.0 - MASTER REPORTS (MULTI-TENANT SaaS)
# File: pages/5_📈_मास्टर_रिपोर्ट.py
###############################################################################

import streamlit as st
import pandas as pd

# 🌟 बदलाव: DEFAULT_SCHOOL की जगह get_current_school इम्पोर्ट किया गया
from database import get_db_connection, get_unified_class_list, get_short_code, show_print_preview, get_school_info, get_current_school, get_teachers, get_subjects, get_time_slots, get_timetable_data

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
    
    df = get_timetable_data(DEFAULT_SCHOOL)
    slots = get_time_slots(DEFAULT_SCHOOL)
    all_teachers = get_teachers(DEFAULT_SCHOOL)
    all_subjects = get_subjects(DEFAULT_SCHOOL)
    
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
        period_names = slots['period_name'].tolist()
        time_map = {row['period_name']: f"{row['start_time']}-{row['end_time']}" for _, row in slots.iterrows()}
        period_labels = [f"{p}<br><span style='font-size:0.8em;'>{time_map.get(p, '')}</span>" for p in period_names]
        
        matrix_data = {label: [] for label in period_labels}
        matrix_data['Class / कालांश'] = []
        
        for cls in classes:
            matrix_data['Class / कालांश'].append(cls)
            for label, p in zip(period_labels, period_names):
                cell_data = df[(df['unified_class'] == cls) & (df['period'] == p)]
                if cell_data.empty:
                    matrix_data[label].append("-")
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
                        
                        line = f"<div style='margin:2px 0; padding:4px; border:1px solid #c8e6c9; background:#e8f5e9; border-radius:6px; text-align:left; line-height:1.2;'><b>{tc}</b> <span style='font-size:0.8em'>/{sc}/</span> <span style='float:right; font-size:0.75em; color:#555;'>{day_str}</span></div>"
                        cell_html_lines.append(line)
                    
                    matrix_data[label].append("".join(cell_html_lines))

        # --- STEP 5: डिस्प्ले और प्रिंट ---
        final_df = pd.DataFrame(matrix_data)
        cols = ['Class / कालांश'] + period_labels
        final_df = final_df[cols]
        
        st.write("### 📅 मास्टर चार्ट (Pro Preview)")
        
        st.markdown("""
        <style>
            .table-container table { width: 100%; border-collapse: collapse; font-size: 11px; }
            .table-container th { background-color: #2e7d32; color: white; text-align: center; padding: 8px; }
            .table-container td { border: 1px solid #ddd; padding: 4px; text-align: center; vertical-align: middle; line-height: 1.4; }
            .table-container tr:nth-child(even) { background-color: #f9f9f9; }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown(f"<div class='table-container'>{final_df.to_html(index=False, escape=False)}</div>", unsafe_allow_html=True)
        
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
                {final_df.to_html(classes='table', escape=False, border=1, index=False)}
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
            header_html = f"""
                <style>
                    body {{ font-family: sans-serif; margin: 10px; color: #111; background: #fff; }}
                    .class-print-wrapper {{ display: flex; flex-wrap: wrap; gap: 10px; justify-content: space-between; }}
                    .class-card {{
                        page-break-inside: avoid;
                        break-inside: avoid;
                        border: 2px solid #333;
                        margin-bottom: 15px;
                        padding: 10px;
                        width: calc(50% - 10px);
                        box-sizing: border-box;
                        background: #fff;
                    }}
                    .class-card h2 {{ margin: 0 0 8px 0; font-size: 14px; background:#000; color:#fff; padding:4px; text-align:center; }}
                    .class-table {{ width:100%; border-collapse: collapse; font-size:11px; table-layout: fixed; }}
                    .class-table th, .class-table td {{ border:1px solid #333; padding:4px; text-align:center; vertical-align: top; word-break: break-word; }}
                    .class-table th {{ background:#eee; }}
                    .class-table td.period-cell {{ background:#f5f5f0; font-weight:600; }}
                    .class-table tr.break-row td {{ background:#faf8e6; color:#333; }}
                    .class-table td div {{ display:block; padding:3px; border-radius:4px; background:#f9f9f9; min-height: auto; }}
                    @media print {{
                        body {{ margin: 5mm; }}
                        .class-print-wrapper {{ display: block; }}
                        .class-card {{ width: 100% !important; margin: 0 0 15px 0; page-break-after: auto; break-inside: avoid; }}
                    }}
                </style>
                <div class='class-print-wrapper'>
            """
            full_html = header_html
            for cls in sel_classes:
                cls_df = get_timetable_data(DEFAULT_SCHOOL, unified_class=cls)
                full_html += f"""
                <div class='class-card'>
                    <h2>कक्षा: {cls}</h2>
                    <table class='class-table'>
                        <tr>
                            <th>कालांश</th>
                            <th>सोम</th>
                            <th>मंगल</th>
                            <th>बुध</th>
                            <th>गुरु</th>
                            <th>शुक्र</th>
                            <th>शनि</th>
                        </tr>
                """
                slot_rows = get_time_slots(DEFAULT_SCHOOL)
                time_map = {row['period_name']: f"{row['start_time']} - {row['end_time']}" for _, row in slot_rows.iterrows()}
                valid_periods = slot_rows['period_name'].tolist()
                for p in valid_periods:
                    slot_time = time_map.get(p, "")
                    row_style = 'background:#faf8e6;' if p in ['प्रार्थना सभा', 'मध्यांतर'] else ''
                    first_td_style = 'border:1px solid #999; padding:4px; background:#f5f5f0;'
                    cell_bg = 'background:#faf8e6;' if p in ['प्रार्थना सभा', 'मध्यांतर'] else ''
                    full_html += f"<tr style='{row_style}'>"
                    full_html += f"<td style='{first_td_style}'><div style='font-size:12px; font-weight:bold;'>{p}</div><div style='font-size:10px; color:#555; margin-top:4px;'>{slot_time}</div></td>"
                    for d in ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार"]:
                        cell = cls_df[(cls_df['day'] == d) & (cls_df['period'] == p)]
                        if not cell.empty:
                            t_name = cell.iloc[0]['teacher']
                            sub = cell.iloc[0]['subject']
                            full_html += f"<td style='border:1px solid #999; text-align:center; {cell_bg}'><div style='background:transparent;'><b>{t_name}</b><br>{sub}</div></td>"
                        else:
                            full_html += f"<td style='border:1px solid #999; text-align:center; {cell_bg}'>-</td>"
                    full_html += "</tr>"
                full_html += "</table></div>"
            full_html += "</div>"
            show_print_preview(full_html, "कक्षा-वार समय सारणी", orientation="portrait", school_id=DEFAULT_SCHOOL)

# ------------------------------------------------------------------------------
# Tab 3: अध्यापक-वार रिपोर्ट
# ------------------------------------------------------------------------------
with tab_teacher:
    st.subheader("👨‍🏫 अध्यापक रिपोर्ट")
    all_teachers = get_teachers(DEFAULT_SCHOOL)
    sel_teachers = st.multiselect("अध्यापक चुनें:", all_teachers)
    
    if st.button("🖨️ अध्यापक टाइम टेबल प्रिंट करें"):
        if not sel_teachers: st.error("अध्यापक चुनें।")
        else:
            full_html = ""
            for tch in sel_teachers:
                t_df = get_timetable_data(DEFAULT_SCHOOL, teacher=tch)
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
                slot_rows = get_time_slots(DEFAULT_SCHOOL)
                time_map = {row['period_name']: f"{row['start_time']} - {row['end_time']}" for _, row in slot_rows.iterrows()}
                valid_periods = slot_rows['period_name'].tolist()
                for p in valid_periods:
                    slot_time = time_map.get(p, "")
                    row_style = "background:#faf8e6;" if p in ['प्रार्थना सभा', 'मध्यांतर'] else ""
                    first_td_style = "border:1px solid #999; padding:4px; background:#f5f5f0;"
                    full_html += f"<tr style='{row_style}'><td style='{first_td_style}'><div style='font-weight:bold;'>{p}</div><div style='font-size:10px; color:#555; margin-top:2px;'>{slot_time}</div></td>"
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
        workload_df = pd.read_sql_query("SELECT teacher as 'अध्यापक', COUNT(*) as 'Periods' FROM timetable_data WHERE school_id=? GROUP BY teacher ORDER BY Periods DESC", conn, params=(DEFAULT_SCHOOL,))
        if workload_df.empty:
            st.info("डेटा उपलब्ध नहीं।")
        else:
            workload_df['Periods'] = workload_df['Periods'].astype(int)
            workload_df['Level'] = workload_df['Periods'].apply(lambda x: 'अधिक' if x >= 6 else ('मध्यम' if x >= 4 else 'कम'))

            total_teachers = len(workload_df)
            total_periods = int(workload_df['Periods'].sum())
            avg_periods = round(workload_df['Periods'].mean(), 1)
            busiest = workload_df.iloc[0]
            least_busy = workload_df.iloc[-1]

            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("कुल अध्यापक", total_teachers)
            kpi2.metric("कुल कालांश", total_periods)
            kpi3.metric("औसत प्रति अध्यापक", avg_periods)

            st.markdown("---")

            top_cards = st.columns(2)
            top_cards[0].metric("सबसे व्यस्त", busiest['अध्यापक'], f"{busiest['Periods']} कालांश")
            top_cards[1].metric("सबसे कम कार्यभार", least_busy['अध्यापक'], f"{least_busy['Periods']} कालांश")

            st.markdown("---")

            chart_col, table_col = st.columns([2, 1])
            chart_col.bar_chart(workload_df.set_index('अध्यापक')[['Periods']])
            table_col.dataframe(workload_df[['अध्यापक', 'Periods', 'Level']].rename(columns={'Periods': 'कालांश', 'Level': 'स्तर'}), use_container_width=True, hide_index=True)

            st.markdown("---")

            sel_teacher = st.selectbox("किस अध्यापक का विवरण देखें:", ["सभी अध्यापक"] + workload_df['अध्यापक'].tolist())
            if sel_teacher != "सभी अध्यापक":
                teacher_df = pd.read_sql_query("SELECT day as 'दिन', period as 'कालांश', subject as 'विषय', unified_class as 'कक्षा' FROM timetable_data WHERE school_id=? AND teacher=? ORDER BY day, period", conn, params=(DEFAULT_SCHOOL, sel_teacher))
                if teacher_df.empty:
                    st.warning("इस अध्यापक के लिए कोई टाइमटेबल रिकॉर्ड नहीं मिला।")
                else:
                    st.write(f"### ✏️ {sel_teacher} का टाइमटेबल")
                    st.dataframe(teacher_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"Error loading workload: {e}")

# ------------------------------------------------------------------------------
# Tab 5: रिक्त कालांश (Free Periods)
# ------------------------------------------------------------------------------
with tab_free:
    st.subheader("🈳 रिक्त कालांश")
    sel_day_free = st.selectbox("दिन चुनें:", ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार"])
    if st.button("🔍 चेक करें"):
        all_t = get_teachers(DEFAULT_SCHOOL)
        slots = get_time_slots(DEFAULT_SCHOOL)
        valid_p = [p for p in slots['period_name'] if p not in ["प्रार्थना सभा", "मध्यांतर"]]
        res = []
        for p in valid_p:
            busy = pd.read_sql_query("SELECT teacher FROM timetable_data WHERE school_id=? AND day=? AND period=?", conn, params=(DEFAULT_SCHOOL, sel_day_free, p))['teacher'].tolist()
            free = [t for t in all_t if t not in busy]
            res.append({"Period": p, "Free Count": len(free), "Teachers": ", ".join(free)})
        st.dataframe(pd.DataFrame(res), use_container_width=True, hide_index=True)

conn.close()