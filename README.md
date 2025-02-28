# 📩 AI-Powered Email Summarization & Reply Generation  

This project is an **AI-powered email summarization and reply suggestion system** that:  
- **Fetches emails** from Gmail using the **Gmail API**  
- **Extracts and cleans email text** (removing HTML content)  
- **Summarizes emails** using **Facebook BART (Transformers)**  
- **Generates smart email replies** using **Google Gemini AI**  
- **Notifies users** of new emails via **desktop notifications**  

---

## 🚀 Features  

✅ **Fetches latest email** from Gmail automatically  
✅ **Summarizes email content** in a short, structured format  
✅ **Suggests AI-generated professional replies**  
✅ **Provides desktop notifications for new emails**  
✅ **Uses BART for summarization & Gemini AI for responses**  

---

## 🛠️ Installation  

### 1️⃣ Manually Upload Files  
Since this project is being manually uploaded to GitHub, **cloning is not required**.  
Ensure you have all the following files in one directory before running the project:  
- `gmailapi.py`  
- `client_secret.json` (Gmail API credentials)  
- `requirements.txt` (dependencies)  

### 2️⃣ Install Dependencies  
Once all the files are in place, install required Python libraries using:  
```bash
pip install -r requirements.txt
```

### 3️⃣ Set up Gmail API  
- Go to **Google Cloud Console** → **Create a Project**  
- Enable **Gmail API**  
- Download `client_secret.json` (OAuth Credentials)  
- Place `client_secret.json` inside your project directory  
- Authenticate your Gmail account:  

```bash
python gmailapi.py
```

The script will:  
- **Fetch new emails**  
- **Summarize them**  
- **Suggest AI-powered replies**  
- **Show a desktop notification**  

If no new emails are found, the script will wait and check again.  

---

## 🖥️ Tech Stack  
This project leverages the following technologies:  

- **Large Language Models (LLMs):**
  - **Facebook BART (Hugging Face Transformers)** for email summarization  
  - **Google Gemini AI** for generating smart email replies  

- **APIs & Authentication:**
  - **Gmail API** (Google API Client) for fetching emails  
  
- **Text Processing & NLP:**
  - `nltk`, `scikit-learn` for natural language processing  
  - `beautifulsoup4` for HTML parsing  

- **Machine Learning & Deep Learning:**
  - `numpy`, `torch`, `transformers` for AI model operations  

- **System Notifications:**
  - `plyer` for sending desktop notifications  

---

## 📦 Dependencies  
This project requires the following Python libraries (included in `requirements.txt`):  

- `google-auth`, `google-auth-oauthlib`, `google-api-python-client` (For Gmail API)  
- `numpy`, `torch`, `transformers` (For AI models)  
- `nltk`, `scikit-learn` (For text processing)  
- `beautifulsoup4` (For HTML parsing)  
- `plyer` (For desktop notifications)  

To install all dependencies:  
```bash
pip install -r requirements.txt
```

---

## ⚠️ Important Notes  
- **Remove API keys from the script before pushing to GitHub.**  
- The project currently supports **Gmail accounts only**.  
- The **BART model** may take a few seconds depending on email length.  
- The script fetches **only the latest email** (modify `fetch_latest_email()` to change this).  

---

## 🎯 Future Improvements  
🔹 **Multi-email support:** Fetch multiple emails at once  
🔹 **Better reply suggestions:** More personalized responses  
🔹 **Email sentiment analysis:** Classify emails as urgent, neutral, or low-priority  
🔹 **Automatic email categorization**  

---

## 👨‍💻 Author  
Developed by **Sanika** 🚀  

---

## ⭐ Contributions  
Feel free to **fork, improve, and create pull requests!**

