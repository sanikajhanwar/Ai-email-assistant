import google.generativeai as genai
import os
import base64
import time
import nltk
import string
import numpy as np
import torch
import re
from datetime import datetime
from plyer import notification  # For desktop notifications
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from transformers import BartTokenizer, BartForConditionalGeneration

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
LAST_CHECKED_ID = None  # Stores the last email ID to prevent duplicate notifications

# DEMO EMAIL FALLBACK
DEMO_EMAILS = [
    {
        "sender": "Product Team <demo@example.com>",
        "date": "Thu, 18 Jul 2024 14:20:00 +0530",
        "text": "Hey Sanika, we're excited to inform you about our new feature updates including personalized dashboards, faster load times, and dark mode support. Stay tuned for more!",
        "id": "demo_1"
    },
    {
        "sender": "College <admissions@university.edu>",
        "date": "Wed, 17 Jul 2024 09:30:00 +0530",
        "text": "Dear Student, This is a reminder that the deadline for project submission is 20th July. Please ensure all documents are uploaded via the portal.",
        "id": "demo_2"
    },
    {
        "sender": "Hackathon Team <noreply@event.com>",
        "date": "Tue, 16 Jul 2024 17:10:00 +0530",
        "text": "Hi Sanika, Thanks for registering for HackRush 2024. The opening ceremony is on July 22nd at 10 AM. Team details will be shared soon.",
        "id": "demo_3"
    }
]

# Function to authenticate Gmail API
def authenticate_gmail():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

# Function to extract email text and clean HTML tags
def extract_email_text(payload):
    email_text = ""
    if "parts" in payload:
        for part in payload["parts"]:
            mime_type = part.get("mimeType", "")
            body_data = part.get("body", {}).get("data", "")
            if body_data:
                decoded_data = base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")
                if mime_type == "text/plain":
                    return decoded_data.strip()
                if mime_type == "text/html" and not email_text:
                    soup = BeautifulSoup(decoded_data, "html.parser")
                    email_text = soup.get_text(separator="\n").strip()
    return re.sub(r'\s+', ' ', email_text).strip() if email_text else "⚠️ No readable email content found."

def fetch_latest_email(use_demo=False):
    if use_demo:
        email = DEMO_EMAILS[0]
        return email["sender"], email["date"], email["text"], email["id"]

    service = authenticate_gmail()
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="category:primary", maxResults=1).execute()
    messages = results.get("messages", [])

    if not messages:
        return None, None, None, None

    msg_data = service.users().messages().get(userId='me', id=messages[0]['id'], format='full').execute()
    payload = msg_data.get("payload", {})
    headers = payload.get("headers", [])
    email_text = extract_email_text(payload)
    sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
    date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown Date")
    return sender, date, email_text, messages[0]["id"]


# Fetch recent emails (real or demo based on mode)
def fetch_top_k_emails(k=3, query_filter=None, use_demo=False):
    if use_demo:
        return DEMO_EMAILS[:k]

    service = authenticate_gmail()
    query = "category:primary"
    if query_filter:
        query += f" {query_filter}"

    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q=query, maxResults=k).execute()
    messages = results.get("messages", [])

    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        payload = msg_data.get("payload", {})
        headers = msg_data.get("payload", {}).get("headers", [])
        email_text = extract_email_text(payload)
        sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
        date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown Date")
        emails.append({
            "sender": sender,
            "date": date,
            "text": email_text,
            "id": msg["id"]
        })
    return emails

# Summarize email using BART
def summarize_email_bart(email_text):
    tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
    model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
    inputs = tokenizer.encode("summarize: " + email_text, return_tensors="pt", max_length=1024, truncation=True)
    summary_ids = model.generate(inputs, max_length=100, min_length=30, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary_text = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return "\n- " + "\n- ".join(summary_text.split(". "))

# Configure Gemini AI API (REMOVE KEY BEFORE USING)
genai.configure(api_key="AIzaSyAB0960f4CkcapfdEZpsLMFvFhyoyAbQaE")

def generate_email_reply(email_summary, sender_email):
    if "no-reply" in sender_email.lower() or "noreply" in sender_email.lower():
        return "⚠️ This is a no-reply email. No response required."

    prompt = f"""
    Based on the following email summary, provide only 3 short professional replies.
    Do not include any other text.

    Email Summary:
    {email_summary}

    Suggested Replies:
    1.
    2.
    3.
    """
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    response = model.generate_content(prompt, stream=True)

    collected = []
    for chunk in response:
        if chunk.text:
            collected.append(chunk.text)
    return ''.join(collected).strip() if collected else "⚠️ No response generated."

# Show desktop notification
def notify_new_email(sender, date, summary):
    notification_title = f"📩 New Email from {sender}"
    notification_message = f"📅 {date}\n🔍 Summary: {summary[:200]}..."
    notification.notify(
        title=notification_title,
        message=notification_message,
        timeout=20
    )

# Run as script to test locally
if __name__ == "__main__":
    print("🔍 Monitoring Gmail for new emails...")
    MAX_RUNS = 1
    run_count = 0
    while run_count < MAX_RUNS:
        emails = fetch_top_k_emails(k=1, use_demo=False)
        if not emails:
            print("❌ No new email.")
            break
        email = emails[0]
        print(f"\n📩 New Email from: {email['sender']}")
        print(f"📅 Received at: {email['date']}")
        print("📌 Summary:")
        summary = summarize_email_bart(email['text'])
        print(summary)
        print("\n✉️ Suggested Replies:")
        reply_suggestions = generate_email_reply(summary, email['sender'])
        print(reply_suggestions)
        notify_new_email(email['sender'], email['date'], summary)
        run_count += 1
        time.sleep(10)
    print("✅ Stopping email monitoring.")
