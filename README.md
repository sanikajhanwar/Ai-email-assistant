
# 📬 AI Email Assistant – Gmail Summarizer & Smart Reply Generator

An end-to-end **AI-powered Gmail assistant** built with **Streamlit**, which:
- Connects to your Gmail inbox
- Summarizes your latest or top-k emails using **Facebook BART**
- Generates professional reply suggestions using **Google Gemini AI**
- Displays everything in an intuitive web interface

> 🔐 100% private: All email processing is done locally after OAuth2 login.  
> 🧠 Ideal for busy professionals or anyone who wants quick email insights.

---

## 🚀 Features

✅ Gmail OAuth login with secure token storage  
✅ Fetch and display **latest or top-K important emails**  
✅ **Summarize** emails using `Facebook BART`  
✅ Generate **smart replies** with **Google Gemini AI**  
✅ Clean UI built with **Streamlit**  
✅ Supports both **single email** and **multi-email (top-K)** view  
✅ Desktop notifications (CLI mode) available via `gmailapi.py` script

---

## 🖥️ Tech Stack

| Layer         | Tools & Libraries |
|---------------|-------------------|
| **Frontend**  | Streamlit |
| **Email API** | Gmail API (`google-api-python-client`) |
| **Summarizer**| Facebook BART via HuggingFace Transformers |
| **Reply Gen.**| Google Gemini AI SDK |
| **NLP**       | NLTK, Scikit-learn, BeautifulSoup |
| **Extras**    | Plyer (for desktop notifications) |

---

## 📂 Project Structure

```

📦 ai-email-assistant
├── app.py                   # Streamlit frontend
├── gmailapi.py              # CLI utility for fetching & summarizing Gmail
├── client\_secret.json       # OAuth2 credentials for Gmail
├── requirements.txt         # All dependencies
├── .env                     # Gemini API Key and environment configs
├── .gitignore               # Ignores venv and keys
└── utils/
├── summarize\_email\_bart()     # Summarizes with BART
├── generate\_email\_reply()     # Generates replies using Gemini
└── fetch\_top\_k\_emails()       # Smart email ranking function

````

---

## ⚙️ Installation

### 1. 📁 Clone the Repo

```bash
git clone https://github.com/sanikajhanwar/ai-email-assistant.git
cd ai-email-assistant
````

### 2. 🧪 Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. 🔐 Set Up Credentials

* In **Google Cloud Console**:

  * Create a project → Enable Gmail API
  * Download `client_secret.json` and place it in the root directory

* In your `.env` file:

```ini
GEMINI_API_KEY=your_google_gemini_api_key
```

---

## ▶️ Run the App

```bash
streamlit run app.py
```

App will open in your browser at:
**[http://localhost:8501/](http://localhost:8501/)**
Or access the **live version** here:
🔗 [https://ai-email-assistant-6qwngbknnvvtwkggczgfvu.streamlit.app](https://ai-email-assistant-6qwngbknnvvtwkggczgfvu.streamlit.app)

---

## 🔍 Smart Email Selection

The app uses an intelligent **Top-K Email Ranking System**, which:

* Prioritizes longer, meaningful emails
* Removes spam or auto-generated system messages
* Lets you choose which email to view, summarize, or respond to

---

## 🧪 Alternate Usage (CLI Mode)

You can also run the standalone `gmailapi.py` script:

```bash
python gmailapi.py
```

It will:

* Fetch the latest email
* Summarize it using BART
* Generate a smart reply using Gemini
* Send a desktop notification

---

## 🎯 Future Improvements

* [ ] Add full inbox search & filters (sender, subject, etc.)
* [ ] Integrate calendar events summarization
* [ ] Auto-categorize emails by sentiment/priority
* [ ] Save drafts directly to Gmail

---

## 👩‍💻 Author

Built with ❤️ by **Sanika**
*Computer Science Engineer | AI & Product Enthusiast

```


