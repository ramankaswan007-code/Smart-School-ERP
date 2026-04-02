# 🏫 Smart School ERP SaaS v12.6

एक आधुनिक, भारतीय स्कूलों के लिए डिज़ाइन किया गया Enterprise Resource Planning (ERP) सिस्टम।

## ✨ मुख्य विशेषताएं

- 📊 **डैशबोर्ड**: स्कूल के महत्वपूर्ण आंकड़े
- 📅 **टाइम टेबल निर्माता**: AI-powered automatic scheduling
- 🏠 **लाइव ट्रेकर**: रियल-टाइम शिक्षक उपस्थिति ट्रैकिंग
- 📝 **व्यवस्था प्रबंधन**: अनुपस्थिति और प्रतिस्थापन प्रबंधन
- 📈 **व्यापक रिपोर्ट्स**: कक्षा, शिक्षक और कार्यभार विश्लेषण
- ⚙️ **मास्टर सेटिंग्स**: पूर्ण विद्यालय कॉन्फ़िगरेशन
- 💾 **डेटा बैकअप**: सुरक्षित बैकअप प्रबंधन
- 👥 **यूजर प्रबंधन**: रोल-आधारित एक्सेस कंट्रोल (Super Admin, Admin, User)

## 🛠️ तकनीकी विशेषताएं

- **Frontend**: Streamlit (Python)
- **Database**: SQLite3
- **Security**: Parameterized SQL queries (SQL injection prevention)
- **Architecture**: Multi-school SaaS platform

## 📋 आवश्यकताएं

- Python 3.8+
- pip package manager

## ⚡ स्थानीय रूप से चलाएं

### 1. Repository क्लोन करें
\`\`\`bash
git clone <repository-url>
cd Smart-School-ERP
\`\`\`

### 2. Dependencies इंस्टॉल करें
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. ऐप चलाएं
\`\`\`bash
streamlit run Main.py
\`\`\`

ऐप `http://localhost:8501` पर खुलेगा

## 🚀 Streamlit Cloud पर Deploy करें

### Step 1: GitHub पर Push करें
\`\`\`bash
git add .
git commit -m "Deploy v12.6 with security improvements"
git push origin main
\`\`\`

### Step 2: Streamlit Cloud पर Account बनाएं
1. [streamlit.io](https://streamlit.io) पर जाएं
2. "Sign up" करें अपने GitHub account से
3. Dashboard खोलें

### Step 3: नया ऐप Deploy करें
1. Dashboard में "Create App" बटन दबाएं
2. अपनी repository चुनें
3. Branch: `main` चुनें
4. Main file path: `Main.py` रखें
5. **Deploy** बटन दबाएं

![Streamlit Deploy](https://docs.streamlit.io/static/img/deploy-diagram.jpeg)

### Step 4: Database Configuration (Important!)
Deploy करने के बाद:
1. Streamlit Cloud में अपनी ऐप खोलें
2. पहली बार login करते समय:
   - School ID: कोई भी यूनिक ID दें (जैसे: `school_001`)
   - यह database में स्वयं जुड़ जाएगा
3. Master Settings से school configuration पूरी करें

## ⚠️ महत्वपूर्ण नोट्स

- **Database**: SQLite (.db फाइल) Streamlit Cloud के filesystem में store होती है
- **Data Persistence**: Production के लिए PostgreSQL या अन्य cloud database की सलाह दी जाती है
- **Backup**: नियमित backup लें (Local पर डाउनलोड करें)
- **Performance**: 1000+ records के लिए database optimization की आवश्यकता हो सकती है

## 📱 Browser Compatibility
- Chrome ✅
- Firefox ✅
- Safari ✅
- Edge ✅

## 🔒 सुरक्षा Features

- SQL Injection Prevention (Parameterized Queries)
- Session Management
- Role-based Access Control
- Password-based Authentication

## 🐛 Bug Reports & Features
किसी समस्या के लिए या नई feature के लिए issue खोलें।

## 📝 लाइसेंस
Proprietary - Internal Use Only

---
**विकास**: Rohitash Kaswan  
**संस्करण**: SaaS v12.6  
**अंतिम अपडेट**: April 2026
