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
    # (Placeholder)

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

    # PDF Preview
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

    fetch_news = st.button("🔍 Fetch News for " + stock_dropdown)

    if fetch_news and stock_dropdown:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"🗂 Top News Links About {stock_dropdown}")
        with col2:
            st.subheader("🧠 News Summary and Sentiment")

        try:
            newsapi = NewsApiClient(api_key=os.getenv("NEWSAPI_KEY"))
            today = datetime.today()
            one_year_ago = today - timedelta(days=365)
            all_articles = newsapi.get_everything(
                q=stock_dropdown,
                from_param=one_year_ago.strftime('%Y-%m-%d'),
                language='en',
                sort_by='relevancy',
                page_size=5
            )

            for article in all_articles["articles"]:
                url = article["url"]
                title = article["title"]
                source = article["source"]["name"]
                published = article["publishedAt"]
                summary_col1, summary_col2 = st.columns([1, 2])

                with summary_col1:
                    st.write(f"🔗 [{title}]({url})")
                    st.caption(f"📰 {source} | 📅 {published[:10]}")

                with summary_col2:
                    if "OPENAI_API_KEY" in os.environ:
                        openai.api_key = os.environ["OPENAI_API_KEY"]
                        try:
                            response = requests.get(url, timeout=10)
                            soup = BeautifulSoup(response.text, "html.parser")
                            text = soup.get_text(" ", strip=True)[:3000]
                            ai_prompt = f"Summarize this financial news article and tag it as Positive, Negative or Neutral:\n{text}"
                            completion = openai.ChatCompletion.create(
                                model="gpt-4",
                                messages=[{"role": "user", "content": ai_prompt}]
                            )
                            summary = completion.choices[0].message.content
                            st.markdown(f"**Summary:** {summary}")
                        except Exception as e:
                            st.error(f"Summarization error: {e}")
                    else:
                        st.warning("OpenAI API key not found. Please set OPENAI_API_KEY.")

        except Exception as e:
            st.error(f"News API error: {e}")
