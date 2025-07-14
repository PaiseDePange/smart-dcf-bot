# 🗕️ Streamlit App to Fetch Company Filings (Using Screener.in)
import streamlit as st
import requests
from bs4 import BeautifulSoup
import streamlit.components.v1 as components

st.set_page_config(page_title="AI Investment Assistant", layout="wide")

# Custom CSS to increase tab label font size further
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab"] {
        font-size: 24px;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 AI-Powered Stock Analysis")

# Tabs for Navigation
tabs = st.tabs(["📥 Inputs", "📚 Fundamentals", "📈 Technical", "🧠 Conclusion", "🧪 Data Checks"])

# --- Tab 1: Inputs ---
with tabs[0]:
    st.header("📥 Inputs")
    st.markdown("Provide data to feed the AI for analysis.")

    st.subheader("1️⃣ Last Two Annual Reports")
    annual_links = [
        st.text_input("Annual Report Link 1 (PDF URL)"),
        st.text_input("Annual Report Link 2 (PDF URL)")
    ]

    st.subheader("2️⃣ Last 4 Earnings Call Transcripts")
    earnings_calls = [
        st.text_input("Earnings Call Transcript 1 (PDF URL)"),
        st.text_input("Earnings Call Transcript 2 (PDF URL)"),
        st.text_input("Earnings Call Transcript 3 (PDF URL)"),
        st.text_input("Earnings Call Transcript 4 (PDF URL)")
    ]

    st.subheader("3️⃣ Last 4 Investor Presentations")
    presentations = [
        st.text_input("Investor Presentation 1 (PDF URL)"),
        st.text_input("Investor Presentation 2 (PDF URL)"),
        st.text_input("Investor Presentation 3 (PDF URL)"),
        st.text_input("Investor Presentation 4 (PDF URL)")
    ]

    st.subheader("4️⃣ Screenshots from Screener.in")
    screener_images = {
        "Quarterly Results": st.file_uploader("Quarterly Results Screenshot", type=["png", "jpg", "jpeg"]),
        "Annual P&L": st.file_uploader("Annual P&L Screenshot", type=["png", "jpg", "jpeg"]),
        "Balance Sheet": st.file_uploader("Balance Sheet Screenshot", type=["png", "jpg", "jpeg"]),
        "Cashflows": st.file_uploader("Cashflows Screenshot", type=["png", "jpg", "jpeg"]),
        "Shareholding Pattern": st.file_uploader("Shareholding Pattern Screenshot", type=["png", "jpg", "jpeg"]),
    }

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
    st.markdown("Verify if uploaded images are converted correctly and if PDFs have readable text.")
    st.markdown("(Placeholder: This section will show previews or summaries of parsed data from uploaded documents and screenshots.)")
