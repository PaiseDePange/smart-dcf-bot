# 🔕️ Streamlit App to Fetch Company Filings (Using Screener.in)
import streamlit as st
import requests
from bs4 import BeautifulSoup
import streamlit.components.v1 as components
from PyPDF2 import PdfReader
from PIL import Image
import io
import os
import shutil

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

    transcripts_files = st.file_uploader("Upload Earnings Call Transcripts (max 6)", type=["pdf"], accept_multiple_files=True)
    presentations_files = st.file_uploader("Upload Investor Presentations (max 6)", type=["pdf"], accept_multiple_files=True)
    annual_reports_files = st.file_uploader("Upload Annual Reports (max 6)", type=["pdf"], accept_multiple_files=True)

    st.subheader("📷 Screener.in Screenshots")
    screener_images = {
        "Quarterly Results": st.file_uploader("Quarterly Results Screenshot", type=["png", "jpg", "jpeg"], key="qr"),
        "Annual P&L": st.file_uploader("Annual P&L Screenshot", type=["png", "jpg", "jpeg"], key="pl"),
        "Balance Sheet": st.file_uploader("Balance Sheet Screenshot", type=["png", "jpg", "jpeg"], key="bs"),
        "Cashflows": st.file_uploader("Cashflows Screenshot", type=["png", "jpg", "jpeg"], key="cf"),
        "Shareholding Pattern": st.file_uploader("Shareholding Pattern Screenshot", type=["png", "jpg", "jpeg"], key="shp"),
    }

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
    st.markdown("Verify if uploaded images are converted correctly and if PDFs have readable text.")

    def tesseract_available():
        try:
            import pytesseract
            return shutil.which("tesseract") is not None
        except:
            return False

    if check_data:
        # OCR Check
        if tesseract_available():
            import pytesseract
            for label, uploaded_image in screener_images.items():
                if uploaded_image is not None:
                    try:
                        st.subheader(f"🖼️ OCR Preview: {label}")
                        image = Image.open(uploaded_image)
                        text = pytesseract.image_to_string(image)
                        st.image(image, caption=label)
                        st.text_area(f"Extracted Text - {label}", text, height=200)
                    except Exception as e:
                        st.error(f"Failed to process {label}: {e}")
        else:
            st.error("Image OCR failed: Tesseract is not installed or not found in PATH.")

        # PDF Preview
        def preview_pdf_text_from_file(uploaded_file):
            try:
                reader = PdfReader(uploaded_file)
                text = "\n".join(page.extract_text() or "" for page in reader.pages[:2])
                return text.strip()[:2000] if text else "No extractable text."
            except Exception as e:
                return f"Error reading PDF: {e}"

        all_groups = {
            "Earnings Call Transcripts": transcripts_files,
            "Investor Presentations": presentations_files,
            "Annual Reports": annual_reports_files,
        }

        for label, files in all_groups.items():
            for i, uploaded_file in enumerate(files or []):
                st.subheader(f"📄 Preview: {label} {i+1}")
                text = preview_pdf_text_from_file(uploaded_file)
                st.text_area(f"Extracted Text - {label} {i+1}", text, height=200)
