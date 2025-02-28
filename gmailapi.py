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
    # Remove excessive blank spaces
    return re.sub(r'\s+', ' ', email_text).strip() if email_text else "⚠️ No readable email content found."

# Fetch latest email
def fetch_latest_email():
    global LAST_CHECKED_ID
    service = authenticate_gmail()
    results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="category:primary", maxResults=1).execute()
    messages = results.get("messages", [])
    if not messages:
        return None, None, None, None
    message_id = messages[0]["id"]
    if message_id == LAST_CHECKED_ID:
        return None, None, None, None  # No new emails
    LAST_CHECKED_ID = message_id
    message = service.users().messages().get(userId='me', id=message_id, format="full").execute()
    payload = message.get("payload", {})
    headers = message.get("payload", {}).get("headers", [])
    email_text = extract_email_text(payload)
    sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")
    date = next((h["value"] for h in headers if h["name"] == "Date"), "Unknown Date")
    return sender, date, email_text, message_id

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

def generate_email_reply(email_summary):
    """Generates AI-powered reply suggestions using Google's Gemini AI."""
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
    response = model.generate_content(prompt)
    return response.text.strip() if response else "⚠️ No response generated."

# Show desktop notification
def notify_new_email(sender, date, summary):
    """Displays a system notification when a new email arrives."""
    notification_title = f"📩 New Email from {sender}"
    notification_message = f"📅 {date}\n🔍 Summary: {summary[:200]}..."  # Trim to avoid crashes
    notification.notify(
        title=notification_title,
        message=notification_message,
        timeout=20
    )

# Main script to monitor emails continuously
if __name__ == "__main__":
    print("🔍 Monitoring Gmail for new emails...")
    MAX_RUNS = 1
    run_count = 0
    while run_count < MAX_RUNS:
        sender, date, email_text, email_id = fetch_latest_email()
        if email_text:
            print(f"\n📩 New Email from: {sender}")
            print(f"📅 Received at: {date}")
            print("📌 Summary:")
            summary = summarize_email_bart(email_text)
            print(summary)
            print("\n✉️ Suggested Replies:")
            reply_suggestions = generate_email_reply(summary)
            print(reply_suggestions)
            notify_new_email(sender, date, summary)
        run_count += 1
        time.sleep(10)  # Check every 60 seconds
    print("✅ Stopping email monitoring.")
