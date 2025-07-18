import os
import base64
import time
import nltk
import string
import numpy as np
import torch
import re
from datetime import datetime
from plyer import notification
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from transformers import BartTokenizer, BartForConditionalGeneration
import google.generativeai as genai
from googleapiclient.discovery import build

nltk.download('punkt')

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Load Gemini API key from environment variable
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')
model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service

def clean_email_body(body):
    if not body:
        return ""
    soup = BeautifulSoup(body, 'html.parser')
    text = soup.get_text()
    return re.sub(r'\s+', ' ', text).strip()

def extract_email_body(payload):
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif part['mimeType'] == 'text/html':
                html_body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                return clean_email_body(html_body)
    elif 'body' in payload and 'data' in payload['body']:
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    return ""

def fetch_latest_email(use_demo=False):
    if use_demo:
        return {
            "subject": "Demo: Internship Confirmation",
            "sender": "hr@company.com",
            "date": "2025-07-17",
            "body": "Dear Sanika, Congratulations! You have been selected for the AI internship..."
        }

    service = authenticate_gmail()
    results = service.users().messages().list(userId='me', maxResults=1, labelIds=['INBOX'], q="").execute()
    messages = results.get('messages', [])
    if not messages:
        return None

    msg = service.users().messages().get(userId='me', id=messages[0]['id']).execute()
    payload = msg['payload']
    headers = payload.get("headers", [])

    email_data = {
        "subject": "",
        "sender": "",
        "date": "",
        "body": extract_email_body(payload)
    }

    for header in headers:
        name = header['name'].lower()
        if name == 'subject':
            email_data['subject'] = header['value']
        elif name == 'from':
            email_data['sender'] = header['value']
        elif name == 'date':
            email_data['date'] = header['value']

    return email_data

def summarize_email_bart(text):
    inputs = tokenizer([text], max_length=1024, return_tensors='pt', truncation=True)
    summary_ids = model.generate(inputs['input_ids'], max_length=150, min_length=40, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

def generate_email_reply(prompt):
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)
    return response.text.strip()

def fetch_top_k_emails(k=3, query_filter="", use_demo=False):
    if use_demo:
        demo_emails = [
            {"subject": "Demo Email 1", "sender": "a@example.com", "date": "2025-07-01", "body": "This is demo email 1."},
            {"subject": "Demo Email 2", "sender": "b@example.com", "date": "2025-07-02", "body": "This is demo email 2."},
            {"subject": "Demo Email 3", "sender": "c@example.com", "date": "2025-07-03", "body": "This is demo email 3."}
        ]
        return demo_emails[:k]

    service = authenticate_gmail()
    results = service.users().messages().list(userId='me', maxResults=k, labelIds=['INBOX'], q=query_filter).execute()
    messages = results.get('messages', [])

    emails = []
    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        payload = msg_detail['payload']
        headers = payload.get("headers", [])
        email_data = {
            "subject": "",
            "sender": "",
            "date": "",
            "body": extract_email_body(payload)
        }
        for header in headers:
            name = header['name'].lower()
            if name == 'subject':
                email_data['subject'] = header['value']
            elif name == 'from':
                email_data['sender'] = header['value']
            elif name == 'date':
                email_data['date'] = header['value']
        emails.append(email_data)

    return emails

def notify_new_email(sender, date, summary):
    notification.notify(
        title=f"📬 New Email from {sender}",
        message=f"Date: {date}\n\nSummary:\n{summary}",
        timeout=10
    )
