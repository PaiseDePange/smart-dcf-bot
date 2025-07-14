# 🔕️ Streamlit App to Fetch Company Filings (Using Screener.in)
import streamlit as st
import requests
from bs4 import BeautifulSoup
import streamlit.components.v1 as components
from PyPDF2 import PdfReader
import io
import os
import shutil
from datetime import datetime, timedelta
from newsapi import NewsApiClient
import openai
import re
import pandas as pd

st.set_page_config(page_title="AI Investment Assistant", layout="wide")

# Custom CSS to increase tab label font size and freeze tab navigation
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab"] {
        font-size: 24px;
        font-weight: 700;
    }
    .stTabs {
        position: sticky;
        top: 0;
        background-color: #0e1117;
        z-index: 999;
        padding-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 AI-Powered Stock Analysis")

# Tabs for Navigation
tabs = st.tabs(["📥 Inputs", "📚 Fundamentals", "📈 Technical", "🧠 Conclusion", "🧪 Data Checks", "📰 News"])

# --- Tab 1: Inputs ---
with tabs[0]:
    st.header("📥 Inputs")
    st.markdown("Provide data to feed the AI for analysis.")

    stock_dropdown = st.selectbox("Select a stock", ["TCS", "INFY", "RELIANCE", "HDFC", "ICICIBANK", "LT", "SBIN", "WIPRO"])

    transcripts_files = st.file_uploader("Upload Earnings Call Transcripts (max 6)", type=["pdf"], accept_multiple_files=True)
    presentations_files = st.file_uploader("Upload Investor Presentations (max 6)", type=["pdf"], accept_multiple_files=True)
    annual_reports_files = st.file_uploader("Upload Annual Reports (max 6)", type=["pdf"], accept_multiple_files=True)

    check_data = st.button("🔍 Check Data Quality")

# --- Tab 2: Fundamentals ---
with tabs[1]:
    st.header("📚 Fundamental Analysis")
    st.markdown("This section will include extracted ratios, growth, and valuation models like DCF.")

    def extract_balance_sheet_text(file):
        try:
            reader = PdfReader(file)
            full_text = "\n".join(page.extract_text() or "" for page in reader.pages)
            # Look for patterns that resemble balance sheet sections
            match = re.search(r"(Consolidated Balance Sheet.*?)(\n\s*Consolidated Statement|\n\s*Statement of Profit|\n\s*Notes|\Z)", full_text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1)
            return "No balance sheet section found."
        except Exception as e:
            return f"Error reading balance sheet: {e}"

    if annual_reports_files:
        data_by_year = {}

        for uploaded_file in annual_reports_files:
            text = extract_balance_sheet_text(uploaded_file)
            year_match = re.search(r'(\d{4})\s*Consolidated Balance Sheet', text, re.IGNORECASE)
            year = year_match.group(1) if year_match else uploaded_file.name[-8:-4]
            data_by_year[year] = text

        st.subheader("📘 Extracted Balance Sheet Sections")

        for year, data in sorted(data_by_year.items()):
            st.text_area(f"Balance Sheet: {year}", data, height=300)

# --- Tab 3: Technical ---
with tabs[2]:
    st.header("📈 Technical Analysis")
    st.markdown("Technical indicators and chart positioning will be shown here.")
    # (Placeholder)

# --- Tab 4: Conclusion ---
with tabs[3]:
    st.header("🧠 Conclusion & Recommendation")
    st.markdown("This section will summarize findings and suggest an investment stance.")
    # (Placeholder)

# --- Tab 5: Data Checks ---
with tabs[4]:
    st.header("🧪 Data Quality Checks")
    st.markdown("Verify if uploaded PDFs have readable text.")

    def preview_pdf_text_from_file(uploaded_file):
        try:
            reader = PdfReader(uploaded_file)
            text = "\n".join(page.extract_text() or "" for page in reader.pages[:2])
            return text.strip()[:2000] if text else "No extractable text."
        except Exception as e:
            return f"Error reading PDF: {e}"

    if check_data:
        all_groups = {
            "Earnings Call Transcripts": transcripts_files,
            "Investor Presentations": presentations_files,
            "Annual Reports": annual_reports_files,
        }

        for label, files in all_groups.items():
            if files:
                st.subheader(f"📁 Uploaded: {label}")
                for i, uploaded_file in enumerate(files):
                    st.markdown(f"**📄 {uploaded_file.name}**")
                    text = preview_pdf_text_from_file(uploaded_file)
                    st.text_area(f"Extracted Text - {label} {i+1}", text, height=200)

# --- Tab 6: News ---
with tabs[5]:
    st.header("📰 Latest News About the Stock")
    st.markdown("This section summarizes news headlines from the past year with AI-powered summaries and sentiment analysis.")
    st.warning("News summarization module requires online access and API keys. This section will be enhanced later.")
