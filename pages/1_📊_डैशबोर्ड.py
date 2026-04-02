###############################################################################
# SMART SCHOOL ERP v12.0 - DASHBOARD (MULTI-TENANT)
# File: 1_📊_डैशबोर्ड.py
###############################################################################

import streamlit as st
import pandas as pd
import datetime
import random

# 🌟 सभी ज़रूरी चीज़ें सही तरीके से import की गई हैं
from database import get_unified_class_list, get_current_school, get_school_info, get_teachers, get_subjects, load_css, day_map

# 🔒 जादुई सुरक्षा लॉक: यह लाइन लॉगिन हुए स्कूल का ID लेकर उसे DEFAULT_SCHOOL मान लेगी
DEFAULT_SCHOOL = get_current_school()

# 1. पेज कॉन्फ़िगरेशन
st.set_page_config(page_title="स्मार्ट स्कूल ईआरपी", page_icon="🏫", layout="wide", initial_sidebar_state="expanded")
load_css()

# डेटाबेस से स्कूल की जानकारी लाना
SCHOOL_NAME, SESSION_YEAR = get_school_info(DEFAULT_SCHOOL)

# ==============================================================================
# 2. साइडबार ब्रांडिंग (SIDEBAR LOGO & INFO)
# ==============================================================================
st.sidebar.markdown(f"""
    <div style='text-align: center; padding: 15px; background: #e0f2f1; border-radius: 10px; border: 1px solid #00695c; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        <h2 style='color: #004d40; margin:0; font-size: 1.5rem;'>🏫 स्मार्ट ERP v12</h2>
        <p style='margin:5px 0 0 0; font-size: 0.9rem; font-weight: bold; color:#00695c;'>{SCHOOL_NAME}</p>
        <p style='margin:0; font-size: 0.8rem; color:#555;'>सत्र: {SESSION_YEAR}</p>
    </div>
""", unsafe_allow_html=True)

# आज की तारीख
curr_date_str = datetime.date.today().strftime('%d-%m-%Y')
curr_day_str = day_map.get(datetime.datetime.now().strftime("%A"), "Unknown")
st.sidebar.info(f"📅 आज: **{curr_date_str}** ({curr_day_str})")

# डेवलपर क्रेडिट
st.sidebar.markdown("""
    <div style='text-align: center; margin-top: 30px; padding: 15px; background: #f1f8e9; border-radius: 8px; border: 1px dashed #a5d6a7;'>
        <small style='color: #555; text-transform: uppercase; font-weight: bold; letter-spacing: 1px;'>Concept & Logic</small><br>
        <b style='color: #2e7d32; font-size: 1.2em;'>रोहिताश कस्वाँ</b><br>
        <span style='font-size: 0.85em; color: #333;'>प्राध्यापक (हिंदी)</span><br>
        <span style='font-size: 0.8em; color: #666;'>रा.उ.मा.वि. जैतसीसर (चूरू)</span>
    </div>
""", unsafe_allow_html=True)

# ==============================================================================
# 3. मुख्य डैशबोर्ड स्क्रीन (MAIN DASHBOARD)
# ==============================================================================
st.markdown("<div class='header-box'><h1>🏫 विद्यालय डैशबोर्ड</h1><p>संपूर्ण विद्यालय की डिजिटल रिपोर्ट</p></div>", unsafe_allow_html=True)

# सुविचार लॉजिक
suvichar_list = [
    "विद्या ददाति विनयं। (विद्या विनम्रता देती है।)",
    "उद्यमेन हि सिध्यन्ति कार्याणि न मनोरथैः। (मेहनत से ही कार्य सिद्ध होते हैं, केवल इच्छा करने से नहीं।)",
    "सत्यमेव जयते। (सत्य की ही जीत होती है।)",
    "गुरुर्ब्रह्मा गुरुर्विष्णुः गुरुर्देवो महेश्वरः।",
    "आलस्य ही मनुष्य का सबसे बड़ा शत्रु है।",
    "शिक्षा वह शेरनी का दूध है जो पियेगा वह दहाड़ेगा। - डॉ. बी.आर. अंबेडकर",
    "सपने वो नहीं जो आप नींद में देखें, सपने वो हैं जो आपको नींद ही नहीं आने दें। - डॉ. कलाम",
    "उठो, जागो और तब तक नहीं रुको जब तक लक्ष्य ना प्राप्त हो जाये। - स्वामी विवेकानंद",
    "एक पेन, एक किताब, एक बच्चा, और एक शिक्षक पूरी दुनिया बदल सकते हैं। - मलाला",
    "ज्ञान एक ऐसा निवेश है जिसका मुनाफा जीवन भर मिलता रहता है।"
]
todays_quote = random.choice(suvichar_list)

st.markdown(f"""
    <div style="background: linear-gradient(to right, #e8f5e9, #c8e6c9); padding: 15px; border-radius: 10px; border-left: 5px solid #2e7d32; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <h4 style="color: #1b5e20; margin:0;">🌟 आज का सुविचार:</h4>
        <p style="font-size: 1.1rem; font-style: italic; color: #333; margin-top: 5px;">"{todays_quote}"</p>
    </div>
""", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

try:
    total_teachers = len(get_teachers(DEFAULT_SCHOOL))
    total_subjects = len(get_subjects(DEFAULT_SCHOOL))
    unified_classes = get_unified_class_list(DEFAULT_SCHOOL)
    
    c1.metric("👨‍🏫 कुल अध्यापक", total_teachers, border=True)
    c2.metric("📦 कुल कक्षाएं", len(unified_classes), border=True)
    c3.metric("📚 कुल विषय", total_subjects, border=True)
    c4.metric("🗓️ वर्तमान सत्र", SESSION_YEAR, border=True)
    
    # त्वरित कार्य
    st.markdown("### 🚀 त्वरित कार्य (Quick Actions)")
    qc1, qc2, qc3 = st.columns(3)
    
    if qc1.button("📅 टाइम टेबल बदलें", use_container_width=True):
        st.switch_page("pages/2_📅_टाइम_टेबल.py")
        
    if qc2.button("📝 व्यवस्था (Arrangement) लगाएं", use_container_width=True):
        st.switch_page("pages/4_📝_अध्यापक_व्यवस्था.py")
        
    if qc3.button("⚙️ नई कक्षा जोड़ें", use_container_width=True):
        st.switch_page("pages/6_⚙️_मास्टर_सैटिंग्स.py")

except Exception as e:
    st.error(f"डेटा लोड एरर: {e}")

st.markdown("---")
st.info("💡 **टिप:** टाइम टेबल भरने और रिपोर्ट देखने के लिए साइडबार (Menu) से अन्य पेज चुनें।")
