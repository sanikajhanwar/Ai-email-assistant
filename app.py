# --- app.py ---
import streamlit as st
import re
from gmailapi import (
    fetch_latest_email,
    summarize_email_bart,
    generate_email_reply,
    fetch_top_k_emails,
)

st.set_page_config(page_title="AI Email Assistant", page_icon="📬", layout="wide")
# Center content
left_col, center_col, right_col = st.columns([1, 2, 1])
with center_col:
    
    st.title("📬 AI Email Assistant")
    st.markdown("Get summaries & reply suggestions for your Gmail!")

    # === Mode Toggle ===
    mode = st.radio("Choose Mode:", ["Demo Mode (No Login)", "Gmail Mode (Login Required)"])
    if mode == "Gmail Mode (Login Required)":
        st.info("""
        To use this mode:
        - You must run the app locally on your machine
        - A browser window will open for Gmail login
        - Make sure your `credentials.json` is properly set up
        \n\n
        ❌ This won't work on Streamlit Cloud because Google login can't happen on shared servers.
        """)

    # === Tab Toggle ===
    tab = st.radio("Choose Task:", ["Latest Email", "Search Emails"])

    # === Demo Email ===
    demo_email = {
        "sender": "Amazon <order-update@amazon.in>",
        "date": "Fri, 18 Jul 2025 10:32:00 +0530",
        "subject": "Your order has been shipped!",
        "body": """
        Hello Sanika,

        Your order #123-4567890-1234567 has been shipped and will arrive by Tuesday.
        You can track your shipment in the Orders section of your Amazon account.

        Thank you for shopping with us!
        """
    }

    # === Handle Tabs ===
    if tab == "Latest Email":
        st.header("📥 Latest Email")

        if st.button("Check for New Email"):
            if mode == "Demo Mode (No Login)":
                sender = demo_email["sender"]
                date = demo_email["date"]
                email_text = demo_email["body"]
            else:
                with st.spinner("Fetching from Gmail..."):
                    sender, date, email_text, _ = fetch_latest_email(use_demo=(mode == "Demo Mode (No Login)"))


            if email_text:
                st.success("Email fetched!")
                st.markdown(f"**From:** `{sender}`  \\n**Date:** `{date}`")

                st.markdown("#### 📈 Email Content")
                st.code(email_text)

                with st.spinner("Summarizing..."):
                    summary = summarize_email_bart(email_text)
                st.markdown("#### 📝 Summary")
                st.info(summary)

                with st.spinner("Generating Replies..."):
                    replies = generate_email_reply(summary, sender)
                st.markdown("#### ✉️ Suggested Replies")
                for line in replies.split("\n"):
                    line = line.strip()
                    if line and re.match(r"^\d+\.", line):
                        st.code(line.split(".", 1)[1].strip())
            else:
                st.warning("No email found.")

    # === Smart Search Tab ===
    elif tab == "Search Emails":
        if mode == "Demo Mode (No Login)":
            st.info("Smart search only works with Gmail login.")
        else:
            st.header("🔎 Search Emails")
            keyword = st.text_input("Keyword (required)", placeholder="e.g. internship")
            k = st.slider("Number of emails to fetch", 1, 10, 3)

            if st.button("Fetch Emails"):
                if not keyword:
                    st.error("Enter a keyword.")
                else:
                    with st.spinner("Fetching emails..."):
                        results = fetch_top_k_emails(k=k, query_filter=keyword, use_demo=(mode == "Demo Mode (No Login)"))


                    if results:
                        for idx, mail in enumerate(results, 1):
                            with st.expander(f"📧 Email {idx} | {mail['sender']} | {mail['date']}"):
                                st.code(mail["text"])
                                summary = summarize_email_bart(mail["text"])
                                st.markdown("**Summary:**")
                                st.info(summary)
                                replies = generate_email_reply(summary, mail["sender"])
                                st.markdown("**Replies:**")
                                for line in replies.split("\n"):
                                    line = line.strip()
                                    if line and re.match(r"^\d+\.", line):
                                        st.code(line.split(".", 1)[1].strip())
