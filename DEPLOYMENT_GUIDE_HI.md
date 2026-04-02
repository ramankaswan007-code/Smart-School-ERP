# 🚀 Smart School ERP - Streamlit Cloud Deployment Guide

**संस्करण**: v12.6  
**तारीख**: 2 अप्रैल 2026  
**स्थिति**: सभी तैयारियाँ संपन्न ✅

---

## 📋 तैयारी की गई चीजें

✅ Database का backup बनाया गया: `school_erp_SaaS_v12.db.backup`  
✅ `requirements.txt` में सभी dependencies जोड़े गए  
✅ `README.md` बनाई गई हिंदी+अंग्रेजी में  
✅ `.streamlit/config.toml` कॉन्फ़िगरेशन सेट किया गया  
✅ `.gitignore` बनाई गई (backup फाइलें exclude)  
✅ सभी changes GitHub पर push किए गए (commit: `659d7c3`)  

---

## 🎯 Streamlit Cloud पर Deploy करने के Steps

### **Step 1: Streamlit Cloud Account बनाएं**
1. https://streamlit.io पर जाएं
2. **"Sign up"** बटन दबाएं (ऊपर दाईं ओर)
3. अपने **GitHub account** से साइन अप करें
4. GitHub को Streamlit को authorize करने दें

### **Step 2: Dashboard में नया ऐप Deploy करें**
1. Streamlit Cloud dashboard खोलें
2. **"Create app"** बटन दबाएं (बाईं ओर)
3. निम्नलिखित भरें:

   ```
   Repository: ramankaswan007-code/Smart-School-ERP
   Branch:    main
   Main file: Main.py
   ```

4. **"Deploy"** बटन दबाएं

### **Step 3: Deploy होने दें**
- यह 2-3 मिनट लगेगा
- आप "Manage" → "Settings" से deployment देख सकते हैं
- एक बार Deploy होने के बाद, ऐप स्वचालित रूप से बड़ा URL मिलेगा:

   ```
   https://smart-school-erp.streamlit.app
   ```

---

## ⚙️ Post-Deployment Configuration

### **पहली बार चलाते समय:**
1. ऐप खोलें: https://smart-school-erp.streamlit.app
2. **Login Page** आएगा - यहाँ नया School बनाएं
3. School ID दें (जैसे: `school_001`)
4. Password सेट करें
5. **Login** करें

### **Master Settings में Configuration करें:**
1. साइडबार से **"⚙️ मास्टर सैटिंग्स"** खोलें
2. **पहली बार के लिए:**
   - **Tab 1**: विद्यालय का नाम और सत्र भरें
   - **Tab 2**: अध्यापकों की सूची जोड़ें
   - **Tab 3**: कक्षाएं सक्रिय करें
   - **Tab 4**: विषय जोड़ें
   - **Tab 5**: टाइम स्लॉट्स सेट करें
   - **Tab 6**: Subject-Teacher mapping करें

---

## 📊 Database Management

### **Cloud पर Database:**
- Streamlit Cloud में SQLite`.db` फाइल `/home/appuser/.streamlit/` में store होती है
- यह persistent है लेकिन app restart पर reset हो सकती है

### **Database Download करने के लिए:**
```bash
# Local terminal से (यदि SSH access है)
scp -i your-key user@streamlit-server:/path/to/school_erp_SaaS_v12.db ./backup.db
```

### **Production के लिए:**
यदि बहुत बड़े डेटा के साथ काम हो, तो **PostgreSQL** use करें:
1. Railway.app या Amazon RDS पर Database बनाएं
2. `database.py` में connection string बदलें
3. फिर से deploy करें

---

## 🔄 Updates करने के लिए

Code में कोई भी बदलाव करने के लिए:

```bash
# 1. Changes करें
# 2. Commit करें
git add .
git commit -m "Description of changes"

# 3. GitHub पर push करें
git push origin main

# 4. Streamlit Cloud स्वचालित रूप से redeploy करेगा
# (या Manage → Reboot करें)
```

---

## 🆘 समस्या निवारण

### **"ModuleNotFoundError: No module named 'streamlit'"**
- `requirements.txt` check करें
- Streamlit Cloud dashboard में "Reboot" करें

### **Database errors**
- Logs देखें: Dashboard → "Logs" section
- Local पर पहले test करें: `streamlit run Main.py`

### **App बहुत slow है**
- Database को optimize करें
- `requirements.txt` में caching libraries जोड़ें
- बड़े queries को break करें

### **GitHub changes नहीं दिख रहे**
```bash
git push origin main
# फिर Dashboard में "Reboot" → "Hard reboot"
```

---

## 🔐 Security Checklist

- ✅ SQL Injection prevention (parameterized queries)
- ✅ Session management implemented
- ✅ Role-based access control
- ℹ️ **Production में निम्न जोड़ें:**
  - API रेट limiting
  - Data encryption at rest
  - HTTPS (Streamlit Cloud स्वचालित)
  - Regular backups

---

## 📱 Access करने का URL

```
🌐 Production: https://github.com/ramankaswan007-code/Smart-School-ERP
📊 Streamlit App: https://smart-school-erp.streamlit.app
```

---

## 💡 अतिरिक्त Features (Future)

- [ ] Multi-language support (English-Hindi toggle)
- [ ] Mobile app (React Native)
- [ ] Email notifications
- [ ] Automated reports
- [ ] Advanced analytics dashboard
- [ ] WhatsApp integration

---

## 📞 Support

किसी समस्या के लिए:
1. GitHub Issues खोलें
2. Local पर reproduce करें
3. Logs attach करें
4. Detailed description दें

---

**Last Deployed**: 2 अप्रैल 2026  
**Deployed By**: GitHub Copilot  
**Version**: v12.6
