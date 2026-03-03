###############################################################################
# SMART SCHOOL ERP v12.0 - SUPER ADMIN BACKUP (MULTI-TENANT SaaS)
# File: pages/7_💾_डेटा_बैकअप.py
###############################################################################

import streamlit as st
import datetime
import time
# 🌟 बदलाव: डायनामिक DB_FILE और यूजर चेक इम्पोर्ट किया
from database import DB_FILE, get_current_school

st.set_page_config(page_title="सुपर एडमिन बैकअप", page_icon="💾", layout="wide")

# 🔒 सुरक्षा जाँच: केवल Super Admin ही इसे देख सके
if st.session_state.get('role') != 'super_admin':
    st.error("🚫 **Access Denied:** यह पेज केवल सॉफ़्टवेयर निर्माता (Super Admin) के लिए आरक्षित है।")
    st.stop()

# 🌟 सुपर एडमिन के लिए लाल रंग की प्रीमियम थीम
st.markdown("""
    <div style='background: linear-gradient(135deg, #b71c1c, #c62828); padding: 25px; border-radius: 12px; text-align: center; margin-bottom: 25px; color: white; box-shadow: 0 4px 12px rgba(0,0,0,0.15); border-bottom: 4px solid #7f0000;'>
        <h1 style='margin: 0; color: white;'>⚙️ सुपर एडमिन बैकअप पैनल</h1>
        <p style='color: #ffcdd2; margin-top: 5px;'>संपूर्ण SaaS मास्टर डेटाबेस (सभी स्कूलों का डेटा) प्रबंधन</p>
    </div>
    """, unsafe_allow_html=True)

st.warning("⚠️ **SaaS सुरक्षा चेतावनी:** इस `.db` फ़ाइल में पोर्टल पर पंजीकृत **सभी विद्यालयों** का डेटा, पासवर्ड और सेटिंग्स मौजूद हैं। बैकअप फ़ाइल को किसी के साथ साझा न करें।")

col_bk, col_rs = st.columns(2)

# --- 1. डाउनलोड (Master Backup) ---
with col_bk:
    st.subheader("📥 मास्टर बैकअप (Download)")
    st.info("पूरे सर्वर का बैकअप लेने के लिए नीचे बटन दबाएं। इसमें सभी स्कूलों का डेटा शामिल है।")
    try:
        with open(DB_FILE, "rb") as f:
            db_bytes = f.read()
        
        st.download_button(
            label="📥 मास्टर डेटाबेस डाउनलोड करें (.db)",
            data=db_bytes,
            file_name=f"SmartERP_MASTER_BACKUP_{datetime.date.today()}.db",
            mime="application/octet-stream",
            help="यह सभी स्कूलों के डेटा की एक कॉपी डाउनलोड करेगा।",
            type="primary"
        )
    except Exception as e: 
        st.error(f"डेटाबेस फाइल नहीं मिली: {e}")

# --- 2. अपलोड/रिस्टोर (Master Restore) ---
with col_rs:
    st.subheader("📤 मास्टर रिस्टोर (Restore)")
    st.error("⚠️ सावधानी: रिस्टोर करने से वर्तमान का सारा डेटा (सभी स्कूलों का) मिट जाएगा!")
    
    up_db = st.file_uploader("मास्टर बैकअप फाइल (.db) अपलोड करें:", type=["db"])
    
    if up_db:
        # रिस्टोर के लिए डबल कन्फर्मेशन
        confirm = st.checkbox("मैं समझता हूँ कि यह पूरे सर्वर का डेटा बदल देगा।")
        
        if st.button("🚀 रिस्टोर प्रक्रिया शुरू करें", type="secondary", disabled=not confirm):
            with st.spinner("सर्वर डेटा रिस्टोर हो रहा है..."):
                try:
                    with open(DB_FILE, "wb") as f:
                        f.write(up_db.getbuffer())
                    
                    st.success("✅ संपूर्ण SaaS डेटा सफलतापूर्वक रिस्टोर हो गया!")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                except Exception as e: 
                    st.error(f"Error during restore: {e}")

st.markdown("---")
st.caption(f"वर्तमान सर्वर फ़ाइल: {DB_FILE} | आज की तिथि: {datetime.date.today()}")